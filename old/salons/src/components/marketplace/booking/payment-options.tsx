import { motion } from "framer-motion";
import {
  CreditCardIcon,
  WalletIcon,
  BankIcon,
  PhoneIcon,
} from "@/components/icons";

interface PaymentOption {
  id: string;
  name: string;
  description: string;
  icon: React.ComponentType<{ size?: number; className?: string }>;
  discount?: number;
}

interface PaymentOptionsProps {
  onSelect: (method: string) => void;
  selectedMethod: string;
}

export function PaymentOptions({
  onSelect,
  selectedMethod,
}: PaymentOptionsProps) {
  const paymentOptions: PaymentOption[] = [
    {
      id: "card",
      name: "Debit/Credit Card",
      description: "Visa, Mastercard, or Verve",
      icon: CreditCardIcon,
      discount: 5,
    },
    {
      id: "wallet",
      name: "Digital Wallet",
      description: "Apple Pay, Google Pay",
      icon: WalletIcon,
    },
    {
      id: "bank_transfer",
      name: "Bank Transfer",
      description: "Direct bank transfer",
      icon: BankIcon,
    },
    {
      id: "ussd",
      name: "USSD",
      description: "Mobile banking USSD",
      icon: PhoneIcon,
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-4">Select Payment Method</h3>
        <div className="space-y-3">
          {paymentOptions.map((option, index) => {
            const Icon = option.icon;
            const isSelected = selectedMethod === option.id;

            return (
              <motion.button
                key={option.id}
                onClick={() => onSelect(option.id)}
                className={`w-full p-4 rounded-lg border-2 transition-all text-left ${
                  isSelected
                    ? "border-[var(--primary)] bg-[var(--primary)]/5"
                    : "border-[var(--border)] hover:border-[var(--primary)]"
                }`}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3 flex-1">
                    <div className="p-2 bg-[var(--muted)] rounded-lg mt-1">
                      <Icon size={20} className="text-[var(--primary)]" />
                    </div>
                    <div>
                      <h4 className="font-semibold text-[var(--foreground)]">
                        {option.name}
                      </h4>
                      <p className="text-sm text-[var(--muted-foreground)]">
                        {option.description}
                      </p>
                    </div>
                  </div>
                  {option.discount && (
                    <motion.div
                      className="bg-green-100 text-green-700 px-3 py-1 rounded-full text-xs font-semibold whitespace-nowrap ml-2"
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ delay: index * 0.05 + 0.2, type: "spring" }}
                    >
                      {option.discount}% OFF
                    </motion.div>
                  )}
                </div>
              </motion.button>
            );
          })}
        </div>
      </div>

      {/* Discount Info */}
      {selectedMethod === "card" && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-green-50 border border-green-200 p-4 rounded-lg"
        >
          <p className="text-sm text-green-800">
            <span className="font-semibold">💰 Special Offer:</span> Get 5%
            discount when you pay with card. This discount will be applied
            automatically at checkout.
          </p>
        </motion.div>
      )}

      {/* Security Info */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="bg-blue-50 border border-blue-200 p-4 rounded-lg"
      >
        <p className="text-sm text-blue-800">
          <span className="font-semibold">🔒 Secure Payment:</span> All
          payments are processed securely through Paystack. Your payment
          information is encrypted and never stored on our servers.
        </p>
      </motion.div>

      {/* Summary */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="bg-[var(--muted)] p-4 rounded-lg"
      >
        <p className="text-sm text-[var(--muted-foreground)]">
          <span className="font-semibold">Payment Method:</span>{" "}
          {paymentOptions.find((opt) => opt.id === selectedMethod)?.name ||
            "Not selected"}
        </p>
      </motion.div>
    </div>
  );
}
