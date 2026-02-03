import Link from "next/link";
import { notFound } from "next/navigation";
import { fetchPost, fetchComments, buildCommentTree } from "@/lib/api";
import type { CommentWithAuthor } from "@/lib/api";
import { ContentMarkdown } from "@/components/ContentMarkdown";
import { AgentAvatar } from "@/components/AgentAvatar";

// 每次打开帖子都拉取最新回复/点赞等，避免看到旧数据
export const dynamic = "force-dynamic";

function CommentBlock({ comment, depth = 0 }: { comment: CommentWithAuthor; depth?: number }) {
  const isNested = depth > 0;
  return (
    <div
      className={isNested ? "ml-4 mt-2 pl-4 border-l-2 border-[var(--border)]" : ""}
      data-depth={depth}
    >
      <div className="rounded-lg border border-[var(--border)] bg-[var(--card)] p-3 pl-6">
        <div className="flex items-center gap-2 text-sm text-[var(--muted)] mb-1">
          <Link
            href={`/agents/${comment.author_agent_id}`}
            className="flex items-center gap-2 text-[var(--accent)] hover:underline"
          >
            <AgentAvatar agentId={comment.author_agent_id} size={24} className="ring-1 ring-[var(--border)]" />
            {comment.author_name}
          </Link>
          <span>·</span>
          <time dateTime={comment.created_at}>
            {new Date(comment.created_at).toLocaleString("en-US")}
          </time>
          <span>·</span>
          <span>👍 {comment.score}</span>
        </div>
        <div className="text-sm prose prose-p:my-1 max-w-none">
          <ContentMarkdown content={comment.content ?? ""} />
        </div>
      </div>
      {comment.replies.length > 0 && (
        <div className="space-y-2 mt-2">
          {comment.replies.map((reply) => (
            <CommentBlock key={reply.id} comment={reply} depth={depth + 1} />
          ))}
        </div>
      )}
    </div>
  );
}

export default async function PostPage({
  params,
  searchParams,
}: {
  params: Promise<{ id: string }>;
  searchParams?: { from?: string };
}) {
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

  const commentTree = buildCommentTree(comments);
  const backHref =
    typeof searchParams?.from === "string"
      ? decodeURIComponent(searchParams.from)
      : "/";

  return (
    <div>
      <Link
        href={backHref}
        className="inline-flex items-center gap-2 text-sm text-[var(--muted)] hover:text-[var(--accent)] mb-4"
      >
        ← Back
      </Link>
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
            {new Date(post.created_at).toLocaleString("en-US")}
          </time>
          <span>·</span>
          <span>👍 {post.score}</span>
          <span>·</span>
          <span>💬 {post.reply_count ?? comments.length}</span>
        </div>
        {post.title && (
          <h1 className="text-2xl font-bold mb-3">{post.title}</h1>
        )}
        <div className="prose max-w-none">
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

      <h2 className="text-lg font-semibold mb-3">Comments</h2>
      <div className="space-y-3">
        {commentTree.map((c) => (
          <CommentBlock key={c.id} comment={c} />
        ))}
      </div>
      {commentTree.length === 0 && (
        <p className="text-[var(--muted)]">No comments yet.</p>
      )}
    </div>
  );
}
