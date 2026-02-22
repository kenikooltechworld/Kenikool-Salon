import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import { useToast } from "@/hooks/use-toast";
import {
  Modal,
  ModalHeader,
  ModalTitle,
  ModalBody,
  ModalFooter,
} from "@/components/ui/modal";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CheckIcon, SparklesIcon } from "@/components/icons";

interface RegistrationIncentiveModalProps {
  isOpen: boolean;
  onClose: () => void;
  guestEmail: string;
  guestName: string;
  bookingCount: number;
  onRegisterSuccess?: (userId: string) => void;
}

export function RegistrationIncentiveModal({
  isOpen,
  onClose,
  guestEmail,
  guestName,
  bookingCount,
  onRegisterSuccess,
}: RegistrationIncentiveModalProps) {
  const { toast } = useToast();
  const [showRegistrationForm, setShowRegistrationForm] = useState(false);
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const registerMutation = useMutation({
    mutationFn: async () => {
      if (password !== confirmPassword) {
        throw new Error("Passwords do not match");
      }

      if (password.length < 8) {
        throw new Error("Password must be at least 8 characters");
      }

      const response = await apiClient.post("/api/auth/register", {
        email: guestEmail,
        password: password,
        full_name: guestName,
      });

      return response.data;
    },
    onSuccess: (data) => {
      toast("Account created successfully!", "success");
      toast("Welcome bonus: 500 loyalty points added!", "success");
      onRegisterSuccess?.(data.user.id);
      onClose();
    },
    onError: (error: any) => {
      toast(
        error.message || error.response?.data?.detail || "Registration failed",
        "error"
      );
    },
  });

  const handleRegister = async () => {
    if (!password || !confirmPassword) {
      toast("Please fill in all fields", "error");
      return;
    }

    await registerMutation.mutateAsync();
  };

  return (
    <Modal open={isOpen} onClose={onClose} size="md">
      <ModalHeader>
        <ModalTitle>Create Your Account</ModalTitle>
      </ModalHeader>

      <ModalBody className="space-y-6">
        {!showRegistrationForm ? (
          <>
            {/* Welcome Message */}
            <div className="text-center space-y-2">
              <p className="text-lg font-semibold text-[var(--foreground)]">
                Welcome back, {guestName}!
              </p>
              <p className="text-sm text-[var(--muted-foreground)]">
                You've made {bookingCount} booking{bookingCount !== 1 ? "s" : ""} with us
              </p>
            </div>

            {/* Benefits */}
            <div className="space-y-3">
              <p className="text-sm font-semibold text-[var(--foreground)]">
                Create an account and get:
              </p>

              <Card>
                <CardContent className="pt-4 space-y-3">
                  <div className="flex items-start gap-3">
                    <CheckIcon
                      size={20}
                      className="text-green-600 flex-shrink-0 mt-0.5"
                    />
                    <div>
                      <p className="font-medium text-[var(--foreground)]">
                        500 Loyalty Points
                      </p>
                      <p className="text-sm text-[var(--muted-foreground)]">
                        Welcome bonus for new members
                      </p>
                    </div>
                  </div>

                  <div className="flex items-start gap-3">
                    <CheckIcon
                      size={20}
                      className="text-green-600 flex-shrink-0 mt-0.5"
                    />
                    <div>
                      <p className="font-medium text-[var(--foreground)]">
                        Booking History
                      </p>
                      <p className="text-sm text-[var(--muted-foreground)]">
                        All your bookings in one place
                      </p>
                    </div>
                  </div>

                  <div className="flex items-start gap-3">
                    <CheckIcon
                      size={20}
                      className="text-green-600 flex-shrink-0 mt-0.5"
                    />
                    <div>
                      <p className="font-medium text-[var(--foreground)]">
                        Exclusive Promotions
                      </p>
                      <p className="text-sm text-[var(--muted-foreground)]">
                        Special offers for members only
                      </p>
                    </div>
                  </div>

                  <div className="flex items-start gap-3">
                    <CheckIcon
                      size={20}
                      className="text-green-600 flex-shrink-0 mt-0.5"
                    />
                    <div>
                      <p className="font-medium text-[var(--foreground)]">
                        Faster Bookings
                      </p>
                      <p className="text-sm text-[var(--muted-foreground)]">
                        Pre-filled information for quick bookings
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Current Promotions */}
            <div className="space-y-2">
              <p className="text-sm font-semibold text-[var(--foreground)]">
                Current Promotions:
              </p>
              <div className="flex flex-wrap gap-2">
                <Badge variant="accent">10% off next booking</Badge>
                <Badge variant="accent">Free consultation</Badge>
              </div>
            </div>
          </>
        ) : (
          <>
            {/* Registration Form */}
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium text-[var(--foreground)]">
                  Email
                </label>
                <input
                  type="email"
                  value={guestEmail}
                  disabled
                  className="w-full mt-1 p-2 border border-[var(--border)] rounded bg-[var(--muted)] text-[var(--muted-foreground)]"
                />
              </div>

              <div>
                <label className="text-sm font-medium text-[var(--foreground)]">
                  Full Name
                </label>
                <input
                  type="text"
                  value={guestName}
                  disabled
                  className="w-full mt-1 p-2 border border-[var(--border)] rounded bg-[var(--muted)] text-[var(--muted-foreground)]"
                />
              </div>

              <div>
                <label className="text-sm font-medium text-[var(--foreground)]">
                  Password *
                </label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="At least 8 characters"
                  className="w-full mt-1 p-2 border border-[var(--border)] rounded"
                />
                <p className="text-xs text-[var(--muted-foreground)] mt-1">
                  Must be at least 8 characters
                </p>
              </div>

              <div>
                <label className="text-sm font-medium text-[var(--foreground)]">
                  Confirm Password *
                </label>
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Re-enter your password"
                  className="w-full mt-1 p-2 border border-[var(--border)] rounded"
                />
              </div>

              <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <p className="text-xs text-blue-900">
                  Your account will be created with the email and name from your booking.
                  You can update these later in your profile.
                </p>
              </div>
            </div>
          </>
        )}
      </ModalBody>

      <ModalFooter>
        {!showRegistrationForm ? (
          <>
            <Button variant="outline" onClick={onClose}>
              Skip for Now
            </Button>
            <Button
              onClick={() => setShowRegistrationForm(true)}
              className="flex items-center gap-2"
            >
              <SparklesIcon size={16} />
              Create Account
            </Button>
          </>
        ) : (
          <>
            <Button
              variant="outline"
              onClick={() => setShowRegistrationForm(false)}
            >
              Back
            </Button>
            <Button
              onClick={handleRegister}
              disabled={registerMutation.isPending || !password || !confirmPassword}
            >
              {registerMutation.isPending ? "Creating..." : "Create Account"}
            </Button>
          </>
        )}
      </ModalFooter>
    </Modal>
  );
}
