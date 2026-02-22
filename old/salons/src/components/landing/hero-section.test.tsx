import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { HeroSection } from "./hero-section";

// Mock window.matchMedia
const mockMatchMedia = (matches: boolean) => {
  Object.defineProperty(window, "matchMedia", {
    writable: true,
    value: vi.fn().mockImplementation((query) => ({
      matches,
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })),
  });
};

// Mock navigator.connection
const mockConnection = (effectiveType: string) => {
  Object.defineProperty(navigator, "connection", {
    writable: true,
    value: {
      effectiveType,
      downlink: 10,
      rtt: 50,
      saveData: false,
    },
    configurable: true,
  });
};

describe("HeroSection", () => {
  beforeEach(() => {
    mockMatchMedia(false);
    mockConnection("4g");
  });

  it("should render hero section with all content", () => {
    render(
      <BrowserRouter>
        <HeroSection />
      </BrowserRouter>
    );

    expect(screen.getByText("Manage Your Salon with Ease")).toBeInTheDocument();
    expect(
      screen.getByText(/Complete salon management platform/i)
    ).toBeInTheDocument();
    expect(screen.getByText("Trusted by 500+ Nigerian Salons")).toBeInTheDocument();
  });

  it("should render CTA buttons", () => {
    render(
      <BrowserRouter>
        <HeroSection />
      </BrowserRouter>
    );

    expect(screen.getByText("Start 30-Day Free Trial")).toBeInTheDocument();
    expect(screen.getByText("Sign In")).toBeInTheDocument();
  });

  it("should render disclaimer text", () => {
    render(
      <BrowserRouter>
        <HeroSection />
      </BrowserRouter>
    );

    expect(
      screen.getByText(/No credit card required.*Free 30-day trial.*Cancel anytime/i)
    ).toBeInTheDocument();
  });

  it("should render statistics section", async () => {
    render(
      <BrowserRouter>
        <HeroSection />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText("Active Salons")).toBeInTheDocument();
      expect(screen.getByText("Bookings Processed")).toBeInTheDocument();
      expect(screen.getByText("Happy Customers")).toBeInTheDocument();
    });
  });

  it("should animate counter from 0 to end value", async () => {
    render(
      <BrowserRouter>
        <HeroSection />
      </BrowserRouter>
    );

    // Wait for counter animation to complete
    await waitFor(
      () => {
        const activeText = screen.getByText(/500\+/);
        expect(activeText).toBeInTheDocument();
      },
      { timeout: 3000 }
    );
  });

  it("should respect prefers-reduced-motion", () => {
    mockMatchMedia(true);

    render(
      <BrowserRouter>
        <HeroSection />
      </BrowserRouter>
    );

    // Floating elements should not be rendered when reduced motion is preferred
    const floatingElements = document.querySelectorAll(".blur-3xl");
    expect(floatingElements.length).toBe(0);
  });

  it("should use image background on mobile", () => {
    // Mock mobile viewport
    Object.defineProperty(window, "innerWidth", {
      writable: true,
      value: 375,
    });

    render(
      <BrowserRouter>
        <HeroSection />
      </BrowserRouter>
    );

    const img = screen.getByAltText("Modern salon interior");
    expect(img).toBeInTheDocument();
  });

  it("should use video background on desktop with good connection", async () => {
    // Mock desktop viewport
    Object.defineProperty(window, "innerWidth", {
      writable: true,
      value: 1920,
    });

    mockConnection("4g");

    render(
      <BrowserRouter>
        <HeroSection />
      </BrowserRouter>
    );

    await waitFor(() => {
      const video = document.querySelector("video");
      expect(video).toBeInTheDocument();
    });
  });

  it("should use image background on slow connection", () => {
    // Mock desktop viewport but slow connection
    Object.defineProperty(window, "innerWidth", {
      writable: true,
      value: 1920,
    });

    mockConnection("3g");

    render(
      <BrowserRouter>
        <HeroSection />
      </BrowserRouter>
    );

    const img = screen.getByAltText("Modern salon interior");
    expect(img).toBeInTheDocument();
  });

  it("should have proper link destinations", () => {
    render(
      <BrowserRouter>
        <HeroSection />
      </BrowserRouter>
    );

    const registerLink = screen.getByText("Start 30-Day Free Trial").closest("a");
    const signInLink = screen.getByText("Sign In").closest("a");

    expect(registerLink).toHaveAttribute("href", "/register");
    expect(signInLink).toHaveAttribute("href", "/login");
  });

  it("should have accessible button styling", () => {
    render(
      <BrowserRouter>
        <HeroSection />
      </BrowserRouter>
    );

    const buttons = screen.getAllByRole("button");
    buttons.forEach((button) => {
      expect(button).toHaveClass("font-semibold");
    });
  });

  it("should render background image with proper attributes", () => {
    render(
      <BrowserRouter>
        <HeroSection />
      </BrowserRouter>
    );

    const img = screen.getByAltText("Modern salon interior");
    expect(img).toHaveAttribute("loading", "eager");
    expect(img).toHaveClass("w-full", "h-full", "object-cover");
  });

  it("should have responsive text sizes", () => {
    render(
      <BrowserRouter>
        <HeroSection />
      </BrowserRouter>
    );

    const heading = screen.getByText("Manage Your Salon with Ease");
    expect(heading).toHaveClass(
      "text-4xl",
      "sm:text-5xl",
      "md:text-6xl",
      "lg:text-7xl"
    );
  });

  it("should have proper overlay gradient", () => {
    render(
      <BrowserRouter>
        <HeroSection />
      </BrowserRouter>
    );

    const overlay = document.querySelector(".bg-linear-to-b");
    expect(overlay).toHaveClass(
      "from-black/50",
      "via-black/60",
      "to-black/70"
    );
  });
});
