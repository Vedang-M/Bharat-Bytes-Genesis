import { useState } from "react";
import { User, Phone } from "lucide-react";
import { saveUserData } from "../utils/authUtils";
import { getTranslations } from "../utils/languageUtils";

const SignupPopup = ({ onClose, onSignupComplete, language = "hi" }) => {
  const [formData, setFormData] = useState({
    name: "",
    phone: "",
  });
  const [errors, setErrors] = useState({});

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

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!validateForm()) return;

    const success = saveUserData({ ...formData, language });
    if (success) {
      onSignupComplete();
      onClose();
    } else {
      alert(t.alerts.saveFailed);
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
        <form onSubmit={handleSubmit} className="space-y-6">
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

          {/* Submit */}
          <button
            type="submit"
            className="
              mt-4 w-full rounded-2xl
              bg-green-600/80 py-4
              text-lg font-bold text-white
              shadow-lg shadow-green-900/20
              transition-all duration-300
              hover:bg-green-600 hover:shadow-green-900/40 hover:-translate-y-0.5
              active:scale-[0.98]
            "
          >
            {t.submit}
          </button>
        </form>
      </div>
    </div>
  );
};

export default SignupPopup;
