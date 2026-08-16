import type { Channel } from "../types";

const CHANNELS: { value: Channel; label: string; icon: string }[] = [
  { value: "call", label: "Call", icon: "📞" },
  { value: "chat", label: "Chat", icon: "💬" },
  { value: "email", label: "Email", icon: "✉️" },
  { value: "portal", label: "ServiceNow", icon: "🎫" },
];

export function ChannelSelector({
  value,
  onChange,
}: {
  value: Channel;
  onChange: (c: Channel) => void;
}) {
  return (
    <div className="channel-selector" role="group" aria-label="Contact channel">
      {CHANNELS.map((c) => (
        <button
          key={c.value}
          className={`channel-btn ${value === c.value ? "active" : ""}`}
          onClick={() => onChange(c.value)}
          title={`Simulate contact via ${c.label}`}
        >
          <span className="channel-icon">{c.icon}</span>
          <span>{c.label}</span>
        </button>
      ))}
    </div>
  );
}