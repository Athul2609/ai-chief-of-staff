"use client";

import { useCallback, useEffect, useState } from "react";

const API_BASE = "http://localhost:8000";
const SESSION_KEY = "cos_session_id";

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);

  useEffect(() => {
    let sid = localStorage.getItem(SESSION_KEY);
    if (!sid) {
      sid = crypto.randomUUID();
      localStorage.setItem(SESSION_KEY, sid);
    }
    setSessionId(sid);
    loadHistory(sid);
  }, []);

  async function loadHistory(sid: string) {
    try {
      const res = await fetch(`${API_BASE}/chat/${sid}/messages`);
      if (!res.ok) return;
      const data = await res.json();
      setMessages(
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        data.messages.map((m: any) => ({ role: m.role, content: m.content }))
      );
    } catch {
      // server not ready or no history yet
    }
  }

  const sendMessage = useCallback(async () => {
    if (!input.trim() || isStreaming || !sessionId) return;

    const userText = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userText }]);
    setIsStreaming(true);

    // placeholder for the assistant turn
    setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

    try {
      const res = await fetch(`${API_BASE}/chat/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userText, session_id: sessionId }),
      });

      if (!res.ok || !res.body) throw new Error("Stream failed");

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() ?? "";

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          const raw = line.slice(6).trim();
          if (!raw) continue;
          try {
            const event = JSON.parse(raw);
            if (event.type === "token") {
              setMessages((prev) => {
                const next = [...prev];
                next[next.length - 1] = {
                  role: "assistant",
                  content: next[next.length - 1].content + event.content,
                };
                return next;
              });
            }
          } catch {
            // partial JSON line — skip
          }
        }
      }
    } catch {
      setMessages((prev) => {
        const next = [...prev];
        next[next.length - 1] = {
          role: "assistant",
          content: "[ERROR] Could not reach server.",
        };
        return next;
      });
    } finally {
      setIsStreaming(false);
    }
  }, [input, isStreaming, sessionId]);

  const clearSession = useCallback(() => {
    const sid = crypto.randomUUID();
    localStorage.setItem(SESSION_KEY, sid);
    setSessionId(sid);
    setMessages([]);
  }, []);

  return { messages, input, setInput, sendMessage, isStreaming, sessionId, clearSession };
}
