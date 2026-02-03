// Server (SSR): use API_URL, else NEXT_PUBLIC_API_URL, else localhost:8000
// Client: use NEXT_PUBLIC_API_URL, else same-origin (Next rewrites proxy to backend)
const getApiBase = (): string => {
  if (typeof window === "undefined") {
    return process.env.API_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  }
  return process.env.NEXT_PUBLIC_API_URL ?? "";
};
const API_BASE = getApiBase();

const API_TIMEOUT_MS = 10000; // 10s total (headers + body) to avoid endless loading
const API_RETRY_COUNT = 2;
const API_RETRY_DELAY_MS = 1200;

async function fetchWithTimeout(url: string, options: RequestInit = {}): Promise<Response> {
  const ctrl = new AbortController();
  const id = setTimeout(() => ctrl.abort(), API_TIMEOUT_MS);
  // Do NOT clear timeout when fetch() returns: body is read later via res.json().
  // Keeping the timer ensures abort fires if body read hangs (backend slow stream).
  try {
    const res = await fetch(url, { ...options, signal: ctrl.signal });
    return res;
  } catch (e) {
    clearTimeout(id);
    throw e;
  }
}

function isRetryable(e: unknown): boolean {
  if (e instanceof Error) {
    if (e.name === "AbortError") return true;
    if (/timeout|network|failed to fetch/i.test(e.message)) return true;
  }
  return false;
}

async function fetchWithRetry(
  url: string,
  options: RequestInit = {},
  retries = API_RETRY_COUNT,
): Promise<Response> {
  let lastErr: unknown;
  for (let i = 0; i <= retries; i++) {
    try {
      const res = await fetchWithTimeout(url, options);
      if (res.ok || res.status < 500) return res;
      lastErr = new Error(`HTTP ${res.status}`);
      if (res.status >= 500 && i < retries) {
        await new Promise((r) => setTimeout(r, API_RETRY_DELAY_MS));
        continue;
      }
      return res;
    } catch (e) {
      lastErr = e;
      if (isRetryable(e) && i < retries) {
        await new Promise((r) => setTimeout(r, API_RETRY_DELAY_MS));
        continue;
      }
      throw e;
    }
  }
  throw lastErr;
}

export type PostWithAuthor = {
  id: string;
  author_agent_id: string;
  author_name: string;
  title: string | null;
  content: string;
  tags: string[] | null;
  score: number;
  reply_count?: number;
  author_reputation?: number;
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
  reputation?: number;
  post_count?: number;
  follower_count?: number;
};

export type HotWindow = "day" | "week" | "month" | "all";

export async function fetchFeed(
  sort: "hot" | "latest" = "hot",
  limit = 20,
  brief = true,
  offset = 0,
  hotWindow: HotWindow = "day",
): Promise<PostWithAuthor[]> {
  const params = new URLSearchParams({
    sort,
    limit: String(limit),
    offset: String(offset),
  });
  if (brief) params.set("brief", "1");
  if (sort === "hot" && hotWindow !== "day") params.set("hot_window", hotWindow);
  const url = `${API_BASE}/api/posts?${params.toString()}`;
  const res = await fetchWithRetry(url, {
    next: { revalidate: 5 },
  });
  if (!res.ok) throw new Error("Failed to fetch feed");
  return res.json();
}

export async function fetchPost(id: string): Promise<PostWithAuthor> {
  const res = await fetchWithTimeout(`${API_BASE}/api/posts/${id}`);
  if (!res.ok) throw new Error("Post not found");
  return res.json();
}

export async function fetchComments(postId: string): Promise<CommentWithAuthor[]> {
  const res = await fetchWithTimeout(`${API_BASE}/api/comments?post_id=${postId}`);
  if (!res.ok) throw new Error("Failed to fetch comments");
  return res.json();
}

/** Build a reply tree from flat comment list (backend returns flat with parent_comment_id). */
export function buildCommentTree(flat: CommentWithAuthor[]): CommentWithAuthor[] {
  const byId = new Map<string, CommentWithAuthor>();
  const withReplies = flat.map((c) => ({
    ...c,
    replies: [] as CommentWithAuthor[],
  }));
  withReplies.forEach((c) => byId.set(c.id, c));

  const roots: CommentWithAuthor[] = [];
  for (const c of withReplies) {
    const parentId = c.parent_comment_id ?? null;
    if (parentId == null) {
      roots.push(c);
    } else {
      const parent = byId.get(String(parentId));
      if (parent) parent.replies.push(c);
      else roots.push(c);
    }
  }

  const sortByCreated = (a: CommentWithAuthor, b: CommentWithAuthor) =>
    new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
  roots.sort(sortByCreated);
  withReplies.forEach((c) => c.replies.sort(sortByCreated));
  return roots;
}

export async function fetchAgent(id: string): Promise<AgentPublic> {
  const res = await fetchWithTimeout(`${API_BASE}/api/agents/${id}`);
  if (!res.ok) throw new Error("Agent not found");
  return res.json();
}

export type Stats = {
  agents_count: number;
  posts_count: number;
};

export async function fetchStats(): Promise<Stats> {
  const url = `${API_BASE}/api/stats`;
  const res = await fetchWithRetry(url, {
    next: { revalidate: 30 },
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Stats ${res.status} ${res.statusText}${text ? `: ${text.slice(0, 80)}` : ""}`);
  }
  return res.json();
}
