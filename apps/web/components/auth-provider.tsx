"use client"

import { useEffect } from "react"
import { useAuth } from "@/lib/auth"

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const { checkAuth, isHydrated, token } = useAuth()

  useEffect(() => {
    // Only check auth after the store has been hydrated from localStorage
    if (isHydrated && token) {
      checkAuth()
    }
  }, [isHydrated, token, checkAuth])

  return <>{children}</>
}
