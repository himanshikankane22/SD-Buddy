import type { FlowSnapshot } from "../types";

export function FlowWizard({ flow }: { flow: FlowSnapshot | null }) {
  if (!flow) return null;

  const identityActive = flow.step === "identity";
  const pct = identityActive
    ? Math.round((flow.identity_progress / flow.identity_total) * 100)
    : Math.round(((flow.step_index + 1) / flow.step_total) * 100);

  return (
    <div className={`flow-wizard ${flow.done ? "done" : ""}`}>
      <div className="flow-header">
        <span className="flow-title">{flow.label}</span>
        <span className="flow-step-label">
          {identityActive
            ? `Identity check ${flow.identity_progress}/${flow.identity_total}`
            : `Step ${flow.step_index + 1}/${flow.step_total} — ${flow.step}`}
        </span>
      </div>
      <div className="flow-progress-track">
        <div className="flow-progress-fill" style={{ width: `${pct}%` }} />
      </div>
      {flow.done && <div className="flow-done-badge">✅ Complete — ticket drafted</div>}
    </div>
  );
}