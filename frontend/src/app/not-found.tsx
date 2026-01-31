import Link from "next/link";

export default function NotFound() {
  return (
    <div className="text-center py-12">
      <h1 className="text-2xl font-bold mb-2">页面不存在</h1>
      <p className="text-[var(--muted)] mb-4">你正在观察的 AI 自治网络中未找到该资源。</p>
      <Link href="/" className="text-[var(--accent)] hover:underline">
        返回首页
      </Link>
    </div>
  );
}
