"use client";

import { useEffect, useState } from "react";
import { getAdminUsers, createAdminUser, updateAdminUser, deleteAdminUser } from "@/utils/api";

interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
  specialty: string | null;
}

export default function AdminUsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState({ email: "", full_name: "", password: "", role: "doctor", specialty: "" });
  const [editingId, setEditingId] = useState<string | null>(null);

  const fetchUsers = () => {
    setLoading(true);
    getAdminUsers()
      .then(setUsers)
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleCreate = () => {
    createAdminUser(form).then(() => {
      setForm({ email: "", full_name: "", password: "", role: "doctor", specialty: "" });
      fetchUsers();
    });
  };

  const handleUpdate = () => {
    if (!editingId) return;
    updateAdminUser(editingId, form).then(() => {
      setEditingId(null);
      setForm({ email: "", full_name: "", password: "", role: "doctor", specialty: "" });
      fetchUsers();
    });
  };

  const handleDelete = (id: string) => {
    deleteAdminUser(id).then(fetchUsers);
  };

  return (
    <main className="min-h-screen p-8">
      <div className="mx-auto max-w-7xl">
        <h1 className="text-3xl font-bold text-sky-600">Admin — Utilisateurs</h1>
        <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-5">
          <input value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} placeholder="Email" className="rounded-md border border-slate-300 px-3 py-2 text-sm" />
          <input value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} placeholder="Nom complet" className="rounded-md border border-slate-300 px-3 py-2 text-sm" />
          <input value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} placeholder="Mot de passe" type="password" className="rounded-md border border-slate-300 px-3 py-2 text-sm" />
          <select value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })} className="rounded-md border border-slate-300 px-3 py-2 text-sm">
            <option value="doctor">Médecin</option>
            <option value="ipa">IPA</option>
            <option value="sec">Secrétaire</option>
            <option value="admin">Admin</option>
          </select>
          <input value={form.specialty} onChange={(e) => setForm({ ...form, specialty: e.target.value })} placeholder="Spécialité" className="rounded-md border border-slate-300 px-3 py-2 text-sm" />
        </div>
        {editingId ? (
          <button onClick={handleUpdate} className="mt-4 rounded-md bg-amber-600 px-4 py-2 text-sm font-medium text-white hover:bg-amber-700">Modifier</button>
        ) : (
          <button onClick={handleCreate} className="mt-4 rounded-md bg-sky-600 px-4 py-2 text-sm font-medium text-white hover:bg-sky-700">Créer</button>
        )}
        <div className="mt-6 overflow-hidden rounded-md border border-slate-200">
          <table className="min-w-full divide-y divide-slate-200">
            <thead className="bg-slate-50"><tr>
              <th className="px-4 py-3 text-left text-sm font-medium text-slate-700">Nom</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-slate-700">Email</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-slate-700">Rôle</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-slate-700">Spécialité</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-slate-700">Actions</th>
            </tr></thead>
            <tbody className="divide-y divide-slate-200 bg-white">
              {loading ? (
                <tr><td colSpan={5} className="px-4 py-8 text-center text-slate-500">Chargement...</td></tr>
              ) : users.length === 0 ? (
                <tr><td colSpan={5} className="px-4 py-8 text-center text-slate-500">Aucun utilisateur.</td></tr>
              ) : users.map((u) => (
                <tr key={u.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 text-sm text-slate-900">{u.full_name}</td>
                  <td className="px-4 py-3 text-sm text-slate-700">{u.email}</td>
                  <td className="px-4 py-3 text-sm text-slate-700">{u.role}</td>
                  <td className="px-4 py-3 text-sm text-slate-700">{u.specialty || "—"}</td>
                  <td className="px-4 py-3 text-sm">
                    <button onClick={() => { setEditingId(u.id); setForm({ ...form, email: u.email, full_name: u.full_name, role: u.role, specialty: u.specialty || "" }); }} className="mr-2 rounded bg-amber-600 px-2 py-1 text-xs text-white hover:bg-amber-700">Modifier</button>
                    <button onClick={() => handleDelete(u.id)} className="rounded bg-red-600 px-2 py-1 text-xs text-white hover:bg-red-700">Supprimer</button>
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
