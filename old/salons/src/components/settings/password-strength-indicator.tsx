import { useMemo } from "react";
import { CheckIcon, XIcon } from "@/components/icons";

interface PasswordStrengthIndicatorProps {
  password: string;
}

export function PasswordStrengthIndicator({
  password,
}: PasswordStrengthIndicatorProps) {
  const strength = useMemo(() => {
    if (!password) return { level: "none", score: 0, label: "" };

    let score = 0;
    const requirements = {
      length: password.length >= 8,
      uppercase: /[A-Z]/.test(password),
      lowercase: /[a-z]/.test(password),
      number: /\d/.test(password),
      special: /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password),
    };

    // Calculate score
    if (requirements.length) score += 20;
    if (requirements.uppercase) score += 20;
    if (requirements.lowercase) score += 20;
    if (requirements.number) score += 20;
    if (requirements.special) score += 20;

    // Determine level
    let level = "weak";
    let label = "Weak";
    if (score >= 80) {
      level = "strong";
      label = "Strong";
    } else if (score >= 60) {
      level = "medium";
      label = "Medium";
    }

    return { level, score, label, requirements };
  }, [password]);

  if (strength.level === "none") {
    return null;
  }

  const colors = {
    weak: "bg-red-500",
    medium: "bg-yellow-500",
    strong: "bg-green-500",
  };

  const textColors = {
    weak: "text-red-600",
    medium: "text-yellow-600",
    strong: "text-green-600",
  };

  return (
    <div className="space-y-3">
      {/* Strength Bar */}
      <div className="space-y-1">
        <div className="flex items-center justify-between">
          <label className="text-sm font-medium text-foreground">
            Password Strength
          </label>
          <span className={`text-sm font-medium ${textColors[strength.level]}`}>
            {strength.label}
          </span>
        </div>
        <div className="w-full bg-muted rounded-full h-2 overflow-hidden">
          <div
            className={`h-full transition-all duration-300 ${
              colors[strength.level]
            }`}
            style={{ width: `${strength.score}%` }}
          />
        </div>
      </div>

      {/* Requirements Checklist */}
      {strength.requirements && (
        <div className="bg-muted p-3 rounded-lg space-y-2">
          <p className="text-xs font-medium text-foreground">Requirements:</p>
          <ul className="space-y-1">
            <li className="flex items-center gap-2 text-xs">
              {strength.requirements.length ? (
                <CheckIcon size={14} className="text-green-600" />
              ) : (
                <XIcon size={14} className="text-muted-foreground" />
              )}
              <span
                className={
                  strength.requirements.length
                    ? "text-foreground"
                    : "text-muted-foreground"
                }
              >
                At least 8 characters
              </span>
            </li>
            <li className="flex items-center gap-2 text-xs">
              {strength.requirements.uppercase ? (
                <CheckIcon size={14} className="text-green-600" />
              ) : (
                <XIcon size={14} className="text-muted-foreground" />
              )}
              <span
                className={
                  strength.requirements.uppercase
                    ? "text-foreground"
                    : "text-muted-foreground"
                }
              >
                Uppercase letter (A-Z)
              </span>
            </li>
            <li className="flex items-center gap-2 text-xs">
              {strength.requirements.lowercase ? (
                <CheckIcon size={14} className="text-green-600" />
              ) : (
                <XIcon size={14} className="text-muted-foreground" />
              )}
              <span
                className={
                  strength.requirements.lowercase
                    ? "text-foreground"
                    : "text-muted-foreground"
                }
              >
                Lowercase letter (a-z)
              </span>
            </li>
            <li className="flex items-center gap-2 text-xs">
              {strength.requirements.number ? (
                <CheckIcon size={14} className="text-green-600" />
              ) : (
                <XIcon size={14} className="text-muted-foreground" />
              )}
              <span
                className={
                  strength.requirements.number
                    ? "text-foreground"
                    : "text-muted-foreground"
                }
              >
                Number (0-9)
              </span>
            </li>
            <li className="flex items-center gap-2 text-xs">
              {strength.requirements.special ? (
                <CheckIcon size={14} className="text-green-600" />
              ) : (
                <XIcon size={14} className="text-muted-foreground" />
              )}
              <span
                className={
                  strength.requirements.special
                    ? "text-foreground"
                    : "text-muted-foreground"
                }
              >
                Special character (!@#$%^&*)
              </span>
            </li>
          </ul>
        </div>
      )}
    </div>
  );
}
