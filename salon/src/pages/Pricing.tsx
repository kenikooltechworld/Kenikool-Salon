import { Link } from "react-router-dom";
import { motion } from "motion/react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { CheckCircleIcon } from "@/components/icons";
import { usePricingPlans } from "@/hooks/owner/useSubscription";

const defaultPricing = [
  {
    name: "Free",
    monthlyPrice: 0,
    annualPrice: 0,
    description: "Perfect for trying out",
    features: [
      "1 staff member",
      "50 bookings/month",
      "Basic client management",
      "100 clients",
      "1 location",
      "Mobile app access",
      "Basic analytics",
      "Email support",
    ],
    cta: "Get Started",
    highlighted: false,
  },
  {
    name: "Starter",
    monthlyPrice: 15000,
    annualPrice: 153000,
    description: "Perfect for small salons",
    features: [
      "Up to 3 staff members",
      "Unlimited bookings",
      "Offline POS system",
      "500 clients",
      "Client management",
      "100 SMS notifications/month",
      "Email support",
      "Mobile app access",
      "Basic analytics",
      "Custom branding",
    ],
    cta: "Start Free Trial",
    highlighted: false,
  },
  {
    name: "Professional",
    monthlyPrice: 35000,
    annualPrice: 357000,
    description: "Most popular for growing salons",
    features: [
      "Up to 10 staff members",
      "Unlimited bookings",
      "Full POS with offline mode",
      "2,000 clients",
      "Inventory management",
      "500 SMS notifications/month",
      "Marketing campaigns",
      "Loyalty programs",
      "Advanced analytics",
      "Priority email support",
      "Custom branding",
      "Gift cards & Packages",
    ],
    cta: "Start Free Trial",
    highlighted: true,
  },
  {
    name: "Business",
    monthlyPrice: 65000,
    annualPrice: 663000,
    description: "For established salons",
    features: [
      "Up to 25 staff members",
      "Unlimited bookings",
      "Unlimited clients",
      "Full inventory management",
      "2,000 SMS notifications/month",
      "Advanced marketing campaigns",
      "Accounting & Financial reports",
      "Package management",
      "Custom domain support",
      "Priority phone support",
      "Dedicated account manager",
      "Advanced security features",
    ],
    cta: "Start Free Trial",
    highlighted: false,
  },
  {
    name: "Enterprise",
    monthlyPrice: 120000,
    annualPrice: 1224000,
    description: "For multi-location salons",
    features: [
      "Up to 50 staff members",
      "Unlimited bookings",
      "Unlimited clients",
      "3 locations",
      "Full inventory management",
      "5,000 SMS notifications/month",
      "Advanced marketing campaigns",
      "Complete accounting suite",
      "White-label booking pages",
      "Custom domain support",
      "Full API access",
      "Priority 24/7 support",
      "Custom integrations",
      "Voice assistant integration",
    ],
    cta: "Contact Sales",
    highlighted: false,
  },
  {
    name: "Unlimited",
    monthlyPrice: 250000,
    annualPrice: 2550000,
    description: "For resellers and agencies",
    features: [
      "Unlimited staff members",
      "Unlimited bookings",
      "Unlimited clients",
      "Unlimited locations",
      "Full inventory management",
      "Unlimited SMS notifications",
      "Advanced marketing campaigns",
      "Complete accounting suite",
      "White-label everything",
      "Unlimited custom domains",
      "Full API access",
      "Priority 24/7 support",
      "Custom integrations",
      "Reseller rights",
      "Dedicated technical support",
      "Custom training & onboarding",
    ],
    cta: "Contact Sales",
    highlighted: false,
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

export default function Pricing() {
  const [isAnnual, setIsAnnual] = useState(false);
  const { data: apiPlans, isLoading } = usePricingPlans();

  // Transform API plans to UI format
  const pricing = (apiPlans || defaultPricing).map((plan: any) => ({
    name: plan.name || "",
    monthlyPrice: plan.monthly_price ?? plan.monthlyPrice ?? 0,
    annualPrice: plan.yearly_price ?? plan.annualPrice ?? 0,
    description: plan.description || "",
    features: Array.isArray(plan.features)
      ? plan.features
      : Object.entries(plan.features || {})
          .filter(
            ([_, featureValue]) =>
              featureValue === true || typeof featureValue === "string",
          )
          .map(([key]) => {
            return key
              .replace(/_/g, " ")
              .replace(/\b\w/g, (l) => l.toUpperCase());
          }),
    cta: (plan.tier_level ?? 0) >= 4 ? "Contact Sales" : "Start Free Trial",
    highlighted: plan.is_featured ?? false,
  }));

  return (
    <div className="min-h-screen bg-background">
      <div className="pt-24 pb-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              viewport={{ once: true }}
            >
              <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold text-foreground mb-4">
                Simple, Transparent Pricing
              </h1>
              <p className="text-xl text-muted-foreground max-w-2xl mx-auto mb-8">
                Choose the perfect plan for your salon business
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

          {isLoading ? (
            <div className="col-span-full text-center py-12">
              <p className="text-muted-foreground">Loading pricing plans...</p>
            </div>
          ) : (
            <motion.div
              variants={containerVariants}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: "-100px" }}
              className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 md:gap-8"
            >
              {pricing.map((plan, idx) => {
                const displayPrice = isAnnual
                  ? plan.annualPrice
                  : plan.monthlyPrice;
                const savings = isAnnual
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
                        {plan.name}
                      </h3>
                      <p className="text-muted-foreground text-xs sm:text-sm mb-6">
                        {plan.description}
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
                            : `₦${displayPrice.toLocaleString()}`}
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
                        {plan.features.map((feature, fidx) => (
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
                        ))}
                      </div>
                    </Card>
                  </motion.div>
                );
              })}
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}
