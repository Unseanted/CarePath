"use client";

type Props = {
  options: string[];
  onSelect: (value: string) => void;
  disabled?: boolean;
};

const LABELS: Record<string, string> = {
  YES: "Yes, continue",
  NO: "No, exit",
  "1": "1 · General health",
  "2": "2 · Fertility",
  "3": "3 · Symptoms",
  "4": "4 · Find a professional",
  DONE: "Done",
  REMIND: "Remind me",
  RESTART: "Start over",
};

export default function QuickReplies({ options, onSelect, disabled }: Props) {
  if (!options?.length) return null;
  return (
    <div className="flex flex-wrap gap-2 px-3 pb-2">
      {options.map((opt) => (
        <button
          key={opt}
          type="button"
          disabled={disabled}
          onClick={() => onSelect(opt)}
          className="text-xs sm:text-sm px-3 py-2 rounded-full border border-accent/40 text-accent
                     hover:bg-accent hover:text-charcoal transition-colors duration-200
                     disabled:opacity-40 disabled:cursor-not-allowed font-medium"
        >
          {LABELS[opt] || opt}
        </button>
      ))}
    </div>
  );
}
