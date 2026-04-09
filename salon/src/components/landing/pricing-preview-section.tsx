import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { CheckCircleIcon } from "@/components/icons";
import { apiClient } from "@/lib/utils/api";

const defaultPricing = [
  {
    name: "Free",
    monthlyPrice: 0,
    annualPrice: 0,
    description: "Perfect for getting started",
    features: [
      "Up to 1 staff member",
      "Up to 100 customers",
      "Basic appointment scheduling",
      "Email support",
      "30-day trial",
    ],
    cta: "Start Free Trial",
    highlighted: false,
  },
  {
    name: "Starter",
    monthlyPrice: 15000,
    annualPrice: 153000,
    description: "For small salons",
    features: [
      "Up to 3 staff members",
      "POS system included",
      "Up to 500 customers",
      "Email support",
      "Mobile app access",
    ],
    cta: "Start Free Trial",
    highlighted: false,
  },
  {
    name: "Professional",
    monthlyPrice: 35000,
    annualPrice: 357000,
    description: "For growing businesses",
    features: [
      "Up to 10 staff members",
      "Advanced analytics",
      "API access",
      "Priority support",
      "Up to 2000 customers",
    ],
    cta: "Start Free Trial",
    highlighted: true,
  },
];

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.6, ease: "easeOut" },
  },
};

export function PricingPreviewSection() {
  const [isAnnual, setIsAnnual] = useState(false);

  const { data: apiPricing = [] } = useQuery({
    queryKey: ["pricing-plans"],
    queryFn: async () => {
      const response = await apiClient.get("/billing/plans");
      return response.data || [];
    },
    staleTime: 1000 * 60 * 5, // 5 minutes
    retry: 2,
  });

  // Transform API response to component format and ensure all required fields exist
  const pricing =
    apiPricing.length > 0
      ? apiPricing.map((plan: any) => ({
          name: plan.name || "",
          monthlyPrice: plan.monthly_price ?? 0,
          annualPrice: plan.yearly_price ?? 0,
          description: plan.description || "",
          features: Array.isArray(plan.features) ? plan.features : [],
          cta: "Start Free Trial",
          highlighted: plan.is_featured || false,
        }))
      : defaultPricing;

  return (
    <section id="pricing" className="py-20 sm:py-32 bg-background">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
          >
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-foreground mb-4">
              Simple, Transparent Pricing
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto mb-8">
              Choose the plan that fits your business needs
            </p>
          </motion.div>

          <div className="flex items-center justify-center gap-4 mb-12">
            <motion.span
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
              viewport={{ once: true }}
              className={`text-sm font-medium ${
                !isAnnual ? "text-foreground" : "text-muted-foreground"
              }`}
            >
              Monthly
            </motion.span>
            <button
              onClick={() => setIsAnnual(!isAnnual)}
              className="relative inline-flex h-8 w-14 items-center rounded-full bg-muted"
            >
              <motion.span
                animate={{ x: isAnnual ? 28 : 4 }}
                transition={{ type: "spring", stiffness: 500, damping: 30 }}
                className="inline-block h-6 w-6 transform rounded-full bg-primary"
              />
            </button>
            <motion.span
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
              viewport={{ once: true }}
              className={`text-sm font-medium ${
                isAnnual ? "text-foreground" : "text-muted-foreground"
              }`}
            >
              Annual
            </motion.span>
            {isAnnual && (
              <motion.span
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ type: "spring", stiffness: 500, damping: 30 }}
                className="ml-2 inline-block text-xs font-semibold px-3 py-1 rounded-full"
                style={{
                  backgroundColor: "var(--primary)",
                  color: "var(--primary-foreground)",
                }}
              >
                Save 20%
              </motion.span>
            )}
          </div>
        </div>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          className="grid grid-cols-1 md:grid-cols-3 gap-6 md:gap-8"
        >
          {pricing.slice(0, 3).map((plan: any, idx: number) => {
            const displayPrice = isAnnual
              ? (plan.annualPrice ?? 0)
              : (plan.monthlyPrice ?? 0);
            const savings =
              isAnnual && plan.monthlyPrice && plan.annualPrice
                ? Math.round((plan.monthlyPrice * 12 - plan.annualPrice) / 12)
                : 0;

            return (
              <motion.div key={idx} variants={itemVariants}>
                <Card
                  className={`p-6 sm:p-8 flex flex-col h-full transition-all duration-300 ${
                    plan.highlighted
                      ? "ring-2 ring-primary shadow-lg md:scale-105"
                      : ""
                  }`}
                >
                  {plan.highlighted && (
                    <div
                      className="text-xs sm:text-sm font-semibold px-3 py-1 rounded-full w-fit mb-4"
                      style={{
                        backgroundColor: "var(--primary)",
                        color: "var(--primary-foreground)",
                      }}
                    >
                      Most Popular
                    </div>
                  )}

                  <h3 className="text-xl sm:text-2xl font-bold text-foreground mb-2">
                    {plan.name || "Plan"}
                  </h3>
                  <p className="text-muted-foreground text-xs sm:text-sm mb-6">
                    {plan.description || ""}
                  </p>

                  <motion.div
                    key={isAnnual ? "annual" : "monthly"}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3 }}
                    className="mb-6"
                  >
                    <span className="text-3xl sm:text-4xl font-bold text-foreground">
                      {displayPrice === 0
                        ? "Free"
                        : `₦${(displayPrice || 0).toLocaleString()}`}
                    </span>
                    {displayPrice > 0 && (
                      <span className="text-muted-foreground text-xs sm:text-sm ml-2">
                        {isAnnual ? "/year" : "/month"}
                      </span>
                    )}
                    {savings > 0 && (
                      <div
                        className="text-xs font-semibold mt-2"
                        style={{ color: "var(--primary)" }}
                      >
                        Save ₦{savings.toLocaleString()}/month
                      </div>
                    )}
                  </motion.div>

                  <Link to="/auth/register" className="mb-8">
                    <Button
                      className="w-full"
                      variant={plan.highlighted ? "primary" : "outline"}
                    >
                      {plan.cta}
                    </Button>
                  </Link>

                  <div className="space-y-4 flex-1">
                    {Array.isArray(plan.features) &&
                    plan.features.length > 0 ? (
                      plan.features.map((feature: string, fidx: number) => (
                        <motion.div
                          key={fidx}
                          initial={{ opacity: 0, x: -10 }}
                          whileInView={{ opacity: 1, x: 0 }}
                          transition={{ delay: fidx * 0.05 }}
                          viewport={{ once: true }}
                          className="flex items-start gap-3"
                        >
                          <CheckCircleIcon className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" />
                          <span className="text-foreground text-xs sm:text-sm">
                            {feature}
                          </span>
                        </motion.div>
                      ))
                    ) : (
                      <p className="text-muted-foreground text-xs sm:text-sm">
                        No features listed
                      </p>
                    )}
                  </div>
                </Card>
              </motion.div>
            );
          })}
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          viewport={{ once: true }}
          className="flex justify-center mt-12"
        >
          <Link to="/pricing">
            <Button size="lg" variant="outline">
              View All Plans
            </Button>
          </Link>
        </motion.div>
      </div>
    </section>
  );
}
