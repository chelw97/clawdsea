export default function Loading() {
  return (
    <div className="flex items-center justify-center py-16" aria-label="加载中">
      <div className="flex flex-col items-center gap-3">
        <div
          className="h-8 w-8 animate-spin rounded-full border-2 border-[var(--border)] border-t-[var(--accent)]"
          aria-hidden
        />
        <p className="text-sm text-[var(--muted)]">加载中…</p>
      </div>
    </div>
  );
}
