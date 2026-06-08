"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useTranslation } from "react-i18next";

const getLinks = (t: (k: string) => string) => [
  { href: "/dashboard", label: t("dashboard") },
  { href: "/patients", label: t("patients") },
  { href: "/agenda", label: t("agenda") },
  { href: "/triage", label: t("triage") },
  { href: "/billing", label: t("billing") },
  { href: "/messages", label: "Messages" },
  { href: "/admin/users", label: t("admin") },
];

export default function NavBar() {
  const { t, i18n } = useTranslation();
  const pathname = usePathname();

  const toggleLang = () => {
    const next = i18n.language === "fr" ? "en" : "fr";
    i18n.changeLanguage(next);
  };

  return (
    <nav className="border-b border-slate-200 bg-white" aria-label="Navigation principale">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3">
        <Link href="/dashboard" className="text-xl font-bold text-sky-600">
          MedFlow
        </Link>
        <ul className="flex items-center gap-6">
          {getLinks(t).map((l) => {
            const active = pathname.startsWith(l.href);
            return (
              <li key={l.href}>
                <Link
                  href={l.href}
                  className={`text-sm font-medium transition-colors ${
                    active ? "text-sky-600" : "text-slate-600 hover:text-sky-600"
                  }`}
                  aria-current={active ? "page" : undefined}
                >
                  {l.label}
                </Link>
              </li>
            );
          })}
          <li>
            <button
              onClick={toggleLang}
              className="rounded border border-slate-300 px-2 py-1 text-xs font-medium text-slate-700 hover:bg-slate-50"
              aria-label={i18n.language === "fr" ? "Switch to English" : "Passer en Francais"}
            >
              {i18n.language === "fr" ? "EN" : "FR"}
            </button>
          </li>
        </ul>
      </div>
    </nav>
  );
}
