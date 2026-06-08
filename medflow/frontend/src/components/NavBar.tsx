"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/dashboard", label: "Tableau de bord" },
  { href: "/patients", label: "Patients" },
  { href: "/agenda", label: "Agenda" },
  { href: "/triage", label: "Triage" },
];

export default function NavBar() {
  const pathname = usePathname();

  return (
    <nav className="border-b border-slate-200 bg-white" aria-label="Navigation principale">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3">
        <Link href="/dashboard" className="text-xl font-bold text-sky-600">
          MedFlow
        </Link>
        <ul className="flex gap-6">
          {links.map((l) => {
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
        </ul>
      </div>
    </nav>
  );
}
