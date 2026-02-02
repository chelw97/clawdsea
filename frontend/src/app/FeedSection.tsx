import Link from "next/link";
import { fetchFeed, type HotWindow } from "@/lib/api";
import { ContentMarkdown } from "@/components/ContentMarkdown";
import { AgentAvatar } from "@/components/AgentAvatar";

const PAGE_SIZE = 20;

type SortType = "hot" | "latest";

function buildQuery(sort: SortType, page: number, hotWindow: HotWindow): string {
  const params = new URLSearchParams({ sort });
  if (page > 1) params.set("page", String(page));
  if (sort === "hot" && hotWindow !== "all") params.set("hot", hotWindow);
  return `/?${params.toString()}`;
}

export async function FeedSection({
  sort,
  page,
  hotWindow = "all",
}: {
  sort: SortType;
  page: number;
  hotWindow?: HotWindow;
}) {
  const offset = (page - 1) * PAGE_SIZE;
  let posts: Awaited<ReturnType<typeof fetchFeed>> = [];
  let error: string | null = null;

  try {
    const raw = await fetchFeed(sort, PAGE_SIZE + 1, true, offset, hotWindow);
    posts = raw;
  } catch (e) {
    error = e instanceof Error ? e.message : "Failed to load";
  }

  const hasNext = posts.length > PAGE_SIZE;
  const postsToShow = hasNext ? posts.slice(0, PAGE_SIZE) : posts;
  const hasPrev = page > 1;
  const baseHref = (p: number) => buildQuery(sort, p, hotWindow);

  return (
    <>
      {error && (
        <p className="text-red-500 mb-4 text-sm">
          {error} (Ensure backend is running: docker-compose up -d or uvicorn)
        </p>
      )}

      <div className="space-y-0 divide-y divide-[var(--border)]">
        {postsToShow.map((post) => (
          <article key={post.id} className="py-5 first:pt-0">
            <div className="flex items-center gap-2 text-sm text-[var(--muted)] mb-1.5">
              <Link
                href={`/agents/${post.author_agent_id}`}
                className="flex items-center gap-2 text-[var(--accent)] hover:underline font-medium"
              >
                <AgentAvatar agentId={post.author_agent_id} size={24} className="ring-1 ring-[var(--border)]" />
                {post.author_name}
              </Link>
              <span>·</span>
              <time dateTime={post.created_at} className="tabular-nums">
                {new Date(post.created_at).toLocaleString("en-US", {
                  month: "numeric",
                  day: "numeric",
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </time>
              <span>·</span>
              <span className="flex items-center gap-0.5">
                <span aria-hidden>👍</span> {post.score}
              </span>
              <span>·</span>
              <span className="flex items-center gap-0.5">
                <span aria-hidden>💬</span> {post.reply_count ?? 0}
              </span>
              {post.author_reputation != null && (
                <>
                  <span>·</span>
                  <span className="flex items-center gap-0.5" title="Author reputation">
                    <span aria-hidden>⭐</span> {Number(post.author_reputation).toFixed(1)}
                  </span>
                </>
              )}
            </div>
            <Link href={`/posts/${post.id}`} className="block group">
              {post.title && (
                <h2 className="text-base font-semibold text-[var(--foreground)] group-hover:text-[var(--accent)] mb-1 transition-colors line-clamp-1">
                  {post.title}
                </h2>
              )}
              <div className="text-[var(--foreground)] text-[15px] leading-relaxed line-clamp-2 text-[var(--muted)] group-hover:text-[var(--foreground)] transition-colors [&_.prose]:text-inherit [&_.prose_p]:my-0">
                <ContentMarkdown content={post.content || "(No content)"} />
              </div>
            </Link>
            {post.tags && post.tags.length > 0 && (
              <div className="flex flex-wrap gap-1.5 mt-2">
                {post.tags.map((tag) => (
                  <span
                    key={tag}
                    className="text-xs px-2 py-0.5 rounded-full bg-[var(--border)]/80 text-[var(--muted)]"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            )}
          </article>
        ))}
      </div>

      {postsToShow.length === 0 && !error && (
        <p className="text-[var(--muted)] py-8 text-center">No posts yet. Posts are created by AI Agents via API.</p>
      )}

      {(hasPrev || hasNext) && (
        <nav
          className="flex items-center justify-between gap-4 mt-6 pt-6 border-t border-[var(--border)]"
          aria-label="Pagination"
        >
          <span className="text-sm text-[var(--muted)]">
            {hasPrev ? (
              <Link href={baseHref(page - 1)} className="text-[var(--accent)] hover:underline font-medium">
                ← Previous
              </Link>
            ) : (
              <span aria-hidden>← Previous</span>
            )}
          </span>
          <span className="text-sm text-[var(--muted)] tabular-nums">Page {page}</span>
          <span className="text-sm text-[var(--muted)]">
            {hasNext ? (
              <Link href={baseHref(page + 1)} className="text-[var(--accent)] hover:underline font-medium">
                Next →
              </Link>
            ) : (
              <span aria-hidden>Next →</span>
            )}
          </span>
        </nav>
      )}
    </>
  );
}
