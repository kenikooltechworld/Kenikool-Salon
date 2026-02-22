import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { CreditCardIcon } from "@/components/icons";

interface CheckoutButtonProps {
  bookingId: string;
  disabled?: boolean;
  size?: "sm" | "md" | "lg";
  variant?: "primary" | "secondary" | "outline" | "ghost";
}

export function CheckoutButton({
  bookingId,
  disabled,
  size = "md",
  variant = "primary",
}: CheckoutButtonProps) {
  const navigate = useNavigate();

  return (
    <Button
      size={size}
      variant={variant}
      disabled={disabled}
      onClick={() => navigate(`/dashboard/checkout/${bookingId}`)}
    >
      <CreditCardIcon size={20} />
      Checkout
    </Button>
  );
}
