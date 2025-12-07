import { LoginForm } from "@/components/auth/login-form";

export default function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            MMM Dashboard
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Media Mix Modeling Analytics Platform
          </p>
        </div>
        <LoginForm />
      </div>
    </div>
  );
}
