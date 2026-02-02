"use client";

import { useRouter } from "next/navigation";

export type HotWindow = "day" | "week" | "month" | "all";

const OPTIONS: { value: HotWindow; label: string }[] = [
  { value: "day", label: "Day" },
  { value: "week", label: "Week" },
  { value: "month", label: "Month" },
  { value: "all", label: "All" },
];

export function HotWindowSelect({ value }: { value: HotWindow }) {
  const router = useRouter();

  return (
    <label className="flex items-center gap-2 pb-3 text-sm text-[var(--muted)]">
      <span className="sr-only">Hot period</span>
      <select
        value={value}
        onChange={(e) => {
          const v = e.target.value as HotWindow;
          const params = new URLSearchParams({ sort: "hot" });
          if (v !== "all") params.set("hot", v);
          router.push(`/?${params.toString()}`);
        }}
        className="rounded border border-[var(--border)] bg-[var(--background)] px-2 py-1.5 text-[var(--foreground)] focus:outline-none focus:ring-2 focus:ring-[var(--accent)]"
        aria-label="Hot period"
      >
        {OPTIONS.map((o) => (
          <option key={o.value} value={o.value}>
            {o.label}
          </option>
        ))}
      </select>
    </label>
  );
}
