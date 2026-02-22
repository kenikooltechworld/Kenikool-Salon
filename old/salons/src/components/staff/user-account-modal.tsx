"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { toast } from "sonner";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Card, CardContent } from "@/components/ui/card";

interface UserAccountModalProps {
  staffId: string;
  staffName: string;
  staffEmail: string;
  isOpen: boolean;
  onClose: () => void;
  onAccountCreated?: () => void;
}

export function UserAccountModal({
  staffId,
  staffName,
  staffEmail,
  isOpen,
  onClose,
  onAccountCreated,
}: UserAccountModalProps) {
  const [email, setEmail] = useState(staffEmail);
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [role, setRole] = useState("stylist");
  const [showPassword, setShowPassword] = useState(false);

  const createAccountMutation = useMutation({
    mutationFn: async () => {
      if (password !== confirmPassword) {
        throw new Error("Passwords do not match");
      }

      if (password.length < 8) {
        throw new Error("Password must be at least 8 characters");
      }

      const res = await fetch(
        `/api/staff/roles/${staffId}/create-user-account`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            email,
            password,
            role,
          }),
        },
      );

      if (!res.ok) {
        const error = await res.json();
        throw new Error(error.detail || "Failed to create account");
      }

      return res.json();
    },
    onSuccess: (data) => {
      toast.success("User account created successfully");
      onAccountCreated?.();
      onClose();
      // Reset form
      setPassword("");
      setConfirmPassword("");
      setRole("stylist");
    },
    onError: (error: any) => {
      toast.error(error.message || "Failed to create account");
    },
  });

  const passwordStrength = {
    length: password.length >= 8,
    hasUppercase: /[A-Z]/.test(password),
    hasLowercase: /[a-z]/.test(password),
    hasNumbers: /\d/.test(password),
    hasSpecial: /[!@#$%^&*]/.test(password),
  };

  const strengthScore = Object.values(passwordStrength).filter(Boolean).length;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Create User Account</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {/* Staff Info */}
          <div className="bg-muted p-3 rounded">
            <p className="text-sm font-medium">{staffName}</p>
            <p className="text-xs text-muted-foreground">Staff ID: {staffId}</p>
          </div>

          {/* Email */}
          <div>
            <Label htmlFor="email">Email Address</Label>
            <Input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="staff@salon.com"
              className="mt-1"
            />
          </div>

          {/* Role */}
          <div>
            <Label htmlFor="role">Role</Label>
            <Select value={role} onValueChange={setRole}>
              <SelectTrigger id="role" className="mt-1">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="owner">Owner</SelectItem>
                <SelectItem value="manager">Manager</SelectItem>
                <SelectItem value="stylist">Stylist</SelectItem>
                <SelectItem value="receptionist">Receptionist</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Password */}
          <div>
            <Label htmlFor="password">Password</Label>
            <div className="relative mt-1">
              <Input
                id="password"
                type={showPassword ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter password"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-muted-foreground hover:text-foreground"
              >
                {showPassword ? "Hide" : "Show"}
              </button>
            </div>
          </div>

          {/* Confirm Password */}
          <div>
            <Label htmlFor="confirm-password">Confirm Password</Label>
            <Input
              id="confirm-password"
              type={showPassword ? "text" : "password"}
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Confirm password"
              className="mt-1"
            />
          </div>

          {/* Password Strength */}
          {password && (
            <Card>
              <CardContent className="pt-4">
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">
                      Password Strength
                    </span>
                    <span className="text-xs">{strengthScore}/5</span>
                  </div>
                  <div className="w-full bg-muted rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all ${
                        strengthScore <= 2
                          ? "bg-red-500"
                          : strengthScore <= 3
                            ? "bg-yellow-500"
                            : "bg-green-500"
                      }`}
                      style={{ width: `${(strengthScore / 5) * 100}%` }}
                    />
                  </div>

                  <div className="space-y-1 text-xs">
                    <div className="flex items-center gap-2">
                      <span
                        className={
                          passwordStrength.length
                            ? "text-green-600"
                            : "text-muted-foreground"
                        }
                      >
                        {passwordStrength.length ? "✓" : "○"}
                      </span>
                      <span>At least 8 characters</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span
                        className={
                          passwordStrength.hasUppercase
                            ? "text-green-600"
                            : "text-muted-foreground"
                        }
                      >
                        {passwordStrength.hasUppercase ? "✓" : "○"}
                      </span>
                      <span>Uppercase letter</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span
                        className={
                          passwordStrength.hasLowercase
                            ? "text-green-600"
                            : "text-muted-foreground"
                        }
                      >
                        {passwordStrength.hasLowercase ? "✓" : "○"}
                      </span>
                      <span>Lowercase letter</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span
                        className={
                          passwordStrength.hasNumbers
                            ? "text-green-600"
                            : "text-muted-foreground"
                        }
                      >
                        {passwordStrength.hasNumbers ? "✓" : "○"}
                      </span>
                      <span>Number</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span
                        className={
                          passwordStrength.hasSpecial
                            ? "text-green-600"
                            : "text-muted-foreground"
                        }
                      >
                        {passwordStrength.hasSpecial ? "✓" : "○"}
                      </span>
                      <span>Special character (!@#$%^&*)</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Info */}
          <div className="bg-blue-50 border border-blue-200 rounded p-3 text-sm text-blue-800">
            ℹ️ The staff member will be able to log in with this email and
            password. They can change their password after first login.
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button
            onClick={() => createAccountMutation.mutate()}
            disabled={
              !email ||
              !password ||
              password !== confirmPassword ||
              password.length < 8 ||
              createAccountMutation.isPending
            }
          >
            {createAccountMutation.isPending ? "Creating..." : "Create Account"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
