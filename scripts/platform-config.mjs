import { existsSync } from "node:fs";

export function portNumber(value, name) {
  if (!/^\d+$/.test(String(value)) || Number(value) < 1 || Number(value) > 65535)
    throw new Error(`${name} must be an integer from 1 to 65535`);
  return String(Number(value));
}

export function developmentConfig(env, raw = [], managed = false, platform = process.platform, exists = existsSync) {
  if (env.MOUCHAK_ENV === "production")
    throw new Error("pnpm dev is development only. Use docs/DEPLOYMENT.md for production services.");
  const args = raw.filter((a) => a !== "--strictPort").map((a) => a === "--host" ? "--hostname" : a);
  const index = args.findIndex((a) => a === "--port" || a === "-p");
  const inline = args.find((a) => a.startsWith("--port="));
  const port = portNumber(index >= 0 ? args[index + 1] : inline ? inline.slice(7) : env.PORT || 3000, "Web port");
  const apiPort = portNumber(env.MOUCHAK_API_PORT || 8000, "API port");
  if (port === apiPort) throw new Error("Web and private API ports must differ");
  const codespace = env.CODESPACE_NAME;
  const domain = env.GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN || "app.github.dev";
  if (codespace && (!/^[a-z0-9-]+$/i.test(codespace) || !/^[a-z0-9.-]+$/i.test(domain)))
    throw new Error("Invalid Codespaces forwarding configuration");
  const fallback = managed ? `http://terminal.local:${port}` : codespace ? `https://${codespace}-${port}.${domain}` : `http://localhost:${port}`;
  const parsed = new URL(env.PUBLIC_ORIGIN || fallback);
  if (!["http:", "https:"].includes(parsed.protocol) || parsed.username || parsed.password || parsed.search || parsed.hash || parsed.pathname !== "/")
    throw new Error("PUBLIC_ORIGIN must be an HTTP(S) origin without credentials, path or query");
  const venv = platform === "win32" ? ".venv/Scripts/python.exe" : ".venv/bin/python";
  const python = env.MOUCHAK_PYTHON || (exists(venv) ? venv : platform === "win32" ? "python" : "python3");
  if (index < 0 && !inline) args.push("--port", port);
  return { python, port, apiPort, origin: parsed.origin, args };
}
