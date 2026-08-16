import type { ReactNode } from "react";
import type { Channel } from "../types";

const CHANNELS: { value: Channel; label: string; icon: ReactNode }[] = [
  {
    value: "call",
    label: "Call",
    icon: (
      <path d="M21.6 16.8v1.9a1.6 1.6 0 0 1-1.7 1.6 19.6 19.6 0 0 1-8.6-3 19 19 0 0 1-6-6 19.6 19.6 0 0 1-3-8.6A1.6 1.6 0 0 1 3.9 1.6h1.9a1.6 1.6 0 0 1 1.6 1.3c.1.8.3 1.5.6 2.2a1.6 1.6 0 0 1-.4 1.7L6.3 8.4a12.4 12.4 0 0 0 6.4 6.4l1.6-1.3a1.6 1.6 0 0 1 1.7-.4c.7.3 1.4.5 2.2.6a1.6 1.6 0 0 1 1.4 1.6z" />
    ),
  },
  {
    value: "chat",
    label: "Chat",
    icon: (
      <path d="M12 3C6.5 3 2 6.9 2 11.7c0 2.7 1.5 5.2 3.8 6.7-.1 1-.5 2.2-1.3 3.2-.2.3 0 .7.4.8 1.4.4 3.2-.1 4.6-1.1.8.1 1.7.2 2.5.2 5.5 0 10-3.9 10-8.7S17.5 3 12 3z" />
    ),
  },
  {
    value: "email",
    label: "Email",
    icon: (
      <>
        <rect x="3" y="5" width="18" height="14" rx="2.5" />
        <path d="M3.5 7.5l8.5 6 8.5-6" />
      </>
    ),
  },
  {
    value: "portal",
    label: "ServiceNow",
    icon: (
      <>
        <rect x="3" y="3" width="7.5" height="7.5" rx="1.8" />
        <rect x="13.5" y="3" width="7.5" height="7.5" rx="1.8" />
        <rect x="3" y="13.5" width="7.5" height="7.5" rx="1.8" />
        <rect x="13.5" y="13.5" width="7.5" height="7.5" rx="1.8" />
      </>
    ),
  },
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
          aria-pressed={value === c.value}
          onClick={() => onChange(c.value)}
          title={`Simulate contact via ${c.label}`}
        >
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.7"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            {c.icon}
          </svg>
          <span>{c.label}</span>
        </button>
      ))}
    </div>
  );
}