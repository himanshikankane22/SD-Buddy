"""Service Desk L1 Copilot — FastAPI application."""
from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .config import get_settings
from .flows import bitlocker, mfa_reset, password_reset
from .flows.router import detect_flow, flow_meta, process_flow, start_flow
from .llm.client import LLMError, OpenRouterClient
from .llm.prompts import make_chat_messages
from .rag.tfidf import format_context
from .sessions import Session, get_store
from .tickets.generator import build_ticket_draft, submit_ticket
from .triage.classifier import classify_type
from .triage.config import load_triage_config
from .triage.priority import detect_priority, guess_impact_urgency

settings = get_settings()

app = FastAPI(title=settings.app_name, version=settings.app_version)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

llm = OpenRouterClient()
store = get_store()


# --------------------------------------------------------------------------- #
# Schemas
# --------------------------------------------------------------------------- #
class SessionCreate(BaseModel):
    role: str = Field("end_user", pattern="^(end_user|l1)$")
    channel: str = Field("chat", pattern="^(call|chat|email|portal)$")


class ChatRequest(BaseModel):
    session_id: str
    message: str
    role: str = Field("end_user", pattern="^(end_user|l1)$")
    channel: str = Field("chat", pattern="^(call|chat|email|portal)$")


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    history: list[dict]
    flow: dict | None = None
    ticket: dict | None = None
    triage: dict | None = None
    llm_used: bool = False
    major_incident: bool = False


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _session(session_id: str) -> Session:
    session = store.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


def _flow_snapshot(session: Session) -> dict | None:
    if not session.active_flow:
        return None
    key = session.active_flow
    state = session.flow_state or {}
    meta = flow_meta(key)
    if meta is None:
        return None

    # Per-flow step ordering for progress display.
    step_orders = {
        password_reset.FLOW_NAME: ["identity", "ad_check", "reset", "advice", "done"],
        bitlocker.FLOW_NAME: ["identity", "device", "retrieve", "confirm", "done"],
        mfa_reset.FLOW_NAME: ["identity", "scenario", "reset", "confirm", "done"],
    }
    order = step_orders.get(key, [])
    step = state.get("step", "identity")
    idx = order.index(step) if step in order else 0
    total = len(order)

    identity = state.get("identity") or {}
    field_index = identity.get("field_index", 0)
    identity_total = 6

    return {
        "key": key,
        "label": meta["label"],
        "name": meta["name"],
        "step": step,
        "step_index": idx,
        "step_total": total,
        "identity_progress": field_index,
        "identity_total": identity_total,
        "done": step == "done",
    }


def _apply_triage(session: Session, message: str, channel: str) -> dict:
    """Run the triage engine on the latest user message, store on session."""
    config = load_triage_config()
    classified = classify_type(message, config)
    impact_urgency = guess_impact_urgency(message, config)
    priority = detect_priority(
        impact_urgency["impact"],
        impact_urgency["urgency"],
        message,
        config,
    )
    triage = {
        "record_type": classified["type"],
        "type_confidence": classified["confidence"],
        "impact": priority["impact"],
        "urgency": priority["urgency"],
        "priority": priority["priority"],
        "priority_name": priority["priority_name"],
        "major_incident": priority["major_incident"],
        "response_sla": priority["response_sla"],
        "resolution_sla": priority["resolution_sla"],
    }
    session.context["last_triage"] = triage
    session.context["last_contact"] = message
    return triage


def _build_draft(session: Session, description: str) -> dict:
    triage = session.context.get("last_triage") or _apply_triage(session, description, session.channel)
    return build_ticket_draft(
        description=description,
        record_type=triage["record_type"],
        impact=triage["impact"],
        urgency=triage["urgency"],
        channel=session.channel,
        caller=session.context.get("caller", ""),
        priority=triage["priority"],
    )


def _finalize_ticket(session: Session, draft: dict) -> dict:
    """Persist draft to the mock ServiceNow store and return enriched ticket dict."""
    ticket = submit_ticket(draft)
    session.ticket = ticket.to_dict()
    return session.ticket


# --------------------------------------------------------------------------- #
# Routes
# --------------------------------------------------------------------------- #
@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
        "llm_configured": llm.available,
        "model": settings.openrouter_model,
    }


@app.post("/api/session")
def create_session(body: SessionCreate) -> dict:
    session = store.create(role=body.role, channel=body.channel)
    return {"session_id": session.id, "role": session.role, "channel": session.channel}


@app.get("/api/session/{session_id}")
def get_session(session_id: str) -> dict:
    session = _session(session_id)
    return {
        "session_id": session.id,
        "role": session.role,
        "channel": session.channel,
        "history": session.history,
        "flow": _flow_snapshot(session),
        "ticket": session.ticket,
        "context": session.context,
    }


@app.post("/api/chat", response_model=ChatResponse)
def chat(body: ChatRequest) -> ChatResponse:
    session = _session(body.session_id)
    session.role = body.role
    session.channel = body.channel

    user_msg = body.message.strip()
    if not user_msg:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    session.history.append({"role": "user", "content": user_msg})
    session.context["caller"] = session.context.get("caller", "")

    # Run triage on the latest message (Incident/SR, priority, major incident).
    triage = _apply_triage(session, user_msg, body.channel)

    # ------------------------------------------------------------------ #
    # Guided flows take priority over free-form chat.
    # ------------------------------------------------------------------ #
    if session.active_flow:
        try:
            result = process_flow(session.active_flow, user_msg, session.flow_state or {})
        except Exception as exc:  # noqa: BLE001 - guard demo runtime
            session.active_flow = None
            session.flow_state = None
            reply = f"Something went wrong in that flow ({exc}). I've reset it — how can I help?"
            session.history.append({"role": "assistant", "content": reply})
            return ChatResponse(
                session_id=session.id,
                reply=reply,
                history=list(session.history),
                flow=None,
                ticket=session.ticket,
                triage=triage,
                major_incident=triage["major_incident"],
            )

        session.flow_state = result["state"]
        messages = result.get("messages", [])
        reply = "\n\n".join(messages)
        session.history.append({"role": "assistant", "content": reply})

        if result.get("cancel"):
            session.active_flow = None
            session.flow_state = None

        if result.get("ticket"):
            session.ticket = _finalize_ticket(session, result["ticket"])

        if result.get("done") and not result.get("cancel"):
            session.active_flow = None
            session.flow_state = None

        return ChatResponse(
            session_id=session.id,
            reply=reply,
            history=list(session.history),
            flow=None if session.active_flow is None else _flow_snapshot(session),
            ticket=session.ticket,
            triage=triage,
            major_incident=triage["major_incident"],
        )

    # ------------------------------------------------------------------ #
    # Detect & start a guided flow.
    # ------------------------------------------------------------------ #
    flow_key, meta = detect_flow(user_msg)
    if flow_key and meta:
        session.active_flow = flow_key
        session.flow_state = start_flow(flow_key)
        first = session.flow_state
        intro = _flow_intro(flow_key, first)
        reply = f"Sure — let me walk you through the **{meta['label']}** process.\n\n{intro}"
        session.history.append({"role": "assistant", "content": reply})
        return ChatResponse(
            session_id=session.id,
            reply=reply,
            history=list(session.history),
            flow=_flow_snapshot(session),
            ticket=session.ticket,
            triage=triage,
            major_incident=triage["major_incident"],
        )

    # ------------------------------------------------------------------ #
    # Free-form: RAG + LLM.
    # ------------------------------------------------------------------ #
    context = format_context(user_msg, top_k=5)
    history_for_llm = [
        {"role": m["role"], "content": m["content"]} for m in session.history[-8:]
    ]
    messages = make_chat_messages(session.role, history_for_llm, context)

    llm_used = False
    if llm.available:
        try:
            reply = llm.chat(messages)
            llm_used = True
        except LLMError as exc:
            reply = (
                "I couldn't reach the LLM service. "
                f"_(backend note: {exc})_ — here's a fallback:\n\n"
                + _fallback_answer(user_msg)
            )
    else:
        reply = _fallback_answer(user_msg)

    session.history.append({"role": "assistant", "content": reply})
    return ChatResponse(
        session_id=session.id,
        reply=reply,
        history=list(session.history),
        flow=None,
        ticket=session.ticket,
        triage=triage,
        major_incident=triage["major_incident"],
        llm_used=llm_used,
    )


@app.post("/api/ticket")
def raise_ticket(body: ChatRequest) -> dict:
    """Explicitly raise a ticket from the current session context."""
    session = _session(body.session_id)
    session.role = body.role
    session.channel = body.channel

    description = body.message or session.context.get("last_contact", "User request — no description captured.")
    if not body.message.strip():
        description = session.context.get("last_contact", description)

    draft = _build_draft(session, description)
    ticket = _finalize_ticket(session, draft)
    return {"ticket": ticket}


@app.get("/api/kb")
def list_kb() -> dict:
    from .rag.loader import load_kb_sections

    sections = load_kb_sections()
    topics: dict[str, list[str]] = {}
    for sec in sections:
        topics.setdefault(sec.source, []).append(sec.title)
    return {"topics": topics}


@app.get("/api/triage/config")
def triage_config() -> dict:
    config = load_triage_config()
    return {
        "matrix": config.matrix,
        "priorities": config.priorities,
        "categories": config.categories,
    }


@app.post("/api/agent/nexthink")
def nexthink_action(body: dict[str, Any]) -> dict:
    """L1-only: simulate a Nexthink remote action."""
    from .integrations.nexthink import get_nexthink

    action = body.get("action", "")
    device = body.get("device", "")
    if not action or not device:
        raise HTTPException(status_code=400, detail="action and device are required")
    return get_nexthink().run(action, device)


def _flow_intro(flow_key: str, state: dict) -> str:
    """Return the first question/prompt for a freshly started flow."""
    if flow_key == password_reset.FLOW_NAME:
        return (
            "To verify your identity, please confirm your **employee code** (e.g. JDE-10452). "
            "I'll ask a few short security questions first — this matches what our L1 team does "
            "before any password reset."
        )
    if flow_key == bitlocker.FLOW_NAME:
        return (
            "To verify your identity, please confirm your **employee code** (e.g. JDE-10452). "
            "Then I'll verify the device before retrieving your recovery key."
        )
    if flow_key == mfa_reset.FLOW_NAME:
        return (
            "To verify your identity, please confirm your **employee code** (e.g. JDE-10452). "
            "Then I'll help you re-register your MFA."
        )
    return "Please confirm your **employee code**."


def _fallback_answer(text: str) -> str:
    """Simple deterministic fallback when no LLM is configured (demo resilience)."""
    t = text.lower()
    config = load_triage_config()
    if config.is_major(text):
        return (
            "🚨 **Major Incident detected.** This matches a high-severity pattern "
            "(site/network/system down or security concern). I've flagged it and the "
            "L1 team will escalate immediately with a bridge call. A P1 ticket is being raised."
        )
    if any(k in t for k in ("password", "login", "sign in")):
        return (
            "I can help with that. For a **password reset**, I can run the guided flow "
            "(identity verification → AD reset → temporary password). Type **password reset** "
            "to start. For anything else, our L1 team is on chat/call 24x7."
        )
    if "bitlocker" in t or "recovery key" in t:
        return (
            "I can help with **BitLocker recovery**. Type **bitlocker** to start the guided flow — "
            "I'll verify your identity and device, then retrieve the key from Entra ID and share "
            "it securely."
        )
    if "mfa" in t or "authenticator" in t:
        return (
            "I can help with an **MFA reset**. Type **mfa reset** to start the guided flow — "
            "I'll verify your identity, decide the right reset (re-register and/or revoke sessions), "
            "and have you re-register."
        )
    return (
        "I've noted your request. For the fastest resolution, try the guided flows: "
        "**password reset**, **bitlocker**, or **mfa reset**. If it's something else, "
        "the L1 team can pick this up from the ticket on the panel."
    )
