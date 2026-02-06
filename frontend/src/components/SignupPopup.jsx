import { useState } from "react";
import { User, Phone, Mail, Lock } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { getTranslations } from "../utils/languageUtils";

const SignupPopup = ({ onClose, onSignupComplete, language = "hi" }) => {
  const { signUp, isFirebaseConfigured } = useAuth();
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

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (errors[name]) setErrors((prev) => ({ ...prev, [name]: "" }));
  };

  const validateForm = () => {
    const newErrors = {};
    if (!formData.name.trim()) newErrors.name = t.errors.nameRequired;
    if (!formData.phone.trim()) {
      newErrors.phone = t.errors.phoneRequired;
    } else if (!/^\d{10}$/.test(formData.phone.replace(/\s/g, ""))) {
      newErrors.phone = t.errors.phoneInvalid;
    }

    // Email and password only required for Firebase mode
    if (isFirebaseConfigured) {
      if (!formData.email.trim()) {
        newErrors.email = language === "hi" ? "ईमेल आवश्यक है" : "Email is required";
      } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
        newErrors.email = language === "hi" ? "अमान्य ईमेल" : "Invalid email";
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
      const result = await signUp({
        name: formData.name,
        phone: formData.phone,
        email: formData.email || `${formData.phone}@waterwallet.local`,
        password: formData.password || formData.phone, // Use phone as password in demo mode
        role: "farmer",
        location: null, // Will be set from geolocation later
      });

      if (result.success) {
        onSignupComplete();
        onClose();
      } else {
        setErrors({ submit: result.error });
      }
    } catch (error) {
      console.error("Signup error:", error);
      setErrors({ submit: error.message || t.alerts?.saveFailed || "Signup failed" });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-[1000] flex items-center justify-center bg-black/40 font-hindi p-4">
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
        {/* Header */}
        <div className="mb-8 text-center">
          <h2 className="text-3xl font-bold text-gray-900 drop-shadow-sm">
            {t.title}{" "}
            <span className="animate-bounce inline-block">{t.emoji}</span>
          </h2>
          <p className="mt-2 text-sm font-medium text-gray-700 bg-white/30 py-1 px-3 rounded-full inline-block">
            {t.tagline}
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Name */}
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

          {/* Phone */}
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

          {/* Email - Only show in Firebase mode */}
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

          {/* Password - Only show in Firebase mode */}
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
                placeholder={language === "hi" ? "पासवर्ड बनाएं" : "Create password"}
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
                {language === "hi" ? "कृपया प्रतीक्षा करें..." : "Please wait..."}
              </>
            ) : (
              t.submit
            )}
          </button>
        </form>
      </div>
    </div>
  );
};

export default SignupPopup;
