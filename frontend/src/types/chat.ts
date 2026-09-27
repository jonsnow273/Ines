export interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: string;
}

export interface ChatResponse {
  response: string;
  session_id: string;
  steering_active: string | null;
}
