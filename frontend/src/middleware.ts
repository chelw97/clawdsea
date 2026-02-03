import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

/**
 * Reject malformed POSTs that Next.js treats as Server Action calls with invalid ID (e.g. "x").
 * Bots/crawlers can send these and trigger "Failed to find Server Action x" → process crash.
 * We don't use Server Actions; blocking short action IDs is safe.
 */
export function middleware(request: NextRequest) {
  if (request.method === "POST") {
    const actionId =
      request.headers.get("next-action") ?? request.headers.get("Next-Action") ?? "";
    if (actionId.length > 0 && actionId.length < 8) {
      return NextResponse.json({ error: "Bad Request" }, { status: 400 });
    }
  }
  return NextResponse.next();
}
