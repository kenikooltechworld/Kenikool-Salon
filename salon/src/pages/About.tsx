export default function About() {
  return (
    <div className="min-h-screen bg-background">
      <main className="pt-24 pb-16">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <h1 className="text-3xl sm:text-4xl font-bold text-foreground mb-6">
            About Kenikool
          </h1>
          <p className="text-base sm:text-lg text-muted-foreground mb-8">
            Kenikool is a salon and booking management platform built to help
            beauty and wellness businesses save time, reduce no-shows, and
            deliver better customer experiences.
          </p>

          <section className="space-y-4 mb-10">
            <h2 className="text-2xl font-semibold text-foreground">
              Our Mission
            </h2>
            <p className="text-sm sm:text-base text-muted-foreground">
              We believe salon owners and staff should spend less time on
              paperwork and more time with clients. Kenikool brings together
              online booking, staff management, payments, and customer
              engagement in one simple system.
            </p>
          </section>

          <section className="space-y-4 mb-10">
            <h2 className="text-2xl font-semibold text-foreground">
              What We Offer
            </h2>
            <ul className="list-disc pl-5 space-y-2 text-sm sm:text-base text-muted-foreground">
              <li>Online booking and appointment scheduling</li>
              <li>Staff performance and commission tracking</li>
              <li>Secure payment processing and invoicing</li>
              <li>Customer relationship management</li>
              <li>Inventory and resource management</li>
              <li>Real-time notifications and waiting room tools</li>
            </ul>
          </section>

          <section className="space-y-4">
            <h2 className="text-2xl font-semibold text-foreground">
              Contact Us
            </h2>
            <p className="text-sm sm:text-base text-muted-foreground">
              Have questions or need support? Reach out and our team will help
              you get the most out of Kenikool.
            </p>
          </section>
        </div>
      </main>
    </div>
  );
}
