import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { validateEmail } from "@/lib/utils/auth-validation";

interface FormFieldWithValidationProps {
  label: string;
  type?: string;
  placeholder?: string;
  value: string;
  onChange: (value: string) => void;
  error?: string;
  disabled?: boolean;
  icon?: React.ReactNode;
  validation?: (value: string) => boolean;
  validationMessage?: string;
  showValidation?: boolean;
}

export function FormFieldWithValidation({
  label,
  type = "text",
  placeholder,
  value,
  onChange,
  error,
  disabled,
  icon,
  validation,
  validationMessage,
  showValidation = true,
}: FormFieldWithValidationProps) {
  const isValid = validation ? validation(value) : true;
  const showError = error || (showValidation && value && !isValid);

  return (
    <div className="space-y-2">
      <Label htmlFor={label}>{label}</Label>
      <div className="relative">
        {icon && (
          <div className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">
            {icon}
          </div>
        )}
        <Input
          id={label}
          type={type}
          placeholder={placeholder}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          disabled={disabled}
          className={`${icon ? "pl-10" : ""} ${
            showError ? "border-destructive focus-visible:ring-destructive" : ""
          } ${isValid && value && showValidation ? "border-green-500" : ""}`}
        />
        {showValidation && value && isValid && (
          <div className="absolute right-3 top-1/2 -translate-y-1/2 text-green-500">
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                clipRule="evenodd"
              />
            </svg>
          </div>
        )}
      </div>
      {showError && (
        <p className="text-xs text-destructive font-medium">
          {error || validationMessage}
        </p>
      )}
    </div>
  );
}
