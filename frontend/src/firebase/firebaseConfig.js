/**
 * Firebase Configuration
 * Initializes Firebase SDK for authentication and Firestore.
 * 
 * SETUP INSTRUCTIONS:
 * 1. Go to https://console.firebase.google.com
 * 2. Create a new project or select existing one
 * 3. Go to Project Settings > General > Your apps > Web app
 * 4. Copy the config values to .env.local file
 */

import { initializeApp } from "firebase/app";
import { getAuth, connectAuthEmulator } from "firebase/auth";
import { getFirestore, connectFirestoreEmulator } from "firebase/firestore";

// Firebase configuration from environment variables
const firebaseConfig = {
    apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
    authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
    projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
    storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
    messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
    appId: import.meta.env.VITE_FIREBASE_APP_ID,
};

// Check if Firebase is configured
const isFirebaseConfigured = () => {
    return Boolean(firebaseConfig.apiKey && firebaseConfig.projectId);
};

// Initialize Firebase
let app = null;
let auth = null;
let db = null;

try {
    if (isFirebaseConfigured()) {
        app = initializeApp(firebaseConfig);
        auth = getAuth(app);
        db = getFirestore(app);

        // Connect to emulators in development (optional)
        if (import.meta.env.DEV && import.meta.env.VITE_USE_FIREBASE_EMULATOR === "true") {
            connectAuthEmulator(auth, "http://localhost:9099");
            connectFirestoreEmulator(db, "localhost", 8080);
            console.log("Connected to Firebase emulators");
        }

        console.log("Firebase initialized successfully");
    } else {
        console.warn("Firebase not configured. Running in demo mode.");
        console.warn("To configure Firebase, create a .env.local file with:");
        console.warn("VITE_FIREBASE_API_KEY=your-api-key");
        console.warn("VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com");
        console.warn("VITE_FIREBASE_PROJECT_ID=your-project-id");
    }
} catch (error) {
    console.error("Firebase initialization error:", error);
}

// Export instances (may be null if not configured)
export { app, auth, db };
export const firebaseConfigured = isFirebaseConfigured();

// Export helper to get ID token
export async function getIdToken() {
    if (!auth?.currentUser) {
        return null;
    }
    try {
        return await auth.currentUser.getIdToken();
    } catch (error) {
        console.error("Error getting ID token:", error);
        return null;
    }
}
