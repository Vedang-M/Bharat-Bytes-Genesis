import { useState, useEffect } from "react";
import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
  useNavigate,
} from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
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
import Documentation from "./components/Documentation";
import SarpanchDashboard from "./sarpanch/SarpanchDashboard";
import AdminDashboard from "./components/AdminDashboard";
import AppLayout from "./components/AppLayout";
import Marketplace from "./pages/Marketplace";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import "./App.css";

/**
 * Protected Route Component
 * Redirects to home if not authenticated or doesn't have required role.
 */
function ProtectedRoute({ children, requiredRole = null }) {
  const { isAuthenticated, hasRole, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#422B06]">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-white border-t-transparent"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  if (requiredRole && !hasRole(requiredRole)) {
    return <Navigate to="/water" replace />;
  }

  return children;
}

function AuthFlow() {
  const navigate = useNavigate();
  const { isAuthenticated, loading, hasRole } = useAuth();
  const [showWelcomePopup, setShowWelcomePopup] = useState(true);
  const [showLanguagePopup, setShowLanguagePopup] = useState(false);
  const [showSignupPopup, setShowSignupPopup] = useState(false);
  const [selectedLanguage, setSelectedLanguage] = useState("hi");

  useEffect(() => {
    // Get saved language preference
    const savedLanguage = getLanguage();
    if (savedLanguage) {
      setSelectedLanguage(savedLanguage);
    }

    // If user is already logged in, redirect based on role
    if (!loading && isAuthenticated) {
      if (hasRole("admin")) {
        navigate("/admin");
      } else if (hasRole("sarpanch")) {
        navigate("/authority/sarpanch");
      } else {
        navigate("/water");
      }
    }
  }, [navigate, isAuthenticated, loading, hasRole]);

  const handleWelcomeClose = () => {
    setShowWelcomePopup(false);

    // After welcome popup closes, check if user is logged in
    if (!isAuthenticated) {
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
    setShowSignupPopup(false);
    // Navigation is handled by useEffect when isAuthenticated becomes true
  };

  // Show loading spinner while checking auth
  if (loading) {
    return (
      <div className="relative w-screen h-screen overflow-hidden font-hindi flex items-center justify-center bg-[#422B06]">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-white border-t-transparent"></div>
      </div>
    );
  }

  return (
    <div className="relative w-screen h-screen overflow-hidden font-hindi">
      {/* Hero Section */}
      <HeroSection />

      {/* Welcome Popup - Shows first on page load */}
      {showWelcomePopup && <WelcomePopup onClose={handleWelcomeClose} />}

      {/* Language Selection Popup - Shows after welcome if not logged in and language not selected */}
      {showLanguagePopup && !isAuthenticated && (
        <LanguageSelectionPopup onLanguageSelect={handleLanguageSelect} />
      )}

      {/* Signup Popup - Shows after language selection if user not logged in */}
      {showSignupPopup && !isAuthenticated && (
        <SignupPopup
          onClose={handleSignupClose}
          onSignupComplete={handleSignupComplete}
          language={selectedLanguage}
        />
      )}
    </div>
  );
}

function AppRoutes() {
  return (
    <Routes>
      {/* Auth flow route */}
      <Route path="/" element={<AuthFlow />} />

      {/* Main app routes with layout - Protected */}
      <Route element={<AppLayout />}>
        <Route
          path="/water"
          element={
            <ProtectedRoute>
              <WaterStatusScreen />
            </ProtectedRoute>
          }
        />
        <Route
          path="/crops"
          element={
            <ProtectedRoute>
              <CropSelect />
            </ProtectedRoute>
          }
        />
        <Route
          path="/advice"
          element={
            <ProtectedRoute>
              <CropResult />
            </ProtectedRoute>
          }
        />
        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <ProfilePage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/marketplace"
          element={
            <ProtectedRoute>
              <Marketplace />
            </ProtectedRoute>
          }
        />
      </Route>

      {/* API Documentation route (no layout, no auth) */}
      <Route path="/dev/api" element={<ApiDocumentation />} />
      <Route path="/documentation" element={<Documentation />} />

      {/* Sarpanch Dashboard route - Requires sarpanch role */}
      <Route
        path="/authority/sarpanch"
        element={
          <ProtectedRoute requiredRole="sarpanch">
            <SarpanchDashboard />
          </ProtectedRoute>
        }
      />

      {/* Admin Dashboard route - Requires admin role */}
      <Route
        path="/admin"
        element={
          <ProtectedRoute requiredRole="admin">
            <AdminDashboard />
          </ProtectedRoute>
        }
      />

      {/* Redirect any unknown routes to home */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
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
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
