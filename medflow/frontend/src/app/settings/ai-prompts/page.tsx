"use client";

import { useEffect, useState } from "react";
import { getAIPrompts, createAIPrompt, updateAIPrompt, deleteAIPrompt } from "@/utils/api";

interface Prompt {
  id: string;
  name: string;
  specialty: string | null;
  version: string;
  prompt_text: string | null;
  is_active: boolean;
}

export default function AIPromptsPage() {
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState({ name: "", specialty: "", version: "1.0.0", prompt_text: "", is_active: true });
  const [editingId, setEditingId] = useState<string | null>(null);

  const fetchAll = () => {
    setLoading(true);
    getAIPrompts()
      .then(setPrompts)
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchAll();
  }, []);

  const handleCreate = () => {
    createAIPrompt(form).then(() => {
      setForm({ name: "", specialty: "", version: "1.0.0", prompt_text: "", is_active: true });
      fetchAll();
    });
  };

  const handleUpdate = () => {
    if (!editingId) return;
    updateAIPrompt(editingId, form).then(() => {
      setEditingId(null);
      setForm({ name: "", specialty: "", version: "1.0.0", prompt_text: "", is_active: true });
      fetchAll();
    });
  };

  const handleDelete = (id: string) => {
    deleteAIPrompt(id).then(fetchAll);
  };

  return (
    <main className="min-h-screen p-8">
      <div className="mx-auto max-w-7xl">
        <h1 className="text-3xl font-bold text-sky-600">Paramètres IA — Prompts</h1>
        <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-4">
          <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Nom du prompt" className="rounded-md border border-slate-300 px-3 py-2 text-sm" />
          <input value={form.specialty} onChange={(e) => setForm({ ...form, specialty: e.target.value })} placeholder="Spécialité" className="rounded-md border border-slate-300 px-3 py-2 text-sm" />
          <input value={form.version} onChange={(e) => setForm({ ...form, version: e.target.value })} placeholder="Version" className="rounded-md border border-slate-300 px-3 py-2 text-sm" />
          <label className="flex items-center gap-2 text-sm text-slate-700">
            <input type="checkbox" checked={form.is_active} onChange={(e) => setForm({ ...form, is_active: e.target.checked })} /> Actif
          </label>
        </div>
        <textarea value={form.prompt_text} onChange={(e) => setForm({ ...form, prompt_text: e.target.value })} placeholder="Contenu du prompt..." rows={4} className="mt-4 w-full rounded-md border border-slate-300 px-3 py-2 text-sm" />
        {editingId ? (
          <button onClick={handleUpdate} className="mt-4 rounded-md bg-amber-600 px-4 py-2 text-sm font-medium text-white hover:bg-amber-700">Modifier</button>
        ) : (
          <button onClick={handleCreate} className="mt-4 rounded-md bg-sky-600 px-4 py-2 text-sm font-medium text-white hover:bg-sky-700">Créer</button>
        )}
        <div className="mt-6 overflow-hidden rounded-md border border-slate-200">
          <table className="min-w-full divide-y divide-slate-200">
            <thead className="bg-slate-50"><tr>
              <th className="px-4 py-3 text-left text-sm font-medium text-slate-700">Nom</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-slate-700">Spécialité</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-slate-700">Version</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-slate-700">Actif</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-slate-700">Actions</th>
            </tr></thead>
            <tbody className="divide-y divide-slate-200 bg-white">
              {loading ? (
                <tr><td colSpan={5} className="px-4 py-8 text-center text-slate-500">Chargement...</td></tr>
              ) : prompts.length === 0 ? (
                <tr><td colSpan={5} className="px-4 py-8 text-center text-slate-500">Aucun prompt.</td></tr>
              ) : prompts.map((p) => (
                <tr key={p.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 text-sm text-slate-900">{p.name}</td>
                  <td className="px-4 py-3 text-sm text-slate-700">{p.specialty || "—"}</td>
                  <td className="px-4 py-3 text-sm text-slate-700">{p.version}</td>
                  <td className="px-4 py-3 text-sm text-slate-700">{p.is_active ? "Oui" : "Non"}</td>
                  <td className="px-4 py-3 text-sm">
                    <button onClick={() => { setEditingId(p.id); setForm({ name: p.name, specialty: p.specialty || "", version: p.version, prompt_text: p.prompt_text || "", is_active: p.is_active }); }} className="mr-2 rounded bg-amber-600 px-2 py-1 text-xs text-white hover:bg-amber-700">Modifier</button>
                    <button onClick={() => handleDelete(p.id)} className="rounded bg-red-600 px-2 py-1 text-xs text-white hover:bg-red-700">Supprimer</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </main>
  );
}
