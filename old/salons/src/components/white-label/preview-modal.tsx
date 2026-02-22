"use client";

import { WhiteLabelBranding } from "@/lib/api/hooks/useWhiteLabel";
import { Modal } from "@/components/ui/modal";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { AlertCircle, Monitor, Smartphone } from "lucide-react";
import { useState } from "react";

interface PreviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  branding: WhiteLabelBranding;
  accessibilityWarnings?: string[];
  useHooks?: boolean;
}

type PageType = "home" | "booking" | "checkout";
type ViewType = "desktop" | "mobile";

export function PreviewModal({
  isOpen,
  onClose,
  branding,
  accessibilityWarnings = [],
  useHooks = false,
}: PreviewModalProps) {
  const [currentPage, setCurrentPage] = useState<PageType>("home");
  const [viewType, setViewType] = useState<ViewType>("desktop");

  const generatePreviewHTML = (pageType: PageType): string => {
    const primaryColor = branding.primary_color || "#FF6B6B";
    const secondaryColor = branding.secondary_color || "#4ECDC4";
    const accentColor = branding.accent_color || "#FFE66D";
    const fontFamily = branding.font_family || "Inter, sans-serif";
    const companyName = branding.company_name || "Your Salon";
    const tagline = branding.tagline || "Professional Beauty Services";

    const baseStyles = `
      * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
      }
      body {
        font-family: ${fontFamily};
        background-color: #f9fafb;
        color: #1f2937;
      }
      .header {
        background-color: ${primaryColor};
        color: white;
        padding: 20px;
        display: flex;
        align-items: center;
        gap: 15px;
      }
      .logo {
        width: 50px;
        height: 50px;
        background-color: rgba(255, 255, 255, 0.2);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
      }
      .header-content h1 {
        font-size: 24px;
        margin-bottom: 4px;
      }
      .header-content p {
        font-size: 14px;
        opacity: 0.9;
      }
      .content {
        padding: 30px;
        max-width: 100%;
      }
      .button {
        background-color: ${secondaryColor};
        color: white;
        padding: 12px 24px;
        border: none;
        border-radius: 6px;
        cursor: pointer;
        font-size: 16px;
        font-weight: 500;
        margin-top: 20px;
      }
      .button:hover {
        opacity: 0.9;
      }
      .accent-text {
        color: ${accentColor};
        font-weight: 600;
      }
      .card {
        background: white;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
      }
      .service-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
        margin-top: 20px;
      }
      .service-card {
        background: white;
        border: 2px solid ${primaryColor};
        border-radius: 8px;
        padding: 20px;
        text-align: center;
      }
      .service-card h3 {
        color: ${primaryColor};
        margin-bottom: 10px;
      }
      .price {
        font-size: 20px;
        color: ${secondaryColor};
        font-weight: bold;
        margin: 10px 0;
      }
    `;

    const homeContent = `
      <div class="header">
        <div class="logo">✨</div>
        <div class="header-content">
          <h1>${companyName}</h1>
          <p>${tagline}</p>
        </div>
      </div>
      <div class="content">
        <div class="card">
          <h2>Welcome to ${companyName}</h2>
          <p>Experience premium beauty services with our expert team.</p>
          <button class="button">Book Now</button>
        </div>
        <div class="card">
          <h3>Our Services</h3>
          <div class="service-grid">
            <div class="service-card">
              <h3>Haircut</h3>
              <p>Professional styling</p>
              <div class="price">$45</div>
            </div>
            <div class="service-card">
              <h3>Coloring</h3>
              <p>Premium color service</p>
              <div class="price">$85</div>
            </div>
            <div class="service-card">
              <h3>Styling</h3>
              <p>Special occasion styling</p>
              <div class="price">$65</div>
            </div>
          </div>
        </div>
      </div>
    `;

    const bookingContent = `
      <div class="header">
        <div class="logo">📅</div>
        <div class="header-content">
          <h1>Book an Appointment</h1>
          <p>Select your preferred service and time</p>
        </div>
      </div>
      <div class="content">
        <div class="card">
          <h3>Step 1: Select Service</h3>
          <div class="service-grid">
            <div class="service-card">
              <h3>Haircut</h3>
              <div class="price">$45</div>
              <button class="button">Select</button>
            </div>
            <div class="service-card">
              <h3>Coloring</h3>
              <div class="price">$85</div>
              <button class="button">Select</button>
            </div>
          </div>
        </div>
        <div class="card">
          <h3>Step 2: Choose Date & Time</h3>
          <p>Calendar and time slots would appear here</p>
          <button class="button">Continue</button>
        </div>
      </div>
    `;

    const checkoutContent = `
      <div class="header">
        <div class="logo">💳</div>
        <div class="header-content">
          <h1>Checkout</h1>
          <p>Complete your booking</p>
        </div>
      </div>
      <div class="content">
        <div class="card">
          <h3>Booking Summary</h3>
          <p><strong>Service:</strong> Haircut</p>
          <p><strong>Date:</strong> Tomorrow at 2:00 PM</p>
          <p><strong>Stylist:</strong> Sarah</p>
          <p style="margin-top: 15px; font-size: 18px;"><strong>Total: <span class="accent-text">$45</span></strong></p>
          <button class="button">Confirm Booking</button>
        </div>
      </div>
    `;

    const content =
      pageType === "home"
        ? homeContent
        : pageType === "booking"
          ? bookingContent
          : checkoutContent;

    return `
      <!DOCTYPE html>
      <html>
        <head>
          <style>${baseStyles}</style>
        </head>
        <body>
          ${content}
        </body>
      </html>
    `;
  };

  const previewHTML = generatePreviewHTML(currentPage);
  const isMobile = viewType === "mobile";
  const containerWidth = isMobile ? "375px" : "100%";
  const containerHeight = isMobile ? "667px" : "600px";

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="xl">
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold">Preview Branding</h2>
          <Button variant="ghost" onClick={onClose}>
            ✕
          </Button>
        </div>

        {/* Accessibility Warnings */}
        {accessibilityWarnings.length > 0 && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
            <div className="flex gap-2">
              <AlertCircle className="h-5 w-5 text-yellow-600 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="font-semibold text-yellow-900 mb-1">
                  Accessibility Warnings
                </h4>
                <ul className="text-sm text-yellow-800 space-y-1">
                  {accessibilityWarnings.map((warning, idx) => (
                    <li key={idx}>• {warning}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* Controls */}
        <div className="flex items-center justify-between gap-4">
          <Tabs value={currentPage} onValueChange={(v) => setCurrentPage(v as PageType)}>
            <TabsList>
              <TabsTrigger value="home">Home</TabsTrigger>
              <TabsTrigger value="booking">Booking</TabsTrigger>
              <TabsTrigger value="checkout">Checkout</TabsTrigger>
            </TabsList>
          </Tabs>

          <div className="flex gap-2">
            <Button
              variant={viewType === "desktop" ? "default" : "outline"}
              size="sm"
              onClick={() => setViewType("desktop")}
              className="gap-2"
            >
              <Monitor className="h-4 w-4" />
              Desktop
            </Button>
            <Button
              variant={viewType === "mobile" ? "default" : "outline"}
              size="sm"
              onClick={() => setViewType("mobile")}
              className="gap-2"
            >
              <Smartphone className="h-4 w-4" />
              Mobile
            </Button>
          </div>
        </div>

        {/* Preview Container */}
        <div className="border rounded-lg bg-gray-100 p-4 flex justify-center">
          <div
            style={{
              width: containerWidth,
              height: containerHeight,
              border: "1px solid #e5e7eb",
              borderRadius: "8px",
              overflow: "hidden",
              backgroundColor: "white",
            }}
          >
            <iframe
              srcDoc={previewHTML}
              style={{
                width: "100%",
                height: "100%",
                border: "none",
              }}
              title="Preview"
            />
          </div>
        </div>

        {/* Footer */}
        <div className="flex justify-end gap-2 pt-4 border-t">
          <Button variant="outline" onClick={onClose}>
            Close
          </Button>
        </div>
      </div>
    </Modal>
  );
}
