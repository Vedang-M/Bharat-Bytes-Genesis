// Language management utilities

const LANGUAGE_KEY = "genesis_language";

/**
 * Get current language from localStorage
 * @returns {string} 'hi' for Hindi or 'en' for English, defaults to 'hi'
 */
export const getLanguage = () => {
  try {
    const language = localStorage.getItem(LANGUAGE_KEY);
    return language || null; // Return null if not set
  } catch (error) {
    console.error("Error getting language:", error);
    return null;
  }
};

/**
 * Set language preference
 * @param {string} language - 'hi' or 'en'
 */
export const setLanguage = (language) => {
  try {
    localStorage.setItem(LANGUAGE_KEY, language);
    return true;
  } catch (error) {
    console.error("Error setting language:", error);
    return false;
  }
};

/**
 * Check if language is already selected
 * @returns {boolean}
 */
export const isLanguageSelected = () => {
  return getLanguage() !== null;
};

// Translation strings
export const translations = {
  en: {
    // Welcome Popup
    welcome: {
      greeting: "Namaste 🙏",
      tagline: "Right Water Calculation",
      subtitle: "for Farming",
    },
    // Language Selection
    languageSelection: {
      title: "Choose Your Language",
      subtitle: "Select your preferred language",
      hindi: "हिन्दी",
      english: "English",
      continue: "Continue",
    },
    // Signup Popup
    signup: {
      title: "Welcome!",
      subtitle: "Join us to get started",
      emoji: "🌾",
      tagline: "Start your farming journey here",
      name: "Name",
      namePlaceholder: "Enter your name",
      phone: "Phone Number",
      phonePlaceholder: "10 digit number",
      location: "Pincode / Location",
      locationPlaceholder: "Pincode or address",
      locationButton: "Location",
      submit: "Sign Up",
      errors: {
        nameRequired: "Name is required",
        phoneRequired: "Phone number is required",
        phoneInvalid: "Please enter a valid 10-digit phone number",
        locationRequired: "Location is required",
      },
      alerts: {
        saveFailed: "Failed to save user data. Please try again.",
      },
    },
    // Water Status Screen
    waterStatus: {
      header: "Water Status in Your Area 💧",
      location: "Location",
      availableWater: "Available Water",
      unit: "mm",
      status: {
        safe: "Safe",
        limited: "Limited",
        critical: "Critical",
      },
      advisory: {
        safe: "Good water availability.\nYou can choose water-intensive crops.",
        limited: "Water is limited this season.\nChoose crops carefully.",
        critical:
          "Very low water availability.\nSelect drought-resistant crops only.",
      },
      cta: "🌱 Check Crops",
    },
    // Profile Page
    profile: {
      title: "My Profile",
      name: "Name",
      phone: "Phone Number",
      location: "Location",
      registeredOn: "Registered On",
      edit: "Edit Profile",
      save: "Save Changes",
      cancel: "Cancel",
      logout: "Logout",
      logoutConfirm: "Are you sure you want to logout?",
      saveSuccess: "Profile updated successfully",
      saveFailed: "Failed to update profile",
      errors: {
        nameRequired: "Name is required",
        phoneRequired: "Phone number is required",
        phoneInvalid: "Please enter a valid 10-digit phone number",
        locationRequired: "Location is required",
      },
    },
    // Crops Page
    crops: {
      title: "Select Crop",
      subtitle: "Check the right crop based on water availability",
      waterNeed: {
        high: "High Water (High)",
        medium: "Medium Water (Medium)",
        low: "Low Water (Low)",
      },
      cropNames: {
        sugarcane: "Sugarcane",
        paddy: "Paddy",
        wheat: "Wheat",
        mustard: "Mustard",
        chickpea: "Chickpea",
        cotton: "Cotton",
      },
    },
    // Advice Page
    advice: {
      title: "Crop Advice",
      subtitle: "Special suggestions for",
      recommendation: {
        suitable: "Suitable Crop",
        caution: "Plant with Caution",
        notRecommended: "Not Recommended",
      },
      messages: {
        suitable:
          "This crop is suitable according to water availability in your area.",
        caution:
          "There may be water shortage. Adopt water conservation techniques.",
        notRecommended:
          "This crop is not suitable right now due to water shortage.",
      },
      waterAnalysis: "Water Requirement",
      waterRequired: "Required Water",
      waterAvailable: "Available Water",
      yieldPrediction: "Yield Prediction",
      tips: "Tips",
      defaultYield: "Good yield expected",
      defaultTips: [
        "Use drip irrigation",
        "Save water with mulching",
        "Irrigate in morning or evening",
      ],
    },
  },
  hi: {
    // Welcome Popup
    welcome: {
      greeting: "नमस्ते 🙏",
      tagline: "खेती के लिए पानी का",
      subtitle: "सही हिसाब",
    },
    // Language Selection
    languageSelection: {
      title: "अपनी भाषा चुनें",
      subtitle: "अपनी पसंदीदा भाषा चुनें",
      hindi: "हिन्दी",
      english: "English",
      continue: "जारी रखें",
    },
    // Signup Popup
    signup: {
      title: "स्वागत है!",
      subtitle: "शुरू करने के लिए हमसे जुड़ें",
      emoji: "🌾",
      tagline: "खेती की सही शुरुआत यहीं से करें",
      name: "नाम",
      namePlaceholder: "अपना नाम दर्ज करें",
      phone: "फोन नंबर",
      phonePlaceholder: "10 अंकों का नंबर",
      location: "पिनकोड / स्थान",
      locationPlaceholder: "पिनकोड या पता",
      locationButton: "स्थान",
      submit: "साइन अप करें",
      errors: {
        nameRequired: "नाम आवश्यक है",
        phoneRequired: "फोन नंबर आवश्यक है",
        phoneInvalid: "कृपया 10 अंकों का फोन नंबर दर्ज करें",
        locationRequired: "स्थान आवश्यक है",
      },
      alerts: {
        saveFailed: "उपयोगकर्ता डेटा सहेजने में विफल। कृपया पुनः प्रयास करें।",
      },
    },
    // Water Status Screen
    waterStatus: {
      header: "आपके क्षेत्र में पानी की स्थिति",
      location: "स्थान",
      availableWater: "उपलब्ध पानी",
      unit: "मिमी",
      status: {
        safe: "सुरक्षित",
        limited: "सीमित",
        critical: "संकट",
      },
      advisory: {
        safe: "पानी की अच्छी उपलब्धता है।\nआप पानी की अधिक जरूरत वाली फसलें चुन सकते हैं।",
        limited: "इस मौसम में पानी कम है।\nसावधानी से फसल चुनें।",
        critical: "पानी बहुत कम है।\nकेवल सूखा प्रतिरोधी फसलें चुनें।",
      },
      cta: "फसल जांचें",
    },
    // Profile Page
    profile: {
      title: "मेरी प्रोफाइल",
      name: "नाम",
      phone: "फोन नंबर",
      location: "स्थान",
      registeredOn: "पंजीकृत",
      edit: "संपादित करें",
      save: "सहेजें",
      cancel: "रद्द करें",
      logout: "लॉग आउट",
      logoutConfirm: "क्या आप वाकई लॉग आउट करना चाहते हैं?",
      saveSuccess: "प्रोफाइल सफलतापूर्वक अपडेट हुई",
      saveFailed: "प्रोफाइल अपडेट करने में विफल",
      errors: {
        nameRequired: "नाम आवश्यक है",
        phoneRequired: "फोन नंबर आवश्यक है",
        phoneInvalid: "कृपया 10 अंकों का फोन नंबर दर्ज करें",
        locationRequired: "स्थान आवश्यक है",
      },
    },
    // Crops Page
    crops: {
      title: "फसल चुनें",
      subtitle: "पानी के हिसाब से सही फसल की जांच करें",
      waterNeed: {
        high: "अधिक पानी (High)",
        medium: "मध्यम पानी (Medium)",
        low: "कम पानी (Low)",
      },
      cropNames: {
        sugarcane: "गन्ना",
        paddy: "धान",
        wheat: "गेहूं",
        mustard: "सरसों",
        chickpea: "चना",
        cotton: "कपास",
      },
    },
    // Advice Page
    advice: {
      title: "फसल सलाह",
      subtitle: "के लिए विशेष सुझाव",
      recommendation: {
        suitable: "उपयुक्त फसल",
        caution: "सावधानी से लगाएं",
        notRecommended: "अनुशंसित नहीं",
      },
      messages: {
        suitable:
          "आपके क्षेत्र में पानी की उपलब्धता के अनुसार यह फसल उपयुक्त है।",
        caution: "पानी की कमी हो सकती है। जल संरक्षण तकनीक अपनाएं।",
        notRecommended: "पानी की कमी के कारण यह फसल अभी उपयुक्त नहीं है।",
      },
      waterAnalysis: "पानी की आवश्यकता",
      waterRequired: "आवश्यक पानी",
      waterAvailable: "उपलब्ध पानी",
      yieldPrediction: "उपज का अनुमान",
      tips: "सुझाव",
      defaultYield: "अच्छी उपज की संभावना",
      defaultTips: [
        "ड्रिप सिंचाई का उपयोग करें",
        "मल्चिंग से पानी बचाएं",
        "सुबह या शाम को सिंचाई करें",
      ],
    },
  },
};

/**
 * Get translation for current language
 * @param {string} language - 'hi' or 'en'
 * @returns {object} Translation object
 */
export const getTranslations = (language) => {
  return translations[language] || translations.hi;
};
