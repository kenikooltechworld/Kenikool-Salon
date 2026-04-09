import { useState } from "react";
import { ChevronDownIcon } from "@/components/icons";

interface FAQItem {
  question: string;
  answer: string;
}

const faqItems: FAQItem[] = [
  {
    question: "How do I book an appointment?",
    answer:
      "Select your desired service, choose a staff member, pick a time slot, and fill in your details. You can pay now or later.",
  },
  {
    question: "Can I cancel or reschedule?",
    answer:
      "Yes, you can cancel or reschedule up to 24 hours before your appointment. Use the links in your confirmation email.",
  },
  {
    question: "What payment methods do you accept?",
    answer:
      "We accept all major credit cards, debit cards, and mobile money payments through our secure payment gateway.",
  },
  {
    question: "What is your cancellation policy?",
    answer:
      "Cancellations made 24 hours before the appointment are free. Cancellations within 24 hours may incur a fee.",
  },
  {
    question: "How will I receive reminders?",
    answer:
      "We send email and SMS reminders 24 hours and 1 hour before your appointment. You can manage your preferences anytime.",
  },
  {
    question: "What if I am late?",
    answer:
      "Please arrive on time. If you are running late, contact us immediately. We may need to reschedule if you are more than 15 minutes late.",
  },
];

export default function PublicFAQSection() {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);

  const toggleExpand = (index: number) => {
    setExpandedIndex(expandedIndex === index ? null : index);
  };

  const handleKeyDown = (e: React.KeyboardEvent, index: number) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      toggleExpand(index);
    } else if (e.key === "ArrowDown") {
      e.preventDefault();
      setExpandedIndex(Math.min(index + 1, faqItems.length - 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setExpandedIndex(Math.max(index - 1, 0));
    }
  };

  return (
    <section className="w-full py-16 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        <h2 className="text-3xl font-bold text-center mb-12">
          Frequently Asked Questions
        </h2>

        <div className="space-y-4">
          {faqItems.map((item, index) => (
            <div
              key={index}
              className="border border-border rounded-lg overflow-hidden"
            >
              <button
                onClick={() => toggleExpand(index)}
                onKeyDown={(e) => handleKeyDown(e, index)}
                className="w-full px-6 py-4 flex items-center justify-between hover:bg-muted transition-colors text-left"
                aria-expanded={expandedIndex === index}
              >
                <span className="font-semibold">{item.question}</span>
                <ChevronDownIcon
                  size={20}
                  className={`transition-transform ${
                    expandedIndex === index ? "rotate-180" : ""
                  }`}
                />
              </button>

              {expandedIndex === index && (
                <div className="px-6 py-4 bg-muted/50 border-t border-border">
                  <p className="text-muted-foreground">{item.answer}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
