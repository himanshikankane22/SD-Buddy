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
      <div className={`bubble ${isUser ? "user" : "bot"}`}>{render(message.content)}</div>
    </div>
  );
}