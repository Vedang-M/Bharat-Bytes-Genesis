/**
 * Water Wallet API Client
 * Utility functions for integrating with the Water Wallet Backend API.
 */

// API Base URL - Update this to your backend URL
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

/**
 * Generic fetch wrapper with error handling
 */
async function apiFetch(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  try {
    const response = await fetch(url, {
      headers: {
        "Content-Type": "application/json",
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
 * Get water status for a location (GET - Simplified)
 * @param {number} latitude - Latitude of the location
 * @param {number} longitude - Longitude of the location
 * @returns {Promise<Object>} Water status data
 * 
 * Example response:
 * {
 *   water_balance_mm: 450,
 *   status: "limited", // "safe", "limited", or "critical"
 *   location: { state: "Uttar Pradesh", district: "Prayagraj", city: "Prayagraj" },
 *   solvency: { is_solvent: true, probability: 0.85, insolvency_in_days: null },
 *   safe_to_sow: true,
 *   weather_summary: { forecast_rainfall_mm: 120, forecast_et0_mm: 80, avg_temp_c: 28 },
 *   groundwater_category: "Semi-Critical"
 * }
 */
export async function getWaterStatus(latitude, longitude) {
  return apiFetch(`/api/water-status?lat=${latitude}&lon=${longitude}`);
}

/**
 * Check if a crop is viable for a location (GET - Simplified)
 * @param {string} cropId - Crop identifier (e.g., 'wheat', 'sugarcane')
 * @param {number} latitude - Latitude
 * @param {number} longitude - Longitude
 * @param {number} [waterMm] - Optional: Available water in mm (if already known)
 * @returns {Promise<Object>} Crop viability data
 * 
 * Example response:
 * {
 *   crop_id: "wheat",
 *   crop_name: "Wheat",
 *   crop_name_hi: "गेहूं",
 *   is_viable: true,
 *   recommendation: "suitable", // "suitable", "caution", or "not-recommended"
 *   water_required_mm: 450,
 *   water_available_mm: 400,
 *   water_ratio: 0.89,
 *   message: "गेहूं के लिए पर्याप्त पानी उपलब्ध है।",
 *   message_en: "Sufficient water available for Wheat."
 * }
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
 * @param {string} rejectedCropId - The crop that was rejected
 * @param {number} waterMm - Available water in mm
 * @param {number} [maxResults=3] - Number of recommendations
 * @returns {Promise<Object>} Alternative crop recommendations
 * 
 * Example response:
 * {
 *   rejected_crop: "sugarcane",
 *   available_water_mm: 400,
 *   recommendations: [
 *     { crop_id: "wheat", crop_name: "Wheat", water_required_mm: 450, ... },
 *     { crop_id: "chickpea", crop_name: "Chickpea", water_required_mm: 300, ... }
 *   ]
 * }
 */
export async function getSmartSwap(rejectedCropId, waterMm, maxResults = 3) {
  return apiFetch(`/api/smart-swap/${rejectedCropId}?water_mm=${waterMm}&max_results=${maxResults}`);
}

/**
 * Get list of all supported crops
 * @returns {Promise<Object>} List of crops with water requirements
 * 
 * Example response:
 * {
 *   crops: [
 *     { id: "wheat", name_en: "Wheat", name_hi: "गेहूं", water_req_mm: 450, water_need_category: "medium" },
 *     { id: "sugarcane", name_en: "Sugarcane", name_hi: "गन्ना", water_req_mm: 1800, water_need_category: "high" },
 *     ...
 *   ]
 * }
 */
export async function getCropsList() {
  return apiFetch("/api/crops");
}

/**
 * Get crops ranked by profit-per-drop
 * @returns {Promise<Object>} Profit ranking
 */
export async function getProfitRanking() {
  return apiFetch("/api/profit-ranking");
}

/**
 * Get best sowing date for a crop at a location
 * @param {string} cropId - Crop identifier
 * @param {number} latitude - Latitude
 * @param {number} longitude - Longitude
 * @returns {Promise<Object>} Best sowing date recommendation
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
 * @param {Object} params - Request parameters
 * @param {number} params.latitude - Latitude
 * @param {number} params.longitude - Longitude
 * @param {string} [params.state] - State name (optional, auto-detected)
 * @param {string} [params.district] - District name (optional, auto-detected)
 * @param {string} [params.block] - Block/Tehsil name (optional)
 * @returns {Promise<Object>} Full water status response
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
 * @returns {Promise<Object>} Health status
 */
export async function checkHealth() {
  return apiFetch("/health");
}

// ============== Helper functions ==============

/**
 * Map water status to UI display properties
 * @param {string} status - Status string ("safe", "limited", "critical")
 * @returns {Object} UI display properties
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
 * @param {string} recommendation - Recommendation string
 * @returns {Object} UI display properties
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
  getProfitRanking,
  getBestSowingDate,
  getWaterStatusFull,
  checkHealth,
  getStatusDisplayConfig,
  getRecommendationDisplayConfig,
};
