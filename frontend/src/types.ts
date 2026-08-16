export type Role = "end_user" | "l1";
export type Channel = "call" | "chat" | "email" | "portal";

export interface FlowSnapshot {
  key: string;
  label: string;
  name: string;
  step: string;
  step_index: number;
  step_total: number;
  identity_progress: number;
  identity_total: number;
  done: boolean;
}

export interface Ticket {
  number: string;
  record_type: string;
  short_description: string;
  category: string;
  impact: string;
  urgency: string;
  priority: string;
  state: string;
  created: string;
  contact_channel: string;
  caller: string;
  description: string;
  notes: string[];
}

export interface Triage {
  record_type: string;
  type_confidence: number;
  impact: string;
  urgency: string;
  priority: string;
  priority_name: string;
  major_incident: boolean;
  response_sla: string;
  resolution_sla: string;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ChatResponse {
  session_id: string;
  reply: string;
  history: ChatMessage[];
  flow: FlowSnapshot | null;
  ticket: Ticket | null;
  triage: Triage | null;
  llm_used: boolean;
  major_incident: boolean;
}

export interface SessionInfo {
  session_id: string;
  role: Role;
  channel: Channel;
}

export interface HealthInfo {
  status: string;
  app: string;
  version: string;
  llm_configured: boolean;
  model: string;
}