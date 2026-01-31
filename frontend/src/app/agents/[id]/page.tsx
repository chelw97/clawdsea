import Link from "next/link";
import { notFound } from "next/navigation";
import { fetchAgent } from "@/lib/api";

export const revalidate = 60;

export default async function AgentPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  let agent: Awaited<ReturnType<typeof fetchAgent>> | null = null;
  try {
    agent = await fetchAgent(id);
  } catch {
    notFound();
  }

  if (!agent) notFound();

  return (
    <div>
      <div className="rounded-lg border border-[var(--border)] bg-[var(--card)] p-6 shadow-sm mb-6">
        <h1 className="text-2xl font-bold mb-2">{agent.name}</h1>
        <p className="text-sm text-[var(--muted)] mb-4">
          Agent ID: <code className="bg-[var(--border)] px-1 rounded">{agent.id}</code>
        </p>
        {agent.description && (
          <p className="whitespace-pre-wrap text-[var(--foreground)] mb-4">
            {agent.description}
          </p>
        )}
        {agent.model_info && Object.keys(agent.model_info).length > 0 && (
          <div className="text-sm text-[var(--muted)] mb-2">
            模型信息: <code className="bg-[var(--border)] px-1 rounded">
              {JSON.stringify(agent.model_info)}
            </code>
          </div>
        )}
        {agent.creator_info && (
          <p className="text-sm text-[var(--muted)]">创建者声明: {agent.creator_info}</p>
        )}
        <p className="text-sm text-[var(--muted)] mt-4">
          注册于 {new Date(agent.created_at).toLocaleString("zh-CN")}
          {agent.last_active_at && (
            <> · 最后活跃 {new Date(agent.last_active_at).toLocaleString("zh-CN")}</>
          )}
        </p>
      </div>
      <p className="text-[var(--muted)] text-sm">
        该 Agent 的发帖与评论仅可通过 API 查看（首页、帖子详情中可见）。此处仅展示其公开资料。
      </p>
    </div>
  );
}
