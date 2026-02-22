import { motion } from "framer-motion";
import { Navbar } from "@/components/layout/navbar";
import { LandingFooter } from "@/components/landing/landing-footer";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import { HelpCircle, MessageSquare, FileText, Mail } from "lucide-react";

export default function HelpPage() {
  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Navbar />
      <main className="flex-1">
        <div className="container mx-auto px-4 py-16">
          <motion.div
            className="max-w-4xl mx-auto"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <h1 className="text-4xl font-bold mb-4">Help Center</h1>
            <p className="text-xl text-muted-foreground mb-12">
              Find answers to common questions and get support
            </p>

            {/* Help Categories */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-16">
              {[
                {
                  icon: HelpCircle,
                  title: "Getting Started",
                  description:
                    "Learn how to set up your account and get started with Kenikool",
                  link: "#getting-started",
                },
                {
                  icon: MessageSquare,
                  title: "FAQ",
                  description: "Find answers to frequently asked questions",
                  link: "#faq",
                },
                {
                  icon: FileText,
                  title: "Documentation",
                  description:
                    "Read our comprehensive documentation and guides",
                  link: "#documentation",
                },
                {
                  icon: Mail,
                  title: "Contact Support",
                  description: "Get in touch with our support team",
                  link: "/contact",
                },
              ].map((item, idx) => {
                const Icon = item.icon;
                return (
                  <motion.div
                    key={idx}
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.6, delay: idx * 0.1 }}
                  >
                    <Link to={item.link}>
                      <div className="bg-card border border-border rounded-lg p-8 hover:border-primary transition-colors cursor-pointer h-full">
                        <Icon className="w-12 h-12 text-primary mb-4" />
                        <h3 className="text-xl font-bold mb-2">{item.title}</h3>
                        <p className="text-muted-foreground">
                          {item.description}
                        </p>
                      </div>
                    </Link>
                  </motion.div>
                );
              })}
            </div>

            {/* FAQ Section */}
            <section id="faq" className="mb-16">
              <h2 className="text-3xl font-bold mb-8">
                Frequently Asked Questions
              </h2>
              <div className="space-y-4">
                {[
                  {
                    q: "How do I create an account?",
                    a: "Click on 'Get Started' and follow the registration process. You'll need to provide your email and create a password.",
                  },
                  {
                    q: "How do I book an appointment?",
                    a: "Browse salons in the marketplace, select a service, choose a time slot, and complete the booking.",
                  },
                  {
                    q: "Can I cancel my booking?",
                    a: "Yes, you can cancel bookings up to 24 hours before the appointment time.",
                  },
                  {
                    q: "How do I reset my password?",
                    a: "Click 'Forgot Password' on the login page and follow the instructions sent to your email.",
                  },
                  {
                    q: "Is my payment information secure?",
                    a: "Yes, we use industry-standard encryption to protect all payment information.",
                  },
                ].map((faq, idx) => (
                  <motion.div
                    key={idx}
                    className="bg-card border border-border rounded-lg p-6"
                    initial={{ opacity: 0, y: 10 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.6, delay: idx * 0.05 }}
                  >
                    <h3 className="font-bold text-lg mb-2">{faq.q}</h3>
                    <p className="text-muted-foreground">{faq.a}</p>
                  </motion.div>
                ))}
              </div>
            </section>

            {/* CTA Section */}
            <section className="bg-linear-to-r from-primary/10 to-secondary/10 rounded-lg p-12 text-center">
              <h2 className="text-3xl font-bold mb-4">Still need help?</h2>
              <p className="text-lg text-muted-foreground mb-8">
                Our support team is here to help you 24/7
              </p>
              <Link to="/contact">
                <Button size="lg" className="bg-primary hover:bg-primary/90">
                  Contact Support
                </Button>
              </Link>
            </section>
          </motion.div>
        </div>
      </main>
      <LandingFooter />
    </div>
  );
}
