import { ToolWorkspace } from "@/components/mouchak/tool";
import source from "@/packages/module-registry/catalogue.json";
import { notFound } from "next/navigation";
export default async function Page({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  if (!source.modules.some((m) => m.slug === slug)) notFound();
  return <ToolWorkspace key={slug} slug={slug} />;
}
