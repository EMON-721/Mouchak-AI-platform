"use client";
import Link from "next/link";
import { LockKeyhole, ArrowRight } from "lucide-react";
import { useApp } from "./context";
export function SignInPrompt() {
  const { t } = useApp();
  return (
    <div className="page-width empty">
      <LockKeyhole size={40} />
      <h1>{t("প্রশাসনিক প্রবেশ প্রয়োজন", "Operator access required")}</h1>
      <p>
        {t(
          "প্রশাসনিক নিয়ন্ত্রণের জন্য অনুমোদিত পরিচয় ও MFA প্রয়োজন। টুল ব্যবহারে কোনো অ্যাকাউন্ট লাগে না।",
          "Administrative controls require an authorized operator and MFA. Tool use needs no account.",
        )}
      </p>
      <Link className="button dark" href="/admin/login">
        {t("প্রশাসনিক প্রবেশ", "Operator access")}
        <ArrowRight size={17} />
      </Link>
      <Link href="/explore">
        {t("সরাসরি টুল ব্যবহার করুন", "Use tools directly")}
      </Link>
    </div>
  );
}
