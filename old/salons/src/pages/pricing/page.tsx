import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { CheckIcon } from "@/components/icons";
import { Link } from "react-router-dom";
import { Navbar } from "@/components/layout/navbar";
import { LandingFooter } from "@/components/landing/landing-footer";
import { useState } from "react";
import { HelpCircle } from "lucide-react";

export default function PricingPage() {
  const [billingCycle, setBillingCycle] = useState<"monthly" | "annual">(
    "monthly",
  );

  const plans = [
    {
      name: "Free",
      price: "₦0",
      annualPrice: "₦0",
      period: "/month",
      description: "Perfect for trying out Kenikool",
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
      notIncluded: [
        "Offline POS",
        "Inventory management",
        "SMS notifications",
        "Marketing campaigns",
        "Custom domain",
      ],
    },
    {
      name: "Starter",
      price: "₦15,000",
      annualPrice: "₦153,000",
      period: "/month",
      description: "Perfect for small salons just getting started",
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
      notIncluded: [
        "Inventory management",
        "Marketing campaigns",
        "Accounting",
        "Custom domain",
        "API access",
      ],
    },
    {
      name: "Professional",
      price: "₦35,000",
      annualPrice: "₦357,000",
      period: "/month",
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
      notIncluded: ["Accounting", "Custom domain", "API access", "White-label"],
      popular: true,
    },
    {
      name: "Business",
      price: "₦65,000",
      annualPrice: "₦663,000",
      period: "/month",
      description: "For established salons with advanced needs",
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
      notIncluded: ["API access", "White-label options", "Reseller rights"],
    },
    {
      name: "Enterprise",
      price: "₦120,000",
      annualPrice: "₦1,224,000",
      period: "/month",
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
      notIncluded: ["Reseller rights"],
    },
    {
      name: "Unlimited",
      price: "₦250,000",
      annualPrice: "₦2,550,000",
      period: "/month",
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
      notIncluded: [],
    },
  ];

  const addOns = [
    {
      name: "Extra SMS Credits",
      price: "₦5,000",
      description: "1,000 additional SMS notifications",
    },
    {
      name: "Extra Location",
      price: "₦10,000",
      description: "Add one more location to your account",
    },
    {
      name: "Priority Support",
      price: "₦8,000",
      description: "24/7 phone and email support",
    },
    {
      name: "Custom Integration",
      price: "₦15,000",
      description: "Custom API integration setup",
    },
  ];

  const faqs = [
    {
      question: "Can I change my plan anytime?",
      answer:
        "Yes! You can upgrade or downgrade your plan at any time. Changes take effect at the start of your next billing cycle.",
    },
    {
      question: "Is there a setup fee?",
      answer:
        "No setup fees! You can start using Kenikool immediately after signing up. All plans include a 30-day free trial.",
    },
    {
      question: "What payment methods do you accept?",
      answer:
        "We accept all major payment methods including credit cards, bank transfers, and mobile money. All payments are secure and encrypted.",
    },
    {
      question: "Do you offer discounts for annual billing?",
      answer:
        "Yes! Annual plans come with 15% discount compared to monthly billing. That's 2 months free on your annual commitment.",
    },
    {
      question: "What happens if I cancel?",
      answer:
        "You can cancel anytime. Your access continues until the end of your billing period. No hidden fees or penalties.",
    },
    {
      question: "Is there a free trial?",
      answer:
        "Yes! All plans include a 30-day free trial with full access to all features. No credit card required to start.",
    },
  ];

  return (
    <div className="min-h-screen bg-[var(--background)]">
      <Navbar />

      {/* Hero Section */}
      <section className="pt-20 pb-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <h1 className="text-4xl sm:text-5xl font-bold text-[var(--foreground)] mb-4">
              Simple, Transparent Pricing
            </h1>
            <p className="text-xl text-[var(--muted-foreground)] mb-8">
              Choose the perfect plan for your salon. All plans include a 30-day
              free trial.
            </p>

            {/* Billing Toggle */}
            <div className="flex items-center justify-center gap-4 mb-12">
              <span
                className={`text-sm font-medium ${
                  billingCycle === "monthly"
                    ? "text-[var(--foreground)]"
                    : "text-[var(--muted-foreground)]"
                }`}
              >
                Monthly
              </span>
              <button
                onClick={() =>
                  setBillingCycle(
                    billingCycle === "monthly" ? "annual" : "monthly",
                  )
                }
                className="relative inline-flex h-8 w-14 items-center rounded-full bg-[var(--muted)]"
              >
                <span
                  className={`inline-block h-6 w-6 transform rounded-full bg-[var(--background)] transition ${
                    billingCycle === "annual"
                      ? "translate-x-7"
                      : "translate-x-1"
                  }`}
                />
              </button>
              <span
                className={`text-sm font-medium ${
                  billingCycle === "annual"
                    ? "text-[var(--foreground)]"
                    : "text-[var(--muted-foreground)]"
                }`}
              >
                Annual
                <span className="ml-2 inline-block bg-[var(--success)] text-[var(--success-foreground)] text-xs font-semibold px-2 py-1 rounded">
                  S%
                </span>
              </span>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Pricing Cards */}
      <section className="py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {plans.map((plan, index) => (
              <motion.div
                key={plan.name}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
              >
                <Card
                  variant={plan.popular ? "gradient" : "default"}
                  hover
                  className={`relative h-full ${
                    plan.popular
                      ? "ring-2 ring-[var(--primary)] shadow-lg scale-105"
                      : ""
                  }`}
                >
                  {plan.popular && (
                    <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                      <span className="bg-[var(--primary)] text-[var(--primary-foreground)] px-4 py-1 rounded-full text-sm font-semibold">
                        Most Popular
                      </span>
                    </div>
                  )}

                  <CardContent className="p-8">
                    <h3 className="text-2xl font-bold text-[var(--foreground)] mb-2">
                      {plan.name}
                    </h3>
                    <p className="text-[var(--muted-foreground)] text-sm mb-6">
                      {plan.description}
                    </p>

                    <div className="mb-6">
                      <span className="text-4xl font-bold text-[var(--foreground)]">
                        {billingCycle === "monthly"
                          ? plan.price
                          : plan.annualPrice}
                      </span>
                      <span className="text-[var(--muted-foreground)] ml-2">
                        {billingCycle === "annual" ? "/year" : plan.period}
                      </span>
                    </div>

                    <Button
                      variant={plan.popular ? "outline" : "primary"}
                      fullWidth
                      className={`mb-8 ${
                        plan.popular
                          ? "border-[var(--primary-foreground)] text-[var(--primary-foreground)]"
                          : ""
                      }`}
                      asChild
                    >
                      <Link to="/auth/signup">Get Started</Link>
                    </Button>

                    <div className="space-y-4">
                      <div>
                        <h4 className="font-semibold text-[var(--foreground)] mb-3">
                          Included:
                        </h4>
                        <ul className="space-y-2">
                          {plan.features.map((feature) => (
                            <li
                              key={feature}
                              className="flex items-start gap-3"
                            >
                              <CheckIcon className="w-5 h-5 text-[var(--success)] shrink-0 mt-0.5" />
                              <span className="text-[var(--foreground)] text-sm">
                                {feature}
                              </span>
                            </li>
                          ))}
                        </ul>
                      </div>

                      {plan.notIncluded.length > 0 && (
                        <div>
                          <h4 className="font-semibold text-[var(--foreground)] mb-3">
                            Not included:
                          </h4>
                          <ul className="space-y-2">
                            {plan.notIncluded.map((feature) => (
                              <li
                                key={feature}
                                className="flex items-start gap-3"
                              >
                                <span className="w-5 h-5 text-[var(--muted-foreground)] shrink-0 mt-0.5">
                                  ✕
                                </span>
                                <span className="text-[var(--muted-foreground)] text-sm">
                                  {feature}
                                </span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Add-ons Section */}
      <section className="py-12 px-4 sm:px-6 lg:px-8 bg-[var(--muted)]">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center mb-12"
          >
            <h2 className="text-3xl font-bold text-[var(--foreground)] mb-4">
              Add-ons & Extras
            </h2>
            <p className="text-[var(--muted-foreground)]">
              Enhance your plan with additional features
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {addOns.map((addon, index) => (
              <motion.div
                key={addon.name}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
              >
                <Card variant="default" hover>
                  <CardContent className="p-6">
                    <h3 className="font-semibold text-[var(--foreground)] mb-2">
                      {addon.name}
                    </h3>
                    <p className="text-sm text-[var(--muted-foreground)] mb-4">
                      {addon.description}
                    </p>
                    <p className="text-2xl font-bold text-[var(--primary)]">
                      {addon.price}
                      <span className="text-sm text-[var(--muted-foreground)]">
                        /month
                      </span>
                    </p>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-3xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center mb-12"
          >
            <h2 className="text-3xl font-bold text-[var(--foreground)] mb-4">
              Frequently Asked Questions
            </h2>
            <p className="text-[var(--muted-foreground)]">
              Have questions? We've got answers.
            </p>
          </motion.div>

          <div className="space-y-6">
            {faqs.map((faq, index) => (
              <motion.div
                key={faq.question}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.05 }}
              >
                <Card variant="default" hover>
                  <CardContent className="p-6">
                    <div className="flex gap-4">
                      <HelpCircle className="w-6 h-6 text-[var(--primary)] shrink-0 mt-1" />
                      <div>
                        <h3 className="font-semibold text-[var(--foreground)] mb-2">
                          {faq.question}
                        </h3>
                        <p className="text-[var(--muted-foreground)] text-sm">
                          {faq.answer}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-[var(--muted)]">
        <div className="max-w-3xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <h2 className="text-3xl font-bold text-[var(--foreground)] mb-4">
              Ready to get started?
            </h2>
            <p className="text-[var(--muted-foreground)] mb-8">
              Start your 30-day free trial today. No credit card required.
            </p>
            <Button variant="primary" size="lg" asChild>
              <Link to="/auth/signup">Start Free Trial</Link>
            </Button>
          </motion.div>
        </div>
      </section>

      <LandingFooter />
    </div>
  );
}
