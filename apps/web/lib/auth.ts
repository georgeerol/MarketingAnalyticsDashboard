/**
 * Authentication with Zustand store
 */

import { create } from "zustand";
import { persist } from "zustand/middleware";

/**
 * User data from the API
 */
export interface User {
  id: number;
  email: string;
  full_name: string;
  company?: string;
  role: string;
  is_active: boolean;
  created_at: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  full_name: string;
  company?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  isHydrated: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;
  setHydrated: () => void;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const API_V1_PREFIX = "/api/v1";

/**
 * Auth hook with Zustand
 *
 * Handles login, logout, registration. Persists to localStorage.
 */
export const useAuth = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isLoading: false,
      isHydrated: false,

      login: async (credentials: LoginCredentials) => {
        set({ isLoading: true });
        try {
          const formData = new FormData();
          formData.append("username", credentials.email);
          formData.append("password", credentials.password);

          const response = await fetch(
            `${API_BASE_URL}${API_V1_PREFIX}/auth/login`,
            {
              method: "POST",
              body: formData,
            },
          );

          if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || "Login failed");
          }

          const data: AuthResponse = await response.json();
          set({
            user: data.user,
            token: data.access_token,
            isLoading: false,
          });
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },

      register: async (data: RegisterData) => {
        set({ isLoading: true });
        try {
          const response = await fetch(
            `${API_BASE_URL}${API_V1_PREFIX}/auth/register`,
            {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
              },
              body: JSON.stringify(data),
            },
          );

          if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || "Registration failed");
          }

          const authData: AuthResponse = await response.json();
          set({
            user: authData.user,
            token: authData.access_token,
            isLoading: false,
          });
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },

      logout: () => {
        set({ user: null, token: null });
      },

      checkAuth: async () => {
        const { token } = get();
        if (!token) return;

        try {
          const response = await fetch(
            `${API_BASE_URL}${API_V1_PREFIX}/auth/me`,
            {
              headers: {
                Authorization: `Bearer ${token}`,
              },
            },
          );

          if (!response.ok) {
            set({ user: null, token: null });
            return;
          }

          const user: User = await response.json();
          set({ user });
        } catch (error) {
          set({ user: null, token: null });
        }
      },

      setHydrated: () => {
        set({ isHydrated: true });
      },
    }),
    {
      name: "auth-storage",
      partialize: (state) => ({
        user: state.user,
        token: state.token,
      }),
      onRehydrateStorage: () => (state) => {
        state?.setHydrated();
      },
    },
  ),
);
