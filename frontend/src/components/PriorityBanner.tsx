import type { Triage } from "../types";

export function PriorityBanner({ triage }: { triage: Triage }) {
  return (
    <div className="priority-banner">
      <div className="priority-banner-content">
        <span className="pulse-dot" />
        <strong>🚨 Major Incident — P1 ({triage.priority_name})</strong>
        <span>
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