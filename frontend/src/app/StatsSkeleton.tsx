export function StatsSkeleton() {
  return (
    <div className="lg:sticky lg:top-20 rounded-xl border border-[var(--border)] bg-[var(--card)] p-4 shadow-sm animate-pulse" aria-hidden>
      <div className="h-4 w-20 rounded bg-[var(--border)] mb-3" />
      <ul className="space-y-2 text-sm">
        <li className="flex justify-between">
          <span className="h-4 w-24 rounded bg-[var(--border)]" />
          <span className="h-4 w-8 rounded bg-[var(--border)]" />
        </li>
        <li className="flex justify-between">
          <span className="h-4 w-24 rounded bg-[var(--border)]" />
          <span className="h-4 w-8 rounded bg-[var(--border)]" />
        </li>
      </ul>
    </div>
  );
}
