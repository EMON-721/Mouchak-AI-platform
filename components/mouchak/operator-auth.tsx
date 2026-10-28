"use client";
import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { useApp } from "./context";
export function OperatorAuth({ mode = "login" }: { mode?: string }) {
  const { api, t, refresh } = useApp();
  const router = useRouter(),
    query = useSearchParams();
  const [email, setEmail] = useState(""),
    [password, setPassword] = useState(""),
    [error, setError] = useState(""),
    [message, setMessage] = useState(""),
    [busy, setBusy] = useState(false);
  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      if (mode === "login") {
        await api("/api/auth/login", {
          method: "POST",
          body: JSON.stringify({ email, password }),
        });
        await refresh();
        router.push("/admin");
      } else {
        const value =
          mode === "forgot"
            ? { email }
            : { token: query.get("token"), password };
        await api("/api/auth/" + (mode === "forgot" ? "request-reset" : mode), {
          method: "POST",
          body: JSON.stringify({ value }),
        });
        setMessage(
          t(
            "অনুরোধ প্রক্রিয়াকরণ হয়েছে। প্রয়োজনে কনফিগার করা সেবায় পরবর্তী নির্দেশনা দেখুন।",
            "Request processed. Follow the next instructions from the configured service if applicable.",
          ),
        );
      }
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="page-width auth-page">
      <section className="panel auth-card">
        <h1>{t("প্রশাসনিক প্রবেশ", "Operator access")}</h1>
        <p>
          {t(
            "এই প্রবেশপথ শুধু অনুমোদিত প্রশাসকের জন্য। সাধারণ ব্যবহারকারী সরাসরি সব উপলভ্য টুল খুলতে পারেন।",
            "This entrance is only for authorized operators. Visitors can open available tools directly.",
          )}
        </p>
        <form onSubmit={submit}>
          {["login", "forgot"].includes(mode) ? (
            <label className="form-field">
              {t("প্রশাসকের ইমেইল", "Operator email")}
              <input
                type="email"
                autoComplete="username"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </label>
          ) : null}
          {["login", "reset"].includes(mode) ? (
            <label className="form-field">
              {t("পাসওয়ার্ড", "Password")}
              <input
                type="password"
                minLength={12}
                autoComplete={
                  mode === "login" ? "current-password" : "new-password"
                }
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </label>
          ) : null}
          <button className="button dark" disabled={busy}>
            {busy
              ? t("অপেক্ষা করুন…", "Please wait…")
              : mode === "login"
                ? t("প্রশাসনিক প্রবেশ", "Operator sign in")
                : t("অনুরোধ পাঠান", "Submit request")}
          </button>
        </form>
        {error ? (
          <p className="error" role="alert">
            {error}
          </p>
        ) : null}
        {message ? <p role="status">{message}</p> : null}
        <Link href="/admin/forgot">
          {t("প্রশাসকের পাসওয়ার্ড পুনরুদ্ধার", "Operator password recovery")}
        </Link>
        <Link href="/explore">
          {t("সরাসরি টুল ব্যবহার করুন", "Use tools directly")}
        </Link>
      </section>
    </div>
  );
}
