"use client";

import { useEffect, useRef } from "react";
import { useChat } from "@/hooks/useChat";

const BOOT_LINES = [
  "AI CHIEF OF STAFF  v0.3.0",
  "Copyright (C) 2025 Alex Johnson Systems",
  "─────────────────────────────────────────",
  "[ OK ] PostgreSQL ........... connected",
  "[ OK ] Ollama LLM ........... online",
  "[ OK ] Memory ............... initialized",
  "─────────────────────────────────────────",
  "Type your message and press ENTER.",
  "",
];

export default function Home() {
  const { messages, input, setInput, sendMessage, isStreaming, sessionId, clearSession } =
    useChat();
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter") sendMessage();
  }

  return (
    <div
      className="flex flex-col h-full bg-terminal-bg text-terminal-green font-mono text-sm"
      onClick={() => inputRef.current?.focus()}
    >
      {/* Top bar */}
      <div className="flex items-center justify-between px-4 py-2 border-b border-terminal-border shrink-0">
        <span className="text-terminal-green tracking-widest text-xs">
          ◈ AI CHIEF OF STAFF
        </span>
        <span className="text-terminal-dark text-xs">
          SID:{" "}
          <span className="text-terminal-dim">
            {sessionId ? sessionId.slice(0, 8).toUpperCase() : "--------"}
          </span>
        </span>
        <button
          onClick={(e) => { e.stopPropagation(); clearSession(); }}
          className="text-terminal-dark hover:text-terminal-amber text-xs transition-colors cursor-pointer"
        >
          [NEW SESSION]
        </button>
      </div>

      {/* Message area */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-1">
        {/* Boot sequence */}
        {BOOT_LINES.map((line, i) => (
          <div key={i} className="text-terminal-dark leading-relaxed">
            {line || " "}
          </div>
        ))}

        {/* Conversation */}
        {messages.map((msg, i) => (
          <div key={i} className="leading-relaxed">
            {msg.role === "user" ? (
              <div className="mt-2">
                <span className="text-terminal-amber">&gt; </span>
                <span className="text-terminal-text">{msg.content}</span>
              </div>
            ) : (
              <div className="mt-1 pl-2 border-l border-terminal-border">
                <span className="text-terminal-dim">$ </span>
                <span className="text-terminal-green whitespace-pre-wrap">{msg.content}</span>
                {i === messages.length - 1 && isStreaming && (
                  <span className="cursor-blink ml-0.5" />
                )}
              </div>
            )}
          </div>
        ))}

        {isStreaming && messages[messages.length - 1]?.role !== "assistant" && (
          <div className="mt-1 pl-2 border-l border-terminal-border">
            <span className="text-terminal-dim">$ </span>
            <span className="cursor-blink" />
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input bar */}
      <div className="shrink-0 border-t border-terminal-border px-4 py-3">
        <div className="flex items-center gap-2">
          <span className="text-terminal-amber select-none">&gt;</span>
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isStreaming}
            placeholder={isStreaming ? "processing..." : "enter command_"}
            autoFocus
            className="flex-1 bg-transparent border-none outline-none text-terminal-text placeholder-terminal-border font-mono text-sm caret-terminal-green disabled:opacity-40"
          />
          <button
            onClick={sendMessage}
            disabled={isStreaming || !input.trim()}
            className="text-xs border border-terminal-border px-3 py-1 text-terminal-dim hover:border-terminal-green hover:text-terminal-green disabled:opacity-20 disabled:cursor-not-allowed transition-colors cursor-pointer"
          >
            {isStreaming ? "WAIT" : "SEND"}
          </button>
        </div>
      </div>
    </div>
  );
}
