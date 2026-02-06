/**
 * Authentication utility functions
 * Now integrated with Firebase Authentication with localStorage fallback.
 */

import { auth, db, firebaseConfigured, getIdToken } from "../firebase/firebaseConfig";
import { doc, getDoc, updateDoc } from "firebase/firestore";

const USER_DATA_KEY = "genesis_user_data";

/**
 * Check if user is logged in
 * @returns {boolean} True if user is authenticated
 */
export const isUserLoggedIn = () => {
  // Check Firebase auth first
  if (firebaseConfigured && auth?.currentUser) {
    return true;
  }

  // Fallback to localStorage
  try {
    const userData = localStorage.getItem(USER_DATA_KEY);
    return userData !== null && userData !== undefined;
  } catch (error) {
    console.error("Error checking login status:", error);
    return false;
  }
};

/**
 * Save user registration data to localStorage (for demo mode)
 * @param {Object} userData - User data object
 */
export const saveUserData = (userData) => {
  try {
    const dataToSave = {
      ...userData,
      registeredAt: new Date().toISOString(),
    };
    localStorage.setItem(USER_DATA_KEY, JSON.stringify(dataToSave));
    return true;
  } catch (error) {
    console.error("Error saving user data:", error);
    return false;
  }
};

/**
 * Retrieve user data
 * @returns {Object|null} User data object or null
 */
export const getUserData = async () => {
  // Try Firebase first
  if (firebaseConfigured && auth?.currentUser && db) {
    try {
      const userDoc = await getDoc(doc(db, "users", auth.currentUser.uid));
      if (userDoc.exists()) {
        return { uid: auth.currentUser.uid, ...userDoc.data() };
      }
    } catch (error) {
      console.error("Error fetching from Firestore:", error);
    }
  }

  // Fallback to localStorage
  try {
    const userData = localStorage.getItem(USER_DATA_KEY);
    return userData ? JSON.parse(userData) : null;
  } catch (error) {
    console.error("Error retrieving user data:", error);
    return null;
  }
};

/**
 * Synchronous version of getUserData for components that can't use async
 * @returns {Object|null} User data from localStorage
 */
export const getUserDataSync = () => {
  try {
    const userData = localStorage.getItem(USER_DATA_KEY);
    return userData ? JSON.parse(userData) : null;
  } catch (error) {
    console.error("Error retrieving user data:", error);
    return null;
  }
};

/**
 * Update user data
 * @param {Object} updates - Fields to update
 */
export const updateUserData = async (updates) => {
  // Update Firebase if available
  if (firebaseConfigured && auth?.currentUser && db) {
    try {
      await updateDoc(doc(db, "users", auth.currentUser.uid), updates);
    } catch (error) {
      console.error("Error updating Firestore:", error);
    }
  }

  // Also update localStorage
  try {
    const currentData = localStorage.getItem(USER_DATA_KEY);
    const userData = currentData ? JSON.parse(currentData) : {};
    const updatedData = { ...userData, ...updates };
    localStorage.setItem(USER_DATA_KEY, JSON.stringify(updatedData));
    return true;
  } catch (error) {
    console.error("Error updating user data:", error);
    return false;
  }
};

/**
 * Clear user data (logout)
 */
export const logoutUser = async () => {
  try {
    // Sign out from Firebase
    if (firebaseConfigured && auth) {
      await auth.signOut();
    }

    // Clear localStorage
    localStorage.removeItem(USER_DATA_KEY);
    return true;
  } catch (error) {
    console.error("Error logging out:", error);
    return false;
  }
};

/**
 * Get Firebase ID token for API calls
 * @returns {string|null} ID token or null
 */
export const getAuthToken = async () => {
  return await getIdToken();
};

/**
 * Get user role
 * @returns {string} User role (farmer, sarpanch, admin)
 */
export const getUserRole = () => {
  try {
    const userData = localStorage.getItem(USER_DATA_KEY);
    if (userData) {
      const parsed = JSON.parse(userData);
      return parsed.role || "farmer";
    }
    return "farmer";
  } catch (error) {
    return "farmer";
  }
};

/**
 * Check if user has required role level
 * @param {string} requiredRole - Role to check against
 * @returns {boolean} True if user has role or higher
 */
export const hasRole = (requiredRole) => {
  const userRole = getUserRole();
  const roleHierarchy = { farmer: 0, sarpanch: 1, admin: 2 };
  const userLevel = roleHierarchy[userRole] || 0;
  const requiredLevel = roleHierarchy[requiredRole] || 0;
  return userLevel >= requiredLevel;
};
