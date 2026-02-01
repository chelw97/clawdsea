export function FeedSkeleton() {
  return (
    <div className="space-y-0 divide-y divide-[var(--border)]" aria-hidden>
      {[1, 2, 3, 4, 5].map((i) => (
        <div key={i} className="py-5 first:pt-0 animate-pulse">
          <div className="flex items-center gap-2 mb-2">
            <div className="h-6 w-6 rounded-full bg-[var(--border)]" />
            <div className="h-4 w-24 rounded bg-[var(--border)]" />
            <div className="h-4 w-20 rounded bg-[var(--border)]" />
          </div>
          <div className="h-4 w-3/4 rounded bg-[var(--border)] mb-2" />
          <div className="h-3 w-full rounded bg-[var(--border)]" />
          <div className="h-3 w-2/3 rounded bg-[var(--border)] mt-1" />
        </div>
      ))}
    </div>
  );
}
