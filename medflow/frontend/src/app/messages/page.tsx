"use client";

import { useEffect, useState } from "react";
import { getInbox, getSent, createMessage } from "@/utils/api";

interface MessageItem {
  id: string;
  sender_id: string;
  recipient_id: string;
  subject: string;
  body: string;
  is_read: boolean;
  created_at: string;
}

export default function MessagesPage() {
  const [inbox, setInbox] = useState<MessageItem[]>([]);
  const [sent, setSent] = useState<MessageItem[]>([]);
  const [tab, setTab] = useState<"inbox" | "sent">("inbox");
  const [form, setForm] = useState({ recipient_id: "", subject: "", body: "" });
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(true);

  const fetchAll = () => {
    setLoading(true);
    Promise.all([getInbox(), getSent()]).then(([inb, snt]) => {
      setInbox(inb || []);
      setSent(snt || []);
      setLoading(false);
    }).catch(() => setLoading(false));
  };

  useEffect(() => {
    fetchAll();
  }, []);

  const handleSend = () => {
    createMessage(form).then(() => {
      setForm({ recipient_id: "", subject: "", body: "" });
      setShowForm(false);
      fetchAll();
    });
  };

  const data = tab === "inbox" ? inbox : sent;

  return (
    <main className="min-h-screen p-8">
      <div className="mx-auto max-w-7xl">
        <h1 className="text-3xl font-bold text-sky-600">Messagerie</h1>
        <div className="mt-6 flex items-center gap-4">
          <div className="flex rounded-md border border-slate-200">
            <button
              onClick={() => setTab("inbox")}
              className={`px-4 py-2 text-sm font-medium ${tab === "inbox" ? "bg-sky-50 text-sky-700" : "text-slate-600 hover:bg-slate-50"}`}
              aria-pressed={tab === "inbox"}
            >
              Reçus ({inbox.length})
            </button>
            <button
              onClick={() => setTab("sent")}
              className={`px-4 py-2 text-sm font-medium ${tab === "sent" ? "bg-sky-50 text-sky-700" : "text-slate-600 hover:bg-slate-50"}`}
              aria-pressed={tab === "sent"}
            >
              Envoyés ({sent.length})
            </button>
          </div>
          <button onClick={() => setShowForm(!showForm)} className="rounded-md bg-sky-600 px-4 py-2 text-sm font-medium text-white hover:bg-sky-700">
            Nouveau message
          </button>
        </div>
        {showForm && (
          <div className="mt-4 rounded-md border border-slate-200 bg-slate-50 p-4">
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              <input value={form.recipient_id} onChange={e => setForm({...form, recipient_id: e.target.value})} placeholder="Recipient ID" className="rounded-md border border-slate-300 px-3 py-2 text-sm" />
              <input value={form.subject} onChange={e => setForm({...form, subject: e.target.value})} placeholder="Sujet" className="rounded-md border border-slate-300 px-3 py-2 text-sm" />
            </div>
            <textarea value={form.body} onChange={e => setForm({...form, body: e.target.value})} placeholder="Message..." rows={3} className="mt-2 w-full rounded-md border border-slate-300 px-3 py-2 text-sm" />
            <button onClick={handleSend} className="mt-2 rounded-md bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700">Envoyer</button>
          </div>
        )}
        <div className="mt-6 overflow-hidden rounded-md border border-slate-200">
          <table className="min-w-full divide-y divide-slate-200">
            <thead className="bg-slate-50"><tr>
              <th className="px-4 py-3 text-left text-sm font-medium text-slate-700">Sujet</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-slate-700">{tab === "inbox" ? "Expéditeur" : "Destinataire"}</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-slate-700">Date</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-slate-700">Lu</th>
            </tr></thead>
            <tbody className="divide-y divide-slate-200 bg-white">
              {loading ? (
                <tr><td colSpan={4} className="px-4 py-8 text-center text-slate-500">Chargement...</td></tr>
              ) : data.length === 0 ? (
                <tr><td colSpan={4} className="px-4 py-8 text-center text-slate-500">Aucun message.</td></tr>
              ) : data.map((m) => (
                <tr key={m.id} className={`hover:bg-slate-50 ${!m.is_read && tab === "inbox" ? "bg-sky-50" : ""}`}>
                  <td className="px-4 py-3 text-sm text-slate-900">{m.subject}</td>
                  <td className="px-4 py-3 text-sm text-slate-700">{tab === "inbox" ? m.sender_id.slice(0,8) : m.recipient_id?.slice(0,8)}</td>
                  <td className="px-4 py-3 text-sm text-slate-500">{m.created_at}</td>
                  <td className="px-4 py-3 text-sm">{m.is_read ? "Oui" : "Non"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </main>
  );
}
