import {
  calculatePasswordStrength,
  getPasswordRequirements,
} from "@/lib/utils/auth-validation";

interface PasswordStrengthIndicatorProps {
  password: string;
  showRequirements?: boolean;
}

export function PasswordStrengthIndicator({
  password,
  showRequirements = true,
}: PasswordStrengthIndicatorProps) {
  const strength = calculatePasswordStrength(password);
  const requirements = getPasswordRequirements(password);

  const getColorClass = (color: string) => {
    const colorMap: Record<string, string> = {
      destructive: "bg-destructive",
      warning: "bg-yellow-500",
      secondary: "bg-secondary",
      primary: "bg-primary",
      success: "bg-green-500",
    };
    return colorMap[color] || "bg-muted";
  };

  const getTextColorClass = (color: string) => {
    const colorMap: Record<string, string> = {
      destructive: "text-destructive",
      warning: "text-yellow-600 dark:text-yellow-400",
      secondary: "text-secondary",
      primary: "text-primary",
      success: "text-green-600 dark:text-green-400",
    };
    return colorMap[color] || "text-muted-foreground";
  };

  if (!password) return null;

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-muted-foreground">
          Password Strength
        </span>
        <span
          className={`text-xs font-semibold ${getTextColorClass(strength.color)}`}
        >
          {strength.label}
        </span>
      </div>

      <div className="h-2 bg-muted rounded-full overflow-hidden">
        <div
          className={`h-full transition-all duration-300 ${getColorClass(strength.color)}`}
          style={{ width: `${strength.percentage}%` }}
        />
      </div>

      {showRequirements && (
        <div className="space-y-1 mt-3">
          <p className="text-xs font-medium text-muted-foreground">
            Requirements:
          </p>
          <ul className="space-y-1">
            <li className="flex items-center gap-2 text-xs">
              <span
                className={`w-4 h-4 rounded-full flex items-center justify-center text-white text-[10px] ${
                  requirements.length ? "bg-green-500" : "bg-muted"
                }`}
              >
                {requirements.length ? "✓" : "○"}
              </span>
              <span
                className={
                  requirements.length
                    ? "text-foreground"
                    : "text-muted-foreground"
                }
              >
                At least 8 characters
              </span>
            </li>
            <li className="flex items-center gap-2 text-xs">
              <span
                className={`w-4 h-4 rounded-full flex items-center justify-center text-white text-[10px] ${
                  requirements.uppercase ? "bg-green-500" : "bg-muted"
                }`}
              >
                {requirements.uppercase ? "✓" : "○"}
              </span>
              <span
                className={
                  requirements.uppercase
                    ? "text-foreground"
                    : "text-muted-foreground"
                }
              >
                One uppercase letter
              </span>
            </li>
            <li className="flex items-center gap-2 text-xs">
              <span
                className={`w-4 h-4 rounded-full flex items-center justify-center text-white text-[10px] ${
                  requirements.lowercase ? "bg-green-500" : "bg-muted"
                }`}
              >
                {requirements.lowercase ? "✓" : "○"}
              </span>
              <span
                className={
                  requirements.lowercase
                    ? "text-foreground"
                    : "text-muted-foreground"
                }
              >
                One lowercase letter
              </span>
            </li>
            <li className="flex items-center gap-2 text-xs">
              <span
                className={`w-4 h-4 rounded-full flex items-center justify-center text-white text-[10px] ${
                  requirements.number ? "bg-green-500" : "bg-muted"
                }`}
              >
                {requirements.number ? "✓" : "○"}
              </span>
              <span
                className={
                  requirements.number
                    ? "text-foreground"
                    : "text-muted-foreground"
                }
              >
                One number
              </span>
            </li>
          </ul>
        </div>
      )}
    </div>
  );
}
