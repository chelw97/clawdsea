/**
 * Quick test for buildCommentTree: flat list -> nested 楼中楼 tree.
 * Run: node frontend/scripts/test-comment-tree.mjs
 */
const flat = [
  { id: "1", post_id: "p1", parent_comment_id: null, author_agent_id: "a1", author_name: "Alice", content: "Root", score: 0, created_at: "2025-01-01T10:00:00Z", replies: [] },
  { id: "2", post_id: "p1", parent_comment_id: "1", author_agent_id: "a2", author_name: "Bob", content: "Reply to root", score: 0, created_at: "2025-01-01T10:01:00Z", replies: [] },
  { id: "3", post_id: "p1", parent_comment_id: "2", author_agent_id: "a1", author_name: "Alice", content: "Reply to reply", score: 0, created_at: "2025-01-01T10:02:00Z", replies: [] },
];

function buildCommentTree(flatList) {
  const byId = new Map();
  const withReplies = flatList.map((c) => ({ ...c, replies: [] }));
  withReplies.forEach((c) => byId.set(c.id, c));

  const roots = [];
  for (const c of withReplies) {
    const parentId = c.parent_comment_id ?? null;
    if (parentId == null) roots.push(c);
    else {
      const parent = byId.get(String(parentId));
      if (parent) parent.replies.push(c);
      else roots.push(c);
    }
  }

  const sortByCreated = (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
  roots.sort(sortByCreated);
  withReplies.forEach((c) => c.replies.sort(sortByCreated));
  return roots;
}

const tree = buildCommentTree(flat);
const ok = tree.length === 1 && tree[0].replies.length === 1 && tree[0].replies[0].replies.length === 1;
if (!ok) {
  console.error("FAIL: expected 1 root -> 1 reply -> 1 reply, got", JSON.stringify(tree, null, 2));
  process.exit(1);
}
console.log("OK: comment tree (楼中楼) – 1 root, 1 reply, 1 nested reply");
console.log("  Root:", tree[0].content);
console.log("    Reply:", tree[0].replies[0].content);
console.log("      Nested:", tree[0].replies[0].replies[0].content);
