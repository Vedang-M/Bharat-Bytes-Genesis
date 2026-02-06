import { useState } from "react";
import { X, User, Phone, MapPin, MapPinned } from "lucide-react";
import { saveUserData } from "../utils/authUtils";
import {
  getUserLocation,
  formatLocation,
  getSavedLocation,
} from "../utils/locationUtils";
import { getTranslations } from "../utils/languageUtils";

const SignupPopup = ({ onClose, onSignupComplete, language = "hi" }) => {
  const [formData, setFormData] = useState({
    name: "",
    phone: "",
    location: "",
  });
  const [isLoadingLocation, setIsLoadingLocation] = useState(false);
  const [errors, setErrors] = useState({});

  // Get translations based on selected language
  const t = getTranslations(language).signup;

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (errors[name]) setErrors((prev) => ({ ...prev, [name]: "" }));
  };

  const handleGetLocation = async () => {
    setIsLoadingLocation(true);
    try {
      // Check if we have saved location first
      let locationData = getSavedLocation();

      // If no saved location or user wants to refresh, fetch new location
      if (!locationData) {
        locationData = await getUserLocation();
      }

      // Format location for display (city, state)
      const formattedLocation = formatLocation(locationData, "short");
      setFormData((prev) => ({ ...prev, location: formattedLocation }));
      setErrors((prev) => ({ ...prev, location: "" }));
    } catch (error) {
      alert(error.message || "Unable to get location. Please enter manually.");
    } finally {
      setIsLoadingLocation(false);
    }
  };

  const validateForm = () => {
    const newErrors = {};
    if (!formData.name.trim()) newErrors.name = t.errors.nameRequired;
    if (!formData.phone.trim()) {
      newErrors.phone = t.errors.phoneRequired;
    } else if (!/^\d{10}$/.test(formData.phone.replace(/\s/g, ""))) {
      newErrors.phone = t.errors.phoneInvalid;
    }
    if (!formData.location.trim())
      newErrors.location = t.errors.locationRequired;

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

          {/* Location */}
          <div>
            <label className="mb-1.5 ml-1 flex items-center gap-2 text-xl font-bold text-gray-800">
              <MapPin size={20} className="text-orange-800" />
              {t.location}
            </label>

            <div className="flex flex-col gap-3 sm:flex-row">
              <input
                type="text"
                name="location"
                value={formData.location}
                onChange={handleInputChange}
                placeholder={t.locationPlaceholder}
                className={`
                  flex-1 rounded-2xl border bg-white/50
                  px-4 py-3.5 text-base outline-none transition-all
                  placeholder:text-gray-500
                  ${errors.location ? "border-red-500 bg-red-50/30" : "border-white/60"}
                  focus:border-white focus:bg-white/80 focus:ring-4 focus:ring-orange-500/10
                `}
              />

              <button
                type="button"
                onClick={handleGetLocation}
                disabled={isLoadingLocation}
                className="
                  flex items-center justify-center gap-2
                  rounded-2xl border border-white/40
                  bg-white/30 px-5 py-3.5
                  text-sm font-bold text-orange-900
                  transition-all hover:bg-white/60 active:scale-95
                  disabled:opacity-50
                "
              >
                <MapPinned size={18} />
                {t.locationButton}
                {isLoadingLocation && (
                  <span className="h-4 w-4 animate-spin rounded-full border-2 border-orange-800 border-t-transparent" />
                )}
              </button>
            </div>

            {errors.location && (
              <p className="mt-1.5 ml-1 text-xs font-bold text-red-600">
                {errors.location}
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
