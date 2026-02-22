import { motion } from "framer-motion";
import { Navbar } from "@/components/layout/navbar";
import { LandingFooter } from "@/components/landing/landing-footer";

export default function TermsPage() {
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
            <h1 className="text-4xl font-bold mb-8">Terms of Service</h1>
            <div className="prose prose-invert max-w-none space-y-6">
              <section>
                <h2 className="text-2xl font-bold mb-4">
                  1. Agreement to Terms
                </h2>
                <p className="text-muted-foreground leading-relaxed">
                  By accessing and using the Kenikool platform, you accept and
                  agree to be bound by the terms and provision of this
                  agreement. If you do not agree to abide by the above, please
                  do not use this service.
                </p>
              </section>

              <section>
                <h2 className="text-2xl font-bold mb-4">2. Use License</h2>
                <p className="text-muted-foreground leading-relaxed">
                  Permission is granted to temporarily download one copy of the
                  materials (information or software) on Kenikool's platform for
                  personal, non-commercial transitory viewing only. This is the
                  grant of a license, not a transfer of title, and under this
                  license you may not:
                </p>
                <ul className="list-disc list-inside space-y-2 text-muted-foreground mt-4">
                  <li>Modify or copy the materials</li>
                  <li>
                    Use the materials for any commercial purpose or for any
                    public display
                  </li>
                  <li>
                    Attempt to decompile or reverse engineer any software
                    contained on the platform
                  </li>
                  <li>
                    Remove any copyright or other proprietary notations from the
                    materials
                  </li>
                  <li>
                    Transfer the materials to another person or "mirror" the
                    materials on any other server
                  </li>
                </ul>
              </section>

              <section>
                <h2 className="text-2xl font-bold mb-4">3. Disclaimer</h2>
                <p className="text-muted-foreground leading-relaxed">
                  The materials on Kenikool's platform are provided on an 'as
                  is' basis. Kenikool makes no warranties, expressed or implied,
                  and hereby disclaims and negates all other warranties
                  including, without limitation, implied warranties or
                  conditions of merchantability, fitness for a particular
                  purpose, or non-infringement of intellectual property or other
                  violation of rights.
                </p>
              </section>

              <section>
                <h2 className="text-2xl font-bold mb-4">4. Limitations</h2>
                <p className="text-muted-foreground leading-relaxed">
                  In no event shall Kenikool or its suppliers be liable for any
                  damages (including, without limitation, damages for loss of
                  data or profit, or due to business interruption) arising out
                  of the use or inability to use the materials on Kenikool's
                  platform.
                </p>
              </section>

              <section>
                <h2 className="text-2xl font-bold mb-4">
                  5. Accuracy of Materials
                </h2>
                <p className="text-muted-foreground leading-relaxed">
                  The materials appearing on Kenikool's platform could include
                  technical, typographical, or photographic errors. Kenikool
                  does not warrant that any of the materials on its platform are
                  accurate, complete, or current. Kenikool may make changes to
                  the materials contained on its platform at any time without
                  notice.
                </p>
              </section>

              <section>
                <h2 className="text-2xl font-bold mb-4">6. Links</h2>
                <p className="text-muted-foreground leading-relaxed">
                  Kenikool has not reviewed all of the sites linked to its
                  platform and is not responsible for the contents of any such
                  linked site. The inclusion of any link does not imply
                  endorsement by Kenikool of the site. Use of any such linked
                  website is at the user's own risk.
                </p>
              </section>

              <section>
                <h2 className="text-2xl font-bold mb-4">7. Modifications</h2>
                <p className="text-muted-foreground leading-relaxed">
                  Kenikool may revise these terms of service for its platform at
                  any time without notice. By using this platform, you are
                  agreeing to be bound by the then current version of these
                  terms of service.
                </p>
              </section>

              <section>
                <h2 className="text-2xl font-bold mb-4">8. Governing Law</h2>
                <p className="text-muted-foreground leading-relaxed">
                  These terms and conditions are governed by and construed in
                  accordance with the laws of Nigeria, and you irrevocably
                  submit to the exclusive jurisdiction of the courts in that
                  location.
                </p>
              </section>

              <section>
                <h2 className="text-2xl font-bold mb-4">9. Contact Us</h2>
                <p className="text-muted-foreground leading-relaxed">
                  If you have any questions about these Terms of Service, please
                  contact us at:
                </p>
                <p className="text-muted-foreground mt-4">
                  Email: legal@kenikool.com
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
