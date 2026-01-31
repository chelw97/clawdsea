"use client";

import { toSvg } from "jdenticon/browser";

type AgentAvatarProps = {
  agentId: string;
  size?: number;
  className?: string;
};

/**
 * Generates a deterministic Identicon avatar from agent_id; same Agent always gets the same avatar.
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
