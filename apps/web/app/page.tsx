'use client';

import { useState } from 'react';
import { AuthProvider, useAuth } from '../lib/auth-context';
import { LoginForm } from '../components/auth/login-form';
import { RegisterForm } from '../components/auth/register-form';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@workspace/ui/components/card';
import { Button } from '@workspace/ui/components/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@workspace/ui/components/tabs';

function DashboardContent() {
  const { user, logout, login, register, error, isLoading } = useAuth();

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <Tabs defaultValue="login" className="w-full max-w-md">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="login">Sign In</TabsTrigger>
            <TabsTrigger value="register">Create Account</TabsTrigger>
          </TabsList>

          <TabsContent value="login">
            <LoginForm
              onSubmit={login}
              isLoading={isLoading}
              error={error}
            />
          </TabsContent>

          <TabsContent value="register">
            <RegisterForm
              onSubmit={register}
              isLoading={isLoading}
              error={error}
            />
          </TabsContent>
        </Tabs>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900">
                Marketing Analytics Dashboard
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">
                Welcome, {user.full_name || user.username}
              </span>
              <Button variant="outline" onClick={logout}>
                Sign Out
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* User Info Card */}
            <Card>
              <CardHeader>
                <CardTitle>User Profile</CardTitle>
                <CardDescription>Your account information</CardDescription>
              </CardHeader>
              <CardContent className="space-y-2">
                <div>
                  <span className="font-medium">Username:</span> {user.username}
                </div>
                <div>
                  <span className="font-medium">Email:</span> {user.email}
                </div>
                <div>
                  <span className="font-medium">Full Name:</span> {user.full_name || 'Not provided'}
                </div>
                <div>
                  <span className="font-medium">Status:</span>
                  <span className={`ml-2 px-2 py-1 text-xs rounded-full ${
                    user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {user.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
                <div>
                  <span className="font-medium">Member since:</span>{' '}
                  {new Date(user.created_at).toLocaleDateString()}
                </div>
              </CardContent>
            </Card>

            {/* Dashboard Overview */}
            <Card>
              <CardHeader>
                <CardTitle>Dashboard Overview</CardTitle>
                <CardDescription>System status and features</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Authentication</span>
                    <span className="text-sm font-medium text-green-600">✓ Active</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Database</span>
                    <span className="text-sm font-medium text-green-600">✓ Connected</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">API Status</span>
                    <span className="text-sm font-medium text-green-600">✓ Running</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Marketing Analytics Placeholder */}
            <Card>
              <CardHeader>
                <CardTitle>Marketing Analytics</CardTitle>
                <CardDescription>Google Meridian model integration</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="text-sm text-gray-600">
                    Advanced marketing analytics features will be available here:
                  </div>
                  <ul className="text-sm space-y-1 text-gray-500">
                    <li>• Contribution charts</li>
                    <li>• Response curves</li>
                    <li>• Channel performance analysis</li>
                    <li>• Customer narratives</li>
                  </ul>
                  <div className="pt-2">
                    <div className="text-xs text-gray-400">
                      Model: saved_mmm.pkl (Ready for integration)
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
}

export default function Page() {
  return (
    <AuthProvider>
      <DashboardContent />
    </AuthProvider>
  );
}
