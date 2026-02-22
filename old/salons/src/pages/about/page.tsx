import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import { Users, Zap, Heart, TrendingUp, Award, Globe } from "lucide-react";
import { Navbar } from "@/components/layout/navbar";
import { LandingFooter } from "@/components/landing/landing-footer";

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Navbar />
      <main className="flex-1">
        {/* Hero Section with Background */}
        <section className="relative py-20 px-4 sm:px-6 overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-transparent to-secondary/10" />
          <div className="container mx-auto relative z-10">
            <motion.div
              className="max-w-3xl mx-auto text-center"
              initial={{ opacity: 0, y: -30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
            >
              <h1 className="text-5xl sm:text-6xl font-bold mb-6 bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
                About Kenikool
              </h1>
              <p className="text-xl text-muted-foreground mb-8">
                Empowering Nigerian salon owners with cutting-edge technology to
                transform their business and achieve unprecedented growth.
              </p>
              <div className="flex gap-4 justify-center flex-wrap">
                <div className="text-center">
                  <div className="text-3xl font-bold text-primary">500+</div>
                  <p className="text-sm text-muted-foreground">Active Salons</p>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-primary">50K+</div>
                  <p className="text-sm text-muted-foreground">Happy Clients</p>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-primary">₦2B+</div>
                  <p className="text-sm text-muted-foreground">
                    Bookings Processed
                  </p>
                </div>
              </div>
            </motion.div>
          </div>
        </section>

        {/* Mission & Vision */}
        <section className="py-20 px-4 sm:px-6">
          <div className="container mx-auto">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
              <motion.div
                initial={{ opacity: 0, x: -50 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.8 }}
              >
                <div className="bg-gradient-to-br from-primary/20 to-secondary/20 rounded-2xl p-12 h-96 flex items-center justify-center">
                  <div className="text-center">
                    <Zap className="w-24 h-24 mx-auto text-primary mb-4" />
                    <p className="text-lg font-semibold">
                      Transforming Salon Management
                    </p>
                  </div>
                </div>
              </motion.div>
              <motion.div
                initial={{ opacity: 0, x: 50 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.8 }}
              >
                <h2 className="text-4xl font-bold mb-6">Our Mission</h2>
                <p className="text-lg text-muted-foreground mb-4">
                  At Kenikool, we believe every salon owner deserves access to
                  world-class business management tools. We're on a mission to
                  revolutionize how salons operate across Nigeria.
                </p>
                <p className="text-lg text-muted-foreground mb-6">
                  Our platform simplifies operations, enhances customer
                  experiences, and empowers salon owners to focus on what they
                  do best—delivering exceptional beauty services.
                </p>
                <ul className="space-y-3">
                  {[
                    "Intuitive & Easy to Use",
                    "Affordable Pricing",
                    "Nigerian-Focused Solutions",
                  ].map((item, i) => (
                    <li key={i} className="flex items-center gap-3">
                      <div className="w-2 h-2 bg-primary rounded-full" />
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </motion.div>
            </div>
          </div>
        </section>

        {/* Core Values */}
        <section className="py-20 px-4 sm:px-6 bg-muted/50">
          <div className="container mx-auto">
            <motion.h2
              className="text-4xl font-bold mb-16 text-center"
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
            >
              Our Core Values
            </motion.h2>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {[
                {
                  icon: Zap,
                  title: "Innovation",
                  description:
                    "We continuously innovate to bring cutting-edge features that solve real salon management challenges.",
                },
                {
                  icon: Award,
                  title: "Excellence",
                  description:
                    "We maintain the highest standards of quality, reliability, and performance in everything we do.",
                },
                {
                  icon: Heart,
                  title: "Customer First",
                  description:
                    "Every feature we build is driven by feedback and needs from salon owners like you.",
                },
              ].map((value, idx) => {
                const Icon = value.icon;
                return (
                  <motion.div
                    key={idx}
                    className="bg-card rounded-xl p-8 border border-border hover:border-primary transition-colors"
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.6, delay: idx * 0.1 }}
                    whileHover={{ y: -5 }}
                  >
                    <Icon className="w-12 h-12 text-primary mb-4" />
                    <h3 className="text-2xl font-bold mb-3">{value.title}</h3>
                    <p className="text-muted-foreground">{value.description}</p>
                  </motion.div>
                );
              })}
            </div>
          </div>
        </section>

        {/* Why Choose Us */}
        <section className="py-20 px-4 sm:px-6">
          <div className="container mx-auto">
            <motion.h2
              className="text-4xl font-bold mb-16 text-center"
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
            >
              Why Choose Kenikool?
            </motion.h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {[
                {
                  icon: TrendingUp,
                  title: "Grow Your Revenue",
                  description:
                    "Our tools help you increase bookings, reduce no-shows, and maximize client lifetime value.",
                },
                {
                  icon: Users,
                  title: "Better Client Management",
                  description:
                    "Keep track of all your clients, preferences, and booking history in one place.",
                },
                {
                  icon: Globe,
                  title: "Online Presence",
                  description:
                    "Get discovered by more clients with our integrated marketplace and booking system.",
                },
                {
                  icon: Award,
                  title: "Industry Leading Support",
                  description:
                    "Our dedicated team is here to help you succeed with 24/7 customer support.",
                },
              ].map((item, idx) => {
                const Icon = item.icon;
                return (
                  <motion.div
                    key={idx}
                    className="flex gap-6 p-6 rounded-lg border border-border hover:bg-muted/50 transition-colors"
                    initial={{ opacity: 0, x: idx % 2 === 0 ? -30 : 30 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.6, delay: idx * 0.1 }}
                  >
                    <Icon className="w-10 h-10 text-primary flex-shrink-0 mt-1" />
                    <div>
                      <h3 className="text-xl font-bold mb-2">{item.title}</h3>
                      <p className="text-muted-foreground">
                        {item.description}
                      </p>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-20 px-4 sm:px-6 bg-gradient-to-r from-primary/10 to-secondary/10">
          <div className="container mx-auto max-w-3xl text-center">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
            >
              <h2 className="text-4xl font-bold mb-6">
                Ready to Transform Your Salon?
              </h2>
              <p className="text-xl text-muted-foreground mb-10">
                Join hundreds of salon owners already using Kenikool to
                streamline operations and grow their business.
              </p>
              <div className="flex gap-4 justify-center flex-wrap">
                <Link to="/auth/register">
                  <Button
                    size="lg"
                    className="bg-primary hover:bg-primary/90 text-lg px-8"
                  >
                    Get Started Free
                  </Button>
                </Link>
                <Link to="/contact">
                  <Button size="lg" variant="outline" className="text-lg px-8">
                    Schedule Demo
                  </Button>
                </Link>
              </div>
            </motion.div>
          </div>
        </section>
      </main>
      <LandingFooter />
    </div>
  );
}
