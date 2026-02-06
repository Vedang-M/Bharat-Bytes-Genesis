/**
 * Location Utility
 * Handles geolocation and reverse geocoding using Nominatim API
 */

const LOCATION_STORAGE_KEY = "user_location";

/**
 * Get user's current position using browser geolocation API
 * @returns {Promise<{latitude: number, longitude: number}>}
 */
export const getCurrentPosition = () => {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error("Geolocation is not supported by your browser"));
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        resolve({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
        });
      },
      (error) => {
        let errorMessage = "Unable to get location";

        switch (error.code) {
          case error.PERMISSION_DENIED:
            errorMessage = "Location permission denied";
            break;
          case error.POSITION_UNAVAILABLE:
            errorMessage = "Location information unavailable";
            break;
          case error.TIMEOUT:
            errorMessage = "Location request timed out";
            break;
          default:
            errorMessage = "An unknown error occurred";
        }

        reject(new Error(errorMessage));
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0,
      },
    );
  });
};

/**
 * Reverse geocode coordinates to address using Nominatim API
 * @param {number} latitude
 * @param {number} longitude
 * @returns {Promise<Object>} Address object with area, city, state, country
 */
export const reverseGeocode = async (latitude, longitude) => {
  const url =
    `https://nominatim.openstreetmap.org/reverse` +
    `?format=json` +
    `&lat=${latitude}` +
    `&lon=${longitude}` +
    `&zoom=18` +
    `&addressdetails=1` +
    `&accept-language=en`;

  try {
    const response = await fetch(url, {
      headers: {
        "User-Agent": "KisanSetu-App/1.0 (contact@yourdomain.com)",
        "Accept-Language": "en",
      },
    });

    if (!response.ok) {
      throw new Error(`Nominatim error: ${response.status}`);
    }

    const data = await response.json();
    const address = data.address || {};

    const city =
      address.city ||
      address.town ||
      address.village ||
      address.county ||
      "";

    return {
      area:
        address.suburb ||
        address.neighbourhood ||
        address.village ||
        "",
      city,
      district: address.state_district || address.county || city,
      state: address.state || "",
      country: address.country || "",
      fullAddress: data.display_name || "",
    };
  } catch (err) {
    console.error("Reverse geocode failed:", err);
    throw err;
  }
};



/**
 * Get user location (coordinates + address)
 * This is the main function to call from components
 * @returns {Promise<Object>} Location object with coordinates and address
 */
export const getUserLocation = async () => {
  try {
    // Step 1: Get coordinates
    const coords = await getCurrentPosition();

    // Step 2: Reverse geocode to get address
    // Add a small delay to respect Nominatim rate limits (max 1 request per second)
    await new Promise((resolve) => setTimeout(resolve, 1000));

    const address = await reverseGeocode(coords.latitude, coords.longitude);

    const locationData = {
      ...coords,
      ...address,
      timestamp: new Date().toISOString(),
    };

    // Save to localStorage
    saveLocation(locationData);

    return locationData;
  } catch (error) {
    console.error("Get user location error:", error);
    throw error;
  }
};

/**
 * Save location data to localStorage
 * @param {Object} locationData
 */
export const saveLocation = (locationData) => {
  try {
    localStorage.setItem(LOCATION_STORAGE_KEY, JSON.stringify(locationData));
  } catch (error) {
    console.error("Error saving location:", error);
  }
};

/**
 * Get saved location from localStorage
 * @returns {Object|null} Saved location data or null
 */
export const getSavedLocation = () => {
  try {
    const saved = localStorage.getItem(LOCATION_STORAGE_KEY);
    console.log("Location in location util file: ", saved);
    return saved ? JSON.parse(saved) : null;
  } catch (error) {
    console.error("Error reading saved location:", error);
    return null;
  }
};

/**
 * Clear saved location from localStorage
 */
export const clearLocation = () => {
  try {
    localStorage.removeItem(LOCATION_STORAGE_KEY);
  } catch (error) {
    console.error("Error clearing location:", error);
  }
};

/**
 * Format location for display
 * @param {Object} location
 * @param {string} format - 'short' | 'medium' | 'full'
 * @returns {string} Formatted location string
 */
export const formatLocation = (location, format = "medium") => {
  if (!location) return "";

  switch (format) {
    case "short":
      // Just city, state
      return [location.city, location.state].filter(Boolean).join(", ");

    case "medium":
      // Area, city, state
      return [location.area, location.city, location.state]
        .filter(Boolean)
        .join(", ");

    case "full":
      // Full address
      return location.fullAddress || "";

    case "district":
      // District and state (for water status)
      return [location.district || location.city, location.state]
        .filter(Boolean)
        .join(", ");

    default:
      return [location.city, location.state].filter(Boolean).join(", ");
  }
};

/**
 * Check if location data is stale (older than 24 hours)
 * @param {Object} location
 * @returns {boolean}
 */
export const isLocationStale = (location) => {
  if (!location || !location.timestamp) return true;

  const timestamp = new Date(location.timestamp);
  const now = new Date();
  const hoursDiff = (now - timestamp) / (1000 * 60 * 60);

  return hoursDiff > 24;
};

// Legacy function for backward compatibility
export const getCurrentLocation = getCurrentPosition;

// Legacy function for backward compatibility
export const formatCoordinates = (latitude, longitude) => {
  return `${latitude.toFixed(6)}, ${longitude.toFixed(6)}`;
};
