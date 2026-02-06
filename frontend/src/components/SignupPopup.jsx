import { useState } from "react";
import { User, Phone, Mail, Lock, ArrowLeft } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { getTranslations } from "../utils/languageUtils";
import RoleSelectionGateway from "./RoleSelectionGateway";

const SignupPopup = ({ onClose, onSignupComplete, language = "hi" }) => {
  const { signUp, signIn, isFirebaseConfigured } = useAuth();

  // Steps: 'role' -> 'form'
  const [step, setStep] = useState(isFirebaseConfigured ? "form" : "role");
  const [isLoginMode, setIsLoginMode] = useState(false);
  const [selectedRole, setSelectedRole] = useState("farmer");

  const [formData, setFormData] = useState({
    name: "",
    phone: "",
    email: "",
    password: "",
  });
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);

  // Get translations based on selected language
  const t = getTranslations(language).signup;

  const handleRoleSelect = (role) => {
    setSelectedRole(role);
    setStep("form");
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (errors[name]) setErrors((prev) => ({ ...prev, [name]: "" }));
  };

  const validateForm = () => {
    const newErrors = {};

    // Validate Name (only if Signup)
    if (!isLoginMode && !formData.name.trim()) newErrors.name = t.errors.nameRequired;

    // Validate Phone (only if Signup)
    if (!isLoginMode) {
      if (!formData.phone.trim()) {
        newErrors.phone = t.errors.phoneRequired;
      } else if (!/^\d{10}$/.test(formData.phone.replace(/\s/g, ""))) {
        newErrors.phone = t.errors.phoneInvalid;
      }
    }

    // Email and password required for both (if Firebase is on)
    if (isFirebaseConfigured) {
      if (!formData.email.trim()) {
        newErrors.email = language === "hi" ? "ईमेल आवश्यक है" : "Email is required";
      }

      if (!formData.password || formData.password.length < 6) {
        newErrors.password = language === "hi" ? "पासवर्ड कम से कम 6 अक्षर का होना चाहिए" : "Password must be at least 6 characters";
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;

    setIsLoading(true);

    try {
      let result;
      if (isLoginMode) {
        result = await signIn(formData.email, formData.password);
      } else {
        result = await signUp({
          name: formData.name,
          phone: formData.phone,
          email: formData.email || `${formData.phone}@waterwallet.local`,
          password: formData.password || formData.phone,
          role: selectedRole,
          location: null,
        });
      }

      if (result.success) {
        onSignupComplete();
        onClose();
      } else {
        setErrors({ submit: result.error });
      }
    } catch (error) {
      console.error("Auth error:", error);
      setErrors({ submit: error.message || "Authentication failed" });
    } finally {
      setIsLoading(false);
    }
  };

  // Toggle Login/Signup
  const toggleAuthMode = () => {
    setIsLoginMode(!isLoginMode);
    setErrors({});
    if (!isLoginMode) {
      // Switching to Login
      setStep("form");
    } else {
      // Switching to Signup
      setStep("role");
    }
  };

  return (
    <div className="fixed inset-0 z-[1000] flex items-center justify-center bg-black/40 font-hindi p-4 overflow-y-auto">
      {step === "role" && !isLoginMode ? (
        <div className="flex flex-col items-center justify-center w-full h-full pointer-events-none">
          <div className="pointer-events-auto relative">
            <RoleSelectionGateway onRoleSelect={handleRoleSelect} language={language} />
            {/* Login Link below role selection */}
            <div className="absolute -bottom-16 left-0 right-0 text-center">
              <button
                onClick={toggleAuthMode}
                className="text-white font-bold bg-black/30 px-6 py-2 rounded-full hover:bg-black/50 transition-all backdrop-blur-sm"
              >
                {language === "hi" ? "खाता है? लॉग इन करें" : "Have an account? Log In"}
              </button>
            </div>
          </div>
        </div>
      ) : (
        <div
          className="
          relative w-full max-w-[460px] rounded-[2rem]
          bg-white/40 
          backdrop-blur-xl 
          backdrop-saturate-150
          border border-white/50
          shadow-[0_20px_50px_rgba(0,0,0,0.2)]
          p-8 animate-slideUp
        "
        >
          {/* Back Button (Only logic, if signup) */}
          {!isLoginMode && (
            <button
              onClick={() => setStep("role")}
              className="absolute top-6 left-6 p-2 rounded-full hover:bg-white/30 transition-colors text-gray-700"
              title={language === "hi" ? "पीछे जाएं" : "Go Back"}
            >
              <ArrowLeft size={24} />
            </button>
          )}

          {/* Header */}
          <div className="mb-8 text-center mt-4">
            <h2 className="text-3xl font-bold text-gray-900 drop-shadow-sm">
              {isLoginMode
                ? (language === "hi" ? "स्वागत है!" : "Welcome Back!")
                : t.title}
              {" "}
              <span className="animate-bounce inline-block">
                {isLoginMode ? "👋" : t.emoji}
              </span>
            </h2>

            {!isLoginMode && (
              <p className="mt-2 text-sm font-medium text-gray-700 bg-white/30 py-1 px-3 rounded-full inline-block uppercase tracking-wider">
                {language === "hi" && selectedRole === "farmer" && "किसान"}
                {language === "hi" && selectedRole === "sarpanch" && "सरपंच"}
                {language === "hi" && selectedRole === "admin" && "एडमिन"}
                {language !== "hi" && selectedRole.toUpperCase()}
              </p>
            )}
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Name - Signup Only */}
            {!isLoginMode && (
              <div className="group">
                <label className="mb-1.5 ml-1 flex items-center gap-2 text-xl font-bold text-gray-800">
                  <User size={20} className="text-green-700" />
                  {t.name}
                </label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  placeholder={t.namePlaceholder}
                  className={`
                  w-full rounded-2xl border bg-white/50
                  px-4 py-3.5 text-base outline-none transition-all
                  placeholder:text-gray-500
                  ${errors.name ? "border-red-500 bg-red-50/30" : "border-white/60"}
                  focus:border-white focus:bg-white/80 focus:ring-4 focus:ring-green-500/10
                `}
                />
                {errors.name && (
                  <p className="mt-1.5 ml-1 text-xs font-bold text-red-600">
                    {errors.name}
                  </p>
                )}
              </div>
            )}

            {/* Phone - Signup Only */}
            {!isLoginMode && (
              <div>
                <label className="mb-1.5 ml-1 flex items-center gap-2 text-xl font-bold text-gray-800">
                  <Phone size={20} className="text-blue-700" />
                  {t.phone}
                </label>
                <input
                  type="tel"
                  name="phone"
                  value={formData.phone}
                  onChange={handleInputChange}
                  placeholder={t.phonePlaceholder}
                  maxLength={10}
                  className={`
                  w-full rounded-2xl border bg-white/50
                  px-4 py-3.5 text-base outline-none transition-all
                  placeholder:text-gray-500
                  ${errors.phone ? "border-red-500 bg-red-50/30" : "border-white/60"}
                  focus:border-white focus:bg-white/80 focus:ring-4 focus:ring-blue-500/10
                `}
                />
                {errors.phone && (
                  <p className="mt-1.5 ml-1 text-xs font-bold text-red-600">
                    {errors.phone}
                  </p>
                )}
              </div>
            )}

            {/* Email - Always */}
            {isFirebaseConfigured && (
              <div>
                <label className="mb-1.5 ml-1 flex items-center gap-2 text-xl font-bold text-gray-800">
                  <Mail size={20} className="text-purple-700" />
                  {language === "hi" ? "ईमेल" : "Email"}
                </label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  placeholder={language === "hi" ? "आपका ईमेल" : "Your email"}
                  className={`
                  w-full rounded-2xl border bg-white/50
                  px-4 py-3.5 text-base outline-none transition-all
                  placeholder:text-gray-500
                  ${errors.email ? "border-red-500 bg-red-50/30" : "border-white/60"}
                  focus:border-white focus:bg-white/80 focus:ring-4 focus:ring-purple-500/10
                `}
                />
                {errors.email && (
                  <p className="mt-1.5 ml-1 text-xs font-bold text-red-600">
                    {errors.email}
                  </p>
                )}
              </div>
            )}

            {/* Password - Always */}
            {isFirebaseConfigured && (
              <div>
                <label className="mb-1.5 ml-1 flex items-center gap-2 text-xl font-bold text-gray-800">
                  <Lock size={20} className="text-orange-700" />
                  {language === "hi" ? "पासवर्ड" : "Password"}
                </label>
                <input
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  placeholder={language === "hi" ? "पासवर्ड" : "Password"}
                  className={`
                  w-full rounded-2xl border bg-white/50
                  px-4 py-3.5 text-base outline-none transition-all
                  placeholder:text-gray-500
                  ${errors.password ? "border-red-500 bg-red-50/30" : "border-white/60"}
                  focus:border-white focus:bg-white/80 focus:ring-4 focus:ring-orange-500/10
                `}
                />
                {errors.password && (
                  <p className="mt-1.5 ml-1 text-xs font-bold text-red-600">
                    {errors.password}
                  </p>
                )}
              </div>
            )}

            {/* Submit Error */}
            {errors.submit && (
              <p className="text-center text-sm font-bold text-red-600 bg-red-50/50 rounded-xl p-3">
                {errors.submit}
              </p>
            )}

            {/* Submit */}
            <button
              type="submit"
              disabled={isLoading}
              className={`
              mt-4 w-full rounded-2xl
              bg-green-600/80 py-4
              text-lg font-bold text-white
              shadow-lg shadow-green-900/20
              transition-all duration-300
              hover:bg-green-600 hover:shadow-green-900/40 hover:-translate-y-0.5
              active:scale-[0.98]
              disabled:opacity-50 disabled:cursor-not-allowed
              flex items-center justify-center gap-2
            `}
            >
              {isLoading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent"></div>
                  {language === "hi" ? "प्रतीक्षा करें..." : "Please wait..."}
                </>
              ) : (
                isLoginMode ? (language === "hi" ? "लॉग इन करें" : "Log In") : t.submit
              )}
            </button>

            {/* Toggle Mode Button */}
            <div className="text-center pt-2">
              <button
                type="button"
                onClick={toggleAuthMode}
                className="text-gray-600 font-bold hover:text-green-700 transition-colors text-sm"
              >
                {isLoginMode
                  ? (language === "hi" ? "खाता नहीं है? साइन अप करें" : "Need an account? Sign Up")
                  : (language === "hi" ? "खाता है? लॉग इन करें" : "Have an account? Log In")
                }
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};

export default SignupPopup;
