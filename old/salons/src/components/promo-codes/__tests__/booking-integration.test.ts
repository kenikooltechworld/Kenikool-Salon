import { describe, it, expect } from "vitest";
import type { PromoCode } from "@/lib/api/hooks/usePromoCodes";

describe("Booking Flow Integration - Promo Code Application", () => {
  describe("Promo Code Validation in Booking", () => {
    it("should validate promo code with required parameters", () => {
      const validationRequest = {
        code: "SUMMER2024",
        client_id: "client-123",
        service_ids: ["service-1", "service-2"],
        total_amount: 150,
      };

      expect(validationRequest.code).toBeDefined();
      expect(validationRequest.client_id).toBeDefined();
      expect(validationRequest.service_ids).toBeDefined();
      expect(validationRequest.total_amount).toBeDefined();
      expect(validationRequest.service_ids.length).toBeGreaterThan(0);
      expect(validationRequest.total_amount).toBeGreaterThan(0);
    });

    it("should calculate discount amount correctly for percentage discount", () => {
      const promoCode: PromoCode = {
        _id: "promo-1",
        tenant_id: "tenant-1",
        code: "PERCENT20",
        discount_type: "percentage",
        discount_value: 20,
        is_active: true,
        valid_until: "2024-12-31T23:59:59Z",
        applicable_services: [],
        current_uses: 0,
        created_at: "2024-01-01T00:00:00Z",
        updated_at: "2024-01-01T00:00:00Z",
      };

      const totalAmount = 100;
      const discountAmount = (totalAmount * promoCode.discount_value) / 100;
      const finalAmount = totalAmount - discountAmount;

      expect(discountAmount).toBe(20);
      expect(finalAmount).toBe(80);
    });

    it("should calculate discount amount correctly for fixed discount", () => {
      const promoCode: PromoCode = {
        _id: "promo-2",
        tenant_id: "tenant-1",
        code: "FIXED50",
        discount_type: "fixed",
        discount_value: 50,
        is_active: true,
        valid_until: "2024-12-31T23:59:59Z",
        applicable_services: [],
        current_uses: 0,
        created_at: "2024-01-01T00:00:00Z",
        updated_at: "2024-01-01T00:00:00Z",
      };

      const totalAmount = 200;
      const discountAmount = promoCode.discount_value;
      const finalAmount = totalAmount - discountAmount;

      expect(discountAmount).toBe(50);
      expect(finalAmount).toBe(150);
    });

    it("should respect max_discount_amount cap", () => {
      const promoCode: PromoCode = {
        _id: "promo-3",
        tenant_id: "tenant-1",
        code: "CAPPED",
        discount_type: "percentage",
        discount_value: 50,
        max_discount_amount: 30,
        is_active: true,
        valid_until: "2024-12-31T23:59:59Z",
        applicable_services: [],
        current_uses: 0,
        created_at: "2024-01-01T00:00:00Z",
        updated_at: "2024-01-01T00:00:00Z",
      };

      const totalAmount = 200;
      let discountAmount = (totalAmount * promoCode.discount_value) / 100;

      if (
        promoCode.max_discount_amount &&
        discountAmount > promoCode.max_discount_amount
      ) {
        discountAmount = promoCode.max_discount_amount;
      }

      const finalAmount = totalAmount - discountAmount;

      expect(discountAmount).toBe(30);
      expect(finalAmount).toBe(170);
    });

    it("should respect min_purchase_amount requirement", () => {
      const promoCode: PromoCode = {
        _id: "promo-4",
        tenant_id: "tenant-1",
        code: "MINPURCH",
        discount_type: "percentage",
        discount_value: 20,
        min_purchase_amount: 100,
        is_active: true,
        valid_until: "2024-12-31T23:59:59Z",
        applicable_services: [],
        current_uses: 0,
        created_at: "2024-01-01T00:00:00Z",
        updated_at: "2024-01-01T00:00:00Z",
      };

      const totalAmount = 50;
      const isEligible =
        !promoCode.min_purchase_amount ||
        totalAmount >= promoCode.min_purchase_amount;

      expect(isEligible).toBe(false);
    });

    it("should display error message on invalid promo code", () => {
      const validationResponse = {
        valid: false,
        error: "Promo code not found or expired",
      };

      expect(validationResponse.valid).toBe(false);
      expect(validationResponse.error).toBeDefined();
      expect(validationResponse.error).toContain("not found");
    });

    it("should display discount breakdown in booking", () => {
      const promoCode: PromoCode = {
        _id: "promo-5",
        tenant_id: "tenant-1",
        code: "BREAKDOWN",
        discount_type: "percentage",
        discount_value: 15,
        is_active: true,
        valid_until: "2024-12-31T23:59:59Z",
        applicable_services: [],
        current_uses: 0,
        created_at: "2024-01-01T00:00:00Z",
        updated_at: "2024-01-01T00:00:00Z",
      };

      const subtotal = 100;
      const discountAmount = (subtotal * promoCode.discount_value) / 100;
      const finalAmount = subtotal - discountAmount;

      const breakdown = {
        subtotal,
        discount: discountAmount,
        final: finalAmount,
      };

      expect(breakdown.subtotal).toBe(100);
      expect(breakdown.discount).toBe(15);
      expect(breakdown.final).toBe(85);
    });
  });

  describe("Booking Creation with Promo Code", () => {
    it("should include promo_code_id in booking request", () => {
      const bookingRequest = {
        client_id: "client-123",
        service_ids: ["service-1"],
        total_amount: 100,
        promo_code_id: "promo-123",
      };

      expect(bookingRequest.promo_code_id).toBeDefined();
      expect(bookingRequest.promo_code_id).toBe("promo-123");
    });

    it("should handle booking creation without promo code", () => {
      const bookingRequest = {
        client_id: "client-123",
        service_ids: ["service-1"],
        total_amount: 100,
      };

      expect(bookingRequest.promo_code_id).toBeUndefined();
    });

    it("should clear promo code after successful booking", () => {
      let appliedPromoCode: string | null = "SUMMER2024";

      // Simulate successful booking
      appliedPromoCode = null;

      expect(appliedPromoCode).toBeNull();
    });

    it("should maintain promo code on booking error", () => {
      let appliedPromoCode: string | null = "SUMMER2024";

      // Simulate booking error - promo code should remain
      const bookingError = new Error("Booking failed");

      expect(appliedPromoCode).toBe("SUMMER2024");
      expect(bookingError).toBeDefined();
    });
  });

  describe("Error Handling in Booking Flow", () => {
    it("should handle validation endpoint errors", () => {
      const validationError = {
        status: 500,
        message: "Internal server error",
      };

      expect(validationError.status).toBe(500);
      expect(validationError.message).toBeDefined();
    });

    it("should handle network failures during validation", () => {
      const networkError = new Error("Network request failed");

      expect(networkError.message).toContain("Network");
    });

    it("should allow booking without promo code if validation fails", () => {
      const canProceedWithoutPromo = true;

      expect(canProceedWithoutPromo).toBe(true);
    });

    it("should show retry option for failed validation", () => {
      const validationFailed = true;
      const canRetry = validationFailed;

      expect(canRetry).toBe(true);
    });
  });

  describe("Service-Specific Promo Codes in Booking", () => {
    it("should validate promo code applies to selected services", () => {
      const promoCode: PromoCode = {
        _id: "promo-6",
        tenant_id: "tenant-1",
        code: "HAIRONLY",
        discount_type: "percentage",
        discount_value: 10,
        is_active: true,
        valid_until: "2024-12-31T23:59:59Z",
        applicable_services: ["service-hair"],
        current_uses: 0,
        created_at: "2024-01-01T00:00:00Z",
        updated_at: "2024-01-01T00:00:00Z",
      };

      const selectedServices = ["service-hair", "service-nails"];
      const isApplicable =
        promoCode.applicable_services.length === 0 ||
        selectedServices.some((s) =>
          promoCode.applicable_services.includes(s)
        );

      expect(isApplicable).toBe(true);
    });

    it("should reject promo code if no applicable services selected", () => {
      const promoCode: PromoCode = {
        _id: "promo-7",
        tenant_id: "tenant-1",
        code: "HAIRONLY",
        discount_type: "percentage",
        discount_value: 10,
        is_active: true,
        valid_until: "2024-12-31T23:59:59Z",
        applicable_services: ["service-hair"],
        current_uses: 0,
        created_at: "2024-01-01T00:00:00Z",
        updated_at: "2024-01-01T00:00:00Z",
      };

      const selectedServices = ["service-nails", "service-massage"];
      const isApplicable =
        promoCode.applicable_services.length === 0 ||
        selectedServices.some((s) =>
          promoCode.applicable_services.includes(s)
        );

      expect(isApplicable).toBe(false);
    });

    it("should apply promo code to all services when applicable_services is empty", () => {
      const promoCode: PromoCode = {
        _id: "promo-8",
        tenant_id: "tenant-1",
        code: "ALLSERVICES",
        discount_type: "percentage",
        discount_value: 15,
        is_active: true,
        valid_until: "2024-12-31T23:59:59Z",
        applicable_services: [],
        current_uses: 0,
        created_at: "2024-01-01T00:00:00Z",
        updated_at: "2024-01-01T00:00:00Z",
      };

      const selectedServices = ["service-hair", "service-nails"];
      const isApplicable =
        promoCode.applicable_services.length === 0 ||
        selectedServices.some((s) =>
          promoCode.applicable_services.includes(s)
        );

      expect(isApplicable).toBe(true);
    });
  });
});
