import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  User,
  Phone,
  Calendar,
  Edit2,
  Save,
  LogOut,
  X,
  Camera,
  Globe,
  ChevronRight,
} from "lucide-react";
import { getUserData, saveUserData, logoutUser } from "../utils/authUtils";
import {
  getTranslations,
  setLanguage,
  getLanguage,
} from "../utils/languageUtils";

const ProfilePage = () => {
  const navigate = useNavigate();
  const [userData, setUserData] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editedData, setEditedData] = useState({
    name: "",
    phone: "",
  });
  const [errors, setErrors] = useState({});
  const [currentLanguage, setCurrentLanguage] = useState("hi");

  // Read language from localStorage on mount
  useEffect(() => {
    const savedLanguage = getLanguage();
    if (savedLanguage) {
      setCurrentLanguage(savedLanguage);
    }
  }, []);

  const t = getTranslations(currentLanguage).profile || {
    title: currentLanguage === "hi" ? "मेरी प्रोफाइल" : "My Profile",
    name: currentLanguage === "hi" ? "नाम" : "Name",
    phone: currentLanguage === "hi" ? "फोन नंबर" : "Phone Number",
    registeredOn: currentLanguage === "hi" ? "पंजीकृत" : "Registered On",
    edit: currentLanguage === "hi" ? "संपादित करें" : "Edit Profile",
    save: currentLanguage === "hi" ? "सहेजें" : "Save Changes",
    cancel: currentLanguage === "hi" ? "रद्द करें" : "Cancel",
    logout: currentLanguage === "hi" ? "लॉग आउट" : "Logout",
    logoutConfirm:
      currentLanguage === "hi"
        ? "क्या आप वाकई लॉग आउट करना चाहते हैं?"
        : "Are you sure you want to logout?",
    saveSuccess:
      currentLanguage === "hi" ? "प्रोफाइल अपडेट हुई" : "Profile updated",
    errors: {
      nameRequired:
        currentLanguage === "hi" ? "नाम आवश्यक है" : "Name is required",
      phoneInvalid:
        currentLanguage === "hi" ? "10 अंक दर्ज करें" : "Enter 10 digits",
    },
  };

  useEffect(() => {
    const data = getUserData();
    if (data) {
      setUserData(data);
      setEditedData({
        name: data.name || "",
        phone: data.phone || "",
      });
    }
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setEditedData((prev) => ({ ...prev, [name]: value }));
    if (errors[name]) setErrors((prev) => ({ ...prev, [name]: "" }));
  };

  const handleSave = () => {
    // Basic validation logic
    if (!editedData.name.trim()) {
      setErrors({ name: t.errors.nameRequired });
      return;
    }
    const updatedData = { ...userData, ...editedData };
    if (saveUserData(updatedData)) {
      setUserData(updatedData);
      setIsEditing(false);
    }
  };

  const handleLanguageToggle = () => {
    const newLanguage = currentLanguage === "hi" ? "en" : "hi";
    setLanguage(newLanguage);
    setCurrentLanguage(newLanguage);
    window.location.reload();
  };

  if (!userData) return null;

  // --- REUSABLE STYLES ---
  const glassCardClass =
    "bg-gradient-to-b from-white/20 to-white/5 backdrop-blur-xl border border-white/10 shadow-[0_8px_32px_0_rgba(0,0,0,0.1)]";
  const glassInputClass =
    "bg-white/10 border border-white/10 focus:bg-white/20 focus:border-white/30 text-white placeholder-white/50 backdrop-blur-sm shadow-inner";

  // Vibrant buttons
  const logoutBtnClass =
    "bg-gradient-to-r from-red-500/90 to-red-600/90 hover:from-red-500 hover:to-red-600 text-white shadow-lg shadow-red-900/20 border border-red-400/30 backdrop-blur-md";
  const langBtnClass =
    "bg-gradient-to-r from-blue-500/90 to-indigo-600/90 hover:from-blue-500 hover:to-indigo-600 text-white shadow-lg shadow-blue-900/20 border border-blue-400/30 backdrop-blur-md";

  return (
    <div className="h-screen bg-[#FAFAF7] font-hindi overflow-hidden relative flex flex-col">
      {/* Fixed Background Layer */}
      <img
        src="/Hero-image-desktop.webp"
        alt=""
        className="absolute inset-0 w-full h-full object-cover hidden md:block"
      />
      <img
        src="/Hero-inmage-mobile.webp"
        alt=""
        className="absolute inset-0 w-full h-full object-cover block md:hidden"
      />
      {/* Consistent Dark Overlay */}
      <div className="absolute inset-0 bg-gradient-to-b from-[#422B06]/80 to-[#422B06]/50" />

      {/* Main Container */}
      <div className="relative z-10 max-w-md lg:max-w-5xl mx-auto px-5 pt-4 pb-36 md:pb-10 md:pt-24 flex flex-col flex-1 h-full w-full">
        {/* Profile Grid System */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start overflow-y-auto lg:overflow-visible pr-1 custom-scrollbar">
          {/* LEFT COLUMN: User Card */}
          <div className="lg:col-span-4 flex flex-col gap-5">
            <div
              className={`${glassCardClass} rounded-[2.5rem] p-8 flex flex-col items-center text-center relative overflow-hidden`}
            >
              {/* Profile Image with Glow */}
              <div className="relative group mb-6">
                <div className="absolute inset-0 bg-[#43A047] blur-2xl opacity-40 rounded-full scale-125 group-hover:scale-150 transition-transform duration-700"></div>
                <div className="relative bg-gradient-to-br from-[#2E7D32] to-[#43A047] p-1.5 rounded-full shadow-2xl ring-4 ring-white/10">
                  <div className="bg-[#422B06]/30 rounded-full p-6 border-2 border-white/20 backdrop-blur-sm">
                    <User size={64} className="text-white drop-shadow-lg" />
                  </div>
                </div>
                <button className="absolute bottom-1 right-1 bg-white p-2.5 rounded-full shadow-lg text-[#2E7D32] hover:scale-110 active:scale-95 transition-all cursor-pointer z-10">
                  <Camera size={18} strokeWidth={2.5} />
                </button>
              </div>

              <h1 className="text-3xl font-black text-white drop-shadow-md mb-2 tracking-tight">
                {userData.name}
              </h1>

              {!isEditing && (
                <button
                  onClick={() => setIsEditing(true)}
                  className="mt-8 w-full flex items-center justify-center gap-2 bg-white/20 hover:bg-white/30 px-6 py-3.5 rounded-2xl text-white font-bold transition-all border border-white/20 shadow-lg active:scale-95"
                >
                  <Edit2 size={18} /> {t.edit}
                </button>
              )}
            </div>

            {/* Desktop-only Action Buttons (Stacked) */}
            <div className="hidden lg:flex flex-col gap-4">
              <button
                onClick={handleLanguageToggle}
                className={`${langBtnClass} w-full flex items-center justify-between px-6 py-4 rounded-[1.5rem] transition-all group`}
              >
                <div className="flex items-center gap-3">
                  <Globe size={22} />
                  <span className="font-black text-lg">
                    {currentLanguage === "hi" ? "English" : "हिन्दी"}
                  </span>
                </div>
                <ChevronRight className="opacity-70 group-hover:translate-x-1 transition-transform" />
              </button>

              <button
                onClick={() => {
                  if (window.confirm(t.logoutConfirm)) {
                    logoutUser();
                    navigate("/");
                  }
                }}
                className={`${logoutBtnClass} w-full flex items-center justify-between px-6 py-4 rounded-[1.5rem] transition-all group`}
              >
                <div className="flex items-center gap-3">
                  <LogOut size={22} />
                  <span className="font-black text-lg">{t.logout}</span>
                </div>
                <ChevronRight className="opacity-70 group-hover:translate-x-1 transition-transform" />
              </button>
            </div>
          </div>

          {/* RIGHT COLUMN: Data Fields */}
          <div className="lg:col-span-8 space-y-4">
            <div className={`${glassCardClass} rounded-[2.5rem] p-6 md:p-10`}>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* Field: Name */}
                <div className="space-y-3">
                  <label className="text-xs font-black text-white/70 uppercase tracking-widest flex items-center gap-2 ml-1">
                    <User size={14} /> {t.name}
                  </label>
                  {isEditing ? (
                    <input
                      name="name"
                      value={editedData.name}
                      onChange={handleInputChange}
                      className={`w-full ${glassInputClass} rounded-2xl px-5 py-4 font-bold outline-none transition-all`}
                    />
                  ) : (
                    <div className="px-1 py-2 border-b border-white/10">
                      <p className="text-2xl font-black text-white drop-shadow-sm">
                        {userData.name}
                      </p>
                    </div>
                  )}
                </div>

                {/* Field: Phone */}
                <div className="space-y-3">
                  <label className="text-xs font-black text-white/70 uppercase tracking-widest flex items-center gap-2 ml-1">
                    <Phone size={14} /> {t.phone}
                  </label>
                  {isEditing ? (
                    <input
                      name="phone"
                      value={editedData.phone}
                      onChange={handleInputChange}
                      className={`w-full ${glassInputClass} rounded-2xl px-5 py-4 font-bold outline-none transition-all`}
                    />
                  ) : (
                    <div className="px-1 py-2 border-b border-white/10">
                      <p className="text-2xl font-black text-white drop-shadow-sm">
                        {userData.phone}
                      </p>
                    </div>
                  )}
                </div>

                {/* Field: Date */}
                <div className="space-y-3">
                  <label className="text-xs font-black text-white/70 uppercase tracking-widest flex items-center gap-2 ml-1">
                    <Calendar size={14} /> {t.registeredOn}
                  </label>
                  <div className="px-1 py-2 border-b border-white/10">
                    <p className="text-2xl font-black text-white/90 drop-shadow-sm">
                      {new Date(userData.registeredAt).toLocaleDateString(
                        currentLanguage === "hi" ? "hi-IN" : "en-IN",
                      )}
                    </p>
                  </div>
                </div>
              </div>

              {/* Edit Actions */}
              {isEditing && (
                <div className="flex flex-col sm:flex-row gap-4 mt-12 pt-6 border-t border-white/10">
                  <button
                    onClick={handleSave}
                    className="flex-1 bg-gradient-to-r from-[#2E7D32] to-[#43A047] text-white rounded-2xl py-4 font-black flex items-center justify-center gap-2 shadow-lg hover:shadow-[#2E7D32]/40 active:scale-95 transition-all border border-white/20"
                  >
                    <Save size={20} /> {t.save}
                  </button>
                  <button
                    onClick={() => setIsEditing(false)}
                    className="flex-1 bg-white/10 hover:bg-white/20 text-white rounded-2xl py-4 font-black border border-white/20 flex items-center justify-center gap-2 backdrop-blur-md transition-all"
                  >
                    <X size={20} /> {t.cancel}
                  </button>
                </div>
              )}
            </div>

            {/* Mobile-only Action Buttons */}
            <div className="lg:hidden flex flex-col gap-4 mt-2">
              <button
                onClick={handleLanguageToggle}
                className={`${langBtnClass} w-full flex items-center justify-center gap-3 rounded-[1.5rem] py-5 font-black active:scale-95 transition-all`}
              >
                <Globe size={20} />
                {currentLanguage === "hi" ? "English" : "हिन्दी"}
              </button>

              <button
                onClick={() => {
                  if (window.confirm(t.logoutConfirm)) {
                    logoutUser();
                    navigate("/");
                  }
                }}
                className={`${logoutBtnClass} w-full flex items-center justify-center gap-3 rounded-[1.5rem] py-5 font-black active:scale-95 transition-all`}
              >
                <LogOut size={20} /> {t.logout}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
