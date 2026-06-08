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
