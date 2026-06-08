"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getPatients } from "@/utils/api";

interface Patient {
  id: string;
  last_name: string;
  first_name: string;
  date_of_birth: string | null;
  gender: string | null;
  phone: string | null;
  email: string | null;
  created_at: string;
}

export default function PatientsPage() {
  const router = useRouter();
  const [patients, setPatients] = useState<Patient[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getPatients()
      .then(setPatients)
      .catch((err) => setError(err instanceof Error ? err.message : "Erreur de chargement"))
      .finally(() => setLoading(false));
  }, []);

  return (
    <main className="min-h-screen p-8">
      <div className="mx-auto max-w-5xl">
        <div className="mb-6 flex items-center justify-between">
          <h1 className="text-3xl font-bold text-sky-600">Patients</h1>
          <button
            onClick={() => router.push("/intake")}
            className="rounded-md bg-sky-600 px-4 py-2 text-white hover:bg-sky-700"
          >
            + Nouveau patient
          </button>
        </div>

        {error && (
          <div className="mb-4 rounded-md bg-red-50 p-4 text-red-700" role="alert">
            {error}
          </div>
        )}

        {loading ? (
          <p className="text-slate-500">Chargement...</p>
        ) : patients.length === 0 ? (
          <div className="rounded-md border border-slate-200 p-8 text-center text-slate-500">
            Aucun patient. <button onClick={() => router.push("/intake")} className="text-sky-600 hover:underline">Créer le premier</button>
          </div>
        ) : (
          <div className="overflow-hidden rounded-md border border-slate-200">
            <table className="min-w-full divide-y divide-slate-200">
              <thead className="bg-slate-50">
                <tr>
                  <th scope="col" className="px-4 py-3 text-left text-sm font-medium text-slate-700">Nom</th>
                  <th scope="col" className="px-4 py-3 text-left text-sm font-medium text-slate-700">Prénom</th>
                  <th scope="col" className="px-4 py-3 text-left text-sm font-medium text-slate-700">Date de naissance</th>
                  <th scope="col" className="px-4 py-3 text-left text-sm font-medium text-slate-700">Téléphone</th>
                  <th scope="col" className="px-4 py-3 text-left text-sm font-medium text-slate-700">Email</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 bg-white">
                {patients.map((patient) => (
                  <tr
                    key={patient.id}
                    className="cursor-pointer hover:bg-slate-50"
                    onClick={() => router.push(`/patients/${patient.id}`)}
                  >
                    <td className="px-4 py-3 text-sm text-slate-900">{patient.last_name}</td>
                    <td className="px-4 py-3 text-sm text-slate-900">{patient.first_name}</td>
                    <td className="px-4 py-3 text-sm text-slate-500">
                      {patient.date_of_birth ? new Date(patient.date_of_birth).toLocaleDateString("fr-FR") : "—"}
                    </td>
                    <td className="px-4 py-3 text-sm text-slate-500">{patient.phone || "—"}</td>
                    <td className="px-4 py-3 text-sm text-slate-500">{patient.email || "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </main>
  );
}