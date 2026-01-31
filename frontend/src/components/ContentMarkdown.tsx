import ReactMarkdown from "react-markdown";

/**
 * Normalize content: literal "\n" (backslash + n) from API to real newlines
 * so Markdown and whitespace-pre-wrap behave correctly.
 */
function normalizeNewlines(text: string): string {
  if (typeof text !== "string") return "";
  return text.replace(/\\n/g, "\n");
}

interface ContentMarkdownProps {
  content: string;
  className?: string;
}

export function ContentMarkdown({ content, className }: ContentMarkdownProps) {
  const normalized = normalizeNewlines(content ?? "");
  return (
    <div className={className}>
      <ReactMarkdown
        components={{
          p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
          strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
          ul: ({ children }) => <ul className="list-disc list-inside my-2 space-y-0.5">{children}</ul>,
          ol: ({ children }) => <ol className="list-decimal list-inside my-2 space-y-0.5">{children}</ol>,
          li: ({ children }) => <li>{children}</li>,
        }}
      >
        {normalized}
      </ReactMarkdown>
    </div>
  );
}
