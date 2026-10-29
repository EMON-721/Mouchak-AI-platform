import type { Metadata } from "next";
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
export async function generateMetadata({
  params,
}: {
  params: Promise<{ path: string[] }>;
}): Promise<Metadata> {
  const { path } = await params;
  return ["admin", "work"].includes(path[0])
    ? { robots: { index: false, follow: false } }
    : {};
}
export default async function Page({
  params,
}: {
  params: Promise<{ path: string[] }>;
}) {
  const { path } = await params;
  if (!allowed.has(path[0])) notFound();
  return <PageRouter key={path.join("/")} path={path} />;
}
