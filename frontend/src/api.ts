import type { Channel, ChatResponse, HealthInfo, Role, SessionInfo, Ticket } from "./types";

const BASE = "";

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API ${res.status}: ${text}`);
  }
  return res.json() as Promise<T>;
}

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) throw new Error(`API ${res.status}`);
  return res.json() as Promise<T>;
}

export function createSession(role: Role, channel: Channel): Promise<SessionInfo> {
  return post<SessionInfo>("/api/session", { role, channel });
}

export function sendMessage(
  sessionId: string,
  message: string,
  role: Role,
  channel: Channel,
): Promise<ChatResponse> {
  return post<ChatResponse>("/api/chat", { session_id: sessionId, message, role, channel });
}

export function raiseTicket(
  sessionId: string,
  message: string,
  role: Role,
  channel: Channel,
): Promise<{ ticket: Ticket }> {
  return post<{ ticket: Ticket }>("/api/ticket", { session_id: sessionId, message, role, channel });
}

export function getHealth(): Promise<HealthInfo> {
  return get<HealthInfo>("/health");
}