import { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Droplet, Sprout, FileText, User } from "lucide-react";
import { getLanguage } from "../utils/languageUtils";

const Navigation = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [language, setLanguage] = useState("hi");

  // Read language from localStorage
  useEffect(() => {
    const savedLanguage = getLanguage();
    if (savedLanguage) {
      setLanguage(savedLanguage);
    }
  }, []);

  // Determine active page from current route
  const getActivePage = () => {
    const path = location.pathname;
    if (path === "/water" || path === "/") return "water";
    if (path === "/crops") return "crops";
    if (path === "/advice") return "advice";
    if (path === "/profile") return "profile";
    return "water";
  };

  const activePage = getActivePage();

  const navItems = [
    {
      id: "water",
      icon: Droplet,
      labelHi: "पानी",
      labelEn: "Water",
      path: "/water",
    },
    {
      id: "crops",
      icon: Sprout,
      labelHi: "फसल",
      labelEn: "Crops",
      path: "/crops",
    },
    {
      id: "advice",
      icon: FileText,
      labelHi: "सलाह",
      labelEn: "Advice",
      path: "/advice",
    },
    {
      id: "profile",
      icon: User,
      labelHi: "प्रोफाइल",
      labelEn: "Profile",
      path: "/profile",
    },
  ];

  const handleNavClick = (path) => {
    navigate(path);
  };

  return (
    <>
      {/* Desktop Navigation - Top */}
      <nav className="hidden md:block fixed top-0 left-0 right-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="bg-white/30 backdrop-blur-2xl rounded-full border border-white/20 shadow-2xl px-8 py-3">
            <div className="flex items-center justify-between">
              {/* Logo/Brand */}
              <div className="flex items-center gap-2">
                <div className="bg-gradient-to-br from-[#2E7D32] to-[#43A047] p-2 rounded-full">
                  <Droplet size={24} className="text-white" fill="white" />
                </div>
                <span className="text-xl font-black text-white drop-shadow-md">
                  KisanSetu
                </span>
              </div>

              {/* Nav Items */}
              <div className="flex items-center gap-2">
                {navItems.map((item) => {
                  const Icon = item.icon;
                  const isActive = activePage === item.id;

                  return (
                    <button
                      key={item.id}
                      onClick={() => handleNavClick(item.path)}
                      className={`
                        flex items-center gap-2 px-6 py-2.5 rounded-full
                        transition-all duration-300
                        ${
                          isActive
                            ? "bg-white/40 text-white shadow-lg"
                            : "text-white/70 hover:bg-white/20 hover:text-white"
                        }
                      `}
                    >
                      <Icon size={20} strokeWidth={2.5} />
                      <span className="font-bold text-base">
                        {language === "hi" ? item.labelHi : item.labelEn}
                      </span>
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Mobile Navigation - Bottom */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 z-50 pb-safe">
        <div className="px-4 pb-4">
          <div className="bg-white/30 backdrop-blur-2xl rounded-[2rem] border border-white/20 shadow-2xl px-2 py-3">
            <div className="flex items-center justify-around">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = activePage === item.id;

                return (
                  <button
                    key={item.id}
                    onClick={() => handleNavClick(item.path)}
                    className={`
                      flex flex-col items-center gap-1.5 px-4 py-2 rounded-2xl
                      transition-all duration-300 min-w-[70px]
                      ${
                        isActive
                          ? "bg-white/40 shadow-lg scale-105"
                          : "hover:bg-white/20"
                      }
                    `}
                  >
                    <div
                      className={`
                      p-2 rounded-xl transition-all
                      ${
                        isActive
                          ? "bg-gradient-to-br from-[#2E7D32] to-[#43A047] text-white"
                          : "text-white/80"
                      }
                    `}
                    >
                      <Icon size={22} strokeWidth={2.5} />
                    </div>
                    <span
                      className={`
                      text-xs leading-none
                      ${isActive ? "text-white font-black" : "text-white/70 font-bold"}
                    `}
                    >
                      {language === "hi" ? item.labelHi : item.labelEn}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      </nav>
    </>
  );
};

export default Navigation;
