"use client";

import { useEffect, useState } from "react";
import { getAppointments, getFieldVisits } from "@/utils/api";

interface Appointment {
  id: string;
  appointment_type: string;
  modality: string;
  status: string;
  scheduled_at: string | null;
  duration_min: number | null;
  location: string | null;
  patient_id: string | null;
  assigned_staff_id: string | null;
  notes: string | null;
}

interface FieldVisit {
  id: string;
  collection_mode: string;
  location_type: string;
  location_address: string | null;
  scheduled_start_at: string | null;
  status: string;
  patient_id: string | null;
  assigned_staff_id: string | null;
  checklist_completion_rate: number;
  notes: string | null;
}

const appointmentTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    consultation: "Consultation",
    exam: "Examen",
    teleconsultation: "Téléconsultation",
    field_visit: "Mission terrain",
  };
  return labels[type] || type;
};

const modalityLabel = (mod: string) => {
  const labels: Record<string, string> = {
    synchronous_presential: "Présentiel",
    synchronous_remote: "Distanciel",
    asynchronous_presential: "Asynchrone présentiel",
    asynchronous_remote: "Télé-expertise",
  };
  return labels[mod] || mod;
};

const statusBadge = (status: string) => {
  const map: Record<string, string> = {
    scheduled: "bg-blue-100 text-blue-700",
    confirmed: "bg-green-100 text-green-700",
    in_progress: "bg-yellow-100 text-yellow-700",
    completed: "bg-slate-100 text-slate-600",
    cancelled: "bg-red-100 text-red-700",
    draft: "bg-slate-100 text-slate-600",
    blocked: "bg-red-100 text-red-700",
  };
  return map[status] || "bg-slate-100 text-slate-600";
};

export default function AgendaPage() {
  const [tab, setTab] = useState<"appointments" | "visits">("appointments");
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [visits, setVisits] = useState<FieldVisit[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAll = () => {
    setLoading(true);
    Promise.all([getAppointments(), getFieldVisits()])
      .then(([a, v]) => {
        setAppointments(a);
        setVisits(v);
      })
      .catch((err) => setError(err instanceof Error ? err.message : "Erreur"))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchAll();
    const interval = setInterval(fetchAll, 10000);
    return () => clearInterval(interval);
  }, []);

  const formatDate = (d: string | null) =>
    d ? new Date(d).toLocaleString("fr-FR", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" }) : "—";

  return (
    <main className="min-h-screen p-8">
      <div className="mx-auto max-w-7xl">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold text-sky-600">Agenda</h1>
        </div>

        {error && (
          <div className="mt-4 rounded-md bg-red-50 p-4 text-red-700" role="alert">
            {error}
          </div>
        )}

        <div className="mt-6 flex gap-2 border-b border-slate-200">
          <button
            onClick={() => setTab("appointments")}
            className={`px-4 py-2 text-sm font-medium transition-colors ${
              tab === "appointments"
                ? "border-b-2 border-sky-600 text-sky-600"
                : "text-slate-600 hover:text-sky-600"
            }`}
            aria-current={tab === "appointments" ? "page" : undefined}
          >
            Rendez-vous
          </button>
          <button
            onClick={() => setTab("visits")}
            className={`px-4 py-2 text-sm font-medium transition-colors ${
              tab === "visits"
                ? "border-b-2 border-sky-600 text-sky-600"
                : "text-slate-600 hover:text-sky-600"
            }`}
            aria-current={tab === "visits" ? "page" : undefined}
          >
            Missions terrain
          </button>
        </div>

        <div className="mt-6 overflow-hidden rounded-md border border-slate-200">
          <table className="min-w-full divide-y divide-slate-200">
            <thead className="bg-slate-50">
              <tr>
                {tab === "appointments" ? (
                  <>
                    <th scope="col" className="px-4 py-3 text-left text-sm font-medium text-slate-700">Type</th>
                    <th scope="col" className="px-4 py-3 text-left text-sm font-medium text-slate-700">Modalité</th>
                    <th scope="col" className="px-4 py-3 text-left text-sm font-medium text-slate-700">Date / Heure</th>
                    <th scope="col" className="px-4 py-3 text-left text-sm font-medium text-slate-700">Durée</th>
                    <th scope="col" className="px-4 py-3 text-left text-sm font-medium text-slate-700">Lieu</th>
                    <th scope="col" className="px-4 py-3 text-left text-sm font-medium text-slate-700">Statut</th>
                    <th scope="col" className="px-4 py-3 text-left text-sm font-medium text-slate-700">Notes</th>
                  </>
                ) : (
                  <>
                    <th scope="col" className="px-4 py-3 text-left text-sm font-medium text-slate-700">Mode</th>
                    <th scope="col" className="px-4 py-3 text-left text-sm font-medium text-slate-700">Lieu</th>
                    <th scope="col" className="px-4 py-3 text-left text-sm font-medium text-slate-700">Adresse</th>
                    <th scope="col" className="px-4 py-3 text-left text-sm font-medium text-slate-700">Date</th>
                    <th scope="col" className="px-4 py-3 text-left text-sm font-medium text-slate-700">Checklist</th>
                    <th scope="col" className="px-4 py-3 text-left text-sm font-medium text-slate-700">Statut</th>
                    <th scope="col" className="px-4 py-3 text-left text-sm font-medium text-slate-700">Notes</th>
                  </>
                )}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 bg-white">
              {loading ? (
                <tr>
                  <td colSpan={7} className="px-4 py-8 text-center text-slate-500">
                    Chargement...
                  </td>
                </tr>
              ) : tab === "appointments" ? (
                appointments.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="px-4 py-8 text-center text-slate-500">
                      Aucun rendez-vous.
                    </td>
                  </tr>
                ) : (
                  appointments.map((a) => (
                    <tr key={a.id} className="hover:bg-slate-50">
                      <td className="px-4 py-3 text-sm text-slate-900">{appointmentTypeLabel(a.appointment_type)}</td>
                      <td className="px-4 py-3 text-sm text-slate-700">{modalityLabel(a.modality)}</td>
                      <td className="px-4 py-3 text-sm text-slate-700">{formatDate(a.scheduled_at)}</td>
                      <td className="px-4 py-3 text-sm text-slate-700">{a.duration_min ? `${a.duration_min} min` : "—"}</td>
                      <td className="px-4 py-3 text-sm text-slate-700">{a.location || "—"}</td>
                      <td className="px-4 py-3">
                        <span className={`inline-flex rounded-full px-2 py-1 text-xs font-semibold ${statusBadge(a.status)}`}>
                          {a.status}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm text-slate-700 max-w-xs truncate" title={a.notes || undefined}>
                        {a.notes || "—"}
                      </td>
                    </tr>
                  ))
                )
              ) : visits.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-4 py-8 text-center text-slate-500">
                    Aucune mission terrain.
                  </td>
                </tr>
              ) : (
                visits.map((v) => (
                  <tr key={v.id} className="hover:bg-slate-50">
                    <td className="px-4 py-3 text-sm text-slate-900">{v.collection_mode}</td>
                    <td className="px-4 py-3 text-sm text-slate-700">{v.location_type}</td>
                    <td className="px-4 py-3 text-sm text-slate-700 max-w-xs truncate" title={v.location_address || undefined}>
                      {v.location_address || "—"}
                    </td>
                    <td className="px-4 py-3 text-sm text-slate-700">{formatDate(v.scheduled_start_at)}</td>
                    <td className="px-4 py-3 text-sm text-slate-700">{v.checklist_completion_rate}%</td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex rounded-full px-2 py-1 text-xs font-semibold ${statusBadge(v.status)}`}>
                        {v.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-slate-700 max-w-xs truncate" title={v.notes || undefined}>
                      {v.notes || "—"}
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
