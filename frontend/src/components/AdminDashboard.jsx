import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { toast } from "react-toastify";
import { Users, Shield, TrendingUp, AlertTriangle, LogOut } from "lucide-react";

const AdminDashboard = () => {
    const { userProfile, getIdToken, logout } = useAuth();
    const navigate = useNavigate();
    const [users, setUsers] = useState([]);
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            const token = await getIdToken();
            if (!token) return;

            const headers = { Authorization: `Bearer ${token}` };

            // Fetch users
            const usersRes = await fetch("http://localhost:8000/api/admin/users?limit=50", { headers });
            const usersData = await usersRes.json();

            // Fetch stats
            const statsRes = await fetch("http://localhost:8000/api/admin/stats", { headers });
            const statsData = await statsRes.json();

            if (usersRes.ok) setUsers(usersData.users);
            if (statsRes.ok) setStats(statsData);

        } catch (error) {
            console.error("Error fetching admin data:", error);
            toast.error("Failed to load dashboard data");
        } finally {
            setLoading(false);
        }
    };

    const assignRole = async (uid, newRole) => {
        if (!window.confirm(`Are you sure you want to promote this user to ${newRole}?`)) return;

        try {
            const token = await getIdToken();
            const res = await fetch("http://localhost:8000/api/auth/assign-role", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`,
                },
                body: JSON.stringify({ uid, role: newRole }),
            });

            const data = await res.json();
            if (res.ok) {
                toast.success(`Role updated to ${newRole}`);
                fetchData(); // Refresh list
            } else {
                toast.error(data.detail || "Failed to update role");
            }
        } catch (error) {
            console.error("Error assigning role:", error);
            toast.error("An error occurred");
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-[#FDF8F3] pt-24 px-6 flex justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-4 border-[#8B5E3C] border-t-transparent"></div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-[#FDF8F3] pb-24 pt-24">
            <div className="max-w-7xl mx-auto px-6">
                <div className="mb-8 flex justify-between items-center">
                    <div>
                        <h1 className="text-3xl font-black text-[#422B06] mb-2">Admin Dashboard</h1>
                        <p className="text-[#8B5E3C]">System Overview & User Management</p>
                    </div>
                    <button
                        onClick={async () => {
                            try {
                                await logout();
                            } catch (err) {
                                toast.error("Logout failed");
                            }
                        }}
                        className="flex items-center gap-2 px-4 py-2 bg-red-100 hover:bg-red-200 text-red-800 rounded-xl font-bold transition-colors"
                    >
                        <LogOut size={18} />
                        Logout
                    </button>
                </div>

                {/* Stats Grid */}
                {stats && (
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-10">
                        <div className="bg-white/80 p-6 rounded-3xl border border-[#E6D5BC] shadow-sm">
                            <div className="flex items-center gap-3 mb-2">
                                <div className="bg-blue-100 p-2 rounded-xl text-blue-600"><Users size={20} /></div>
                                <span className="text-sm font-bold text-gray-500">Total Users</span>
                            </div>
                            <p className="text-3xl font-black text-gray-800">{stats.users.total}</p>
                        </div>
                        <div className="bg-white/80 p-6 rounded-3xl border border-[#E6D5BC] shadow-sm">
                            <div className="flex items-center gap-3 mb-2">
                                <div className="bg-green-100 p-2 rounded-xl text-green-600"><Users size={20} /></div>
                                <span className="text-sm font-bold text-gray-500">Farmers</span>
                            </div>
                            <p className="text-3xl font-black text-gray-800">{stats.users.farmers}</p>
                        </div>
                        <div className="bg-white/80 p-6 rounded-3xl border border-[#E6D5BC] shadow-sm">
                            <div className="flex items-center gap-3 mb-2">
                                <div className="bg-orange-100 p-2 rounded-xl text-orange-600"><Shield size={20} /></div>
                                <span className="text-sm font-bold text-gray-500">Sarpanch</span>
                            </div>
                            <p className="text-3xl font-black text-gray-800">{stats.users.sarpanch}</p>
                        </div>
                        <div className="bg-white/80 p-6 rounded-3xl border border-[#E6D5BC] shadow-sm">
                            <div className="flex items-center gap-3 mb-2">
                                <div className="bg-red-100 p-2 rounded-xl text-red-600"><AlertTriangle size={20} /></div>
                                <span className="text-sm font-bold text-gray-500">Active Alerts</span>
                            </div>
                            <p className="text-3xl font-black text-gray-800">{stats.system.active_alerts}</p>
                        </div>
                    </div>
                )}

                {/* Users Table */}
                <div className="bg-white rounded-3xl border border-[#E6D5BC] shadow-md overflow-hidden">
                    <div className="p-6 border-b border-[#E6D5BC] bg-[#FCF8F3]">
                        <h2 className="text-xl font-bold text-[#422B06]">Registered Users</h2>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead className="bg-[#FAF4EB]">
                                <tr>
                                    <th className="px-6 py-4 text-left text-sm font-bold text-[#8B5E3C]">User</th>
                                    <th className="px-6 py-4 text-left text-sm font-bold text-[#8B5E3C]">Role</th>
                                    <th className="px-6 py-4 text-left text-sm font-bold text-[#8B5E3C]">Location</th>
                                    <th className="px-6 py-4 text-left text-sm font-bold text-[#8B5E3C]">Joined</th>
                                    <th className="px-6 py-4 text-right text-sm font-bold text-[#8B5E3C]">Actions</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-[#E6D5BC]">
                                {users.map((user) => (
                                    <tr key={user.uid} className="hover:bg-[#FAF4EB]/50 transition-colors">
                                        <td className="px-6 py-4">
                                            <div>
                                                <p className="font-bold text-[#422B06]">{user.name || "Unknown"}</p>
                                                <p className="text-xs text-gray-500">{user.email}</p>
                                                <p className="text-xs text-gray-400 font-mono">{user.uid.substring(0, 8)}...</p>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4">
                                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold
                        ${user.role === 'admin' ? 'bg-red-100 text-red-800' :
                                                    user.role === 'sarpanch' ? 'bg-orange-100 text-orange-800' :
                                                        'bg-green-100 text-green-800'}`}>
                                                {user.role}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 text-sm text-gray-600">
                                            {user.location?.district ? `${user.location.district}, ${user.location.state}` : "Unknown"}
                                        </td>
                                        <td className="px-6 py-4 text-sm text-gray-500">
                                            {new Date(user.createdAt).toLocaleDateString()}
                                        </td>
                                        <td className="px-6 py-4 text-right">
                                            <div className="flex justify-end gap-2">
                                                {user.role === 'farmer' && (
                                                    <button
                                                        onClick={() => assignRole(user.uid, "sarpanch")}
                                                        className="bg-orange-100 hover:bg-orange-200 text-orange-700 px-3 py-1 rounded-lg text-xs font-bold transition-colors"
                                                    >
                                                        Promote to Sarpanch
                                                    </button>
                                                )}
                                                {user.role !== 'admin' && (
                                                    <button
                                                        onClick={() => assignRole(user.uid, "admin")}
                                                        className="bg-red-100 hover:bg-red-200 text-red-700 px-3 py-1 rounded-lg text-xs font-bold transition-colors"
                                                    >
                                                        Make Admin
                                                    </button>
                                                )}
                                                {user.role !== 'farmer' && (
                                                    <button
                                                        onClick={() => assignRole(user.uid, "farmer")}
                                                        className="bg-gray-100 hover:bg-gray-200 text-gray-600 px-3 py-1 rounded-lg text-xs font-bold transition-colors"
                                                    >
                                                        Demote to Farmer
                                                    </button>
                                                )}
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AdminDashboard;
