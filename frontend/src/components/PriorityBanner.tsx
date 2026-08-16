import type { Triage } from "../types";

export function PriorityBanner({ triage }: { triage: Triage }) {
  return (
    <div className="priority-banner" role="alert">
      <svg
        className="priority-icon"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
        strokeLinejoin="round"
        aria-hidden="true"
      >
        <path d="M12 3.5 21 19.5H3L12 3.5z" />
        <path d="M12 9.5v3.5" />
        <circle cx="12" cy="16" r="0.5" fill="currentColor" />
      </svg>
      <div className="priority-banner-content">
        <strong>Major Incident · P1 ({triage.priority_name})</strong>
        <span className="priority-meta">
          {triage.record_type} · Impact {triage.impact} × Urgency {triage.urgency} · Response{" "}
          {triage.response_sla} · Resolution {triage.resolution_sla}
        </span>
        <span className="priority-note">
          Escalated: bridge call + Service Manager + comms cadence (KB-006).
        </span>
      </div>
    </div>
  );
}