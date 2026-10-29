import { siteMetadata } from "@/components/mouchak/site-metadata";
import type { Metadata } from "next";
import "./globals.css";
import { Provider } from "@/components/mouchak/context";
import { Shell } from "@/components/mouchak/shell";
export async function generateMetadata(): Promise<Metadata> {
  return siteMetadata();
}
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="bn">
      <body>
        <Provider>
          <Shell>{children}</Shell>
        </Provider>
      </body>
    </html>
  );
}
