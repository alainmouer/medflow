const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function apiClient(
  endpoint: string,
  options: RequestInit = {}
) {
  const url = `${API_BASE_URL}${endpoint}`;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(url, { ...options, headers });
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }
  return response.json();
}

// Auth
export const login = (email: string, password: string) => {
  const formData = new URLSearchParams();
  formData.append("username", email);
  formData.append("password", password);
  
  return fetch(`${API_BASE_URL}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: formData.toString(),
  }).then(async (res) => {
    if (!res.ok) {
      const error = await res.json().catch(() => ({}));
      throw new Error(error.detail || `HTTP ${res.status}`);
    }
    return res.json();
  });
};

export const getMe = () => apiClient("/api/auth/me");

// Patients
export const createPatient = (data: Record<string, unknown>) =>
  apiClient("/api/patients", { method: "POST", body: JSON.stringify(data) });

export const getPatients = () => apiClient("/api/patients");

export const getPatient = (id: string) => apiClient(`/api/patients/${id}`);

// Episodes
export const createEpisode = (data: Record<string, unknown>) =>
  apiClient("/api/episodes", { method: "POST", body: JSON.stringify(data) });

export const getEpisodes = (patientId?: string) =>
  apiClient(patientId ? `/api/episodes?patient_id=${patientId}` : "/api/episodes");

export const updateEpisode = (id: string, data: Record<string, unknown>) =>
  apiClient(`/api/episodes/${id}`, { method: "PATCH", body: JSON.stringify(data) });

export const getEpisode = (id: string) =>
  apiClient(`/api/episodes/${id}`);

export const analyzeEpisode = (id: string) =>
  apiClient(`/api/episodes/${id}/analyze`, { method: "POST" });

export const signEpisode = (id: string) =>
  apiClient(`/api/episodes/${id}/sign`, { method: "POST" });

// Triage
export const getTriageEntries = (params?: { status?: string; priority?: string }) => {
  const qs = params ? new URLSearchParams(params).toString() : "";
  return apiClient(qs ? `/api/triage?${qs}` : "/api/triage");
};

export const getTriageStats = () => apiClient("/api/triage/stats/counts");

export const createTriageEntry = (data: Record<string, unknown>) =>
  apiClient("/api/triage", { method: "POST", body: JSON.stringify(data) });

export const updateTriageEntry = (id: string, data: Record<string, unknown>) =>
  apiClient(`/api/triage/${id}`, { method: "PATCH", body: JSON.stringify(data) });

// Agenda
export const getAppointments = (params?: Record<string, string>) => {
  const qs = params ? new URLSearchParams(params).toString() : "";
  return apiClient(qs ? `/api/appointments?${qs}` : "/api/appointments");
};

export const createAppointment = (data: Record<string, unknown>) =>
  apiClient("/api/appointments", { method: "POST", body: JSON.stringify(data) });

export const updateAppointment = (id: string, data: Record<string, unknown>) =>
  apiClient(`/api/appointments/${id}`, { method: "PATCH", body: JSON.stringify(data) });

export const getFieldVisits = (params?: Record<string, string>) => {
  const qs = params ? new URLSearchParams(params).toString() : "";
  return apiClient(qs ? `/api/field-visits?${qs}` : "/api/field-visits");
};

export const createFieldVisit = (data: Record<string, unknown>) =>
  apiClient("/api/field-visits", { method: "POST", body: JSON.stringify(data) });

export const updateFieldVisit = (id: string, data: Record<string, unknown>) =>
  apiClient(`/api/field-visits/${id}`, { method: "PATCH", body: JSON.stringify(data) });

// Prescriptions
export const getPrescriptions = (episodeId?: string) =>
  apiClient(episodeId ? `/api/prescriptions?episode_id=${episodeId}` : "/api/prescriptions");

export const createPrescription = (data: Record<string, unknown>) =>
  apiClient("/api/prescriptions", { method: "POST", body: JSON.stringify(data) });

export const updatePrescription = (id: string, data: Record<string, unknown>) =>
  apiClient(`/api/prescriptions/${id}`, { method: "PATCH", body: JSON.stringify(data) });

export const signPrescription = (id: string) =>
  apiClient(`/api/prescriptions/${id}/sign`, { method: "POST" });

export const sendPrescription = (id: string, data?: { sent_to_email?: string }) =>
  apiClient(`/api/prescriptions/${id}/send`, { method: "POST", body: JSON.stringify(data || {}) });

export const cancelPrescription = (id: string, reason?: string) =>
  apiClient(`/api/prescriptions/${id}/cancel`, { method: "POST", body: JSON.stringify({ cancellation_reason: reason || null }) });

// Billing
export const getBillings = (episodeId?: string) =>
  apiClient(episodeId ? `/api/billings?episode_id=${episodeId}` : "/api/billings");

export const createBilling = (data: Record<string, unknown>) =>
  apiClient("/api/billings", { method: "POST", body: JSON.stringify(data) });

export const updateBilling = (id: string, data: Record<string, unknown>) =>
  apiClient(`/api/billings/${id}`, { method: "PATCH", body: JSON.stringify(data) });

export const validateBilling = (id: string) =>
  apiClient(`/api/billings/${id}/validate`, { method: "POST" });

export const exportBilling = (id: string) =>
  apiClient(`/api/billings/${id}/export`, { method: "POST" });
