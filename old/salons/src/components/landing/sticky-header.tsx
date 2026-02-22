import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import {
  ArrowRightIcon,
  XIcon,
  MenuIcon,
  ScissorsIcon,
} from "@/components/icons";

export function StickyHeader() {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50);
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const navItems = [
    { label: "Browse Salons", href: "/marketplace" },
    { label: "About", href: "/about" },
    { label: "Contact", href: "/contact" },
    { label: "Features", href: "#features" },
    { label: "Pricing", href: "#pricing" },
    { label: "Testimonials", href: "#testimonials" },
  ];

  const handleNavClick = () => {
    setIsMobileMenuOpen(false);
  };

  return (
    <>
      <motion.header
        className={`fixed top-0 left-0 right-0 z-40 transition-all duration-300 ${
          isScrolled
            ? "bg-white/95 backdrop-blur-md shadow-lg"
            : "bg-transparent"
        }`}
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="container mx-auto px-3 sm:px-4 md:px-6 py-2 sm:py-3 md:py-4 flex items-center justify-between">
          {/* Logo */}
          <motion.div
            className="flex items-center gap-1 sm:gap-2 cursor-pointer"
            whileHover={{ scale: 1.05 }}
          >
            <ScissorsIcon
              size={24}
              className={`sm:w-7 sm:h-7 ${isScrolled ? "text-primary" : "text-white"}`}
            />
            <span
              className={`font-bold text-lg sm:text-xl md:text-2xl ${isScrolled ? "text-foreground" : "text-white"}`}
            >
              Kenikool
            </span>
          </motion.div>

          {/* Desktop Navigation Links */}
          <motion.nav
            className="hidden md:flex items-center gap-4 lg:gap-8"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
          >
            {navItems.map((item, index) => (
              <motion.div
                key={item.label}
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 + index * 0.1 }}
              >
                {item.href.startsWith("#") ? (
                  <motion.button
                    onClick={() => {
                      const element = document.querySelector(item.href);
                      element?.scrollIntoView({ behavior: "smooth" });
                    }}
                    className={`text-xs md:text-sm font-medium transition-colors cursor-pointer ${
                      isScrolled
                        ? "text-foreground hover:text-primary"
                        : "text-white hover:text-accent"
                    }`}
                    whileHover={{ scale: 1.05 }}
                  >
                    {item.label}
                  </motion.button>
                ) : (
                  <Link
                    to={item.href}
                    className={`text-xs md:text-sm font-medium transition-colors cursor-pointer ${
                      isScrolled
                        ? "text-foreground hover:text-primary"
                        : "text-white hover:text-accent"
                    }`}
                  >
                    <motion.span whileHover={{ scale: 1.05 }}>
                      {item.label}
                    </motion.span>
                  </Link>
                )}
              </motion.div>
            ))}
          </motion.nav>

          {/* Desktop CTA Buttons */}
          <motion.div
            className="hidden md:flex items-center gap-2 lg:gap-3"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
          >
            <Button
              variant="ghost"
              size="sm"
              className={`text-xs md:text-sm cursor-pointer font-medium ${isScrolled ? "text-foreground hover:text-primary" : "text-white hover:text-accent"}`}
              asChild
            >
              <Link to="/login">Sign In</Link>
            </Button>

            <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
              <Button
                size="sm"
                className="bg-accent hover:bg-accent-dark text-white text-xs md:text-sm cursor-pointer font-medium"
                asChild
              >
                <Link to="/register" className="flex items-center gap-1">
                  Start Free Trial
                  <ArrowRightIcon size={12} className="md:w-4 md:h-4" />
                </Link>
              </Button>
            </motion.div>
          </motion.div>

          {/* Mobile Menu Button */}
          <motion.button
            className="md:hidden p-2 cursor-pointer"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            whileTap={{ scale: 0.95 }}
          >
            {isMobileMenuOpen ? (
              <XIcon
                size={20}
                className={isScrolled ? "text-foreground" : "text-white"}
              />
            ) : (
              <MenuIcon
                size={20}
                className={isScrolled ? "text-foreground" : "text-white"}
              />
            )}
          </motion.button>
        </div>
      </motion.header>

      {/* Mobile Menu */}
      <AnimatePresence>
        {isMobileMenuOpen && (
          <motion.div
            className="fixed inset-0 z-30 md:hidden"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setIsMobileMenuOpen(false)}
          >
            <motion.div
              className="absolute top-14 sm:top-16 left-0 right-0 bg-white shadow-lg"
              initial={{ y: -20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              exit={{ y: -20, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
            >
              <div className="container mx-auto px-3 sm:px-4 py-3 sm:py-4 flex flex-col gap-3">
                {navItems.map((item) => (
                  <motion.div key={item.label} whileHover={{ x: 4 }}>
                    {item.href.startsWith("#") ? (
                      <motion.button
                        onClick={() => {
                          const element = document.querySelector(item.href);
                          element?.scrollIntoView({ behavior: "smooth" });
                          handleNavClick();
                        }}
                        className="text-sm font-medium text-foreground hover:text-primary py-2 w-full text-left cursor-pointer"
                      >
                        {item.label}
                      </motion.button>
                    ) : (
                      <Link
                        to={item.href}
                        onClick={handleNavClick}
                        className="text-sm font-medium text-foreground hover:text-primary py-2 w-full text-left cursor-pointer block"
                      >
                        {item.label}
                      </Link>
                    )}
                  </motion.div>
                ))}
                <div className="border-t border-border pt-3 sm:pt-4 flex flex-col gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    className="w-full cursor-pointer text-xs sm:text-sm"
                    asChild
                  >
                    <Link to="/login" onClick={handleNavClick}>
                      Sign In
                    </Link>
                  </Button>
                  <Button
                    size="sm"
                    className="w-full bg-accent hover:bg-accent-dark text-white cursor-pointer text-xs sm:text-sm"
                    asChild
                  >
                    <Link to="/register" onClick={handleNavClick}>
                      Start Free Trial
                    </Link>
                  </Button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
