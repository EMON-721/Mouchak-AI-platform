"use client";
import Link from "next/link";
import Image from "next/image";
import { siteAssetUrl } from "./site-config";
import { usePathname } from "next/navigation";
import { useState } from "react";
import {
  ArrowUpRight,
  Menu,
  X,
  LayoutGrid,
  House,
  FolderLock,
  Sun,
  Moon,
  Accessibility,
  Hexagon,
} from "lucide-react";
import { useApp } from "./context";
export function Brand() {
  const { t, brand, site } = useApp();
  return (
    <Link
      href="/"
      className="brand"
      aria-label={t(
        brand.name_bn || "মৌচাক এআই",
        brand.name_en || "Mouchak AI",
      )}
    >
      {site.brand.logo_asset ? (
        <Image
          unoptimized
          src={siteAssetUrl(site.brand.logo_asset)}
          alt=""
          width={62}
          height={62}
        />
      ) : (
        <svg viewBox="0 0 62 62" aria-hidden="true">
          <path
            d="M20 4 33 11v15l-13 8-13-8V11ZM44 18l13 8v15l-13 8-13-8V26ZM20 32l13 8v15l-13 7-13-7V40Z"
            fill="currentColor"
          />
          <path
            d="m20 18 24 15-24 14"
            fill="none"
            stroke="#DBAA4D"
            strokeWidth="4"
          />
        </svg>
      )}
      <span>
        {t(brand.name_bn || "মৌচাক এআই", brand.name_en || "Mouchak AI")}
        <small>{t(site.brand.tagline_bn, site.brand.tagline_en)}</small>
      </span>
    </Link>
  );
}
export function Shell({ children }: { children: React.ReactNode }) {
  const { t, lang, setLang, brand, site, sitePublished } = useApp();
  const path = usePathname();
  const [menu, setMenu] = useState(false),
    [dark, setDark] = useState(false),
    [large, setLarge] = useState(false);
  function theme() {
    setDark((v) => !v);
    document.documentElement.dataset.theme = dark ? "light" : "dark";
  }
  function size() {
    setLarge((v) => !v);
    document.documentElement.dataset.large = large ? "false" : "true";
  }
  const nav = site.navigation.map((x) => [x.href, t(x.bn, x.en)]);
  return (
    <>
      <a className="skip" href="#main">
        {t("মূল অংশে যান", "Skip to content")}
      </a>
      <header className="site-header">
        <div className="header-inner">
          <Brand />
          <nav
            className="desktop-nav"
            aria-label={t("প্রধান নেভিগেশন", "Main navigation")}
          >
            {nav.map(([url, label]) => (
              <Link
                className={path === url ? "active" : ""}
                key={url}
                href={url}
              >
                {label}
              </Link>
            ))}
          </nav>
          <div className="header-actions">
            <button
              className="language"
              onClick={() => setLang(lang === "bn" ? "en" : "bn")}
              aria-label="Switch language"
            >
              {lang === "bn" ? "EN" : "বাংলা"}
            </button>
            <button
              className="icon-button theme-button"
              onClick={theme}
              aria-label={t("রং পরিবর্তন", "Toggle theme")}
            >
              {dark ? <Sun size={18} /> : <Moon size={18} />}
            </button>
            <button
              className="icon-button access-button"
              onClick={size}
              aria-label={t("বড় অক্ষর", "Toggle larger text")}
              aria-pressed={large}
            >
              <Accessibility size={19} />
            </button>
            <Link className="button small dark" href="/explore">
              {t("টুল ব্যবহার করুন", "Use tools")}
              <ArrowUpRight size={16} />
            </Link>
            <button
              className="icon-button mobile-menu"
              aria-expanded={menu}
              aria-label={t("মেনু", "Menu")}
              onClick={() => setMenu(!menu)}
            >
              {menu ? <X /> : <Menu />}
            </button>
          </div>
        </div>
        {menu ? (
          <nav className="mobile-dropdown">
            {nav.map(([url, label]) => (
              <Link onClick={() => setMenu(false)} key={url} href={url}>
                {label}
              </Link>
            ))}
          </nav>
        ) : null}
      </header>
      <main id="main">{children}</main>
      <footer>
        <div className="footer-inner">
          <div>
            <Brand />
            <p>
              {t(
                sitePublished
                  ? site.footer.text.bn
                  : brand.tagline_bn || site.footer.text.bn,
                sitePublished
                  ? site.footer.text.en
                  : brand.tagline_en || site.footer.text.en,
              )}
              <br />
              {t(
                "ফলাফলের সঙ্গে যুক্তি, উৎস ও সীমাবদ্ধতা।",
                "Evidence, sources and honest limitations.",
              )}
            </p>
          </div>
          <div className="footer-links">
            {[
              ...site.footer.links.map((x) => [x.href, t(x.bn, x.en)]),
              ["/admin", t("প্রশাসন", "Administration")],
            ].map(([href, label]) => (
              <Link key={href} href={href}>
                {label}
              </Link>
            ))}
          </div>
        </div>
        <div className="footer-note">
          <span>
            © {new Date().getFullYear()}{" "}
            {t(brand.name_bn || "মৌচাক এআই", brand.name_en || "Mouchak AI")}
          </span>
          <span>{t(site.footer.note.bn, site.footer.note.en)}</span>
          <span className="dot-label">
            {t(
              "সীমিত কার্যক্রম · পরীক্ষাধীন",
              "Limited capabilities · under evaluation",
            )}
          </span>
        </div>
      </footer>
      <nav className="bottom-nav" aria-label="Mobile navigation">
        {[
          ["/", House, t("হোম", "Home")],
          ["/explore", LayoutGrid, t("টুল", "Explore")],
          ["/work", FolderLock, t("এই সেশনের কাজ", "Session work")],
          ["/help", Accessibility, t("সহায়তা", "Help")],
        ].map(([href, Icon, label]) => {
          const I = Icon as typeof Hexagon;
          return (
            <Link
              key={String(href)}
              href={String(href)}
              className={path === href ? "active" : ""}
            >
              <I size={20} />
              <span>{String(label)}</span>
            </Link>
          );
        })}
      </nav>
    </>
  );
}
