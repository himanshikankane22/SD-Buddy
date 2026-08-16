import { useEffect, useRef, useState } from "react";
import { createSession, getHealth, sendMessage } from "./api";
import { ChannelSelector } from "./components/ChannelSelector";
import { FlowWizard } from "./components/FlowWizard";
import { MessageBubble } from "./components/MessageBubble";
import { PriorityBanner } from "./components/PriorityBanner";
import { RoleToggle } from "./components/RoleToggle";
import { TicketPanel } from "./components/TicketPanel";
import { TypingIndicator } from "./components/TypingIndicator";
import type { Channel, ChatMessage, ChatResponse, FlowSnapshot, HealthInfo, Role, Ticket, Triage } from "./types";

const SUGGESTIONS = [
  "I forgot my password, please reset",
  "My laptop needs a BitLocker recovery key",
  "I got a new phone, my MFA isn't working",
  "Outlook is not syncing my email",
  "SAP says my user is locked",
];

const WELCOME_END_USER =
  "Hi! I'm **SD Buddy**, your IT Service Desk assistant. I can help you reset passwords, " +
  "recover BitLocker keys, fix MFA, and more — and I'll draft a ticket for you as we go.\n\n" +
  "Try one of the quick actions below, or just tell me what's going on.";

const WELCOME_L1 =
  "Hi, agent! I'm **SD Buddy** in L1 copilot mode. I'll give you runbook steps, triage, " +
  "and ticket drafts as you work a ticket. Try: \"password reset for a locked user\", " +
  "\"bitlocker recovery\", or \"mfa reset\".";

export default function App() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [role, setRole] = useState<Role>("end_user");
  const [channel, setChannel] = useState<Channel>("chat");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [flow, setFlow] = useState<FlowSnapshot | null>(null);
  const [ticket, setTicket] = useState<Ticket | null>(null);
  const [triage, setTriage] = useState<Triage | null>(null);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [health, setHealth] = useState<HealthInfo | null>(null);
  const [error, setError] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    getHealth().then(setHealth).catch(() => undefined);
    createSession(role, channel)
      .then((s) => {
        setSessionId(s.session_id);
        setMessages([{ role: "assistant", content: WELCOME_END_USER }]);
      })
      .catch(() => setError("Could not reach the backend. Is it running? (uvicorn app.main:app)"));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, busy]);

  const switchRole = async (next: Role) => {
    setRole(next);
    setMessages([]);
    setFlow(null);
    setTicket(null);
    setTriage(null);
    const s = await createSession(next, channel);
    setSessionId(s.session_id);
    setMessages([{ role: "assistant", content: next === "l1" ? WELCOME_L1 : WELCOME_END_USER }]);
  };

  const switchChannel = async (next: Channel) => {
    setChannel(next);
    // Keep the session, just reflect the new channel going forward.
    await createSession(role, next);
  };

  const handleSend = async (text: string) => {
    const trimmed = text.trim();
    if (!trimmed || !sessionId || busy) return;
    setInput("");
    setBusy(true);
    setError(null);
    setMessages((m) => [...m, { role: "user", content: trimmed }]);

    try {
      const res: ChatResponse = await sendMessage(sessionId, trimmed, role, channel);
      setMessages(res.history);
      setFlow(res.flow);
      setTicket(res.ticket);
      if (res.triage) setTriage(res.triage);
      if (res.major_incident) {
        setTriage((t) =>
          t
            ? { ...t, major_incident: true, priority: "P1" }
            : {
                record_type: "Incident",
                type_confidence: 1,
                impact: "high",
                urgency: "high",
                priority: "P1",
                priority_name: "Critical",
                major_incident: true,
                response_sla: "15 minutes",
                resolution_sla: "4 hours",
              },
        );
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong.");
      setMessages((m) => [
        ...m,
        { role: "assistant", content: "⚠️ Sorry, I hit an error. Please try again." },
      ]);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="brand">
          <div className="brand-mark" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 3.5c-4.7 0-8.5 3.2-8.5 7.2 0 2.2 1.2 4.2 3 5.5-.1.9-.5 2.1-1.3 3.2-.2.3 0 .7.4.8 1.4.4 3.2-.1 4.6-1.1.6.1 1.2.1 1.8.1 4.7 0 8.5-3.2 8.5-7.2S16.7 3.5 12 3.5z" />
            </svg>
          </div>
          <div className="brand-copy">
            <h1>SD Buddy</h1>
            <span className="brand-sub">Service Desk Copilot</span>
          </div>
        </div>
        <div className="header-controls">
          <RoleToggle value={role} onChange={switchRole} />
          <ChannelSelector value={channel} onChange={switchChannel} />
          {health && (
            <span className={`llm-badge ${health.llm_configured ? "on" : "off"}`} title="Model status">
              <span className="badge-dot" aria-hidden="true" />
              {health.llm_configured ? `LLM: ${health.model.split("/").pop()}` : "LLM: fallback mode"}
            </span>
          )}
        </div>
      </header>

      {triage?.major_incident && <PriorityBanner triage={triage} />}

      <main className="app-main">
        <section className="chat-column">
          <FlowWizard flow={flow} />
          <div className="chat-scroll" ref={scrollRef} role="log" aria-label="Conversation">
            {messages.map((m, i) => (
              <MessageBubble key={i} message={m} />
            ))}
            {busy && <TypingIndicator />}
          </div>
          {messages.length <= 1 && (
            <div className="suggestions">
              {SUGGESTIONS.map((s) => (
                <button key={s} onClick={() => handleSend(s)} disabled={busy}>
                  {s}
                </button>
              ))}
            </div>
          )}
          {error && <div className="error-bar">{error}</div>}
          <form
            className="composer"
            onSubmit={(e) => {
              e.preventDefault();
              void handleSend(input);
            }}
            aria-label="Send a message"
          >
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={flow ? "Type your answer to continue the guided flow…" : "Describe your issue…"}
              aria-label="Message"
              disabled={busy}
            />
            <button type="submit" className="send-btn" aria-label="Send" disabled={busy || !input.trim()}>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 19V5M5 12l7-7 7 7" />
              </svg>
            </button>
          </form>
        </section>

        <aside className="side-column">
          <TicketPanel ticket={ticket} triage={triage} />
        </aside>
      </main>
    </div>
  );
}