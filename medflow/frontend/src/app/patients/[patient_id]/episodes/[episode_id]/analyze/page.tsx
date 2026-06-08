"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { analyzeEpisode, getEpisode, getPatient } from "@/utils/api";

interface AnalysisResult {
  episode_id: string;
  clinical_complete_percent: number;
  can_process: boolean;
  missing_fields: string[];
  violations: RuleViolation[];
  recommendations: string[];
  ai_analysis: string | null;
  confidence: ConfidenceScore | null;
  next_steps: string[];
}

interface RuleViolation {
  field: string;
  severity: string;
  message: string;
  recommendation: string | null;
}

interface ConfidenceScore {
  score: number;
  level: string;
  risk_category: string | null;
  triage_notes: string[];
  flags: string[];
}

const SEVERITY_COLORS: Record<string, string> = {
  error: "bg-red-50 text-red-700 border-red-200",
  warning: "bg-amber-50 text-amber-800 border-amber-200",
  info: "bg-blue-50 text-blue-700 border-blue-200",
};

const CONFIDENCE_COLORS: Record<string, string> = {
  high: "bg-green-100 text-green-700",
  medium: "bg-yellow-100 text-yellow-700",
  low: "bg-red-100 text-red-700",
};

export default function AnalyzePage() {
  const params = useParams();
  const router = useRouter();
  const patientId = params.patient_id as string;
  const episodeId = params.episode_id as string;

  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [patientName, setPatientName] = useState<string>("");

  useEffect(() => {
    getPatient(patientId)
      .then((p) => setPatientName(`${p.last_name} ${p.first_name}`))
      .catch(() => setPatientName("Patient inconnu"))
      .finally(() => setFetching(false));
  }, [patientId]);

  const handleAnalyze = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await analyzeEpisode(episodeId);
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur lors de l'analyse");
    } finally {
      setLoading(false);
    }
  };

  if (fetching) {
    return (
      <main className="min-h-screen p-8">
        <p className="text-slate-500">Chargement...</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen p-8">
      <div className="mx-auto max-w-5xl space-y-6">
        <div className="flex items-center gap-4">
          <button
            onClick={() => router.back()}
            className="text-slate-500 hover:text-slate-700"
            aria-label="Retour"
          >
            ←
          </button>
          <div>
            <h1 className="text-2xl font-bold text-sky-600">Analyse IA</h1>
            <p className="text-sm text-slate-500">Patient : {patientName}</p>
          </div>
        </div>

        {!result && !loading && (
          <div className="rounded-md border border-slate-200 bg-white p-8 text-center">
            <h2 className="mb-2 text-lg font-semibold text-slate-800">Lancer l&apos;analyse</h2>
            <p className="mb-6 text-slate-600">
              Le pipeline IA évalue la complétude clinique, les règles de sécurité et génère des recommandations.
            </p>
            <button
              onClick={handleAnalyze}
              className="rounded-md bg-sky-600 px-6 py-2 text-sm font-medium text-white hover:bg-sky-700 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:ring-offset-2"
              aria-label="Lancer l'analyse IA"
            >
              Analyser l&apos;épisode
            </button>
            {error && <p className="mt-4 text-sm text-red-600" role="alert">{error}</p>}
          </div>
        )}

        {loading && (
          <div className="rounded-md border border-slate-200 bg-white p-8 text-center" aria-live="polite">
            <p className="text-slate-600">Analyse en cours...</p>
            <div className="mx-auto mt-4 h-8 w-8 animate-spin rounded-full border-2 border-slate-300 border-t-sky-600" role="status" />
          </div>
        )}

        {result && (
          <div className="space-y-6" aria-live="polite">
            {/* Completude */}
            <div className="rounded-md border border-slate-200 bg-white p-6">
              <h2 className="mb-4 text-lg font-semibold text-slate-800">Complétude clinique</h2>
              <div className="flex items-center gap-4">
                <div
                  className={`rounded-full px-4 py-2 text-sm font-bold ${
                    result.clinical_complete_percent >= 70
                      ? "bg-green-100 text-green-700"
                      : result.clinical_complete_percent >= 40
                      ? "bg-yellow-100 text-yellow-700"
                      : "bg-red-100 text-red-700"
                  }`}
                >
                  {result.clinical_complete_percent}%
                </div>
                <p className="text-sm text-slate-600">
                  {result.can_process
                    ? "Données suffisantes pour le traitement IA."
                    : "Données incomplètes — le traitement IA est bloqué."}
                </p>
              </div>
              {result.missing_fields.length > 0 && (
                <ul className="mt-4 list-inside list-disc text-sm text-slate-600">
                  {result.missing_fields.map((field) => (
                    <li key={field}>{field}</li>
                  ))}
                </ul>
              )}
            </div>

            {/* Violations & Recommendations */}
            <div className="rounded-md border border-slate-200 bg-white p-6">
              <h2 className="mb-4 text-lg font-semibold text-slate-800">Règles de sécurité</h2>
              {result.violations.length === 0 ? (
                <p className="text-sm text-green-700">Aucune violation détectée.</p>
              ) : (
                <div className="space-y-3">
                  {result.violations.map((v, idx) => (
                    <div
                      key={idx}
                      className={`rounded-md border p-3 text-sm ${SEVERITY_COLORS[v.severity] || "bg-slate-50 text-slate-700 border-slate-200"}`}
                      role="alert"
                    >
                      <p className="font-semibold">{v.message}</p>
                      {v.recommendation && <p className="mt-1">Recommandation : {v.recommendation}</p>}
                    </div>
                  ))}
                </div>
              )}
              {result.recommendations.length > 0 && (
                <div className="mt-4">
                  <h3 className="mb-2 text-sm font-semibold text-slate-700">Suggestions</h3>
                  <ul className="list-inside list-disc text-sm text-slate-600">
                    {result.recommendations.map((rec, idx) => (
                      <li key={idx}>{rec}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            {/* AI Analysis & Confidence */}
            {result.ai_analysis && (
              <div className="rounded-md border border-slate-200 bg-white p-6">
                <h2 className="mb-4 text-lg font-semibold text-slate-800">Analyse IA</h2>
                <p className="whitespace-pre-wrap text-sm text-slate-700">{result.ai_analysis}</p>
              </div>
            )}

            {result.confidence && (
              <div className="rounded-md border border-slate-200 bg-white p-6">
                <h2 className="mb-4 text-lg font-semibold text-slate-800">Score de confiance</h2>
                <div className="flex flex-wrap items-center gap-4">
                  <span
                    className={`rounded-full px-3 py-1 text-xs font-bold ${
                      CONFIDENCE_COLORS[result.confidence.level] || "bg-slate-100 text-slate-700"
                    }`}
                  >
                    {Math.round(result.confidence.score * 100)}% — {result.confidence.level.toUpperCase()}
                  </span>
                  {result.confidence.risk_category && (
                    <span className="text-sm text-slate-600">
                      Catégorie de risque : <strong>{result.confidence.risk_category}</strong>
                    </span>
                  )}
                </div>
                {result.confidence.flags.length > 0 && (
                  <ul className="mt-3 list-inside list-disc text-sm text-amber-700">
                    {result.confidence.flags.map((flag, idx) => (
                      <li key={idx}>{flag}</li>
                    ))}
                  </ul>
                )}
              </div>
            )}

            {/* Next Steps */}
            {result.next_steps.length > 0 && (
              <div className="rounded-md border border-slate-200 bg-white p-6">
                <h2 className="mb-4 text-lg font-semibold text-slate-800">Prochaines étapes</h2>
                <ol className="list-inside list-decimal text-sm text-slate-700">
                  {result.next_steps.map((step, idx) => (
                    <li key={idx}>{step}</li>
                  ))}
                </ol>
              </div>
            )}

            {/* Actions */}
            <div className="flex flex-wrap gap-4">
              <button
                onClick={handleAnalyze}
                className="rounded-md border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:ring-offset-1"
                aria-label="Relancer l'analyse"
              >
                Relancer l&apos;analyse
              </button>
              {result.can_process && (
                <button
                  className="rounded-md bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-1"
                  aria-label="Valider et signer"
                >
                  Valider pour signature
                </button>
              )}
              <button
                onClick={() => router.push(`/patients/${patientId}`)}
                className="rounded-md bg-slate-800 px-4 py-2 text-sm font-medium text-white hover:bg-slate-900 focus:outline-none focus:ring-2 focus:ring-slate-500 focus:ring-offset-1"
              >
                Retour au patient
              </button>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
