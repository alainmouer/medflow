"use client";

import { useEffect, useState } from "react";
import { getBillings, createBilling, validateBilling, exportBilling } from "@/utils/api";

interface Billing {
  id: string;
  episode_id: string;
  acts_total: number;
  social_security_base: number;
  social_security_paid: number;
  mutuelle_paid: number;
  patient_liability: number;
  status: string;
  validated_by: string | null;
  exported_at: string | null;
}

export default function BillingPage() {
  const [billings, setBillings] = useState<Billing[]>([]);
  const [loading, setLoading] = useState(true);
  const [episodeId, setEpisodeId] = useState("");

  const fetchAll = () => {
    setLoading(true);
    getBillings()
      .then(setBillings)
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchAll();
  }, []);

  const handleCreate = () => {
    if (!episodeId) return;
    createBilling({ episode_id: episodeId, acts_total: 50.0 }).then(() => {
      setEpisodeId("");
      fetchAll();
    });
  };

  return (
    <main className="min-h-screen p-8">
      <div className="mx-auto max-w-7xl">
        <h1 className="text-3xl font-bold text-sky-600">Facturation</h1>
        <div className="mt-6 flex gap-2">
          <input
            value={episodeId}
            onChange={(e) => setEpisodeId(e.target.value)}
            placeholder="Episode ID"
            className="rounded-md border border-slate-300 px-3 py-2 text-sm"
          />
          <button onClick={handleCreate} className="rounded-md bg-sky-600 px-4 py-2 text-sm font-medium text-white hover:bg-sky-700">
            Nouvelle facture
          </button>
        </div>
        <div className="mt-6 overflow-hidden rounded-md border border-slate-200">
          <table className="min-w-full divide-y divide-slate-200">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-medium text-slate-700">Episode</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-slate-700">Total</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-slate-700">SS Base</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-slate-700">SS Payé</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-slate-700">Mutuelle</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-slate-700">Reste patient</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-slate-700">Statut</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-slate-700">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 bg-white">
              {loading ? (
                <tr>
                  <td colSpan={8} className="px-4 py-8 text-center text-slate-500">
                    Chargement...
                  </td>
                </tr>
              ) : billings.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-4 py-8 text-center text-slate-500">
                    Aucune facture.
                  </td>
                </tr>
              ) : (
                billings.map((b) => (
                  <tr key={b.id} className="hover:bg-slate-50">
                    <td className="px-4 py-3 text-sm text-slate-900">{b.episode_id.slice(0, 8)}</td>
                    <td className="px-4 py-3 text-sm text-slate-700">{b.acts_total} €</td>
                    <td className="px-4 py-3 text-sm text-slate-700">{b.social_security_base} €</td>
                    <td className="px-4 py-3 text-sm text-slate-700">{b.social_security_paid} €</td>
                    <td className="px-4 py-3 text-sm text-slate-700">{b.mutuelle_paid} €</td>
                    <td className="px-4 py-3 text-sm text-slate-700">{b.patient_liability} €</td>
                    <td className="px-4 py-3">
                      <span
                        className={`inline-flex rounded-full px-2 py-1 text-xs font-semibold ${
                          b.status === "draft"
                            ? "bg-slate-100 text-slate-600"
                            : b.status === "validated"
                            ? "bg-green-100 text-green-700"
                            : "bg-blue-100 text-blue-700"
                        }`}
                      >
                        {b.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm">
                      {b.status === "draft" && (
                        <button
                          onClick={() => validateBilling(b.id).then(fetchAll)}
                          className="rounded bg-green-600 px-2 py-1 text-xs text-white hover:bg-green-700"
                        >
                          Valider
                        </button>
                      )}
                      {b.status === "validated" && (
                        <button
                          onClick={() => exportBilling(b.id).then(fetchAll)}
                          className="rounded bg-blue-600 px-2 py-1 text-xs text-white hover:bg-blue-700"
                        >
                          Exporter
                        </button>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </main>
  );
}
