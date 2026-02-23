import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

const faqs = [
  {
    question: "How do I book an appointment?",
    answer:
      "Simply select your desired service, choose a staff member, pick a time slot, and fill in your details. You'll receive a confirmation email immediately.",
  },
  {
    question: "Can I cancel or reschedule my appointment?",
    answer:
      "Yes! You can cancel or reschedule your appointment up to 24 hours before your scheduled time. You'll find the options in your confirmation email.",
  },
  {
    question: "What payment methods do you accept?",
    answer:
      "We accept all major credit cards, debit cards, and mobile money payments. You can choose to pay now or pay when you arrive.",
  },
  {
    question: "What is your cancellation policy?",
    answer:
      "Cancellations made 24 hours or more before your appointment are free. Cancellations within 24 hours may incur a fee. Refunds are processed within 3-5 business days.",
  },
  {
    question: "How will I receive reminders?",
    answer:
      "We'll send you email reminders 24 hours and 1 hour before your appointment. You can customize your notification preferences in your booking confirmation.",
  },
  {
    question: "What if I'm late?",
    answer:
      "Please arrive on time to ensure you receive the full duration of your service. If you're running late, contact us as soon as possible.",
  },
  {
    question: "Do you offer group bookings?",
    answer:
      "Yes! For group bookings of 3 or more people, please contact us directly for special arrangements and pricing.",
  },
  {
    question: "How do I leave a review?",
    answer:
      "After your appointment is completed, you'll receive an email with a link to leave a review. Your feedback helps us improve our services!",
  },
];

export default function PublicFAQSection() {
  const [openIndex, setOpenIndex] = useState<number | null>(0);

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

  return (
    <section className="py-20 sm:py-32 bg-gradient-to-br from-primary/5 to-secondary/5">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
          >
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-foreground mb-4">
              Frequently Asked Questions
            </h2>
            <p className="text-lg text-muted-foreground">
              Find answers to common questions about booking with us
            </p>
          </motion.div>
        </div>

        <div className="space-y-4">
          <motion.div
            variants={containerVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-100px" }}
          >
            {faqs.map((faq, idx) => (
              <div
                key={idx}
                className="border border-border rounded-lg overflow-hidden"
              >
                <motion.div variants={itemVariants}>
                  <button
                    onClick={() => setOpenIndex(openIndex === idx ? null : idx)}
                    className="w-full px-6 py-4 flex items-center justify-between hover:bg-muted transition"
                  >
                    <span className="font-semibold text-foreground text-left">
                      {faq.question}
                    </span>
                    <div className="text-primary inline-block">
                      <motion.span
                        animate={{ rotate: openIndex === idx ? 180 : 0 }}
                        transition={{ duration: 0.3 }}
                      >
                        ▼
                      </motion.span>
                    </div>
                  </button>
                  <AnimatePresence>
                    {openIndex === idx && (
                      <div className="px-6 py-4 bg-muted border-t border-border">
                        <motion.div
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: "auto" }}
                          exit={{ opacity: 0, height: 0 }}
                          transition={{ duration: 0.3 }}
                        >
                          <p className="text-muted-foreground">{faq.answer}</p>
                        </motion.div>
                      </div>
                    )}
                  </AnimatePresence>
                </motion.div>
              </div>
            ))}
          </motion.div>
        </div>
      </div>
    </section>
  );
}
