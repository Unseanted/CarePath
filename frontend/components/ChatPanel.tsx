"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import gsap from "gsap";
import ChatMessage from "./ChatMessage";
import QuickReplies from "./QuickReplies";
import { sendChat, resetChat, healthCheck } from "@/lib/api";
import { getOrCreateSessionId, clearSessionId } from "@/lib/session";

type Msg = {
  id: string;
  role: "user" | "assistant" | "system";
  text: string;
  triage?: string | null;
  redFlag?: boolean | null;
};

export default function ChatPanel() {
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [quick, setQuick] = useState<string[]>([]);
  const [online, setOnline] = useState<boolean | null>(null);
  const [sessionId, setSessionId] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);
  const panelRef = useRef<HTMLDivElement>(null);
  const started = useRef(false);

  useEffect(() => {
    setSessionId(getOrCreateSessionId());
    healthCheck().then(setOnline);
    if (panelRef.current) {
      gsap.fromTo(
        panelRef.current,
        { opacity: 0, y: 24 },
        { opacity: 1, y: 0, duration: 0.7, ease: "power3.out" }
      );
    }
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, quick, loading]);

  const push = useCallback((m: Omit<Msg, "id">) => {
    setMessages((prev) => [
      ...prev,
      { ...m, id: `${Date.now()}-${Math.random().toString(36).slice(2, 7)}` },
    ]);
  }, []);

  const bootstrap = useCallback(async () => {
    if (started.current || !sessionId) return;
    started.current = true;
    setLoading(true);
    try {
      const res = await sendChat(sessionId, "hello");
      push({ role: "assistant", text: res.reply });
      setQuick(res.quick_replies || ["YES", "NO"]);
    } catch (e) {
      push({
        role: "system",
        text: "Backend unreachable. Start the API on :8000 and refresh.",
      });
      setOnline(false);
    } finally {
      setLoading(false);
    }
  }, [sessionId, push]);

  useEffect(() => {
    if (sessionId && messages.length === 0) bootstrap();
  }, [sessionId, messages.length, bootstrap]);

  const send = async (text: string) => {
    const trimmed = text.trim();
    if (!trimmed || loading || !sessionId) return;
    setInput("");
    setQuick([]);
    push({ role: "user", text: trimmed });
    setLoading(true);
    try {
      const res = await sendChat(sessionId, trimmed);
      push({
        role: "assistant",
        text: res.reply,
        triage: res.triage,
        redFlag: res.red_flag,
      });
      setQuick(res.quick_replies || []);
      setOnline(true);
    } catch {
      push({
        role: "system",
        text: "Could not reach CarePath API. Check that the backend is running.",
      });
      setOnline(false);
    } finally {
      setLoading(false);
    }
  };

  const onReset = async () => {
    if (!sessionId) return;
    await resetChat(sessionId);
    clearSessionId();
    const newId = getOrCreateSessionId();
    setSessionId(newId);
    setMessages([]);
    setQuick([]);
    started.current = false;
  };

  return (
    <div
      ref={panelRef}
      className="flex flex-col w-full max-w-lg mx-auto h-[min(720px,85vh)] rounded-2xl overflow-hidden
                 border border-charcoal-300 bg-charcoal-50/95 backdrop-blur-md shadow-2xl shadow-black/50"
    >
      {/* Header */}
      <header className="flex items-center justify-between px-4 py-3 border-b border-charcoal-300 bg-charcoal/90">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-accent flex items-center justify-center font-display font-bold text-charcoal text-sm">
            CP
          </div>
          <div>
            <h1 className="font-display font-semibold text-sm tracking-wide text-neutral-50">
              CarePath
            </h1>
            <p className="text-[10px] text-neutral-500 uppercase tracking-widest">
              Health navigation · not a diagnosis
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span
            className={`w-2 h-2 rounded-full ${
              online === null
                ? "bg-neutral-600"
                : online
                ? "bg-emerald-400"
                : "bg-red-500"
            }`}
            title={online ? "API online" : "API offline"}
          />
          <button
            type="button"
            onClick={onReset}
            className="text-[11px] text-neutral-400 hover:text-accent transition-colors px-2 py-1"
          >
            Reset
          </button>
        </div>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto chat-scroll px-3 py-4 space-y-1">
        {messages.map((m) => (
          <ChatMessage
            key={m.id}
            role={m.role}
            text={m.text}
            triage={m.triage}
            redFlag={m.redFlag}
          />
        ))}
        {loading && (
          <div className="flex justify-start px-1 mb-3">
            <div className="bg-charcoal-200 border border-charcoal-300 rounded-2xl rounded-bl-md px-4 py-3">
              <div className="flex gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-accent animate-pulse" />
                <span className="w-1.5 h-1.5 rounded-full bg-accent animate-pulse delay-75" />
                <span className="w-1.5 h-1.5 rounded-full bg-accent animate-pulse delay-150" />
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <QuickReplies
        options={quick}
        onSelect={(v) => send(v)}
        disabled={loading}
      />

      {/* Input */}
      <form
        className="flex gap-2 p-3 border-t border-charcoal-300 bg-charcoal/90"
        onSubmit={(e) => {
          e.preventDefault();
          send(input);
        }}
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type a message…"
          disabled={loading}
          className="flex-1 bg-charcoal-100 border border-charcoal-300 rounded-xl px-4 py-2.5 text-sm
                     text-neutral-100 placeholder:text-neutral-600 focus:outline-none focus:border-accent/60
                     disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="px-4 py-2.5 rounded-xl bg-accent text-charcoal font-semibold text-sm
                     hover:bg-accent-dim transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
        >
          Send
        </button>
      </form>
    </div>
  );
}
