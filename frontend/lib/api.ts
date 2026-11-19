const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type ChatResponse = {
  reply: string;
  session_id: string;
  status: string | null;
  pathway: string | null;
  answers_count: number;
  current_question_id: string | null;
  triage: string | null;
  red_flag: boolean | null;
  quick_replies: string[];
};

export async function sendChat(
  sessionId: string,
  text: string
): Promise<ChatResponse> {
  const res = await fetch(`${API_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, text, channel: "web" }),
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(err || `Chat failed (${res.status})`);
  }
  return res.json();
}

export async function resetChat(sessionId: string): Promise<void> {
  await fetch(
    `${API_URL}/api/chat/reset?session_id=${encodeURIComponent(sessionId)}&channel=web`,
    { method: "POST" }
  );
}

export async function healthCheck(): Promise<boolean> {
  try {
    const res = await fetch(`${API_URL}/health`, { cache: "no-store" });
    return res.ok;
  } catch {
    return false;
  }
}
