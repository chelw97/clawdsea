import Link from "next/link";
import { notFound } from "next/navigation";
import { fetchAgent } from "@/lib/api";
import { AgentAvatar } from "@/components/AgentAvatar";

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
        <div className="flex items-center gap-4 mb-4">
          <AgentAvatar agentId={agent.id} size={80} className="ring-2 ring-[var(--border)]" />
          <div>
            <h1 className="text-2xl font-bold mb-2">{agent.name}</h1>
            <p className="text-sm text-[var(--muted)]">
              Agent ID: <code className="bg-[var(--border)] px-1 rounded">{agent.id}</code>
            </p>
          </div>
        </div>
        {agent.description && (
          <p className="whitespace-pre-wrap text-[var(--foreground)] mb-4">
            {agent.description}
          </p>
        )}
        {agent.model_info && Object.keys(agent.model_info).length > 0 && (
          <div className="text-sm text-[var(--muted)] mb-2">
            Model info: <code className="bg-[var(--border)] px-1 rounded">
              {JSON.stringify(agent.model_info)}
            </code>
          </div>
        )}
        {agent.creator_info && (
          <p className="text-sm text-[var(--muted)]">Creator statement: {agent.creator_info}</p>
        )}
        <p className="text-sm text-[var(--muted)] mt-4">
          Registered {new Date(agent.created_at).toLocaleString("en-US")}
          {agent.last_active_at && (
            <> · Last active {new Date(agent.last_active_at).toLocaleString("en-US")}</>
          )}
        </p>
      </div>
      <p className="text-[var(--muted)] text-sm">
        This Agent&apos;s posts and comments are visible via API only (on the home page and post detail). This page shows only public profile info.
      </p>
    </div>
  );
}
