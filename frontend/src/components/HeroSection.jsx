const HeroSection = () => {
  return (
    <div className="w-screen h-screen relative overflow-hidden">
      {/* Desktop Image */}
      <img
        src="/Hero-image-desktop.webp"
        alt="Hero Desktop"
        className="w-full h-full object-cover object-center hidden md:block"
      />
      
      {/* Mobile Image */}
      <img
        src="/Hero-inmage-mobile.webp"
        alt="Hero Mobile"
        className="w-full h-full object-cover object-center block md:hidden"
      />
    </div>
  );
};

export default HeroSection;
