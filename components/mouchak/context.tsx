"use client";
import {
  createContext,
  useContext,
  useEffect,
  useState,
  useCallback,
  useSyncExternalStore,
  ReactNode,
} from "react";
import type { Lang, User } from "./types";
import { usePathname } from "next/navigation";
type Ctx = {
  lang: Lang;
  t: (bn: string, en: string) => string;
  setLang: (l: Lang) => void;
  user: User | null;
  csrf: string;
  loading: boolean;
  refresh: () => Promise<void>;
  api: <T = unknown>(path: string, options?: RequestInit) => Promise<T>;
  brand: Record<string, string>;
};
const Context = createContext<Ctx | null>(null);
type Snapshot = { user: User | null; csrf: string };
let publicHandshake: Promise<Snapshot> | null = null;
async function readIdentity(mode: string): Promise<Snapshot> {
  async function request(): Promise<Snapshot> {
    const r = await fetch(
      mode === "admin" ? "/api/auth/me" : "/api/session",
      mode === "admin" ? {} : { method: "POST" },
    );
    if (!r.ok) return { user: null, csrf: "" };
    const d = (await r.json()) as {
      user?: User;
      visitor_id?: string;
      role?: string;
      csrf?: string;
    };
    if (
      typeof d.csrf !== "string" ||
      (mode === "admin"
        ? !d.user?.id
        : typeof d.visitor_id !== "string" || typeof d.role !== "string")
    )
      throw new Error("Invalid session response");
    return {
      user:
        mode === "admin"
          ? d.user!
          : {
              id: d.visitor_id!,
              role: d.role!,
              email: "",
              name: "",
              verified: false,
              language: "bn",
              mfa_enabled: false,
            },
      csrf: d.csrf,
    };
  }
  if (mode === "admin") return request();
  if (!publicHandshake)
    publicHandshake = request().finally(() => {
      publicHandshake = null;
    });
  return publicHandshake;
}

function subscribeLanguage(callback: () => void) {
  window.addEventListener("mouchak-language", callback);
  window.addEventListener("storage", callback);
  return () => {
    window.removeEventListener("mouchak-language", callback);
    window.removeEventListener("storage", callback);
  };
}
function languageSnapshot(): Lang {
  try {
    return localStorage.getItem("mouchak-language-v1") === "en" ? "en" : "bn";
  } catch {
    return "bn";
  }
}
export function Provider({ children }: { children: ReactNode }) {
  const path = usePathname();
  const mode = path.startsWith("/admin") ? "admin" : "public";
  const [loadedMode, setLoadedMode] = useState<string | null>(null);
  const lang = useSyncExternalStore(
    subscribeLanguage,
    languageSnapshot,
    () => "bn" as Lang,
  );
  const [user, setUser] = useState<User | null>(null),
    [csrf, setCsrf] = useState(""),
    [loading, setLoading] = useState(true),
    [brand, setBrand] = useState<Record<string, string>>({});
  const refresh = useCallback(async () => {
    try {
      const d = await readIdentity(mode);
      setUser(d.user);
      setCsrf(d.csrf);
    } catch {
      setUser(null);
      setCsrf("");
    } finally {
      setLoadedMode(mode);
      setLoading(false);
    }
  }, [mode]);
  useEffect(() => {
    let live = true;
    readIdentity(mode)
      .then((d) => {
        if (live) {
          setUser(d.user);
          setCsrf(d.csrf);
        }
      })
      .catch(() => {
        if (live) {
          setUser(null);
          setCsrf("");
        }
      })
      .finally(() => {
        if (live) {
          setLoadedMode(mode);
          setLoading(false);
        }
      });
    return () => {
      live = false;
    };
  }, [mode]);
  useEffect(() => {
    let live = true;
    fetch("/api/public/cms/brand")
      .then((r) => (r.ok ? r.json() : {}))
      .then((d) => {
        if (live) setBrand(d);
      })
      .catch(() => {});
    return () => {
      live = false;
    };
  }, []);
  useEffect(() => {
    document.documentElement.lang = lang;
  }, [lang]);
  const setLang = (l: Lang) => {
    localStorage.setItem("mouchak-language-v1", l);
    window.dispatchEvent(new Event("mouchak-language"));
  };
  const api = useCallback(
    async <T,>(path: string, options: RequestInit = {}): Promise<T> => {
      const h = new Headers(options.headers);
      if (
        options.body &&
        !(options.body instanceof FormData) &&
        !h.has("Content-Type")
      )
        h.set("Content-Type", "application/json");
      if (csrf && loadedMode === mode) h.set("X-CSRF-Token", csrf);
      const r = await fetch(path, { ...options, headers: h });
      const d = (await r.json()) as Record<string, unknown>;
      if (!r.ok)
        throw new Error(
          typeof d.detail === "string"
            ? d.detail
            : "অনুরোধ ব্যর্থ / Request failed",
        );
      return d as T;
    },
    [csrf, loadedMode, mode],
  );
  return (
    <Context.Provider
      value={{
        lang,
        t: (bn, en) => (lang === "bn" ? bn : en),
        setLang,
        user: loadedMode === mode ? user : null,
        csrf: loadedMode === mode ? csrf : "",
        loading: loadedMode !== mode || loading,
        refresh,
        api,
        brand,
      }}
    >
      {children}
    </Context.Provider>
  );
}
export function useApp() {
  const c = useContext(Context);
  if (!c) throw Error("Provider required");
  return c;
}
