import { Languages } from 'lucide-react';
import { setLanguage } from '../utils/languageUtils';

const LanguageSelectionPopup = ({ onLanguageSelect }) => {
  const handleLanguageSelection = (lang) => {
    setLanguage(lang);
    onLanguageSelect(lang);
  };

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-[1000] animate-fadeIn font-hindi px-4">
      <div 
        className="
          relative overflow-hidden
          bg-white/30 
          backdrop-blur-2xl 
          backdrop-saturate-180
          border border-white/40
          shadow-[0_25px_50px_-12px_rgba(0,0,0,0.25)] 
          rounded-[2.5rem] 
          text-center 
          animate-slideUp 
          max-w-md w-full
          py-12 px-8
        "
      >
        {/* Decorative elements */}
        <div className="absolute -top-24 -left-24 w-48 h-48 bg-white/20 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-24 -right-24 w-48 h-48 bg-blue-400/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative space-y-8">
          {/* Header */}
          <div className="space-y-3">
            <div className="flex justify-center">
              <div className="bg-white/40 p-4 rounded-2xl">
                <Languages size={40} className="text-gray-800" />
              </div>
            </div>
            <h2 className="text-3xl md:text-4xl font-extrabold text-gray-900 drop-shadow-sm">
              Choose Your Language
            </h2>
            <p className="text-base font-semibold text-gray-700">
              अपनी भाषा चुनें
            </p>
          </div>

          {/* Language Options */}
          <div className="space-y-4">
            {/* Hindi Button */}
            <button
              onClick={() => handleLanguageSelection('hi')}
              className="
                w-full rounded-2xl
                bg-white/50 border-2 border-white/60
                px-6 py-5
                text-left
                transition-all duration-300
                hover:bg-white/70 hover:border-white/80 hover:scale-[1.02]
                active:scale-[0.98]
                group
              "
            >
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <div className="text-2xl font-bold text-gray-900">
                    हिन्दी
                  </div>
                  <div className="text-sm font-medium text-gray-600">
                    Hindi
                  </div>
                </div>
                <div className="text-4xl group-hover:scale-110 transition-transform">
                  🇮🇳
                </div>
              </div>
            </button>

            {/* English Button */}
            <button
              onClick={() => handleLanguageSelection('en')}
              className="
                w-full rounded-2xl
                bg-white/50 border-2 border-white/60
                px-6 py-5
                text-left
                transition-all duration-300
                hover:bg-white/70 hover:border-white/80 hover:scale-[1.02]
                active:scale-[0.98]
                group
              "
            >
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <div className="text-2xl font-bold text-gray-900">
                    English
                  </div>
                  <div className="text-sm font-medium text-gray-600">
                    अंग्रेज़ी
                  </div>
                </div>
                <div className="text-4xl group-hover:scale-110 transition-transform">
                  🌐
                </div>
              </div>
            </button>
          </div>

          {/* Helper Text */}
          <p className="text-xs font-medium text-gray-600 bg-white/30 py-2 px-4 rounded-full">
            You can change this later in settings
          </p>
        </div>
      </div>
    </div>
  );
};

export default LanguageSelectionPopup;
