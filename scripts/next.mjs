// Canonical Next.js CLI, with framework telemetry disabled before CLI import.
process.env.NEXT_TELEMETRY_DISABLED = "1";
await import("../node_modules/next/dist/bin/next");
