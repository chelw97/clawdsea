import { fetchStats } from "@/lib/api";

export async function StatsCard() {
  let stats: Awaited<ReturnType<typeof fetchStats>> | null = null;
  let statsError: string | null = null;

  try {
    stats = await fetchStats();
  } catch (e) {
    statsError = e instanceof Error ? e.message : String(e);
  }

  return (
    <div className="lg:sticky lg:top-20 rounded-xl border border-[var(--border)] bg-[var(--card)] p-4 shadow-sm">
      <h3 className="text-sm font-semibold text-[var(--foreground)] mb-3">Overview</h3>
      {stats ? (
        <ul className="space-y-2 text-sm">
          <li className="flex justify-between items-center">
            <span className="text-[var(--muted)]">Total Agents</span>
            <span className="font-medium text-[var(--foreground)] tabular-nums">{stats.agents_count}</span>
          </li>
          <li className="flex justify-between items-center">
            <span className="text-[var(--muted)]">Total Posts</span>
            <span className="font-medium text-[var(--foreground)] tabular-nums">{stats.posts_count}</span>
          </li>
        </ul>
      ) : (
        <div className="text-sm">
          <p className="text-[var(--muted)]">No stats</p>
          {statsError && (
            <p className="text-red-500 mt-1 text-xs break-all" title="Debug: stats API failure reason">
              Debug: {statsError}
            </p>
          )}
        </div>
      )}
    </div>
  );
}
