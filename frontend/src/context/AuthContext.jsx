/**
 * Authentication Context
 * Provides global authentication state and Firebase auth functions.
 */

import { createContext, useContext, useState, useEffect } from "react";
import {
    createUserWithEmailAndPassword,
    signInWithEmailAndPassword,
    signOut,
    onAuthStateChanged,
    updateProfile,
} from "firebase/auth";
import { doc, setDoc, getDoc, updateDoc, serverTimestamp } from "firebase/firestore";
import { auth, db, firebaseConfigured, getIdToken } from "../firebase/firebaseConfig";

// Create context
const AuthContext = createContext(null);

// User roles
export const ROLES = {
    FARMER: "farmer",
    SARPANCH: "sarpanch",
    ADMIN: "admin",
};

/**
 * AuthProvider component
 * Wrap your app with this to provide auth state to all components.
 */
export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [userProfile, setUserProfile] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // Backend API URL
    const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

    // Listen for auth state changes
    useEffect(() => {
        if (!firebaseConfigured || !auth) {
            // Demo mode - check localStorage
            const storedUser = localStorage.getItem("genesis_user_data");
            if (storedUser) {
                try {
                    const userData = JSON.parse(storedUser);
                    setUser({ uid: "demo-user", email: null });
                    setUserProfile(userData);
                } catch (e) {
                    console.error("Error parsing stored user:", e);
                }
            }
            setLoading(false);
            return;
        }

        const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
            if (firebaseUser) {
                // If user is already loaded and matches (e.g. token refresh), don't reload profile unnecessarily
                if (user?.uid === firebaseUser.uid && userProfile) {
                    setUser(firebaseUser); // Update auth object (could have fresher token)
                    return;
                }

                setLoading(true);
                setUser(firebaseUser);
                // Fetch user profile from Firestore (with fallback to Firebase Auth data)
                await fetchUserProfile(firebaseUser.uid, firebaseUser);
            } else {
                setUser(null);
                setUserProfile(null);
            }
            setLoading(false);
        });

        return () => unsubscribe();
    }, []);

    // Fetch user profile from Firestore
    const fetchUserProfile = async (uid, firebaseUser = null) => {
        try {
            if (db) {
                const userDoc = await getDoc(doc(db, "users", uid));
                if (userDoc.exists()) {
                    setUserProfile({ uid, ...userDoc.data() });
                    return;
                }
            }
        } catch (error) {
            console.error("Error fetching user profile:", error);
        }

        // Fallback: Create basic profile from Firebase Auth or localStorage
        // IMPORTANT: Read role from localStorage first to preserve sarpanch/admin roles
        let storedRole = "farmer"; // Default fallback
        try {
            const storedUser = localStorage.getItem("genesis_user_data");
            if (storedUser) {
                const parsed = JSON.parse(storedUser);
                if (parsed.role) {
                    storedRole = parsed.role; // Use stored role if available
                }
            }
        } catch (e) {
            console.error("Error reading stored role:", e);
        }

        let fallbackProfile = { uid, role: storedRole };

        if (firebaseUser) {
            fallbackProfile.name = firebaseUser.displayName || firebaseUser.email?.split("@")[0] || "User";
            fallbackProfile.email = firebaseUser.email;
            fallbackProfile.createdAt = firebaseUser.metadata?.creationTime || new Date().toISOString();
        }

        // Merge with full localStorage data for other fields
        try {
            const storedUser = localStorage.getItem("genesis_user_data");
            if (storedUser) {
                const parsed = JSON.parse(storedUser);
                // Merge but keep the role we already determined
                fallbackProfile = { ...fallbackProfile, ...parsed, role: fallbackProfile.role };
            }
        } catch (e) {
            console.error("Error reading stored user:", e);
        }

        setUserProfile(fallbackProfile);
    };

    // Sign up with email and password
    const signUp = async ({ name, phone, email, password, role = "farmer", location = null }) => {
        setError(null);

        try {
            // Demo mode - use localStorage
            if (!firebaseConfigured || !auth) {
                const userData = {
                    name,
                    phone,
                    email,
                    role,
                    location,
                    registeredAt: new Date().toISOString(),
                };
                localStorage.setItem("genesis_user_data", JSON.stringify(userData));
                setUser({ uid: "demo-user", email });
                setUserProfile(userData);
                return { success: true, user: userData };
            }

            // Create Firebase auth user
            const userCredential = await createUserWithEmailAndPassword(auth, email, password);
            const firebaseUser = userCredential.user;

            // Update display name
            await updateProfile(firebaseUser, { displayName: name });

            // Create user document in Firestore
            const userData = {
                name,
                phone,
                email,
                role,
                location: location || {},
                farmIds: [],
                createdAt: serverTimestamp(),
                lastLogin: serverTimestamp(),
            };

            await setDoc(doc(db, "users", firebaseUser.uid), userData);

            // Also register with backend
            try {
                const token = await firebaseUser.getIdToken();
                await fetch(`${API_URL}/api/auth/register`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: `Bearer ${token}`,
                    },
                    body: JSON.stringify({
                        name,
                        phone,
                        email,
                        role,
                        location,
                        firebase_uid: firebaseUser.uid,
                    }),
                });
            } catch (backendError) {
                console.warn("Backend registration failed:", backendError);
                // Continue anyway - Firestore has the data
            }

            setUserProfile({ uid: firebaseUser.uid, ...userData });
            return { success: true, user: firebaseUser };
        } catch (error) {
            console.error("Sign up error:", error);
            setError(error.message);
            return { success: false, error: error.message };
        }
    };

    // Sign in with email and password
    const signIn = async (email, password) => {
        setError(null);

        try {
            // Demo mode
            if (!firebaseConfigured || !auth) {
                const storedUser = localStorage.getItem("genesis_user_data");
                if (storedUser) {
                    const userData = JSON.parse(storedUser);
                    setUser({ uid: "demo-user", email });
                    setUserProfile(userData);
                    return { success: true };
                }
                return { success: false, error: "No user found. Please sign up first." };
            }

            const userCredential = await signInWithEmailAndPassword(auth, email, password);

            // Update last login (fire and forget)
            updateDoc(doc(db, "users", userCredential.user.uid), {
                lastLogin: serverTimestamp(),
            }).catch(err => console.error("Error updating last login:", err));

            // Don't fetch profile here - onAuthStateChanged will handle it
            // This prevents double fetching and race conditions

            return { success: true, user: userCredential.user };
        } catch (error) {
            console.error("Sign in error:", error);
            setError(error.message);
            return { success: false, error: error.message };
        }
    };

    // Sign out
    const logout = async () => {
        try {
            if (firebaseConfigured && auth) {
                await signOut(auth);
            }
            localStorage.removeItem("genesis_user_data");
            setUser(null);
            setUserProfile(null);
        } catch (error) {
            console.error("Logout error:", error);
        }
    };

    // Update user profile
    const updateUserProfile = async (updates) => {
        if (!user) return { success: false, error: "Not authenticated" };

        try {
            // Demo mode
            if (!firebaseConfigured || !db) {
                const storedUser = localStorage.getItem("genesis_user_data");
                if (storedUser) {
                    const userData = { ...JSON.parse(storedUser), ...updates };
                    localStorage.setItem("genesis_user_data", JSON.stringify(userData));
                    setUserProfile(userData);
                    return { success: true };
                }
                return { success: false, error: "No user data found" };
            }

            await updateDoc(doc(db, "users", user.uid), updates);
            setUserProfile((prev) => ({ ...prev, ...updates }));
            return { success: true };
        } catch (error) {
            console.error("Update profile error:", error);
            return { success: false, error: error.message };
        }
    };

    // Check if user has a specific role or higher
    const hasRole = (requiredRole) => {
        if (!userProfile?.role) return false;

        const roleHierarchy = { farmer: 0, sarpanch: 1, admin: 2 };
        const userLevel = roleHierarchy[userProfile.role] || 0;
        const requiredLevel = roleHierarchy[requiredRole] || 0;

        return userLevel >= requiredLevel;
    };

    // Get auth token for API calls
    const getAuthToken = async () => {
        return await getIdToken();
    };

    // Refresh user profile (for manual refresh after updates)
    const refreshUserProfile = async () => {
        if (user?.uid && user.uid !== "demo-user") {
            await fetchUserProfile(user.uid);
        } else {
            // Demo mode - re-read from localStorage
            const storedUser = localStorage.getItem("genesis_user_data");
            if (storedUser) {
                setUserProfile(JSON.parse(storedUser));
            }
        }
    };

    const value = {
        user,
        currentUser: user, // Alias for compatibility
        userProfile,
        loading,
        error,
        isAuthenticated: !!user,
        isFirebaseConfigured: firebaseConfigured,
        signUp,
        signIn,
        logout,
        updateUserProfile,
        refreshUserProfile,
        hasRole,
        getAuthToken,
        ROLES,
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

/**
 * Hook to use auth context
 */
export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error("useAuth must be used within an AuthProvider");
    }
    return context;
}

export default AuthContext;
