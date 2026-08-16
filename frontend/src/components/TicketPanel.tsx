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
          <span className={`type-chip ${triage.record_type === "Incident" ? "incident" : "request"}`}>
            {triage.record_type}
          </span>
          <span className={`prio-chip ${priorityClass(triage.priority)}`}>{triage.priority}</span>
          <span className="impact-chip">
            I {triage.impact} · U {triage.urgency}
          </span>
          {triage.major_incident && <span className="major-chip">Major</span>}
        </div>
      )}

      {!ticket && (
        <div className="panel-empty">
          <p>No ticket yet.</p>
          <p className="panel-empty-sub">
            Start describing your issue — the bot builds a ServiceNow-style draft as you go.
          </p>
        </div>
      )}

      {ticket && (
        <div className="ticket-body">
          <div className="ticket-head">
            <span className="ticket-number">{ticket.number}</span>
            <span className={`type-chip ${ticket.record_type === "Incident" ? "incident" : "request"}`}>
              {ticket.record_type}
            </span>
          </div>
          <dl className="ticket-fields">
            <div>
              <dt>Short description</dt>
              <dd>{ticket.short_description}</dd>
            </div>
            <div>
              <dt>Category</dt>
              <dd>{ticket.category}</dd>
            </div>
            <div className="fields-row">
              <div>
                <dt>Priority</dt>
                <dd className={priorityClass(ticket.priority)}>{ticket.priority}</dd>
              </div>
              <div>
                <dt>Impact</dt>
                <dd>{ticket.impact}</dd>
              </div>
              <div>
                <dt>Urgency</dt>
                <dd>{ticket.urgency}</dd>
              </div>
            </div>
            <div>
              <dt>Channel</dt>
              <dd className="capitalize">{ticket.contact_channel}</dd>
            </div>
            <div>
              <dt>Caller</dt>
              <dd>{ticket.caller || "—"}</dd>
            </div>
            <div>
              <dt>Description</dt>
              <dd>{ticket.description}</dd>
            </div>
          </dl>
          <button className="copy-btn" onClick={copyTicket}>
            {copied ? "✓ Copied" : "Copy JSON"}
          </button>
        </div>
      )}
    </div>
  );
}