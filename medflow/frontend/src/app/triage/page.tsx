"use client";

import { useEffect, useState, useCallback } from "react";
import { getTriageEntries, getTriageStats } from "@/utils/api";

interface TriageEntry {
  id: string;
  priority: string;
  score: number;
  status: string;
  chief_complaint: string | null;
  heart_rate: number | null;
  blood_pressure_systolic: number | null;
  temperature: number | null;
  oxygen_saturation: number | null;
  pain_scale: number | null;
  assigned_to: string | null;
  created_at: string;
}

interface TriageStats {
  counts: Record<string, number>;
}

interface Alert {
  priority: string;
  score: number;
  chief_complaint: string | null;
  id: string;
}

function useTriageWebSocket(token: string | null, onAlert: (alert: Alert) => void) {
  useEffect(() => {
    if (!token) return;
    const wsUrl = `${(process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000")
      .replace(/^http/, "ws")}/ws/triage?token=${token}`;
    const ws = new WebSocket(wsUrl);
    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.type === "triage_alert") onAlert(msg);
      } catch {
        // ignore
      }
    };
    const ping = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) ws.send("ping");
    }, 30000);
    return () => {
      clearInterval(ping);
      ws.close();
    };
  }, [token, onAlert]);
}

const priorityBadge = (p: string) => {
  const map: Record<string, string> = {
    P1: "bg-red-600 text-white",
    P2: "bg-orange-500 text-white",
    P3: "bg-yellow-400 text-slate-900",
    P4: "bg-green-500 text-white",
    P5: "bg-slate-200 text-slate-700",
  };
  return map[p] || map.P5;
};

export default function TriagePage() {
  const [entries, setEntries] = useState<TriageEntry[]>([]);
  const [stats, setStats] = useState<TriageStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [playedIds, setPlayedIds] = useState<Set<string>>(new Set());

  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;

  const fetchAll = useCallback(() => {
    setLoading(true);
    Promise.all([getTriageEntries(), getTriageStats()])
      .then(([e, s]) => {
        setEntries(e);
        setStats(s);
      })
      .catch((err) => setError(err instanceof Error ? err.message : "Erreur"))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    fetchAll();
    const interval = setInterval(fetchAll, 10000);
    return () => clearInterval(interval);
  }, [fetchAll]);

  const onAlert = useCallback(
    (alert: Alert) => {
      if (playedIds.has(alert.id)) return;
      setPlayedIds((prev) => new Set(prev).add(alert.id));

      // Visual toast
      const toast = document.createElement("div");
      toast.setAttribute("role", "alert");
      toast.className = `fixed bottom-6 right-6 z-50 rounded-lg px-6 py-4 shadow-lg text-white animate-bounce ${
        alert.priority === "P1" ? "bg-red-600" : "bg-orange-500"
      }`;
      toast.innerHTML = `<strong>${alert.priority} — Urgence</strong><br/>${alert.chief_complaint || "Alerte triage"}`;
      document.body.appendChild(toast);
      setTimeout(() => toast.remove(), 5000);

      // Audio notification (beep) — use Web Audio API to avoid file dependency
      try {
        const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
        if (AudioCtx) {
          const ctx = new AudioCtx();
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.connect(gain);
          gain.connect(ctx.destination);
          osc.frequency.value = alert.priority === "P1" ? 880 : 660;
          gain.gain.value = 0.1;
          osc.start();
          osc.stop(ctx.currentTime + 0.2);
        }
      } catch {
        // ignore audio errors
      }

      fetchAll();
    },
    [playedIds, fetchAll]
  );

  useTriageWebSocket(token, onAlert);

  return (
    <main className="min-h-screen p-8">
      <div className="mx-auto max-w-7xl">
        <h1 className="text-3xl font-bold text-sky-600">Triage</h1>

        {error && (
          <div className="mt-4 rounded-md bg-red-50 p-4 text-red-700" role="alert">
            {error}
          </div>
        )}

        {stats && (
          <div className="mt-6 grid grid-cols-2 gap-4 sm:grid-cols-5">
            {["P1", "P2", "P3", "P4", "P5"].map((p) => (
              <div
                key={p}
                className={`flex flex-col items-center rounded-lg p-4 ${priorityBadge(p).replace(/text-(white|slate-900|slate-700)/g, "")} bg-opacity-20`}
              >
                <span className={`inline-flex h-10 w-10 items-center justify-center rounded-full text-sm font-bold ${priorityBadge(p)}`}>
                  {p}
                </span>
                <span className="mt-2 text-2xl font-bold text-slate-800">
                  {stats.counts[p] || 0}
                </span>
              </div>
            ))}
          </div>
        )}

        <div className="mt-8 overflow-hidden rounded-md border border-slate-200">
          <table className="min-w-full divide-y divide-slate-200">
            <thead className="bg-slate-50">
              <tr>
                <th scope="col" className="px-4 py-3 text-left text-sm font-medium text-slate-700">Priorité</th>
                <th scope="col" className="px-4 py-3 text-left text-sm font-medium text-slate-700">Score</th>
                <th scope="col" className="px-4 py-3 text-left text-sm font-medium text-slate-700">Motif</th>
                <th scope="col" className="px-4 py-3 text-left text-sm font-medium text-slate-700">FC</th>
                <th scope="col" className="px-4 py-3 text-left text-sm font-medium text-slate-700">PAS</th>
                <th scope="col" className="px-4 py-3 text-left text-sm font-medium text-slate-700">Temp.</th>
                <th scope="col" className="px-4 py-3 text-left text-sm font-medium text-slate-700">SpO2</th>
                <th scope="col" className="px-4 py-3 text-left text-sm font-medium text-slate-700">Douleur</th>
                <th scope="col" className="px-4 py-3 text-left text-sm font-medium text-slate-700">Statut</th>
                <th scope="col" className="px-4 py-3 text-left text-sm font-medium text-slate-700">Arrivée</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 bg-white">
              {loading ? (
                <tr>
                  <td colSpan={10} className="px-4 py-8 text-center text-slate-500">
                    Chargement...
                  </td>
                </tr>
              ) : entries.length === 0 ? (
                <tr>
                  <td colSpan={10} className="px-4 py-8 text-center text-slate-500">
                    Aucune entrée de triage.
                  </td>
                </tr>
              ) : (
                entries.map((entry) => (
                  <tr key={entry.id} className="hover:bg-slate-50">
                    <td className="px-4 py-3">
                      <span className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${priorityBadge(entry.priority)}`}>
                        {entry.priority}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-slate-900 font-mono">{entry.score}</td>
                    <td className="px-4 py-3 text-sm text-slate-700 max-w-xs truncate" title={entry.chief_complaint || undefined}>
                      {entry.chief_complaint || "—"}
                    </td>
                    <td className="px-4 py-3 text-sm text-slate-700">{entry.heart_rate ?? "—"}</td>
                    <td className="px-4 py-3 text-sm text-slate-700">{entry.blood_pressure_systolic ?? "—"}</td>
                    <td className="px-4 py-3 text-sm text-slate-700">{entry.temperature ? `${entry.temperature}°C` : "—"}</td>
                    <td className="px-4 py-3 text-sm text-slate-700">{entry.oxygen_saturation ? `${entry.oxygen_saturation}%` : "—"}</td>
                    <td className="px-4 py-3 text-sm text-slate-700">{entry.pain_scale ?? "—"}/10</td>
                    <td className="px-4 py-3 text-sm text-slate-700 capitalize">{entry.status}</td>
                    <td className="px-4 py-3 text-sm text-slate-500">
                      {new Date(entry.created_at).toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" })}
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
