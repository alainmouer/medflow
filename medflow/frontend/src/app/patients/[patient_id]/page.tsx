"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { getPatient } from "@/utils/api";
import { getEpisodes, updateEpisode } from "@/utils/api";

interface Patient {
  id: string;
  last_name: string;
  first_name: string;
  date_of_birth: string | null;
  gender: string | null;
  phone: string | null;
  email: string | null;
  address: string | null;
  emergency_contact: string | null;
  emergency_phone: string | null;
  allergies: string | null;
}

interface Episode {
  id: string;
  status: string;
  episode_type: string | null;
  chief_complaint: string | null;
  clinical_notes: string | null;
  intake_method: string | null;
  created_at: string;
}

const STATUS_LABELS: Record<string, { label: string; color: string }> = {
  pending: { label: "En attente", color: "bg-slate-100 text-slate-700" },
  consented: { label: "Consenté", color: "bg-blue-100 text-blue-700" },
  collecting: { label: "Collecte en cours", color: "bg-yellow-100 text-yellow-700" },
  collected: { label: "Collecté", color: "bg-indigo-100 text-indigo-700" },
  processing: { label: "En traitement IA", color: "bg-purple-100 text-purple-700" },
  signed: { label: "Signé", color: "bg-green-100 text-green-700" },
};

export default function PatientDetailPage() {
  const params = useParams();
  const router = useRouter();
  const patientId = params.patient_id as string;

  const [patient, setPatient] = useState<Patient | null>(null);
  const [episodes, setEpisodes] = useState<Episode[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [updating, setUpdating] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([getPatient(patientId), getEpisodes(patientId)])
      .then(([p, eps]) => {
        setPatient(p);
        setEpisodes(eps);
      })
      .catch((err) => setError(err instanceof Error ? err.message : "Erreur"))
      .finally(() => setLoading(false));
  }, [patientId]);

  const handleStatusChange = async (episodeId: string, newStatus: string) => {
    setUpdating(episodeId);
    try {
      const updated = await updateEpisode(episodeId, { status: newStatus });
      setEpisodes((prev) => prev.map((e) => (e.id === episodeId ? { ...e, status: updated.status } : e)));
    } catch (err) {
      alert(err instanceof Error ? err.message : "Erreur de mise à jour");
    } finally {
      setUpdating(null);
    }
  };

  if (loading) return <main className="min-h-screen p-8"><p className="text-slate-500">Chargement...</p></main>;
  if (error) return <main className="min-h-screen p-8"><p className="text-red-600">{error}</p></main>;
  if (!patient) return null;

  return (
    <main className="min-h-screen p-8">
      <div className="mx-auto max-w-4xl space-y-6">
        <div className="flex items-center gap-4">
          <button onClick={() => router.back()} className="text-slate-500 hover:text-slate-700" aria-label="Retour">←</button>
          <h1 className="text-3xl font-bold text-sky-600">{patient.last_name} {patient.first_name}</h1>
        </div>

        <div className="rounded-md border border-slate-200 bg-white p-6">
          <h2 className="mb-4 text-lg font-semibold text-slate-800">Informations patient</h2>
          <dl className="grid grid-cols-2 gap-x-6 gap-y-3 text-sm">
            <div><dt className="text-slate-500">Date de naissance</dt><dd className="font-medium text-slate-900">{patient.date_of_birth ? new Date(patient.date_of_birth).toLocaleDateString("fr-FR") : "—"}</dd></div>
            <div><dt className="text-slate-500">Genre</dt><dd className="font-medium text-slate-900">{patient.gender || "—"}</dd></div>
            <div><dt className="text-slate-500">Téléphone</dt><dd className="font-medium text-slate-900">{patient.phone || "—"}</dd></div>
            <div><dt className="text-slate-500">Email</dt><dd className="font-medium text-slate-900">{patient.email || "—"}</dd></div>
            <div className="col-span-2"><dt className="text-slate-500">Adresse</dt><dd className="font-medium text-slate-900">{patient.address || "—"}</dd></div>
            <div><dt className="text-slate-500">Contact d&apos;urgence</dt><dd className="font-medium text-slate-900">{patient.emergency_contact || "—"}</dd></div>
            <div><dt className="text-slate-500">Tel. d&apos;urgence</dt><dd className="font-medium text-slate-900">{patient.emergency_phone || "—"}</dd></div>
            <div className="col-span-2"><dt className="text-slate-500">Allergies</dt><dd className="font-medium text-slate-900">{patient.allergies || "Aucune"}</dd></div>
          </dl>
        </div>

        <div>
          <h2 className="mb-4 text-lg font-semibold text-slate-800">Épisodes cliniques</h2>
          {episodes.length === 0 ? (
            <div className="rounded-md border border-slate-200 p-6 text-center text-slate-500">
              Aucun épisode. <button onClick={() => router.push("/intake")} className="text-sky-600 hover:underline">Créer un intake</button>
            </div>
          ) : (
            <div className="space-y-4">
              {episodes.map((ep) => {
                const status = STATUS_LABELS[ep.status] || { label: ep.status, color: "bg-slate-100 text-slate-700" };
                return (
                  <div key={ep.id} className="rounded-md border border-slate-200 bg-white p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="mb-2 flex flex-wrap items-center gap-2">
                          <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${status.color}`}>{status.label}</span>
                          {ep.episode_type && <span className="text-xs text-slate-500">{ep.episode_type}</span>}
                          <span className="text-xs text-slate-400">{new Date(ep.created_at).toLocaleDateString("fr-FR")}</span>
                        </div>
                        {ep.chief_complaint && <p className="mb-1 text-sm font-medium text-slate-800">{ep.chief_complaint}</p>}
                        {ep.clinical_notes && <p className="text-sm text-slate-600">{ep.clinical_notes}</p>}
                      </div>
                      <div className="ml-4 flex flex-col gap-2">
                        <button
                          onClick={() => router.push(`/patients/${patientId}/episodes/${ep.id}/analyze`)}
                          className="rounded-md bg-sky-600 px-3 py-1 text-xs font-medium text-white hover:bg-sky-700 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:ring-offset-1"
                          aria-label="Analyser avec l'IA"
                        >
                          Analyser
                        </button>
                        <select
                          value={ep.status}
                          disabled={updating === ep.id}
                          onChange={(e) => handleStatusChange(ep.id, e.target.value)}
                          className="rounded-md border border-slate-300 px-2 py-1 text-sm focus:border-sky-500 focus:outline-none focus:ring-1 focus:ring-sky-500"
                          aria-label="Changer le statut"
                        >
                          <option value="pending">En attente</option>
                          <option value="consented">Consenté</option>
                          <option value="collecting">Collecte en cours</option>
                          <option value="collected">Collecté</option>
                          <option value="processing">En traitement IA</option>
                          <option value="signed">Signé</option>
                        </select>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </main>
  );
}