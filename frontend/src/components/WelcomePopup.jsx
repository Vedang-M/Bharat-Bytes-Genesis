import { useEffect } from 'react';

const WelcomePopup = ({ onClose }) => {
  useEffect(() => {
    // Auto-close after 1.5 seconds
    const timer = setTimeout(() => {
      onClose();
    }, 1500);

    return () => clearTimeout(timer);
  }, [onClose]);

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-[1000] animate-fadeIn font-hindi px-4">
      <div 
        className="
          relative overflow-hidden
          /* Glassmorphism Core */
          bg-white/20 
          backdrop-blur-2xl 
          backdrop-saturate-180
          border border-white/40
          /* Shadow & Depth */
          shadow-[0_25px_50px_-12px_rgba(0,0,0,0.25)] 
          rounded-[2.5rem] 
          text-center 
          animate-scaleIn 
          max-w-md w-full
          py-12 px-8
        "
      >
        {/* Decorative light flare inside the glass */}
        <div className="absolute -top-24 -left-24 w-48 h-48 bg-white/20 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-24 -right-24 w-48 h-48 bg-green-400/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative flex flex-col gap-6">
          <div className="space-y-2">
            <h1 className="text-5xl md:text-6xl font-extrabold text-white drop-shadow-md">
              नमस्ते 🙏
            </h1>
            <div className="h-1.5 w-16 bg-white/40 rounded-full mx-auto" />
          </div>
          
          <p className="text-xl md:text-2xl font-bold text-white/90 leading-tight drop-shadow-sm">
            खेती के लिए पानी का <br /> 
            <span className="text-white">सही हिसाब</span>
          </p>
        </div>
      </div>
    </div>
  );
};

export default WelcomePopup;