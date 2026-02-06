// Authentication utility functions for localStorage management

const USER_DATA_KEY = 'genesis_user_data';

/**
 * Check if user is logged in by verifying localStorage data
 * @returns {boolean} True if user data exists
 */
export const isUserLoggedIn = () => {
  try {
    const userData = localStorage.getItem(USER_DATA_KEY);
    return userData !== null && userData !== undefined;
  } catch (error) {
    console.error('Error checking login status:', error);
    return false;
  }
};

/**
 * Save user registration data to localStorage
 * @param {Object} userData - User data object containing name, phone, location
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
    console.error('Error saving user data:', error);
    return false;
  }
};

/**
 * Retrieve user data from localStorage
 * @returns {Object|null} User data object or null if not found
 */
export const getUserData = () => {
  try {
    const userData = localStorage.getItem(USER_DATA_KEY);
    return userData ? JSON.parse(userData) : null;
  } catch (error) {
    console.error('Error retrieving user data:', error);
    return null;
  }
};

/**
 * Clear user data from localStorage (logout)
 */
export const logoutUser = () => {
  try {
    localStorage.removeItem(USER_DATA_KEY);
    return true;
  } catch (error) {
    console.error('Error logging out:', error);
    return false;
  }
};
