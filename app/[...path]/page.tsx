import { PageRouter } from "@/components/mouchak/router";
import { notFound } from "next/navigation";
const allowed = new Set([
  "explore",
  "work",
  "admin",
  "about",
  "methodology",
  "sources",
  "privacy",
  "terms",
  "help",
  "contact",
  "status",
]);
export default async function Page({
  params,
}: {
  params: Promise<{ path: string[] }>;
}) {
  const { path } = await params;
  if (!allowed.has(path[0])) notFound();
  return <PageRouter key={path.join("/")} path={path} />;
}
