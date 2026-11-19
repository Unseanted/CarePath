"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";

type Props = {
  role: "user" | "assistant" | "system";
  text: string;
  triage?: string | null;
  redFlag?: boolean | null;
};

export default function ChatMessage({ role, text, triage, redFlag }: Props) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!ref.current) return;
    gsap.fromTo(
      ref.current,
      { opacity: 0, y: 14, scale: 0.98 },
      { opacity: 1, y: 0, scale: 1, duration: 0.45, ease: "power3.out" }
    );
  }, []);

  if (role === "system") {
    return (
      <div ref={ref} className="flex justify-center my-3">
        <span className="text-xs text-neutral-500 bg-charcoal-100 px-3 py-1 rounded-full border border-charcoal-300">
          {text}
        </span>
      </div>
    );
  }

  const isUser = role === "user";

  return (
    <div
      ref={ref}
      className={`flex ${isUser ? "justify-end" : "justify-start"} mb-3 px-1`}
    >
      <div
        className={`max-w-[85%] sm:max-w-[75%] rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap ${
          isUser
            ? "bg-accent text-charcoal rounded-br-md font-medium"
            : redFlag
            ? "bg-red-950/80 border border-red-700/60 text-red-50 rounded-bl-md"
            : "bg-charcoal-200 border border-charcoal-300 text-neutral-100 rounded-bl-md"
        }`}
      >
        {!isUser && (
          <div className="flex items-center gap-2 mb-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-accent" />
            <span className="text-[10px] uppercase tracking-widest text-accent/90 font-display">
              CarePath
            </span>
            {triage && (
              <span className="text-[10px] uppercase tracking-wide text-neutral-500 ml-auto">
                {triage.replace("_", " ")}
              </span>
            )}
          </div>
        )}
        {text}
      </div>
    </div>
  );
}
