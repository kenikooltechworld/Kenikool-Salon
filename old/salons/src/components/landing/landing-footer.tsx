import { Link } from "react-router-dom";

export function LandingFooter() {
  const currentYear = new Date().getFullYear();

  const footerSections = [
    {
      title: "Product",
      links: [
        {
          label: "Features",
          href: "/",
          external: false,
          isAnchor: true,
          anchorId: "features",
        },
        {
          label: "Pricing",
          href: "/",
          external: false,
          isAnchor: true,
          anchorId: "pricing",
        },
        { label: "Salon Directory", href: "/marketplace", external: false },
      ],
    },
    {
      title: "Company",
      links: [
        { label: "About Us", href: "/about", external: false },
        { label: "Contact", href: "/contact", external: false },
        { label: "Blog", href: "/blog", external: false },
      ],
    },
    {
      title: "Support",
      links: [
        { label: "Help Center", href: "/help", external: false },
        { label: "Documentation", href: "/help", external: false },
        { label: "Contact Support", href: "/contact", external: false },
      ],
    },
    {
      title: "Legal",
      links: [
        { label: "Privacy Policy", href: "/privacy", external: false },
        { label: "Terms of Service", href: "/terms", external: false },
        { label: "Security", href: "/help", external: false },
      ],
    },
  ];

  const socialLinks = [
    { label: "Twitter", href: "https://twitter.com/kenikool" },
    { label: "Facebook", href: "https://facebook.com/kenikool" },
    { label: "Instagram", href: "https://instagram.com/kenikool" },
  ];

  return (
    <footer className="border-t border-border py-8 sm:py-12 px-4 sm:px-6">
      <div className="container mx-auto">
        {/* Footer Grid - Mobile First */}
        <div className="grid grid-cols-2 sm:grid-cols-2 md:grid-cols-4 gap-4 sm:gap-6 md:gap-8 mb-6 sm:mb-8">
          {footerSections.map((section, idx) => (
            <div key={idx}>
              <h3 className="font-bold mb-3 sm:mb-4 text-sm sm:text-base">
                {section.title}
              </h3>
              <ul className="space-y-2">
                {section.links.map((link, linkIdx) => (
                  <li key={linkIdx}>
                    {link.external ? (
                      <a
                        href={link.href}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs sm:text-sm text-muted-foreground hover:text-foreground transition-colors"
                      >
                        {link.label}
                      </a>
                    ) : link.isAnchor ? (
                      <Link
                        to={link.href}
                        onClick={() => {
                          const element = document.getElementById(
                            link.anchorId,
                          );
                          if (element) {
                            element.scrollIntoView({ behavior: "smooth" });
                          }
                        }}
                        className="text-xs sm:text-sm text-muted-foreground hover:text-foreground transition-colors"
                      >
                        {link.label}
                      </Link>
                    ) : (
                      <Link
                        to={link.href}
                        className="text-xs sm:text-sm text-muted-foreground hover:text-foreground transition-colors"
                      >
                        {link.label}
                      </Link>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Divider */}
        <div className="border-t border-border pt-6 sm:pt-8">
          {/* Copyright */}
          <div className="text-center">
            <p className="text-xs sm:text-sm text-muted-foreground">
              © {currentYear} Kenikool Salon Management. All rights reserved.
            </p>
            <p className="text-xs sm:text-sm text-muted-foreground mt-2">
              Made with ❤️ for Nigerian salon owners
            </p>
          </div>

          {/* Social Links */}
          <div className="flex justify-center gap-4 mt-4 sm:mt-6">
            {socialLinks.map((link, idx) => (
              <a
                key={idx}
                href={link.href}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs sm:text-sm text-muted-foreground hover:text-foreground transition-colors"
              >
                {link.label}
              </a>
            ))}
          </div>
        </div>
      </div>
    </footer>
  );
}
