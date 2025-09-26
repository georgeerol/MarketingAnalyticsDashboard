"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@workspace/ui/components/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@workspace/ui/components/card"
import { useAuth } from "@/lib/auth"

export default function DashboardPage() {
  const { user, token, logout, checkAuth } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!token) {
      router.push("/login")
      return
    }
    checkAuth()
  }, [token, router, checkAuth])

  const handleLogout = () => {
    logout()
    router.push("/login")
  }

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
          <p className="mt-2 text-muted-foreground">Loading...</p>
        </div>
      </div>
    )
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
                    Next Steps
                  </h3>
                  <p className="text-sm text-purple-700 dark:text-purple-300 mt-1">
                    MMM model integration coming soon
                  </p>
                  <p className="text-sm text-purple-700 dark:text-purple-300">
                    Phase 2: Dashboard features
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Placeholder Cards for Future Features */}
          <Card>
            <CardHeader>
              <CardTitle>Channel Performance</CardTitle>
              <CardDescription>
                View media channel effectiveness
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-32 bg-gray-100 dark:bg-gray-800 rounded-lg flex items-center justify-center">
                <p className="text-sm text-gray-500">Coming in Phase 2</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Response Curves</CardTitle>
              <CardDescription>
                Analyze diminishing returns
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-32 bg-gray-100 dark:bg-gray-800 rounded-lg flex items-center justify-center">
                <p className="text-sm text-gray-500">Coming in Phase 2</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>MMM Insights</CardTitle>
              <CardDescription>
                Model recommendations
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-32 bg-gray-100 dark:bg-gray-800 rounded-lg flex items-center justify-center">
                <p className="text-sm text-gray-500">Coming in Phase 2</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  )
}
