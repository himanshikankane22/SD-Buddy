import type { ChatMessage } from "../types";

export function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user";
  // Very light markdown: bold **text** and inline code `text`.
  const render = (content: string) => {
    const parts = content.split(/(\*\*[^*]+\*\*|`[^`]+`)/g);
    return parts.map((p, i) => {
      if (p.startsWith("**") && p.endsWith("**")) {
        return <strong key={i}>{p.slice(2, -2)}</strong>;
      }
      if (p.startsWith("`") && p.endsWith("`")) {
        return <code key={i}>{p.slice(1, -1)}</code>;
      }
      return <span key={i}>{p}</span>;
    });
  };

  return (
    <div className={`bubble-row ${isUser ? "user" : "bot"}`}>
      {!isUser && (
        <span className="avatar" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2.6c.5 4.3 2.7 6.5 7 7-4.3.5-6.5 2.7-7 7-.5-4.3-2.7-6.5-7-7 4.3-.5 6.5-2.7 7-7z" />
            <path d="M19.2 14.8c.3 2 1.2 2.9 3.2 3.2-2 .3-2.9 1.2-3.2 3.2-.3-2-1.2-2.9-3.2-3.2 2-.3 2.9-1.2 3.2-3.2z" />
          </svg>
        </span>
      )}
      <div className={`bubble ${isUser ? "user" : "bot"}`}>{render(message.content)}</div>
    </div>
  );
}