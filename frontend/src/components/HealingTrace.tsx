"use client";

import type { HealingEvent, HealingStage } from "@/lib/api";

// One short label per stage for the timeline pill. Keeping these terse so the
// trace stays scannable even on 8+ events.
const STAGE_LABEL: Record<HealingStage, string> = {
  routing: "route",
  cache_hit: "cache",
  hyde: "hyde",
  retrieval: "retrieve",
  grading: "grade",
  rerank: "rerank",
  rewrite: "rewrite",
  generation: "generate",
  faithfulness: "verify",
  retry: "retry",
  give_up: "give up",
  done: "done",
};

// Stages that represent the system *correcting itself* get the accent colour
// so they pop visually - that's the whole point of surfacing the trace.
const HEALING_STAGES = new Set<HealingStage>(["rewrite", "retry", "give_up", "hyde", "cache_hit"]);

interface Props {
  trace: HealingEvent[];
  fromCache: boolean;
  fallback: boolean;
  attempts: number;
}

export function HealingTrace({ trace, fromCache, fallback, attempts }: Props) {
  if (!trace || trace.length === 0) return null;

  return (
    <details className="mt-3 group">
      <summary className="cursor-pointer font-mono text-[11px] uppercase tracking-[0.15em] text-muted hover:text-ink flex items-center gap-2">
        <span>Self-healing trace · {trace.length} steps</span>
        {attempts > 1 && (
          <span className="px-1.5 py-px bg-accent/15 text-accent normal-case tracking-normal">
            {attempts} attempts
          </span>
        )}
        {fromCache && (
          <span className="px-1.5 py-px bg-emerald-700/15 text-emerald-800 normal-case tracking-normal">
            cached
          </span>
        )}
        {fallback && (
          <span className="px-1.5 py-px bg-amber-700/15 text-amber-800 normal-case tracking-normal">
            fallback
          </span>
        )}
      </summary>

      <ol className="mt-3 space-y-1.5 border-l border-rule pl-3">
        {trace.map((ev, i) => {
          const isHealing = HEALING_STAGES.has(ev.stage);
          return (
            <li key={i} className="text-[12px] leading-snug">
              <div className="flex items-baseline gap-2">
                <span
                  className={
                    "font-mono text-[10px] uppercase tracking-[0.12em] " +
                    (isHealing ? "text-accent" : "text-muted")
                  }
                  title={`stage: ${ev.stage}`}
                >
                  {STAGE_LABEL[ev.stage] ?? ev.stage}
                </span>
                <span className="text-[10px] font-mono text-muted/70">
                  #{ev.attempt}
                </span>
                <span className="text-ink/80 flex-1">{ev.message}</span>
                {typeof ev.score === "number" && (
                  <span className="text-[10px] font-mono text-muted">
                    {ev.score.toFixed(2)}
                  </span>
                )}
              </div>
              {/* Show rewrite "from -> to" inline when present */}
              {ev.stage === "rewrite" && ev.detail && (ev.detail as any).to && (
                <div className="ml-2 mt-0.5 text-[11px] italic text-muted">
                  →{" "}
                  <span className="text-ink/70">
                    {String((ev.detail as any).to)}
                  </span>
                </div>
              )}
            </li>
          );
        })}
      </ol>
    </details>
  );
}
