"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";

const COMMANDS = [
  { label: "Dashboard", shortcut: "g d", href: "/dashboard" },
  { label: "Patients", shortcut: "g p", href: "/patients" },
  { label: "Agenda", shortcut: "g a", href: "/agenda" },
  { label: "Triage", shortcut: "g t", href: "/triage" },
  { label: "Facturation", shortcut: "g b", href: "/billing" },
  { label: "Messages", shortcut: "g m", href: "/messages" },
  { label: "Admin Utilisateurs", shortcut: "g u", href: "/admin/users" },
  { label: "Paramètres IA", shortcut: "g s", href: "/settings/ai-prompts" },
  { label: "Nouveau patient", shortcut: "c p", href: "" },
  { label: "Nouveau message", shortcut: "c m", href: "/messages" },
];

export default function CommandPalette() {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const router = useRouter();

  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
      e.preventDefault();
      setOpen((v) => !v);
    }
    if (e.key === "Escape") {
      setOpen(false);
    }
  }, []);

  useEffect(() => {
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [handleKeyDown]);

  const filtered = COMMANDS.filter((c) => c.label.toLowerCase().includes(query.toLowerCase()));

  const handleSelect = (href: string) => {
    setOpen(false);
    if (href) router.push(href);
  };

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center bg-black/50 pt-32"
      role="dialog"
      aria-modal="true"
      aria-label="Command palette"
      onClick={() => setOpen(false)}
    >
      <div
        className="w-full max-w-lg rounded-lg bg-white shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        <input
          autoFocus
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Tapez une commande..."
          className="w-full rounded-t-lg border-b border-slate-200 px-4 py-3 text-sm outline-none"
          aria-label="Recherche commandes"
        />
        <ul className="max-h-72 overflow-auto py-2" role="listbox">
          {filtered.map((cmd, i) => (
            <li key={cmd.label}>
              <button
                onClick={() => handleSelect(cmd.href)}
                className="flex w-full items-center justify-between px-4 py-2 text-left text-sm hover:bg-slate-100 focus:bg-slate-100 focus:outline-none"
                role="option"
                aria-selected={i === 0}
              >
                <span className="text-slate-700">{cmd.label}</span>
                <span className="rounded bg-slate-100 px-1.5 py-0.5 text-xs text-slate-500">{cmd.shortcut}</span>
              </button>
            </li>
          ))}
          {filtered.length === 0 && (
            <li className="px-4 py-3 text-sm text-slate-500">Aucune commande trouvée.</li>
          )}
        </ul>
        <div className="flex items-center justify-between rounded-b-lg border-t border-slate-200 bg-slate-50 px-4 py-2 text-xs text-slate-500">
          <span>Ctrl+K pour ouvrir</span>
          <span>Entrée pour sélectionner</span>
          <span>Échap pour fermer</span>
        </div>
      </div>
    </div>
  );
}
