import type { Metadata } from "next";
import "./globals.css";
import { Provider } from "@/components/mouchak/context";
import { Shell } from "@/components/mouchak/shell";
export const metadata: Metadata = {
  title: { default: "মৌচাক এআই · Mouchak AI", template: "%s · Mouchak AI" },
  description:
    "৫০টি বাংলাদেশভিত্তিক টুল, এক কেন্দ্রীয় কর্মক্ষেত্র। Verified capabilities and honest limitations.",
  robots: { index: false, follow: false },
};
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
