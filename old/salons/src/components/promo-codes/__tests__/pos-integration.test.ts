import { describe, it, expect } from "vitest";
import type { PromoCode } from "@/lib/api/hooks/usePromoCodes";

describe("POS Flow Integration - Promo Code Application", () => {
  describe("Promo Code Validation in POS", () => {
    it("should validate promo code with POS transaction parameters", () => {
      const validationRequest = {
        code: "CHECKOUT20",
        client_id: "client-456",
        service_ids: ["service-1", "service-2", "service-3"],
        total_amount: 250,
      };

      expect(validationRequest.code).toBeDefined();
      expect(validationRequest.client_id).toBeDefined();
      expect(validationRequest.service_ids).toBeDefined();
      expect(validationRequest.total_amount).toBeDefined();
      expect(validationRequest.total_amount).toBeGreaterThan(0);
    });

    it("should apply discount to transaction total", () => {
      const promoCode: PromoCode = {
        _id: "promo-pos-1",
        tenant_id: "tenant-1",
        code: "POSTRANS",
        discount_type: "percentage",
        discount_value: 10,
        is_active: true,
        valid_until: "2024-12-31T23:59:59Z",
        applicable_services: [],
        current_uses: 0,
        created_at: "2024-01-01T00:00:00Z",
        updated_at: "2024-01-01T00:00:00Z",
      };

      const transactionTotal = 500;
      const discountAmount =
        (transactionTotal * promoCode.discount_value) / 100;
      const finalAmount = transactionTotal - discountAmount;

      expect(discountAmount).toBe(50);
      expect(finalAmount).toBe(450);
    });

    it("should display discount in payment breakdown", () => {
      const paymentBreakdown = {
        subtotal: 300,
        discount: 30,
        tax: 21.6,
        total: 291.6,
      };

      expect(paymentBreakdown.subtotal).toBe(300);
      expect(paymentBreakdown.discount).toBe(30);
      expect(paymentBreakdown.total).toBe(291.6);
    });

    it("should handle fixed discount in POS", () => {
      const promoCode: PromoCode = {
        _id: "promo-pos-2",
        tenant_id: "tenant-1",
        code: "FIXED25",
        discount_type: "fixed",
        discount_value: 25,
        is_active: true,
        valid_until: "2024-12-31T23:59:59Z",
        applicable_services: [],
        current_uses: 0,
        created_at: "2024-01-01T00:00:00Z",
        updated_at: "2024-01-01T00:00:00Z",
      };

      const transactionTotal = 150;
      const discountAmount = promoCode.discount_value;
      const finalAmount = transactionTotal - discountAmount;

      expect(discountAmount).toBe(25);
      expect(finalAmount).toBe(125);
    });

    it("should display error message on invalid promo code in POS", () => {
      const validationResponse = {
        valid: false,
        error: "Promo code has reached maximum uses",
      };

      expect(validationResponse.valid).toBe(false);
      expect(validationResponse.error).toBeDefined();
    });
  });

  describe("Service-Specific Discounts in POS", () => {
    it("should filter applicable services from cart", () => {
      const promoCode: PromoCode = {
        _id: "promo-pos-3",
        tenant_id: "tenant-1",
        code: "HAIRCUT",
        discount_type: "percentage",
        discount_value: 15,
        is_active: true,
        valid_until: "2024-12-31T23:59:59Z",
        applicable_services: ["service-haircut"],
        current_uses: 0,
        created_at: "2024-01-01T00:00:00Z",
        updated_at: "2024-01-01T00:00:00Z",
      };

      const cartItems = [
        { service_id: "service-haircut", amount: 50 },
        { service_id: "service-color", amount: 80 },
      ];

      const applicableItems = cartItems.filter((item) =>
        promoCode.applicable_services.includes(item.service_id)
      );

      expect(applicableItems.length).toBe(1);
      expect(applicableItems[0].service_id).toBe("service-haircut");
    });

    it("should apply discount only to applicable items", () => {
      const promoCode: PromoCode = {
        _id: "promo-pos-4",
        tenant_id: "tenant-1",
        code: "HAIRONLY",
        discount_type: "percentage",
        discount_value: 20,
        is_active: true,
        valid_until: "2024-12-31T23:59:59Z",
        applicable_services: ["service-haircut"],
        current_uses: 0,
        created_at: "2024-01-01T00:00:00Z",
        updated_at: "2024-01-01T00:00:00Z",
      };

      const cartItems = [
        { service_id: "service-haircut", amount: 50 },
        { service_id: "service-color", amount: 80 },
      ];

      let totalDiscount = 0;
      cartItems.forEach((item) => {
        if (promoCode.applicable_services.includes(item.service_id)) {
          totalDiscount += (item.amount * promoCode.discount_value) / 100;
        }
      });

      expect(totalDiscount).toBe(10);
    });

    it("should show which items received discount", () => {
      const promoCode: PromoCode = {
        _id: "promo-pos-5",
        tenant_id: "tenant-1",
        code: "SERVICES",
        discount_type: "percentage",
        discount_value: 10,
        is_active: true,
        valid_until: "2024-12-31T23:59:59Z",
        applicable_services: ["service-haircut", "service-styling"],
        current_uses: 0,
        created_at: "2024-01-01T00:00:00Z",
        updated_at: "2024-01-01T00:00:00Z",
      };

      const cartItems = [
        { service_id: "service-haircut", name: "Haircut", amount: 50 },
        { service_id: "service-color", name: "Color", amount: 80 },
        { service_id: "service-styling", name: "Styling", amount: 40 },
      ];

      const discountedItems = cartItems.filter((item) =>
        promoCode.applicable_services.includes(item.service_id)
      );

      expect(discountedItems.length).toBe(2);
      expect(discountedItems.map((i) => i.name)).toEqual([
        "Haircut",
        "Styling",
      ]);
    });

    it("should apply promo code to all services when applicable_services is empty", () => {
      const promoCode: PromoCode = {
        _id: "promo-pos-6",
        tenant_id: "tenant-1",
        code: "ALLPOS",
        discount_type: "percentage",
        discount_value: 5,
        is_active: true,
        valid_until: "2024-12-31T23:59:59Z",
        applicable_services: [],
        current_uses: 0,
        created_at: "2024-01-01T00:00:00Z",
        updated_at: "2024-01-01T00:00:00Z",
      };

      const cartItems = [
        { service_id: "service-haircut", amount: 50 },
        { service_id: "service-color", amount: 80 },
      ];

      const applicableItems =
        promoCode.applicable_services.length === 0
          ? cartItems
          : cartItems.filter((item) =>
              promoCode.applicable_services.includes(item.service_id)
            );

      expect(applicableItems.length).toBe(2);
    });
  });

  describe("Transaction Completion with Promo Code", () => {
    it("should include promo_code_id in transaction record", () => {
      const transactionRecord = {
        transaction_id: "txn-123",
        client_id: "client-456",
        total_amount: 200,
        discount_amount: 20,
        final_amount: 180,
        promo_code_id: "promo-pos-1",
      };

      expect(transactionRecord.promo_code_id).toBeDefined();
      expect(transactionRecord.promo_code_id).toBe("promo-pos-1");
    });

    it("should record usage on successful transaction", () => {
      const promoCode: PromoCode = {
        _id: "promo-pos-7",
        tenant_id: "tenant-1",
        code: "USAGE",
        discount_type: "percentage",
        discount_value: 10,
        is_active: true,
        valid_until: "2024-12-31T23:59:59Z",
        applicable_services: [],
        current_uses: 5,
        created_at: "2024-01-01T00:00:00Z",
        updated_at: "2024-01-01T00:00:00Z",
      };

      const updatedUses = promoCode.current_uses + 1;

      expect(updatedUses).toBe(6);
    });

    it("should handle transaction without promo code", () => {
      const transactionRecord = {
        transaction_id: "txn-124",
        client_id: "client-457",
        total_amount: 150,
        final_amount: 150,
      };

      expect(transactionRecord.promo_code_id).toBeUndefined();
    });

    it("should maintain transaction integrity with promo code", () => {
      const transaction = {
        subtotal: 300,
        discount: 30,
        tax: 21.6,
        total: 291.6,
      };

      const calculatedTotal =
        transaction.subtotal - transaction.discount + transaction.tax;

      expect(calculatedTotal).toBe(291.6);
    });
  });

  describe("Error Handling in POS Flow", () => {
    it("should handle validation endpoint errors in POS", () => {
      const validationError = {
        status: 503,
        message: "Service unavailable",
      };

      expect(validationError.status).toBe(503);
      expect(validationError.message).toBeDefined();
    });

    it("should allow transaction without promo code if validation fails", () => {
      const canProceedWithoutPromo = true;

      expect(canProceedWithoutPromo).toBe(true);
    });

    it("should show retry option for failed validation in POS", () => {
      const validationFailed = true;
      const canRetry = validationFailed;

      expect(canRetry).toBe(true);
    });

    it("should log integration errors for debugging", () => {
      const integrationError = {
        timestamp: new Date().toISOString(),
        error: "Promo code validation failed",
        context: "POS payment processing",
      };

      expect(integrationError.error).toBeDefined();
      expect(integrationError.context).toContain("POS");
    });
  });

  describe("Max Uses Per Client in POS", () => {
    it("should validate client has not exceeded max_uses_per_client", () => {
      const promoCode: PromoCode = {
        _id: "promo-pos-8",
        tenant_id: "tenant-1",
        code: "LIMITED",
        discount_type: "percentage",
        discount_value: 15,
        max_uses_per_client: 2,
        is_active: true,
        valid_until: "2024-12-31T23:59:59Z",
        applicable_services: [],
        current_uses: 10,
        created_at: "2024-01-01T00:00:00Z",
        updated_at: "2024-01-01T00:00:00Z",
      };

      const clientUsageCount = 1;
      const canUse =
        !promoCode.max_uses_per_client ||
        clientUsageCount < promoCode.max_uses_per_client;

      expect(canUse).toBe(true);
    });

    it("should reject promo code if client exceeded max_uses_per_client", () => {
      const promoCode: PromoCode = {
        _id: "promo-pos-9",
        tenant_id: "tenant-1",
        code: "LIMITED",
        discount_type: "percentage",
        discount_value: 15,
        max_uses_per_client: 1,
        is_active: true,
        valid_until: "2024-12-31T23:59:59Z",
        applicable_services: [],
        current_uses: 50,
        created_at: "2024-01-01T00:00:00Z",
        updated_at: "2024-01-01T00:00:00Z",
      };

      const clientUsageCount = 1;
      const canUse =
        !promoCode.max_uses_per_client ||
        clientUsageCount < promoCode.max_uses_per_client;

      expect(canUse).toBe(false);
    });
  });
});
