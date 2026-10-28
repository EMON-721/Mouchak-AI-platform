"use client";
import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useApp } from "./context";
import { SignInPrompt } from "./account";
type Device = {
  id: string;
  device: string;
  last_seen: number;
  expires: number;
  current: boolean;
};
export function OperatorSecurity() {
  const { api, t, user, loading, refresh } = useApp(),
    router = useRouter();
  const [devices, setDevices] = useState<Device[]>([]),
    [secret, setSecret] = useState(""),
    [code, setCode] = useState(""),
    [error, setError] = useState(""),
    [message, setMessage] = useState(""),
    [busy, setBusy] = useState(false);
  useEffect(() => {
    if (!user) return;
    let live = true;
    api<Device[]>("/api/auth/sessions")
      .then((d) => {
        if (live) setDevices(d);
      })
      .catch((e) => {
        if (live) setError(e.message);
      });
    return () => {
      live = false;
    };
  }, [api, user]);
  async function perform(fn: () => Promise<void>) {
    setError("");
    setBusy(true);
    try {
      await fn();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  if (loading)
    return <p className="page-width">{t("প্রস্তুত হচ্ছে…", "Loading…")}</p>;
  if (!user) return <SignInPrompt />;
  return (
    <div className="page-width settings-page">
      <div className="page-heading">
        <span className="eyebrow">
          {t("শুধু প্রশাসনিক নিরাপত্তা", "OPERATOR SECURITY ONLY")}
        </span>
        <h1>{t("প্রশাসকের MFA ও নিরাপত্তা", "Operator MFA & security")}</h1>
        <p>
          {t(
            "সাধারণ visitor-এর login বা profile নেই। এই পাতাটি শুধু প্রশাসকের সুরক্ষার জন্য।",
            "Visitors have no login or profile. This page protects administrative access only.",
          )}
        </p>
      </div>
      <Link href="/admin">
        {t("প্রশাসনিক নিয়ন্ত্রণে ফিরুন", "Back to administration")}
      </Link>
      {error ? (
        <p className="error" role="alert">
          {error}
        </p>
      ) : null}
      {message ? <p role="status">{message}</p> : null}
      <section className="panel">
        <h2>{t("দুই ধাপের নিরাপত্তা", "Two-factor authentication")}</h2>
        <p>
          {t(
            "Authenticator-এ TOTP setup করে বর্তমান ছয় সংখ্যার code দিন। প্রশাসনিক পরিবর্তনের আগে সাম্প্রতিক MFA যাচাই প্রয়োজন।",
            "Set up TOTP in your authenticator and enter its current six-digit code. Administrative actions require recently verified MFA.",
          )}
        </p>
        {!user.mfa_enabled ? (
          <button
            className="button outline"
            disabled={busy}
            onClick={() =>
              perform(async () => {
                const d = await api<{ secret: string }>(
                  "/api/auth/mfa/enroll",
                  { method: "POST" },
                );
                setSecret(d.secret);
              })
            }
          >
            {t("Authenticator setup শুরু", "Start authenticator setup")}
          </button>
        ) : null}
        {secret ? (
          <div className="notice">
            <p>
              {t(
                "এই key শুধু আপনার authenticator-এ দিন।",
                "Enter this key only into your authenticator.",
              )}
            </p>
            <code>{secret}</code>
          </div>
        ) : null}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            void perform(async () => {
              await api("/api/auth/mfa/verify", {
                method: "POST",
                body: JSON.stringify({ value: { code } }),
              });
              setSecret("");
              setCode("");
              setMessage(t("MFA যাচাই হয়েছে।", "MFA verified."));
              await refresh();
            });
          }}
        >
          <label className="form-field">
            {t("Authenticator code", "Authenticator code")}
            <input
              autoComplete="one-time-code"
              inputMode="numeric"
              pattern="[0-9]{6}"
              maxLength={6}
              required
              value={code}
              onChange={(e) => setCode(e.target.value)}
            />
          </label>
          <button className="button dark" disabled={busy}>
            {t("MFA যাচাই করুন", "Verify MFA")}
          </button>
        </form>
      </section>
      <section className="panel">
        <h2>{t("প্রশাসকের সক্রিয় সেশন", "Active operator sessions")}</h2>
        {devices.map((d) => (
          <article className="grant-card" key={d.id}>
            <p>
              {d.device} {d.current ? t("· এই সেশন", "· this session") : ""}
            </p>
            <p>
              {new Date(d.last_seen * 1000).toLocaleString(undefined, {
                timeZone: "Asia/Dhaka",
              })}
            </p>
            <button
              className="button outline small"
              disabled={busy}
              onClick={() =>
                perform(async () => {
                  await api("/api/auth/sessions/" + d.id, { method: "DELETE" });
                  setDevices(devices.filter((s) => s.id !== d.id));
                  if (d.current) await refresh();
                })
              }
            >
              {t("এই প্রবেশ বাতিল করুন", "Revoke this session")}
            </button>
          </article>
        ))}
        <button
          className="button outline"
          disabled={busy}
          onClick={() =>
            perform(async () => {
              await api("/api/auth/logout", { method: "POST" });
              await refresh();
              router.push("/admin/login");
            })
          }
        >
          {t("প্রশাসনিক প্রবেশ বন্ধ করুন", "End operator access")}
        </button>
      </section>
    </div>
  );
}
