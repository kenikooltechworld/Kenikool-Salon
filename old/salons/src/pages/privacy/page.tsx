import { motion } from "framer-motion";
import { Navbar } from "@/components/layout/navbar";
import { LandingFooter } from "@/components/landing/landing-footer";

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Navbar />
      <main className="flex-1">
        <div className="container mx-auto px-4 py-16 max-w-4xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <h1 className="text-4xl font-bold mb-8">Privacy Policy</h1>
            <div className="prose prose-invert max-w-none space-y-6">
              <section>
                <h2 className="text-2xl font-bold mb-4">1. Introduction</h2>
                <p className="text-muted-foreground leading-relaxed">
                  Kenikool ("we", "us", "our") operates the Kenikool platform.
                  This page informs you of our policies regarding the
                  collection, use, and disclosure of personal data when you use
                  our Service and the choices you have associated with that
                  data.
                </p>
              </section>

              <section>
                <h2 className="text-2xl font-bold mb-4">
                  2. Information Collection and Use
                </h2>
                <p className="text-muted-foreground leading-relaxed">
                  We collect several different types of information for various
                  purposes to provide and improve our Service to you.
                </p>
                <ul className="list-disc list-inside space-y-2 text-muted-foreground mt-4">
                  <li>
                    Personal Data: Name, email address, phone number, location
                  </li>
                  <li>
                    Usage Data: Browser type, IP address, pages visited, time
                    spent
                  </li>
                  <li>
                    Cookies and Tracking: We use cookies to track activity on
                    our Service
                  </li>
                </ul>
              </section>

              <section>
                <h2 className="text-2xl font-bold mb-4">3. Use of Data</h2>
                <p className="text-muted-foreground leading-relaxed">
                  Kenikool uses the collected data for various purposes:
                </p>
                <ul className="list-disc list-inside space-y-2 text-muted-foreground mt-4">
                  <li>To provide and maintain our Service</li>
                  <li>To notify you about changes to our Service</li>
                  <li>To allow you to participate in interactive features</li>
                  <li>To provide customer support</li>
                  <li>
                    To gather analysis or valuable information for improving our
                    Service
                  </li>
                  <li>To monitor the usage of our Service</li>
                </ul>
              </section>

              <section>
                <h2 className="text-2xl font-bold mb-4">4. Security of Data</h2>
                <p className="text-muted-foreground leading-relaxed">
                  The security of your data is important to us but remember that
                  no method of transmission over the Internet or method of
                  electronic storage is 100% secure. While we strive to use
                  commercially acceptable means to protect your Personal Data,
                  we cannot guarantee its absolute security.
                </p>
              </section>

              <section>
                <h2 className="text-2xl font-bold mb-4">
                  5. Changes to This Privacy Policy
                </h2>
                <p className="text-muted-foreground leading-relaxed">
                  We may update our Privacy Policy from time to time. We will
                  notify you of any changes by posting the new Privacy Policy on
                  this page and updating the "effective date" at the top of this
                  Privacy Policy.
                </p>
              </section>

              <section>
                <h2 className="text-2xl font-bold mb-4">6. Contact Us</h2>
                <p className="text-muted-foreground leading-relaxed">
                  If you have any questions about this Privacy Policy, please
                  contact us at:
                </p>
                <p className="text-muted-foreground mt-4">
                  Email: privacy@kenikool.com
                  <br />
                  Address: Lagos, Nigeria
                </p>
              </section>
            </div>
          </motion.div>
        </div>
      </main>
      <LandingFooter />
    </div>
  );
}
