"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import ChatPanel from "@/components/ChatPanel";

// Unsplash – calm clinical / abstract health (dark-friendly overlays)
const BG =
  "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&w=1920&q=80";
const BG2 =
  "https://images.unsplash.com/photo-1559757148-5c350d0d3c56?auto=format&fit=crop&w=1920&q=80";

export default function HomePage() {
  const heroRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!heroRef.current) return;
    gsap.fromTo(
      heroRef.current.querySelectorAll("[data-fade]"),
      { opacity: 0, y: 20 },
      {
        opacity: 1,
        y: 0,
        duration: 0.8,
        stagger: 0.12,
        ease: "power3.out",
        delay: 0.15,
      }
    );
  }, []);

  return (
    <main className="relative min-h-screen flex flex-col">
      {/* Background */}
      <div className="fixed inset-0 -z-10">
        <div
          className="absolute inset-0 bg-cover bg-center opacity-30"
          style={{ backgroundImage: `url(${BG})` }}
        />
        <div
          className="absolute inset-0 bg-cover bg-center opacity-20 mix-blend-lighten"
          style={{ backgroundImage: `url(${BG2})` }}
        />
        <div className="absolute inset-0 bg-gradient-to-b from-charcoal via-charcoal/95 to-charcoal" />
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-accent/5 via-transparent to-transparent" />
      </div>

      {/* Top bar */}
      <nav className="relative z-10 flex items-center justify-between px-4 sm:px-8 py-5">
        <div className="flex items-center gap-2">
          <span className="w-8 h-8 rounded-lg bg-accent text-charcoal font-display font-bold text-xs flex items-center justify-center">
            CP
          </span>
          <span className="font-display font-semibold tracking-wide text-neutral-100">
            CarePath
          </span>
        </div>
        <p className="hidden sm:block text-[11px] text-neutral-500 uppercase tracking-widest">
          Prototype · Challenge 2026
        </p>
      </nav>

      {/* Hero + chat */}
      <div
        ref={heroRef}
        className="relative z-10 flex-1 flex flex-col lg:flex-row items-center justify-center gap-10 px-4 sm:px-8 pb-12 pt-4"
      >
        <div className="max-w-md text-center lg:text-left space-y-4">
          <p
            data-fade
            className="text-accent text-xs font-display uppercase tracking-[0.2em]"
          >
            Men&apos;s reproductive health
          </p>
          <h2
            data-fade
            className="font-display text-3xl sm:text-4xl font-semibold text-neutral-50 leading-tight"
          >
            From a private question to the right next step
          </h2>
          <p data-fade className="text-neutral-400 text-sm leading-relaxed">
            CarePath helps you recognise when care may be needed, complete a
            careful assessment, and find an appropriate pathway — without
            diagnosing conditions or replacing a clinician.
          </p>
          <ul
            data-fade
            className="text-xs text-neutral-500 space-y-1.5 pt-2"
          >
            <li className="flex items-center gap-2 justify-center lg:justify-start">
              <span className="w-1 h-1 rounded-full bg-accent" /> Explicit
              consent before sensitive questions
            </li>
            <li className="flex items-center gap-2 justify-center lg:justify-start">
              <span className="w-1 h-1 rounded-full bg-accent" /> Deterministic
              clinical rules · red-flag escalation
            </li>
            <li className="flex items-center gap-2 justify-center lg:justify-start">
              <span className="w-1 h-1 rounded-full bg-accent" /> Web chat live ·
              Telegram ready · WhatsApp architecture ready
            </li>
          </ul>
        </div>

        <div data-fade className="w-full max-w-lg">
          <ChatPanel />
        </div>
      </div>

      <footer className="relative z-10 text-center text-[10px] text-neutral-600 pb-6 px-4">
        Screening &amp; navigation only · Not medical advice · Rules version
        2026-11-prototype-v0.1
      </footer>
    </main>
  );
}
