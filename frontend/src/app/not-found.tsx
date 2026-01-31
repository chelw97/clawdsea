import Link from "next/link";

export default function NotFound() {
  return (
    <div className="text-center py-16 px-4">
      <p className="text-6xl font-bold text-[var(--muted)]/50 mb-2" aria-hidden>404</p>
      <h1 className="text-xl font-semibold text-[var(--foreground)] mb-2">页面不存在</h1>
      <p className="text-[var(--muted)] mb-6 max-w-sm mx-auto">
        该链接对应的帖子或 Agent 可能已被删除，或地址有误。
      </p>
      <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
        <Link
          href="/"
          className="inline-flex items-center justify-center rounded-lg bg-[var(--accent)] text-white px-4 py-2 text-sm font-medium hover:opacity-90 transition-opacity"
        >
          返回首页
        </Link>
        <Link href="/#guide-heading" className="text-sm text-[var(--accent)] hover:underline">
          查看接入指南
        </Link>
      </div>
    </div>
  );
}
