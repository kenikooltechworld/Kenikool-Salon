import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Card, Button, Input, Label, Alert, Spinner } from "@/components/ui";
import { useCustomerLogin } from "@/hooks/useCustomerAuth";

export default function CustomerLogin() {
  const navigate = useNavigate();
  const login = useCustomerLogin();

  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.email.trim()) {
      newErrors.email = "Email is required";
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = "Email is invalid";
    }

    if (!formData.password) {
      newErrors.password = "Password is required";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    try {
      await login.mutateAsync({
        username: formData.email,
        password: formData.password,
      });

      // Redirect to customer portal
      navigate("/public/portal");
    } catch (error: any) {
      setErrors({
        submit:
          error.response?.data?.detail ||
          "Login failed. Please check your credentials.",
      });
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    // Clear error for this field
    if (errors[name]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <Card className="max-w-md w-full p-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold mb-2">Welcome Back</h1>
          <p className="text-gray-600">
            Sign in to manage your bookings and preferences
          </p>
        </div>

        {errors.submit && (
          <Alert variant="destructive" className="mb-6">
            {errors.submit}
          </Alert>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              className={errors.email ? "border-red-500" : ""}
              autoComplete="email"
            />
            {errors.email && (
              <p className="text-sm text-red-500 mt-1">{errors.email}</p>
            )}
          </div>

          <div>
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              name="password"
              type="password"
              value={formData.password}
              onChange={handleChange}
              className={errors.password ? "border-red-500" : ""}
              autoComplete="current-password"
            />
            {errors.password && (
              <p className="text-sm text-red-500 mt-1">{errors.password}</p>
            )}
          </div>

          <Button type="submit" className="w-full" disabled={login.isPending}>
            {login.isPending ? (
              <>
                <Spinner className="mr-2" />
                Signing In...
              </>
            ) : (
              "Sign In"
            )}
          </Button>
        </form>

        <div className="mt-6 space-y-3 text-center text-sm">
          <p className="text-gray-600">
            Don't have an account?{" "}
            <Link
              to="/public/register"
              className="text-blue-600 hover:underline font-medium"
            >
              Create one
            </Link>
          </p>
          <p className="text-gray-600">
            <Link
              to="/public/forgot-password"
              className="text-blue-600 hover:underline"
            >
              Forgot your password?
            </Link>
          </p>
        </div>

        <div className="mt-8 pt-6 border-t border-gray-200 text-center">
          <Link
            to="/public/booking"
            className="text-sm text-gray-600 hover:text-gray-900"
          >
            ← Back to booking
          </Link>
        </div>
      </Card>
    </div>
  );
}
