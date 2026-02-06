import { useState, useEffect } from "react";
import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
  useNavigate,
} from "react-router-dom";
import { isUserLoggedIn } from "./utils/authUtils";
import { isLanguageSelected, getLanguage } from "./utils/languageUtils";
import WelcomePopup from "./components/WelcomePopup";
import LanguageSelectionPopup from "./components/LanguageSelectionPopup";
import SignupPopup from "./components/SignupPopup";
import HeroSection from "./components/HeroSection";
import WaterStatusScreen from "./components/WaterStatusScreen";
import CropSelect from "./components/CropSelect";
import CropResult from "./components/CropResult";
import ProfilePage from "./components/ProfilePage";
import ApiDocumentation from "./components/ApiDocumentation";
import SarpanchDashboard from "./sarpanch/SarpanchDashboard";
import AppLayout from "./components/AppLayout";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import "./App.css";

function AuthFlow() {
  const navigate = useNavigate();
  const [showWelcomePopup, setShowWelcomePopup] = useState(true);
  const [showLanguagePopup, setShowLanguagePopup] = useState(false);
  const [showSignupPopup, setShowSignupPopup] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [selectedLanguage, setSelectedLanguage] = useState("hi");

  useEffect(() => {
    // Check if user is already logged in
    const loggedIn = isUserLoggedIn();
    setIsLoggedIn(loggedIn);

    // Get saved language preference
    const savedLanguage = getLanguage();
    if (savedLanguage) {
      setSelectedLanguage(savedLanguage);
    }

    // If user is logged in, redirect to water page
    if (loggedIn) {
      navigate("/water");
    }
  }, [navigate]);

  const handleWelcomeClose = () => {
    setShowWelcomePopup(false);

    // After welcome popup closes, check if user is logged in
    if (!isLoggedIn) {
      // Check if language is already selected
      if (isLanguageSelected()) {
        // Language already selected, go directly to signup
        setShowSignupPopup(true);
      } else {
        // Show language selection first
        setShowLanguagePopup(true);
      }
    }
  };

  const handleLanguageSelect = (language) => {
    setSelectedLanguage(language);
    setShowLanguagePopup(false);
    // After language selection, show signup popup
    setShowSignupPopup(true);
  };

  const handleSignupClose = () => {
    setShowSignupPopup(false);
  };

  const handleSignupComplete = () => {
    setIsLoggedIn(true);
    setShowSignupPopup(false);
    // Navigate to water status screen after signup
    navigate("/water");
  };

  return (
    <div className="relative w-screen h-screen overflow-hidden font-hindi">
      {/* Hero Section */}
      <HeroSection />

      {/* Welcome Popup - Shows first on page load */}
      {showWelcomePopup && <WelcomePopup onClose={handleWelcomeClose} />}

      {/* Language Selection Popup - Shows after welcome if not logged in and language not selected */}
      {showLanguagePopup && !isLoggedIn && (
        <LanguageSelectionPopup onLanguageSelect={handleLanguageSelect} />
      )}

      {/* Signup Popup - Shows after language selection if user not logged in */}
      {showSignupPopup && !isLoggedIn && (
        <SignupPopup
          onClose={handleSignupClose}
          onSignupComplete={handleSignupComplete}
          language={selectedLanguage}
        />
      )}
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Auth flow route */}
        <Route path="/" element={<AuthFlow />} />

        {/* Main app routes with layout */}
        <Route element={<AppLayout />}>
          <Route path="/water" element={<WaterStatusScreen />} />
          <Route path="/crops" element={<CropSelect />} />
          <Route path="/advice" element={<CropResult />} />
          <Route path="/profile" element={<ProfilePage />} />
        </Route>

        {/* API Documentation route (no layout) */}
        <Route path="/dev/api" element={<ApiDocumentation />} />

        {/* Sarpanch Dashboard route (no layout) */}
        <Route path="/authority/sarpanch" element={<SarpanchDashboard />} />

        {/* Redirect any unknown routes to home */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      <ToastContainer
        position="top-right"
        autoClose={5000}
        hideProgressBar={false}
        newestOnTop
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme="colored"
      />
    </BrowserRouter>
  );
}

export default App;
