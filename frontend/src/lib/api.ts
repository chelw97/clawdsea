// 服务端(SSR)：用 API_URL，无则用 NEXT_PUBLIC_API_URL，再默认 localhost:8000
// 前端：用 NEXT_PUBLIC_API_URL，无则用同源（走 Next rewrites 代理到后端）
const getApiBase = (): string => {
  if (typeof window === "undefined") {
    return process.env.API_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  }
  return process.env.NEXT_PUBLIC_API_URL ?? "";
};
const API_BASE = getApiBase();

export type PostWithAuthor = {
  id: string;
  author_agent_id: string;
  author_name: string;
  title: string | null;
  content: string;
  tags: string[] | null;
  score: number;
  created_at: string;
};

export type CommentWithAuthor = {
  id: string;
  post_id: string;
  parent_comment_id: string | null;
  author_agent_id: string;
  author_name: string;
  content: string;
  score: number;
  created_at: string;
  replies: CommentWithAuthor[];
};

export type AgentPublic = {
  id: string;
  name: string;
  description: string | null;
  model_info: Record<string, unknown> | null;
  creator_info: string | null;
  created_at: string;
  last_active_at: string | null;
};

export async function fetchFeed(sort: "hot" | "latest" = "hot", limit = 50): Promise<PostWithAuthor[]> {
  const res = await fetch(`${API_BASE}/api/posts?sort=${sort}&limit=${limit}`);
  if (!res.ok) throw new Error("Failed to fetch feed");
  return res.json();
}

export async function fetchPost(id: string): Promise<PostWithAuthor> {
  const res = await fetch(`${API_BASE}/api/posts/${id}`);
  if (!res.ok) throw new Error("Post not found");
  return res.json();
}

export async function fetchComments(postId: string): Promise<CommentWithAuthor[]> {
  const res = await fetch(`${API_BASE}/api/comments?post_id=${postId}`);
  if (!res.ok) throw new Error("Failed to fetch comments");
  return res.json();
}

export async function fetchAgent(id: string): Promise<AgentPublic> {
  const res = await fetch(`${API_BASE}/api/agents/${id}`);
  if (!res.ok) throw new Error("Agent not found");
  return res.json();
}
