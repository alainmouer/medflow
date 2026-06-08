"use client";

import React from "react";
import { useRouter } from "next/navigation";
import { login } from "@/utils/api";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [error, setError] = React.useState("");
  const [loading, setLoading] = React.useState(false);

  const handleLogin = async (e?: React.FormEvent, customEmail?: string, customPassword?: string) => {
    if (e) e.preventDefault();
    setError("");
    setLoading(true);

    const loginEmail = customEmail || email;
    const loginPassword = customPassword || password;

    try {
      const data = await login(loginEmail, loginPassword);
      localStorage.setItem("token", data.access_token);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message || "Erreur de connexion");
    } finally {
      setLoading(false);
    }
  };

  const quickLogin = (roleEmail: string) => {
    setEmail(roleEmail);
    setPassword("medflow2026");
    handleLogin(undefined, roleEmail, "medflow2026");
  };

  return (
    <main className="flex min-h-screen items-center justify-center bg-[#f0f7ff] p-4">
      <div className="w-full max-w-[500px] rounded-[24px] bg-white p-12 shadow-[0_10px_40px_rgba(0,0,0,0.04)]">
        <div className="mb-10 text-center">
          <h1 className="mb-2 text-[44px] font-extrabold tracking-tight text-[#00a3ff]">
            MedFlow
          </h1>
          <p className="text-[17px] text-[#64748b]">
            Plateforme médicale SaaS de nouvelle génération
          </p>
        </div>

        <form onSubmit={handleLogin} className="space-y-6">
          <div className="space-y-2">
            <label className="text-[13px] font-bold uppercase tracking-wider text-[#64748b]">
              ADRESSE EMAIL
            </label>
            <div className="relative">
              <input
                type="email"
                placeholder="ex: doctor@medflow.fr"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="block h-[54px] w-full rounded-[12px] border border-[#e2e8f0] bg-[#f8fafc] px-4 text-[16px] transition-all focus:border-[#00a3ff] focus:outline-none focus:ring-4 focus:ring-[#00a3ff]/10"
                required
              />
              <div className="absolute right-4 top-1/2 -translate-y-1/2 text-[#94a3b8]">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M16 12l2 2 4-4" />
                  <circle cx="12" cy="12" r="10" />
                </svg>
              </div>
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-[13px] font-bold uppercase tracking-wider text-[#64748b]">
              MOT DE PASSE
            </label>
            <div className="relative">
              <input
                type="password"
                placeholder="••••••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="block h-[54px] w-full rounded-[12px] border border-[#e2e8f0] bg-[#f8fafc] px-4 text-[16px] transition-all focus:border-[#00a3ff] focus:outline-none focus:ring-4 focus:ring-[#00a3ff]/10"
                required
              />
              <div className="absolute right-4 top-1/2 -translate-y-1/2 text-[#94a3b8]">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
                  <path d="M7 11V7a5 5 0 0110 0v4" />
                </svg>
              </div>
            </div>
          </div>

          {error && (
            <div className="rounded-[8px] bg-red-50 p-3 text-center text-[14px] text-red-600">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="flex h-[54px] w-full items-center justify-center rounded-[12px] bg-[#00a3ff] text-[18px] font-bold text-white transition-all hover:bg-[#0091e6] active:scale-[0.98] disabled:opacity-50"
          >
            {loading ? "Chargement..." : "Se connecter"}
          </button>
        </form>

        {process.env.NODE_ENV === "development" && (
          <div className="mt-12">
            <div className="mb-6 flex items-center gap-4">
              <div className="h-[1px] flex-1 bg-[#e2e8f0]"></div>
              <span className="text-[12px] font-bold uppercase tracking-widest text-[#94a3b8]">
                CONNEXION RAPIDE (DÉVELOPPEMENT)
              </span>
              <div className="h-[1px] flex-1 bg-[#e2e8f0]"></div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={() => quickLogin("doctor@medflow.fr")}
                className="flex items-center justify-center gap-2 rounded-[12px] border border-[#00a3ff]/30 h-[48px] text-[15px] font-medium text-[#0066cc] transition-all hover:bg-[#00a3ff]/5"
              >
                <span>🩺</span> Médecin
              </button>
              <button
                onClick={() => quickLogin("ipa@medflow.fr")}
                className="flex items-center justify-center gap-2 rounded-[12px] border border-[#00a3ff]/30 h-[48px] text-[15px] font-medium text-[#0066cc] transition-all hover:bg-[#00a3ff]/5"
              >
                <span>🚑</span> IPA
              </button>
              <button
                onClick={() => quickLogin("sec@medflow.fr")}
                className="flex items-center justify-center gap-2 rounded-[12px] border border-[#00a3ff]/30 h-[48px] text-[15px] font-medium text-[#0066cc] transition-all hover:bg-[#00a3ff]/5"
              >
                <span>✍️</span> Secrétaire
              </button>
              <button
                onClick={() => quickLogin("admin@medflow.fr")}
                className="flex items-center justify-center gap-2 rounded-[12px] border border-[#00a3ff]/30 h-[48px] text-[15px] font-medium text-[#0066cc] transition-all hover:bg-[#00a3ff]/5"
              >
                <span>⚙️</span> Admin
              </button>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
