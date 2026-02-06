/**
 * API Client — talks to the FastAPI backend
 * ==========================================
 * Base URL is proxied by Vite in dev (/api → http://localhost:8000/api)
 * In production, change VITE_API_BASE_URL in .env
 */

const API_BASE = import.meta.env.VITE_API_BASE_URL || "/api";

/**
 * Fetch water availability for a given location.
 * @param {{ district: string, state: string }} location
 * @returns {Promise<{ district, state, waterAvailability, maxCapacity, status }>}
 */
export async function fetchWaterStatus({ district, state }) {
  const params = new URLSearchParams();
  if (district) params.append("district", district);
  if (state) params.append("state", state);

  const res = await fetch(`${API_BASE}/water-status?${params.toString()}`);
  if (!res.ok) throw new Error("Failed to fetch water status");
  return res.json();
}

/**
 * Get crop recommendation based on selected crop and water availability.
 * @param {{ crop_id: string, water_availability: number, district?: string, state?: string, language?: string }} payload
 * @returns {Promise<{ crop_id, recommendation, water_required, water_available, yield_prediction, tips }>}
 */
export async function fetchCropAdvice(payload) {
  const res = await fetch(`${API_BASE}/crop-advice`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Failed to fetch crop advice");
  return res.json();
}

/**
 * Save / update user on the backend.
 * @param {{ email?: string, full_name?: string, phone?: string, location?: string }} userData
 */
export async function saveUser(userData) {
  const res = await fetch(`${API_BASE}/../users/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(userData),
  });
  if (!res.ok) throw new Error("Failed to save user");
  return res.json();
}
