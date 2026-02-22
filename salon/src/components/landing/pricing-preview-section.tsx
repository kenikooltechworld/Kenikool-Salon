import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { CheckCircleIcon } from "@/components/icons";

const pricing = [
  {
    name: "Starter",
    monthlyPrice: 29,
    annualPrice: 290,
    description: "Perfect for small salons",
    features: [
      "Up to 5 staff members",
      "Unlimited appointments",
      "Basic analytics",
      "Email support",
      "Mobile app access",
    ],
    cta: "Start Free Trial",
    highlighted: false,
  },
  {
    name: "Professional",
    monthlyPrice: 79,
    annualPrice: 790,
    description: "For growing businesses",
    features: [
      "Up to 20 staff members",
      "Advanced analytics",
      "Custom branding",
      "Priority support",
      "API access",
      "Team collaboration",
    ],
    cta: "Start Free Trial",
    highlighted: true,
  },
  {
    name: "Enterprise",
    monthlyPrice: 199,
    annualPrice: 1990,
    description: "For large operations",
    features: [
      "Unlimited staff",
      "Multi-location support",
      "Custom integrations",
      "Dedicated account manager",
      "Advanced security",
      "SLA guarantee",
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

export function PricingPreviewSection() {
  const [isAnnual, setIsAnnual] = useState(false);

  return (
    <section id="pricing" className="py-20 sm:py-32 bg-background">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          className="text-center mb-16"
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

          {/* Billing Toggle */}
          <motion.div
            className="flex items-center justify-center gap-4 mb-12"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            viewport={{ once: true }}
          >
            <span
              className={`text-sm font-medium ${
                !isAnnual ? "text-foreground" : "text-muted-foreground"
              }`}
            >
              Monthly
            </span>
            <button
              onClick={() => setIsAnnual(!isAnnual)}
              className="relative inline-flex h-8 w-14 items-center rounded-full bg-muted"
            >
              <motion.span
                className="inline-block h-6 w-6 transform rounded-full bg-primary"
                animate={{ x: isAnnual ? 28 : 4 }}
                transition={{ type: "spring", stiffness: 500, damping: 30 }}
              />
            </button>
            <span
              className={`text-sm font-medium ${
                isAnnual ? "text-foreground" : "text-muted-foreground"
              }`}
            >
              Annual
            </span>
            {isAnnual && (
              <motion.span
                className="ml-2 inline-block bg-accent text-white text-xs font-semibold px-3 py-1 rounded-full"
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ type: "spring", stiffness: 500, damping: 30 }}
              >
                Save 20%
              </motion.span>
            )}
          </motion.div>
        </motion.div>

        <motion.div
          className="grid grid-cols-1 md:grid-cols-3 gap-6 md:gap-8"
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
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
                  className={`p-8 flex flex-col h-full transition-all duration-300 ${
                    plan.highlighted
                      ? "ring-2 ring-primary shadow-lg md:scale-105"
                      : ""
                  }`}
                >
                  {plan.highlighted && (
                    <div className="bg-primary text-white text-sm font-semibold px-3 py-1 rounded-full w-fit mb-4">
                      Most Popular
                    </div>
                  )}

                  <h3 className="text-2xl font-bold text-foreground mb-2">
                    {plan.name}
                  </h3>
                  <p className="text-muted-foreground text-sm mb-6">
                    {plan.description}
                  </p>

                  <motion.div
                    className="mb-6"
                    key={isAnnual ? "annual" : "monthly"}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    <span className="text-4xl font-bold text-foreground">
                      ₦{displayPrice.toLocaleString()}
                    </span>
                    <span className="text-muted-foreground text-sm ml-2">
                      {isAnnual ? "/year" : "/month"}
                    </span>
                    {savings > 0 && (
                      <div className="text-xs text-accent font-semibold mt-2">
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
                        className="flex items-start gap-3"
                        initial={{ opacity: 0, x: -10 }}
                        whileInView={{ opacity: 1, x: 0 }}
                        transition={{ delay: fidx * 0.05 }}
                        viewport={{ once: true }}
                      >
                        <CheckCircleIcon className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" />
                        <span className="text-foreground text-sm">
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
      </div>
    </section>
  );
}
