import React from "react";
import { Trees, Landmark, Settings } from "lucide-react";

const RoleSelectionGateway = ({ onRoleSelect, language = "hi" }) => {
    const roles = [
        {
            id: "farmer",
            title: language === "hi" ? "किसान" : "Farmer",
            icon: <Trees size={48} className="text-green-600 mb-4" />,
            description:
                language === "hi"
                    ? "फसल सलाह और जल स्थिति प्राप्त करें"
                    : "Get crop advice and water status",
            color: "hover:border-green-500 hover:bg-green-50/50",
        },
        {
            id: "sarpanch",
            title: language === "hi" ? "सरपंच" : "Sarpanch",
            icon: <Landmark size={48} className="text-amber-600 mb-4" />,
            description:
                language === "hi"
                    ? "गांव के जल स्तर की निगरानी करें"
                    : "Monitor village water levels",
            color: "hover:border-amber-500 hover:bg-amber-50/50",
        },
        {
            id: "admin",
            title: language === "hi" ? "एडमिस" : "Admin",
            icon: <Settings size={48} className="text-gray-600 mb-4" />,
            description:
                language === "hi"
                    ? "सिस्टम सेटिंग्स प्रबंधित करें"
                    : "Manage system settings",
            color: "hover:border-gray-500 hover:bg-gray-50/50",
        },
    ];

    return (
        <div className="w-full max-w-4xl p-4 animate-fadeIn">
            <div className="text-center mb-8">
                <h2 className="text-3xl font-bold text-gray-900 drop-shadow-sm mb-2">
                    {language === "hi" ? "अपनी भूमिका चुनें" : "Select Your Role"}
                </h2>
                <p className="text-gray-600">
                    {language === "hi"
                        ? "आगे बढ़ने के लिए कृपया अपनी पहचान चुनें"
                        : "Please select your identity to proceed"}
                </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {roles.map((role) => (
                    <button
                        key={role.id}
                        onClick={() => onRoleSelect(role.id)}
                        className={`
              flex flex-col items-center text-center p-6 rounded-[2rem]
              bg-white/40 backdrop-blur-xl border-2 border-white/50
              shadow-[0_8px_30px_rgb(0,0,0,0.12)]
              transition-all duration-300 hover:scale-105 hover:-translate-y-1
              active:scale-95 cursor-pointer group
              ${role.color}
            `}
                    >
                        <div className="bg-white/60 p-4 rounded-full shadow-sm mb-4 group-hover:shadow-md transition-all">
                            {role.icon}
                        </div>
                        <h3 className="text-xl font-bold text-gray-800 mb-2">
                            {role.title}
                        </h3>
                        <p className="text-sm font-medium text-gray-600 leading-relaxed">
                            {role.description}
                        </p>
                    </button>
                ))}
            </div>
        </div>
    );
};

export default RoleSelectionGateway;
