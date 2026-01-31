"use client";

import { toSvg } from "jdenticon/browser";

type AgentAvatarProps = {
  agentId: string;
  size?: number;
  className?: string;
};

/**
 * 根据 agent_id 生成确定性 Identicon 头像，同一 Agent 始终相同。
 */
export function AgentAvatar({ agentId, size = 32, className = "" }: AgentAvatarProps) {
  const svg = toSvg(agentId, size);
  return (
    <span
      className={`inline-block shrink-0 overflow-hidden rounded-full bg-[var(--border)] ${className}`}
      style={{ width: size, height: size }}
      title={agentId}
    >
      <span
        className="block"
        style={{ width: size, height: size }}
        dangerouslySetInnerHTML={{ __html: svg }}
      />
    </span>
  );
}
