import { useState } from "react";
import type { Ticket, Triage } from "../types";

function priorityClass(p: string) {
  return `prio-${p}`;
}

export function TicketPanel({ ticket, triage }: { ticket: Ticket | null; triage: Triage | null }) {
  const [copied, setCopied] = useState(false);

  const copyTicket = async () => {
    if (!ticket) return;
    const text = JSON.stringify(ticket, null, 2);
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  return (
    <div className="ticket-panel">
      <div className="panel-header">
        <h2>Ticket Draft</h2>
        <span className="panel-sub">ServiceNow · live as you chat</span>
      </div>

      {triage && (
        <div className="triage-strip">
          <span className={`chip ${triage.record_type === "Incident" ? "incident" : "request"}`}>
            {triage.record_type}
          </span>
          <span className={`chip ${priorityClass(triage.priority)}`}>{triage.priority}</span>
          <span className="chip">
            I {triage.impact} · U {triage.urgency}
          </span>
          {triage.major_incident && <span className="chip major">Major</span>}
        </div>
      )}

      {!ticket && (
        <div className="panel-empty">
          <div className="empty-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
              <path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8l-5-5z" />
              <path d="M14 3v5h5" />
              <path d="M9 13h6M9 17h4" />
            </svg>
          </div>
          <p>No ticket yet.</p>
          <p className="panel-empty-sub">
            Start describing your issue. The bot builds a ServiceNow-style draft as you chat.
          </p>
        </div>
      )}

      {ticket && (
        <div className="ticket-body">
          <div className="ticket-head">
            <span className="ticket-number">{ticket.number}</span>
            <span className={`chip ${ticket.record_type === "Incident" ? "incident" : "request"}`}>
              {ticket.record_type}
            </span>
          </div>
          <dl className="ticket-rows">
            <div className="ticket-row">
              <dt>Short description</dt>
              <dd>{ticket.short_description}</dd>
            </div>
            <div className="ticket-row">
              <dt>Category</dt>
              <dd>{ticket.category}</dd>
            </div>
            <div className="ticket-row">
              <dt>Priority</dt>
              <dd className={priorityClass(ticket.priority)}>{ticket.priority}</dd>
            </div>
            <div className="ticket-row">
              <dt>Impact</dt>
              <dd>{ticket.impact}</dd>
            </div>
            <div className="ticket-row">
              <dt>Urgency</dt>
              <dd>{ticket.urgency}</dd>
            </div>
            <div className="ticket-row">
              <dt>Channel</dt>
              <dd className="capitalize">{ticket.contact_channel}</dd>
            </div>
            <div className="ticket-row">
              <dt>Caller</dt>
              <dd>{ticket.caller || "—"}</dd>
            </div>
            <div className="ticket-row">
              <dt>Description</dt>
              <dd>{ticket.description}</dd>
            </div>
          </dl>
          <button
            className={`copy-btn ${copied ? "copied" : ""}`}
            onClick={copyTicket}
            aria-label={copied ? "Copied ticket to clipboard" : "Copy ticket as JSON"}
          >
            {copied ? (
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2.4"
                strokeLinecap="round"
                strokeLinejoin="round"
                aria-hidden="true"
              >
                <path d="M4 12.5l5 5L20 6.5" />
              </svg>
            ) : (
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.7"
                strokeLinecap="round"
                strokeLinejoin="round"
                aria-hidden="true"
              >
                <rect x="9" y="9" width="11" height="11" rx="2" />
                <path d="M5 15V6a2 2 0 0 1 2-2h9" />
              </svg>
            )}
            {copied ? "Copied" : "Copy JSON"}
          </button>
        </div>
      )}
    </div>
  );
}