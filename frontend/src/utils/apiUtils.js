/**
 * Water Wallet API Client
 * Utility functions for integrating with the Water Wallet Backend API.
 * Now with Firebase authentication support.
 */

import { getIdToken } from "../firebase/firebaseConfig";

// API Base URL - In development, Vite proxy handles /api/* routes
// In production, set VITE_API_URL to your backend URL
const API_BASE_URL = import.meta.env.VITE_API_URL || "";

/**
 * Get auth headers with Firebase ID token
 */
async function getAuthHeaders() {
  const token = await getIdToken();
  if (token) {
    return { Authorization: `Bearer ${token}` };
  }
  return {};
}

/**
 * Generic fetch wrapper with error handling and optional authentication
 */
async function apiFetch(endpoint, options = {}, requireAuth = false) {
  const url = `${API_BASE_URL}${endpoint}`;

  try {
    // Get auth headers if needed
    const authHeaders = requireAuth ? await getAuthHeaders() : {};

    const response = await fetch(url, {
      headers: {
        "Content-Type": "application/json",
        ...authHeaders,
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `API error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`API Error (${endpoint}):`, error);
    throw error;
  }
}

/**
 * Authenticated fetch - always includes auth token
 */
async function authenticatedFetch(endpoint, options = {}) {
  return apiFetch(endpoint, options, true);
}

/**
 * Get water status for a location (GET - Simplified)
 * Requires authentication.
 */
export async function getWaterStatus(latitude, longitude) {
  return authenticatedFetch(`/api/water-status?lat=${latitude}&lon=${longitude}`);
}

/**
 * Check if a crop is viable for a location (GET - Simplified)
 */
export async function checkCropViability(cropId, latitude, longitude, waterMm = null) {
  let url = `/api/crop-check/${cropId}?lat=${latitude}&lon=${longitude}`;
  if (waterMm !== null) {
    url += `&water_mm=${waterMm}`;
  }
  return apiFetch(url);
}

/**
 * Get alternative crop recommendations (Smart-Swap)
 */
export async function getSmartSwap(rejectedCropId, waterMm, maxResults = 3) {
  return apiFetch(`/api/smart-swap/${rejectedCropId}?water_mm=${waterMm}&max_results=${maxResults}`);
}

/**
 * Get list of all supported crops
 */
export async function getCropsList() {
  return apiFetch("/api/crops");
}

/**
 * Get fertilizer advertisements based on crop, region, and season
 * @param {string} crop - Target crop ID (e.g., "wheat", "rice")
 * @param {string} region - Target region/state (e.g., "Maharashtra")
 * @param {string} season - Target season ("kharif", "rabi", "zaid")
 * @returns {Promise<{ads: Array, count: number, filters_applied: object}>}
 */
export async function getFertilizerAds(crop, region, season = "kharif") {
  const params = new URLSearchParams();
  if (crop) params.append("crop", crop);
  if (region) params.append("region", region);
  if (season) params.append("season", season);
  
  return apiFetch(`/api/ads?${params.toString()}`);
}

/**
 * Get crops ranked by profit-per-drop
 */
export async function getProfitRanking() {
  return apiFetch("/api/profit-ranking");
}

/**
 * Get best sowing date for a crop at a location
 */
export async function getBestSowingDate(cropId, latitude, longitude) {
  return apiFetch("/api/best-sowing-date", {
    method: "POST",
    body: JSON.stringify({
      crop_id: cropId,
      latitude,
      longitude,
    }),
  });
}

/**
 * Full water status request (POST version with all details)
 */
export async function getWaterStatusFull({ latitude, longitude, state, district, block }) {
  return apiFetch("/api/water-status", {
    method: "POST",
    body: JSON.stringify({
      latitude,
      longitude,
      state,
      district,
      block,
    }),
  });
}

/**
 * Check API health
 */
export async function checkHealth() {
  return apiFetch("/health");
}

// ==================== ML ENDPOINTS ====================

/**
 * Get groundwater forecast using Prophet model
 */
export async function getGroundwaterForecast(lat, lon, days = 30, soilData = {}) {
  return apiFetch("/ml/groundwater/forecast", {
    method: "POST",
    body: JSON.stringify({
      lat,
      lon,
      days,
      ...soilData,
    }),
  });
}

/**
 * Analyze crop viability using XGBoost
 */
export async function analyzeViability(params) {
  return apiFetch("/ml/viability/analyze", {
    method: "POST",
    body: JSON.stringify(params),
  });
}

// ==================== AUTHENTICATED ENDPOINTS ====================

/**
 * Register user (after Firebase signup)
 */
export async function registerUser(userData) {
  return authenticatedFetch("/api/auth/register", {
    method: "POST",
    body: JSON.stringify(userData),
  });
}

/**
 * Login and get user profile
 */
export async function loginUser(idToken) {
  return apiFetch("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ id_token: idToken }),
  });
}

/**
 * Get current user profile (requires auth)
 */
export async function getUserProfile() {
  return authenticatedFetch("/api/auth/profile");
}

/**
 * Update user profile (requires auth)
 */
export async function updateUserProfile(updates) {
  return authenticatedFetch("/api/auth/profile", {
    method: "PUT",
    body: JSON.stringify(updates),
  });
}

/**
 * Check auth status
 */
export async function checkAuthStatus() {
  return authenticatedFetch("/api/auth/check");
}

// ==================== HELPER FUNCTIONS ====================

/**
 * Map water status to UI display properties
 */
export function getStatusDisplayConfig(status) {
  const configs = {
    safe: {
      color: "#2E7D32",
      gradient: "from-[#2E7D32] to-[#43A047]",
      labelHi: "सुरक्षित",
      labelEn: "Safe",
    },
    limited: {
      color: "#F9A825",
      gradient: "from-[#F9A825] to-[#FBC02D]",
      labelHi: "सीमित",
      labelEn: "Limited",
    },
    critical: {
      color: "#E53935",
      gradient: "from-[#E53935] to-[#EF5350]",
      labelHi: "गंभीर",
      labelEn: "Critical",
    },
  };

  return configs[status] || configs.limited;
}

/**
 * Map recommendation to UI display properties
 */
export function getRecommendationDisplayConfig(recommendation) {
  const configs = {
    suitable: {
      color: "#2E7D32",
      gradient: "from-[#2E7D32] to-[#43A047]",
      labelHi: "उपयुक्त",
      labelEn: "Suitable",
    },
    caution: {
      color: "#F9A825",
      gradient: "from-[#F9A825] to-[#FBC02D]",
      labelHi: "सावधानी",
      labelEn: "Caution",
    },
    "not-recommended": {
      color: "#E53935",
      gradient: "from-[#E53935] to-[#EF5350]",
      labelHi: "अनुशंसित नहीं",
      labelEn: "Not Recommended",
    },
  };

  return configs[recommendation] || configs.caution;
}

export default {
  getWaterStatus,
  checkCropViability,
  getSmartSwap,
  getCropsList,
  getFertilizerAds,
  getProfitRanking,
  getBestSowingDate,
  getWaterStatusFull,
  checkHealth,
  getGroundwaterForecast,
  analyzeViability,
  registerUser,
  loginUser,
  getUserProfile,
  updateUserProfile,
  checkAuthStatus,
  getStatusDisplayConfig,
  getRecommendationDisplayConfig,
};
