import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { ChevronDownIcon, InfoIcon } from "@/components/icons";
import { motion, AnimatePresence } from "framer-motion";

export function FAQSection() {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);

  const faqs = [
    {
      question: "How long is the free trial?",
      answer:
        "You get a full 30-day free trial with access to all features. No credit card required to start.",
      icon: <InfoIcon size={20} className="text-primary" />,
    },
    {
      question: "Can I use Kenikool offline?",
      answer:
        "Yes! Our POS system works completely offline. All transactions sync automatically when you're back online.",
      icon: <InfoIcon size={20} className="text-secondary" />,
    },
    {
      question: "What payment methods do you accept?",
      answer:
        "We accept all major Nigerian payment methods through Paystack including cards, bank transfers, and USSD.",
      icon: <InfoIcon size={20} className="text-accent" />,
    },
    {
      question: "Can I cancel anytime?",
      answer:
        "Absolutely! You can cancel your subscription at any time. No long-term contracts or cancellation fees.",
      icon: <InfoIcon size={20} className="text-success" />,
    },
    {
      question: "Do you provide training?",
      answer:
        "Yes! We provide free onboarding training and have 24/7 support to help you get started and answer any questions.",
      icon: <InfoIcon size={20} className="text-primary" />,
    },
    {
      question: "Is my data secure?",
      answer:
        "Your data is protected with enterprise-grade security, encrypted both in transit and at rest. We're fully GDPR compliant.",
      icon: <InfoIcon size={20} className="text-secondary" />,
    },
  ];

  return (
    <section className="py-12 sm:py-16 md:py-20 px-4 sm:px-6 bg-muted/30">
      <div className="container mx-auto max-w-4xl">
        <div className="text-center mb-8 sm:mb-12 animate__animated animate__fadeInDown">
          <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold mb-3 sm:mb-4">
            Frequently Asked Questions
          </h2>
          <p className="text-base sm:text-lg md:text-xl text-muted-foreground">
            Got questions? We've got answers
          </p>
        </div>

        <div className="space-y-3 sm:space-y-4">
          {faqs.map((faq, index) => (
            <motion.div
              key={index}
              className="animate__animated animate__fadeInUp"
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <Card
                hover
                className="cursor-pointer"
                onClick={() =>
                  setExpandedIndex(expandedIndex === index ? null : index)
                }
              >
                <CardContent className="pt-4 sm:pt-6">
                  <div className="flex items-start gap-3 sm:gap-4">
                    <div className="flex-shrink-0 mt-1">{faq.icon}</div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between gap-2">
                        <h3 className="font-bold text-sm sm:text-base text-foreground">
                          {faq.question}
                        </h3>
                        <motion.div
                          animate={{
                            rotate: expandedIndex === index ? 180 : 0,
                          }}
                          transition={{ duration: 0.3 }}
                          className="flex-shrink-0"
                        >
                          <ChevronDownIcon
                            size={20}
                            className="text-muted-foreground"
                          />
                        </motion.div>
                      </div>

                      <AnimatePresence>
                        {expandedIndex === index && (
                          <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: "auto" }}
                            exit={{ opacity: 0, height: 0 }}
                            transition={{ duration: 0.3 }}
                          >
                            <p className="text-xs sm:text-sm text-muted-foreground mt-3">
                              {faq.answer}
                            </p>
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
