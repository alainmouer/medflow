"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { createPatient, createEpisode, getEpisodes } from "@/utils/api";

export default function IntakePage() {
  const router = useRouter();
  const [step, setStep] = useState<"patient" | "episode">("patient");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Patient fields
  const [lastName, setLastName] = useState("");
  const [firstName, setFirstName] = useState("");
  const [dateOfBirth, setDateOfBirth] = useState("");
  const [gender, setGender] = useState("");
  const [phone, setPhone] = useState("");
  const [email, setEmail] = useState("");
  const [address, setAddress] = useState("");
  const [emergencyContact, setEmergencyContact] = useState("");
  const [emergencyPhone, setEmergencyPhone] = useState("");
  const [allergies, setAllergies] = useState("");

  // Episode fields
  const [episodeType, setEpisodeType] = useState("");
  const [chiefComplaint, setChiefComplaint] = useState("");
  const [clinicalNotes, setClinicalNotes] = useState("");
  const [intakeMethod, setIntakeMethod] = useState("");

  const [patientId, setPatientId] = useState<string | null>(null);

  const handlePatientSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const patient = await createPatient({
        last_name: lastName,
        first_name: firstName,
        date_of_birth: dateOfBirth || null,
        gender: gender || null,
        phone: phone || null,
        email: email || null,
        address: address || null,
        emergency_contact: emergencyContact || null,
        emergency_phone: emergencyPhone || null,
        allergies: allergies || null,
      });
      setPatientId(patient.id);
      setStep("episode");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur lors de la creation du patient");
    } finally {
      setLoading(false);
    }
  };

  const handleEpisodeSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!patientId) return;
    setLoading(true);
    setError(null);
    try {
      await createEpisode({
        patient_id: patientId,
        episode_type: episodeType || null,
        chief_complaint: chiefComplaint || null,
        clinical_notes: clinicalNotes || null,
        intake_method: intakeMethod || null,
      });
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur lors de la creation de l'episode");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen p-8">
      <div className="mx-auto max-w-2xl">
        <h1 className="text-3xl font-bold text-sky-600">Nouveau Patient — Intake</h1>
        <p className="mt-2 text-slate-600">
          {step === "patient" ? "Step 1/2: Informations du patient" : "Step 2/2: Creation de l'episode"}
        </p>

        {error && (
          <div className="mt-4 rounded-md bg-red-50 p-4 text-red-700" role="alert">
            {error}
          </div>
        )}

        {step === "patient" && (
          <form onSubmit={handlePatientSubmit} className="mt-6 space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="lastName" className="block text-sm font-medium text-slate-700">
                  Nom <span className="text-red-500">*</span>
                </label>
                <input
                  id="lastName"
                  type="text"
                  required
                  value={lastName}
                  onChange={(e) => setLastName(e.target.value)}
                  className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 focus:border-sky-500 focus:outline-none focus:ring-1 focus:ring-sky-500"
                />
              </div>
              <div>
                <label htmlFor="firstName" className="block text-sm font-medium text-slate-700">
                  Prenom <span className="text-red-500">*</span>
                </label>
                <input
                  id="firstName"
                  type="text"
                  required
                  value={firstName}
                  onChange={(e) => setFirstName(e.target.value)}
                  className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 focus:border-sky-500 focus:outline-none focus:ring-1 focus:ring-sky-500"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="dateOfBirth" className="block text-sm font-medium text-slate-700">
                  Date de naissance
                </label>
                <input
                  id="dateOfBirth"
                  type="date"
                  value={dateOfBirth}
                  onChange={(e) => setDateOfBirth(e.target.value)}
                  className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 focus:border-sky-500 focus:outline-none focus:ring-1 focus:ring-sky-500"
                />
              </div>
              <div>
                <label htmlFor="gender" className="block text-sm font-medium text-slate-700">
                  Genre
                </label>
                <select
                  id="gender"
                  value={gender}
                  onChange={(e) => setGender(e.target.value)}
                  className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 focus:border-sky-500 focus:outline-none focus:ring-1 focus:ring-sky-500"
                >
                  <option value="">—</option>
                  <option value="M">Masculin</option>
                  <option value="F">Feminin</option>
                  <option value="Autre">Autre</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="phone" className="block text-sm font-medium text-slate-700">
                  Telephone
                </label>
                <input
                  id="phone"
                  type="tel"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 focus:border-sky-500 focus:outline-none focus:ring-1 focus:ring-sky-500"
                />
              </div>
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-slate-700">
                  Email
                </label>
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 focus:border-sky-500 focus:outline-none focus:ring-1 focus:ring-sky-500"
                />
              </div>
            </div>

            <div>
              <label htmlFor="address" className="block text-sm font-medium text-slate-700">
                Adresse
              </label>
              <textarea
                id="address"
                rows={2}
                value={address}
                onChange={(e) => setAddress(e.target.value)}
                className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 focus:border-sky-500 focus:outline-none focus:ring-1 focus:ring-sky-500"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="emergencyContact" className="block text-sm font-medium text-slate-700">
                  Contact d&apos;urgence
                </label>
                <input
                  id="emergencyContact"
                  type="text"
                  value={emergencyContact}
                  onChange={(e) => setEmergencyContact(e.target.value)}
                  className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 focus:border-sky-500 focus:outline-none focus:ring-1 focus:ring-sky-500"
                />
              </div>
              <div>
                <label htmlFor="emergencyPhone" className="block text-sm font-medium text-slate-700">
                  Tel. d&apos;urgence
                </label>
                <input
                  id="emergencyPhone"
                  type="tel"
                  value={emergencyPhone}
                  onChange={(e) => setEmergencyPhone(e.target.value)}
                  className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 focus:border-sky-500 focus:outline-none focus:ring-1 focus:ring-sky-500"
                />
              </div>
            </div>

            <div>
              <label htmlFor="allergies" className="block text-sm font-medium text-slate-700">
                Allergies
              </label>
              <textarea
                id="allergies"
                rows={2}
                value={allergies}
                onChange={(e) => setAllergies(e.target.value)}
                placeholder="Aucune ou liste des allergies connues"
                className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 focus:border-sky-500 focus:outline-none focus:ring-1 focus:ring-sky-500"
              />
            </div>

            <div className="flex justify-end gap-3 pt-4">
              <button
                type="button"
                onClick={() => router.back()}
                className="rounded-md border border-slate-300 px-4 py-2 text-slate-700 hover:bg-slate-50"
              >
                Annuler
              </button>
              <button
                type="submit"
                disabled={loading}
                className="rounded-md bg-sky-600 px-4 py-2 text-white hover:bg-sky-700 disabled:opacity-50"
              >
                {loading ? "Creation..." : "Continuer vers episode"}
              </button>
            </div>
          </form>
        )}

        {step === "episode" && (
          <form onSubmit={handleEpisodeSubmit} className="mt-6 space-y-4">
            <div className="rounded-md bg-sky-50 p-4 text-sm text-sky-700">
              Patient cree : <strong>{lastName} {firstName}</strong>
            </div>

            <div>
              <label htmlFor="episodeType" className="block text-sm font-medium text-slate-700">
                Type d&apos;episode
              </label>
              <select
                id="episodeType"
                value={episodeType}
                onChange={(e) => setEpisodeType(e.target.value)}
                className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 focus:border-sky-500 focus:outline-none focus:ring-1 focus:ring-sky-500"
              >
                <option value="">—</option>
                <option value="in_clinic">En clinique</option>
                <option value="field_visit">Visite a domicile</option>
                <option value="teleconsult">Teleconsultation</option>
              </select>
            </div>

            <div>
              <label htmlFor="intakeMethod" className="block text-sm font-medium text-slate-700">
                Methode d&apos;intake
              </label>
              <select
                id="intakeMethod"
                value={intakeMethod}
                onChange={(e) => setIntakeMethod(e.target.value)}
                className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 focus:border-sky-500 focus:outline-none focus:ring-1 focus:ring-sky-500"
              >
                <option value="">—</option>
                <option value="paper">Formulaire papier</option>
                <option value="digital">Saisie digitale</option>
                <option value="phone">Telephone</option>
              </select>
            </div>

            <div>
              <label htmlFor="chiefComplaint" className="block text-sm font-medium text-slate-700">
                Plainte principale
              </label>
              <textarea
                id="chiefComplaint"
                rows={3}
                value={chiefComplaint}
                onChange={(e) => setChiefComplaint(e.target.value)}
                placeholder="Motif de la visite / symptomes principaux"
                className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 focus:border-sky-500 focus:outline-none focus:ring-1 focus:ring-sky-500"
              />
            </div>

            <div>
              <label htmlFor="clinicalNotes" className="block text-sm font-medium text-slate-700">
                Notes cliniques
              </label>
              <textarea
                id="clinicalNotes"
                rows={4}
                value={clinicalNotes}
                onChange={(e) => setClinicalNotes(e.target.value)}
                placeholder="Observations, historique medical, notes libres..."
                className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 focus:border-sky-500 focus:outline-none focus:ring-1 focus:ring-sky-500"
              />
            </div>

            <div className="flex justify-end gap-3 pt-4">
              <button
                type="button"
                onClick={() => setStep("patient")}
                className="rounded-md border border-slate-300 px-4 py-2 text-slate-700 hover:bg-slate-50"
              >
                Retour
              </button>
              <button
                type="submit"
                disabled={loading}
                className="rounded-md bg-sky-600 px-4 py-2 text-white hover:bg-sky-700 disabled:opacity-50"
              >
                {loading ? "Creation..." : "Creer episode"}
              </button>
            </div>
          </form>
        )}
      </div>
    </main>
  );
}