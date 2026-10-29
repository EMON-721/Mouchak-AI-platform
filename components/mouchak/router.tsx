"use client";
import { Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { Explore } from "./catalogue";
import { OperatorSecurity } from "./operator-security";
import { SessionWork } from "./session-work";
import { OperatorAuth } from "./operator-auth";
import dynamic from "next/dynamic";
const SitePreview = dynamic(() =>
  import("./site-builder").then((m) => m.SitePreview),
);
import { AdminPage } from "./admin";
import { PublicPage, SourcesPage, StatusPage } from "./public";
function ExploreQuery() {
  const p = useSearchParams();
  return <Explore initialQuery={p.get("q") || ""} />;
}
export function PageRouter({ path }: { path: string[] }) {
  const [first, second] = path;
  if (first === "explore")
    return (
      <Suspense>
        <ExploreQuery />
      </Suspense>
    );
  if (first === "work")
    return <SessionWork key={path.join("/")} pane={second || "history"} />;
  if (
    first === "admin" &&
    ["login", "forgot", "reset", "verify"].includes(second)
  )
    return (
      <Suspense>
        <OperatorAuth mode={second} />
      </Suspense>
    );
  if (first === "admin" && second === "site-preview" && path[2])
    return <SitePreview key={path[2]} version={path[2]} />;
  if (first === "admin" && second === "security") return <OperatorSecurity />;
  if (first === "admin")
    return (
      <AdminPage tab={second === "tools" ? "modules" : second || "overview"} />
    );
  if (first === "sources") return <SourcesPage />;
  if (first === "status") return <StatusPage />;
  return <PublicPage page={first} />;
}
