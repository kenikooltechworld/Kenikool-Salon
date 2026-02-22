import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { CheckIcon } from "@/components/icons";
import { motion } from "framer-motion";
import { useState } from "react";

export function PricingPreviewSection() {
  const [billingCycle, setBillingCycle] = useState<"monthly" | "annual">(
    "monthly",
  );

  const plans = [
    {
      name: "Free",
      price: "₦0",
      annualPrice: "₦0",
      period: "/month",
      description: "Try Kenikool free",
      features: [
        "1 staff member",
        "50 bookings/month",
        "100 clients",
        "Basic analytics",
        "Mobile app",
      ],
    },
    {
      name: "Starter",
      price: "₦15,000",
      annualPrice: "₦153,000",
      period: "/month",
      description: "For small salons",
      features: [
        "Up to 3 staff",
        "Unlimited bookings",
        "500 clients",
        "Offline POS",
        "100 SMS/month",
      ],
    },
    {
      name: "Professional",
      price: "₦35,000",
      annualPrice: "₦357,000",
      period: "/month",
      description: "Most popular",
      features: [
        "Up to 10 staff",
        "2,000 clients",
        "Inventory management",
        "500 SMS/month",
        "Marketing campaigns",
      ],
      popular: true,
    },
    {
      name: "Business",
      price: "₦65,000",
      annualPrice: "₦663,000",
      period: "/month",
      description: "For growing salons",
      features: [
        "Up to 25 staff",
        "Unlimited clients",
        "Accounting suite",
        "2,000 SMS/month",
        "Custom domain",
      ],
    },
    {
      name: "Enterprise",
      price: "₦120,000",
      annualPrice: "₦1,224,000",
      period: "/month",
      description: "Multi-location",
      features: [
        "Up to 50 staff",
        "3 locations",
        "White-label",
        "5,000 SMS/month",
        "API access",
      ],
    },
    {
      name: "Unlimited",
      price: "₦250,000",
      annualPrice: "₦2,550,000",
      period: "/month",
      description: "For resellers",
      features: [
        "Unlimited everything",
        "Reseller rights",
        "Unlimited locations",
        "Unlimited SMS",
        "Full API access",
      ],
    },
  ];

  // Animation variants
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
      transition: {
        duration: 0.6,
        ease: "easeOut",
      },
    },
  };

  const headerVariants = {
    hidden: { opacity: 0, y: -20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.6,
        ease: "easeOut",
      },
    },
  };

  const toggleVariants = {
    hidden: { opacity: 0, scale: 0.95 },
    visible: {
      opacity: 1,
      scale: 1,
      transition: {
        duration: 0.5,
        ease: "easeOut",
      },
    },
  };

  const cardHoverVariants = {
    rest: {
      scale: 1,
      boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)",
    },
    hover: {
      scale: 1.05,
      boxShadow: "0 20px 25px rgba(0, 0, 0, 0.15)",
      transition: {
        duration: 0.3,
        ease: "easeOut",
      },
    },
  };

  const priceVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        duration: 0.4,
      },
    },
  };

  const featureVariants = {
    hidden: { opacity: 0, x: -10 },
    visible: (i: number) => ({
      opacity: 1,
      x: 0,
      transition: {
        delay: i * 0.05,
        duration: 0.3,
      },
    }),
  };

  const toggleButtonVariants = {
    rest: {
      scale: 1,
      backgroundColor: "transparent",
    },
    hover: {
      scale: 1.05,
      transition: {
        duration: 0.2,
      },
    },
    active: {
      scale: 0.98,
      transition: {
        duration: 0.1,
      },
    },
  };

  const savingsBadgeVariants = {
    hidden: { opacity: 0, scale: 0.8 },
    visible: {
      opacity: 1,
      scale: 1,
      transition: {
        duration: 0.4,
        ease: "easeOut",
      },
    },
  };

  const getDisplayPrice = (plan: (typeof plans)[0]) => {
    return billingCycle === "annual" ? plan.annualPrice : plan.price;
  };

  const calculateSavings = (plan: (typeof plans)[0]) => {
    const monthlyTotal = parseInt(plan.price.replace(/[^0-9]/g, "")) * 12;
    const annualPrice = parseInt(plan.annualPrice.replace(/[^0-9]/g, ""));
    const savings = monthlyTotal - annualPrice;
    const savingsPercent = Math.round((savings / monthlyTotal) * 100);
    return { savings, savingsPercent };
  };

  return (
    <section className="py-12 sm:py-16 md:py-20 px-4 sm:px-6" id="pricing">
      <div className="container mx-auto">
        {/* Header */}
        <motion.div
          className="text-center mb-8 sm:mb-12"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          variants={headerVariants}
        >
          <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold mb-3 sm:mb-4">
            Simple, Transparent Pricing
          </h2>
          <p className="text-base sm:text-lg md:text-xl text-muted-foreground px-2">
            Choose the plan that fits your salon. All plans include 30-day free
            trial.
          </p>
        </motion.div>

        {/* Billing Toggle */}
        <motion.div
          className="flex justify-center mb-8 sm:mb-12"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          variants={toggleVariants}
        >
          <div className="inline-flex bg-muted rounded-full p-1 shadow-md">
            {["monthly", "annual"].map((cycle) => (
              <motion.button
                key={cycle}
                onClick={() => setBillingCycle(cycle as "monthly" | "annual")}
                className={`px-4 sm:px-6 py-2 rounded-full font-medium transition-all text-sm sm:text-base ${
                  billingCycle === cycle
                    ? "bg-primary text-white shadow-lg"
                    : "text-muted-foreground hover:text-foreground"
                }`}
                variants={toggleButtonVariants}
                initial="rest"
                whileHover="hover"
                whileTap="active"
              >
                {cycle === "monthly" ? "Monthly" : "Annual (Save 20%)"}
              </motion.button>
            ))}
          </div>
        </motion.div>

        {/* Pricing Cards */}
        <motion.div
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 max-w-7xl mx-auto mb-8"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          variants={containerVariants}
        >
          {plans.slice(0, 3).map((plan, index) => (
            <motion.div key={index} variants={itemVariants} custom={index}>
              <motion.div
                variants={cardHoverVariants}
                initial="rest"
                whileHover="hover"
              >
                <Card
                  hover
                  variant={plan.popular ? "gradient" : "default"}
                  className="relative h-full overflow-hidden"
                >
                  {plan.popular && (
                    <motion.div
                      className="absolute -top-3 sm:-top-4 left-1/2 -translate-x-1/2 bg-accent text-white px-3 sm:px-4 py-1 rounded-full text-xs sm:text-sm font-semibold"
                      variants={savingsBadgeVariants}
                      initial="hidden"
                      whileInView="visible"
                      viewport={{ once: true }}
                    >
                      Most Popular
                    </motion.div>
                  )}

                  {billingCycle === "annual" && (
                    <motion.div
                      className="absolute top-4 right-4 bg-green-500 text-white px-2 sm:px-3 py-1 rounded text-xs font-semibold"
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ duration: 0.3 }}
                    >
                      Save {calculateSavings(plan).savingsPercent}%
                    </motion.div>
                  )}

                  <CardContent className="pt-6 sm:pt-8">
                    <h3 className="text-xl sm:text-2xl font-bold mb-2">
                      {plan.name}
                    </h3>
                    <p
                      className={
                        plan.popular
                          ? "text-white/90 mb-4 text-sm sm:text-base"
                          : "text-muted-foreground mb-4 text-sm sm:text-base"
                      }
                    >
                      {plan.description}
                    </p>

                    {/* Price with Animation */}
                    <motion.div
                      className="mb-6 overflow-hidden"
                      key={billingCycle}
                      variants={priceVariants}
                      initial="hidden"
                      animate="visible"
                    >
                      <span className="text-3xl sm:text-4xl font-bold">
                        {getDisplayPrice(plan)}
                      </span>
                      <span
                        className={
                          plan.popular
                            ? "text-white/90 text-sm sm:text-base"
                            : "text-muted-foreground text-sm sm:text-base"
                        }
                      >
                        {billingCycle === "annual" ? "/year" : "/month"}
                      </span>
                    </motion.div>

                    {/* Features List with Stagger Animation */}
                    <ul className="space-y-2 sm:space-y-3 mb-6">
                      {plan.features.map((feature, i) => (
                        <motion.li
                          key={i}
                          className="flex items-start gap-2"
                          variants={featureVariants}
                          initial="hidden"
                          whileInView="visible"
                          viewport={{ once: true }}
                          custom={i}
                        >
                          <CheckIcon
                            size={16}
                            className={
                              plan.popular
                                ? "text-white shrink-0 mt-0.5"
                                : "text-success shrink-0 mt-0.5"
                            }
                          />
                          <span
                            className={`text-sm sm:text-base ${plan.popular ? "text-white/90" : ""}`}
                          >
                            {feature}
                          </span>
                        </motion.li>
                      ))}
                    </ul>

                    {/* CTA Button */}
                    <Link to="/register" className="block">
                      <motion.div
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                      >
                        <Button
                          variant={plan.popular ? "outline" : "primary"}
                          fullWidth
                          className={`text-sm sm:text-base transition-all ${
                            plan.popular
                              ? "border-white text-white hover:bg-white/20"
                              : ""
                          }`}
                        >
                          Start Free Trial
                        </Button>
                      </motion.div>
                    </Link>
                  </CardContent>
                </Card>
              </motion.div>
            </motion.div>
          ))}
        </motion.div>

        {/* Footer CTA */}
        <motion.div
          className="text-center"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          variants={itemVariants}
        >
          <p className="text-muted-foreground mb-4 text-sm sm:text-base px-2">
            Need more? Check out our Enterprise and Unlimited plans
          </p>
          <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
            <Link to="/pricing" className="inline-block">
              <Button variant="outline" className="text-sm sm:text-base">
                View All Pricing Plans
              </Button>
            </Link>
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
}
