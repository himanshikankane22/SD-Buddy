import type { Role } from "../types";

export function RoleToggle({ value, onChange }: { value: Role; onChange: (r: Role) => void }) {
  return (
    <div className="role-toggle" role="group" aria-label="Persona">
      <button
        className={value === "end_user" ? "active" : ""}
        onClick={() => onChange("end_user")}
      >
        End User
      </button>
      <button className={value === "l1" ? "active" : ""} onClick={() => onChange("l1")}>
        L1 Agent
      </button>
    </div>
  );
}