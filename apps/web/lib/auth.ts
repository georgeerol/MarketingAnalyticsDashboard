/**
 * @fileoverview Authentication Store and Types
 * 
 * Provides authentication state management using Zustand with persistence.
 * Handles user login, registration, logout, and token management for the MMM Dashboard.
 * 
 * @author MMM Dashboard Team
 * @version 1.0.0
 */

import { create } from 'zustand'
import { persist } from 'zustand/middleware'

/**
 * User data structure returned from the authentication API
 * @interface User
 */
export interface User {
  /** Unique user identifier */
  id: number
  /** User's email address (used for login) */
  email: string
  /** User's full display name */
  full_name: string
  /** Optional company/organization name */
  company?: string
  /** User role (e.g., 'admin', 'user', 'manager') */
  role: string
  /** Whether the user account is active */
  is_active: boolean
  /** Account creation timestamp */
  created_at: string
}

/**
 * Login credentials structure
 * @interface LoginCredentials
 */
export interface LoginCredentials {
  /** User's email address */
  email: string
  /** User's password */
  password: string
}

/**
 * Registration data structure
 * @interface RegisterData
 */
export interface RegisterData {
  /** User's email address */
  email: string
  /** User's password */
  password: string
  /** User's full name */
  full_name: string
  /** Optional company name */
  company?: string
}

/**
 * Authentication response from the API
 * @interface AuthResponse
 */
export interface AuthResponse {
  /** JWT access token */
  access_token: string
  /** Token type (typically 'bearer') */
  token_type: string
  /** User data */
  user: User
}

/**
 * Authentication store state and actions
 * @interface AuthState
 */
interface AuthState {
  /** Currently authenticated user (null if not logged in) */
  user: User | null
  /** JWT access token (null if not logged in) */
  token: string | null
  /** Loading state for auth operations */
  isLoading: boolean
  /** Login function */
  login: (credentials: LoginCredentials) => Promise<void>
  /** Registration function */
  register: (data: RegisterData) => Promise<void>
  /** Logout function */
  logout: () => void
  /** Check current authentication status */
  checkAuth: () => Promise<void>
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const API_V1_PREFIX = '/api/v1'

/**
 * Authentication Hook
 * 
 * Zustand store hook that provides authentication state and actions for the MMM Dashboard.
 * Includes automatic persistence of user data and tokens to localStorage, and handles
 * all authentication operations including login, registration, logout, and token validation.
 * 
 * Features:
 * - Persistent authentication state across browser sessions
 * - Automatic token validation and refresh
 * - Loading states for all auth operations
 * - Error handling for authentication failures
 * - Integration with FastAPI backend authentication
 * 
 * @returns {AuthState} Authentication state and action functions
 * 
 * @example
 * ```tsx
 * function LoginComponent() {
 *   const { login, user, token, isLoading } = useAuth()
 *   
 *   const handleLogin = async () => {
 *     try {
 *       await login({ email: 'user@example.com', password: 'password' })
 *       // User is now logged in, redirect to dashboard
 *     } catch (error) {
 *       // Handle login error
 *     }
 *   }
 *   
 *   if (user) {
 *     return <div>Welcome, {user.full_name}!</div>
 *   }
 *   
 *   return <LoginForm onSubmit={handleLogin} loading={isLoading} />
 * }
 * ```
 * 
 * @see {@link User} for user data structure
 * @see {@link LoginCredentials} for login parameters
 * @see {@link RegisterData} for registration parameters
 */
export const useAuth = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isLoading: false,

      login: async (credentials: LoginCredentials) => {
        set({ isLoading: true })
        try {
          const formData = new FormData()
          formData.append('username', credentials.email)
          formData.append('password', credentials.password)

          const response = await fetch(`${API_BASE_URL}${API_V1_PREFIX}/auth/login`, {
            method: 'POST',
            body: formData,
          })

          if (!response.ok) {
            const error = await response.json()
            throw new Error(error.detail || 'Login failed')
          }

          const data: AuthResponse = await response.json()
          set({ 
            user: data.user, 
            token: data.access_token, 
            isLoading: false 
          })
        } catch (error) {
          set({ isLoading: false })
          throw error
        }
      },

      register: async (data: RegisterData) => {
        set({ isLoading: true })
        try {
          const response = await fetch(`${API_BASE_URL}${API_V1_PREFIX}/auth/register`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
          })

          if (!response.ok) {
            const error = await response.json()
            throw new Error(error.detail || 'Registration failed')
          }

          const authData: AuthResponse = await response.json()
          set({ 
            user: authData.user, 
            token: authData.access_token, 
            isLoading: false 
          })
        } catch (error) {
          set({ isLoading: false })
          throw error
        }
      },

      logout: () => {
        set({ user: null, token: null })
      },

      checkAuth: async () => {
        const { token } = get()
        if (!token) return

        try {
          const response = await fetch(`${API_BASE_URL}${API_V1_PREFIX}/auth/me`, {
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          })

          if (!response.ok) {
            set({ user: null, token: null })
            return
          }

          const user: User = await response.json()
          set({ user })
        } catch (error) {
          set({ user: null, token: null })
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ 
        user: state.user, 
        token: state.token 
      }),
    }
  )
)
