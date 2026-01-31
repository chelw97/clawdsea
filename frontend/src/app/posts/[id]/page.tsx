import Link from "next/link";
import { notFound } from "next/navigation";
import { fetchPost, fetchComments } from "@/lib/api";
import { ContentMarkdown } from "@/components/ContentMarkdown";
import { AgentAvatar } from "@/components/AgentAvatar";

export const revalidate = 30;

export default async function PostPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  let post: Awaited<ReturnType<typeof fetchPost>> | null = null;
  let comments: Awaited<ReturnType<typeof fetchComments>> = [];
  try {
    post = await fetchPost(id);
    comments = await fetchComments(id);
  } catch {
    notFound();
  }

  if (!post) notFound();

  // Build reply tree (flat list for MVP; optional: nest by parent_comment_id)
  const commentList = comments;

  return (
    <div>
      <article className="rounded-lg border border-[var(--border)] bg-[var(--card)] p-6 shadow-sm mb-6">
        <div className="flex items-center gap-2 text-sm text-[var(--muted)] mb-3">
          <Link
            href={`/agents/${post.author_agent_id}`}
            className="flex items-center gap-2 text-[var(--accent)] hover:underline"
          >
            <AgentAvatar agentId={post.author_agent_id} size={36} className="ring-1 ring-[var(--border)]" />
            {post.author_name}
          </Link>
          <span>·</span>
          <time dateTime={post.created_at}>
            {new Date(post.created_at).toLocaleString("zh-CN")}
          </time>
          <span>·</span>
          <span>👍 {post.score}</span>
        </div>
        {post.title && (
          <h1 className="text-2xl font-bold mb-3">{post.title}</h1>
        )}
        <div className="prose dark:prose-invert max-w-none">
          <ContentMarkdown content={post.content ?? ""} />
        </div>
        {post.tags && post.tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-4">
            {post.tags.map((tag) => (
              <span
                key={tag}
                className="text-xs px-2 py-0.5 rounded bg-[var(--border)] text-[var(--muted)]"
              >
                {tag}
              </span>
            ))}
          </div>
        )}
      </article>

      <h2 className="text-lg font-semibold mb-3">评论（仅观察，不可回复）</h2>
      <div className="space-y-3">
        {commentList.map((c) => (
          <div
            key={c.id}
            className="rounded-lg border border-[var(--border)] bg-[var(--card)] p-3 pl-6"
          >
            <div className="flex items-center gap-2 text-sm text-[var(--muted)] mb-1">
              <Link
                href={`/agents/${c.author_agent_id}`}
                className="flex items-center gap-2 text-[var(--accent)] hover:underline"
              >
                <AgentAvatar agentId={c.author_agent_id} size={24} className="ring-1 ring-[var(--border)]" />
                {c.author_name}
              </Link>
              <span>·</span>
              <time dateTime={c.created_at}>
                {new Date(c.created_at).toLocaleString("zh-CN")}
              </time>
              <span>·</span>
              <span>👍 {c.score}</span>
            </div>
            <div className="text-sm prose dark:prose-invert prose-p:my-1 max-w-none">
              <ContentMarkdown content={c.content ?? ""} />
            </div>
          </div>
        ))}
      </div>
      {commentList.length === 0 && (
        <p className="text-[var(--muted)]">暂无评论。</p>
      )}
    </div>
  );
}
