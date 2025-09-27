"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@workspace/ui/components/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@workspace/ui/components/card"
import { useAuth } from "@/lib/auth"
import { SimpleContributionChart, SimpleResponseCurves, SimpleMMInsights } from "@/components/mmm/simple-charts"
import { CheckCircle, BarChart3 } from "lucide-react"

export default function DashboardPage() {
  const { user, token, logout, checkAuth, isHydrated } = useAuth()
  const router = useRouter()

  useEffect(() => {
    // Wait for hydration before making auth decisions
    if (!isHydrated) return
    
    if (!token) {
      router.push("/login")
      return
    }
    // Only check auth once when component mounts if we have a token
    if (token && !user) {
      checkAuth()
    }
  }, [token, router, isHydrated, user, checkAuth])

  const handleLogout = () => {
    logout()
    router.push("/login")
  }

  // Show loading while hydrating or while we have a token but no user data
  if (!isHydrated || (token && !user)) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
          <p className="mt-2 text-muted-foreground">Loading...</p>
        </div>
      </div>
    )
  }

  // If hydrated and no token, redirect will happen in useEffect
  if (!token) {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div>
              <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
                MMM Dashboard
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600 dark:text-gray-400">
                Welcome, {user.full_name}
              </span>
              <Button variant="outline" size="sm" onClick={handleLogout}>
                Sign Out
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Welcome Card */}
          <Card className="md:col-span-2 lg:col-span-3">
            <CardHeader>
              <CardTitle>Welcome to MMM Dashboard</CardTitle>
              <CardDescription>
                Your Media Mix Modeling analytics platform is ready to use.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                  <h3 className="font-medium text-blue-900 dark:text-blue-100">
                    User Profile
                  </h3>
                  <p className="text-sm text-blue-700 dark:text-blue-300 mt-1">
                    Email: {user.email}
                  </p>
                  {user.company && (
                    <p className="text-sm text-blue-700 dark:text-blue-300">
                      Company: {user.company}
                    </p>
                  )}
                  <p className="text-sm text-blue-700 dark:text-blue-300">
                    Role: {user.role}
                  </p>
                </div>
                <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                  <h3 className="font-medium text-green-900 dark:text-green-100">
                    Account Status
                  </h3>
                  <p className="text-sm text-green-700 dark:text-green-300 mt-1">
                    Status: {user.is_active ? "Active" : "Inactive"}
                  </p>
                  <p className="text-sm text-green-700 dark:text-green-300">
                    Member since: {new Date(user.created_at).toLocaleDateString()}
                  </p>
                </div>
                <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                  <h3 className="font-medium text-purple-900 dark:text-purple-100">
                    Model Status
                  </h3>
                  <p className="text-sm text-purple-700 dark:text-purple-300 mt-1 flex items-center gap-1">
                    <CheckCircle className="h-4 w-4" />
                    MMM Model: Active
                  </p>
                  <p className="text-sm text-purple-700 dark:text-purple-300 flex items-center gap-1">
                    <BarChart3 className="h-4 w-4" />
                    Data: 105 weeks, 10 channels
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* MMM Analytics Components */}
          <div className="md:col-span-2 lg:col-span-2">
            <SimpleContributionChart />
          </div>

          <div className="md:col-span-2 lg:col-span-1">
            <SimpleResponseCurves />
          </div>

          <div className="md:col-span-2 lg:col-span-3">
            <SimpleMMInsights />
          </div>
        </div>
      </main>
    </div>
  )
}
