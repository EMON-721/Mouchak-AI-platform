import type { NextConfig } from "next";
const developmentScripts = process.env.NODE_ENV === "development" ? " 'unsafe-eval'" : "";
const developmentOrigins = ["terminal.local"];
if (process.env.CODESPACE_NAME) {
  developmentOrigins.push(`${process.env.CODESPACE_NAME}-3000.${process.env.GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN || "app.github.dev"}`);
}
if (process.env.PUBLIC_ORIGIN) {
  // Exact owner-configured preview host; never trust arbitrary forwarded headers.
  developmentOrigins.push(new URL(process.env.PUBLIC_ORIGIN).hostname);
}
const config: NextConfig = {
  output: "standalone",
  allowedDevOrigins: developmentOrigins,
  poweredByHeader: false,
  async headers() {
    return [{
      source: "/:path*",
      headers: [
        { key: "X-Content-Type-Options", value: "nosniff" },
        { key: "Referrer-Policy", value: "same-origin" },
        { key: "X-Frame-Options", value: "DENY" },
        { key: "Content-Security-Policy", value: `default-src 'self'; script-src 'self' 'unsafe-inline'${developmentScripts}; style-src 'self' 'unsafe-inline'; font-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'` },
      ],
    }];
  },
};
export default config;
