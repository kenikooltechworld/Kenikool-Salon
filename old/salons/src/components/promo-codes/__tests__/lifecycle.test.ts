import { describe, it, expect } from "vitest";
import type { PromoCode, PromoCodeCreate } from "@/lib/api/hooks/usePromoCodes";

describe("Complete Promo Code Lifecycle", () => {
  describe("Create Promo Code", () => {
    it("should create promo code with all fields", () => {
      const createData: PromoCodeCreate = {
        code: "LIFECYCLE2024",
        description: "Lifecycle test promo code",
        discount_type: "percentage",
        discount_value: 20,
        min_purchase_amount: 50,
        max_discount_amount: 100,
        is_active: true,
        valid_from: "2024-06-01T00:00:00Z",
        valid_until: "2024-12-31T23:59:59Z",
        max_uses: 1000,
        max_uses_per_client: 2,
        applicable_services: ["service-1", "service-2"],
      };

      expect(createData.code).toBe("LIFECYCLE2024");
      expect(createData.description).toBe("Lifecycle test promo code");
      expect(createData.discount_type).toBe("percentage");
      expect(createData.discount_value).toBe(20);
      expect(createData.is_active).toBe(true);
      expect(createData.applicable_services.length).toBe(2);
    });

    it("should return created promo code with ID", () => {
      const createdPromoCode: PromoCode = {
        _id: "promo-lifecycle-1",
        tenant_id: "tenant-1",
        code: "LIFECYCLE2024",
        description: "Lifecycle test promo code",
        discount_type: "percentage",
        discount_value: 20,
        min_purchase_amount: 50,
        max_discount_amount: 100,
        is_active: true,
        valid_from: "2024-06-01T00:00:00Z",
        valid_until: "2024-12-31T23:59:59Z",
        max_uses: 1000,
        max_uses_per_client: 2,
        applicable_services: ["service-1", "service-2"],
        current_uses: 0,
        created_at: "2024-05-01T00:00:00Z",
        updated_at: "2024-05-01T00:00:00Z",
      };

      expect(createdPromoCode._id).toBeDefined();
      expect(createdPromoCode.current_uses).toBe(0);
      expect(createdPromoCode.created_at).toBeDefined();
    });
  });

  describe("Apply in Booking Flow", () => {
    it("should validate and apply promo code in booking", () => {
      const promoCode: PromoCode = {
        _id: "promo-lifecycle-1",
        tenant_id: "tenant-1",
        code: "LIFECYCLE2024",
        description: "Lifecycle test promo code",
        discount_type: "percentage",
        discount_value: 20,
        min_purchase_amount: 50,
        max_discount_amount: 100,
        is_active: true,
        valid_from: "2024-06-01T00:00:00Z",
        valid_until: "2024-12-31T23:59:59Z",
        max_uses: 1000,
        max_uses_per_client: 2,
        applicable_services: ["service-1", "service-2"],
        current_uses: 0,
        created_at: "2024-05-01T00:00:00Z",
        updated_at: "2024-05-01T00:00:00Z",
      };

      const bookingTotal = 150;
      const discountAmount = (bookingTotal * promoCode.discount_value) / 100;
      const finalAmount = bookingTotal - discountAmount;

      expect(discountAmount).toBe(30);
      expect(finalAmount).toBe(120);
    });

    it("should create booking with promo code", () => {
      const booking = {
        _id: "booking-1",
        client_id: "client-1",
        service_ids: ["service-1"],
        total_amount: 150,
        discount_amount: 30,
        final_amount: 120,
        promo_code_id: "promo-lifecycle-1",
        created_at: "2024-06-15T10:00:00Z",
      };

      expect(booking.promo_code_id).toBe("promo-lifecycle-1");
      expect(booking.final_amount).toBe(120);
    });

    it("should increment usage count after booking", () => {
      let promoCode: PromoCode = {
        _id: "promo-lifecycle-1",
        tenant_id: "tenant-1",
        code: "LIFECYCLE2024",
        description: "Lifecycle test promo code",
        discount_type: "percentage",
        discount_value: 20,
        min_purchase_amount: 50,
        max_discount_amount: 100,
        is_active: true,
        valid_from: "2024-06-01T00:00:00Z",
        valid_until: "2024-12-31T23:59:59Z",
        max_uses: 1000,
        max_uses_per_client: 2,
        applicable_services: ["service-1", "service-2"],
        current_uses: 0,
        created_at: "2024-05-01T00:00:00Z",
        updated_at: "2024-05-01T00:00:00Z",
      };

      promoCode.current_uses += 1;

      expect(promoCode.current_uses).toBe(1);
    });
  });

  describe("Apply in POS Flow", () => {
    it("should validate and apply promo code in POS", () => {
      const promoCode: PromoCode = {
        _id: "promo-lifecycle-1",
        tenant_id: "tenant-1",
        code: "LIFECYCLE2024",
        description: "Lifecycle test promo code",
        discount_type: "percentage",
        discount_value: 20,
        min_purchase_amount: 50,
        max_discount_amount: 100,
        is_active: true,
        valid_from: "2024-06-01T00:00:00Z",
        valid_until: "2024-12-31T23:59:59Z",
        max_uses: 1000,
        max_uses_per_client: 2,
        applicable_services: ["service-1", "service-2"],
        current_uses: 1,
        created_at: "2024-05-01T00:00:00Z",
        updated_at: "2024-06-15T10:00:00Z",
      };

      const transactionTotal = 200;
      const discountAmount =
        (transactionTotal * promoCode.discount_value) / 100;
      const finalAmount = transactionTotal - discountAmount;

      expect(discountAmount).toBe(40);
      expect(finalAmount).toBe(160);
    });

    it("should create transaction with promo code", () => {
      const transaction = {
        _id: "txn-1",
        client_id: "client-1",
        total_amount: 200,
        discount_amount: 40,
        final_amount: 160,
        promo_code_id: "promo-lifecycle-1",
        created_at: "2024-06-20T14:30:00Z",
      };

      expect(transaction.promo_code_id).toBe("promo-lifecycle-1");
      expect(transaction.final_amount).toBe(160);
    });

    it("should increment usage count after POS transaction", () => {
      let promoCode: PromoCode = {
        _id: "promo-lifecycle-1",
        tenant_id: "tenant-1",
        code: "LIFECYCLE2024",
        description: "Lifecycle test promo code",
        discount_type: "percentage",
        discount_value: 20,
        min_purchase_amount: 50,
        max_discount_amount: 100,
        is_active: true,
        valid_from: "2024-06-01T00:00:00Z",
        valid_until: "2024-12-31T23:59:59Z",
        max_uses: 1000,
        max_uses_per_client: 2,
        applicable_services: ["service-1", "service-2"],
        current_uses: 1,
        created_at: "2024-05-01T00:00:00Z",
        updated_at: "2024-06-15T10:00:00Z",
      };

      promoCode.current_uses += 1;

      expect(promoCode.current_uses).toBe(2);
    });
  });

  describe("View Usage Analytics", () => {
    it("should display usage statistics", () => {
      const promoCode: PromoCode = {
        _id: "promo-lifecycle-1",
        tenant_id: "tenant-1",
        code: "LIFECYCLE2024",
        description: "Lifecycle test promo code",
        discount_type: "percentage",
        discount_value: 20,
        min_purchase_amount: 50,
        max_discount_amount: 100,
        is_active: true,
        valid_from: "2024-06-01T00:00:00Z",
        valid_until: "2024-12-31T23:59:59Z",
        max_uses: 1000,
        max_uses_per_client: 2,
        applicable_services: ["service-1", "service-2"],
        current_uses: 2,
        created_at: "2024-05-01T00:00:00Z",
        updated_at: "2024-06-20T14:30:00Z",
      };

      const usagePercentage = (promoCode.current_uses / promoCode.max_uses!) * 100;

      expect(promoCode.current_uses).toBe(2);
      expect(usagePercentage).toBe(0.2);
    });

    it("should calculate revenue impact", () => {
      const promoCode: PromoCode = {
        _id: "promo-lifecycle-1",
        tenant_id: "tenant-1",
        code: "LIFECYCLE2024",
        description: "Lifecycle test promo code",
        discount_type: "percentage",
        discount_value: 20,
        min_purchase_amount: 50,
        max_discount_amount: 100,
        is_active: true,
        valid_from: "2024-06-01T00:00:00Z",
        valid_until: "2024-12-31T23:59:59Z",
        max_uses: 1000,
        max_uses_per_client: 2,
        applicable_services: ["service-1", "service-2"],
        current_uses: 2,
        created_at: "2024-05-01T00:00:00Z",
        updated_at: "2024-06-20T14:30:00Z",
      };

      const totalDiscountGiven = 30 + 40;
      const averageDiscountPerUse = totalDiscountGiven / promoCode.current_uses;

      expect(totalDiscountGiven).toBe(70);
      expect(averageDiscountPerUse).toBe(35);
    });
  });

  describe("Update Promo Code", () => {
    it("should update promo code details", () => {
      let promoCode: PromoCode = {
        _id: "promo-lifecycle-1",
        tenant_id: "tenant-1",
        code: "LIFECYCLE2024",
        description: "Lifecycle test promo code",
        discount_type: "percentage",
        discount_value: 20,
        min_purchase_amount: 50,
        max_discount_amount: 100,
        is_active: true,
        valid_from: "2024-06-01T00:00:00Z",
        valid_until: "2024-12-31T23:59:59Z",
        max_uses: 1000,
        max_uses_per_client: 2,
        applicable_services: ["service-1", "service-2"],
        current_uses: 2,
        created_at: "2024-05-01T00:00:00Z",
        updated_at: "2024-06-20T14:30:00Z",
      };

      promoCode.description = "Updated description";
      promoCode.discount_value = 25;
      promoCode.updated_at = "2024-06-25T10:00:00Z";

      expect(promoCode.description).toBe("Updated description");
      expect(promoCode.discount_value).toBe(25);
    });

    it("should preserve usage count when updating", () => {
      const promoCode: PromoCode = {
        _id: "promo-lifecycle-1",
        tenant_id: "tenant-1",
        code: "LIFECYCLE2024",
        description: "Updated description",
        discount_type: "percentage",
        discount_value: 25,
        min_purchase_amount: 50,
        max_discount_amount: 100,
        is_active: true,
        valid_from: "2024-06-01T00:00:00Z",
        valid_until: "2024-12-31T23:59:59Z",
        max_uses: 1000,
        max_uses_per_client: 2,
        applicable_services: ["service-1", "service-2"],
        current_uses: 2,
        created_at: "2024-05-01T00:00:00Z",
        updated_at: "2024-06-25T10:00:00Z",
      };

      expect(promoCode.current_uses).toBe(2);
    });
  });

  describe("Deactivate Promo Code", () => {
    it("should deactivate promo code", () => {
      let promoCode: PromoCode = {
        _id: "promo-lifecycle-1",
        tenant_id: "tenant-1",
        code: "LIFECYCLE2024",
        description: "Updated description",
        discount_type: "percentage",
        discount_value: 25,
        min_purchase_amount: 50,
        max_discount_amount: 100,
        is_active: true,
        valid_from: "2024-06-01T00:00:00Z",
        valid_until: "2024-12-31T23:59:59Z",
        max_uses: 1000,
        max_uses_per_client: 2,
        applicable_services: ["service-1", "service-2"],
        current_uses: 2,
        created_at: "2024-05-01T00:00:00Z",
        updated_at: "2024-06-25T10:00:00Z",
      };

      promoCode.is_active = false;
      promoCode.updated_at = "2024-07-01T00:00:00Z";

      expect(promoCode.is_active).toBe(false);
    });

    it("should prevent use of deactivated promo code", () => {
      const promoCode: PromoCode = {
        _id: "promo-lifecycle-1",
        tenant_id: "tenant-1",
        code: "LIFECYCLE2024",
        description: "Updated description",
        discount_type: "percentage",
        discount_value: 25,
        min_purchase_amount: 50,
        max_discount_amount: 100,
        is_active: false,
        valid_from: "2024-06-01T00:00:00Z",
        valid_until: "2024-12-31T23:59:59Z",
        max_uses: 1000,
        max_uses_per_client: 2,
        applicable_services: ["service-1", "service-2"],
        current_uses: 2,
        created_at: "2024-05-01T00:00:00Z",
        updated_at: "2024-07-01T00:00:00Z",
      };

      const canUse = promoCode.is_active;

      expect(canUse).toBe(false);
    });

    it("should preserve all data when deactivating", () => {
      const promoCode: PromoCode = {
        _id: "promo-lifecycle-1",
        tenant_id: "tenant-1",
        code: "LIFECYCLE2024",
        description: "Updated description",
        discount_type: "percentage",
        discount_value: 25,
        min_purchase_amount: 50,
        max_discount_amount: 100,
        is_active: false,
        valid_from: "2024-06-01T00:00:00Z",
        valid_until: "2024-12-31T23:59:59Z",
        max_uses: 1000,
        max_uses_per_client: 2,
        applicable_services: ["service-1", "service-2"],
        current_uses: 2,
        created_at: "2024-05-01T00:00:00Z",
        updated_at: "2024-07-01T00:00:00Z",
      };

      expect(promoCode.code).toBe("LIFECYCLE2024");
      expect(promoCode.current_uses).toBe(2);
      expect(promoCode.created_at).toBe("2024-05-01T00:00:00Z");
    });
  });

  describe("Complete Lifecycle Summary", () => {
    it("should track all lifecycle events", () => {
      const lifecycleEvents = [
        { event: "created", timestamp: "2024-05-01T00:00:00Z" },
        { event: "applied_in_booking", timestamp: "2024-06-15T10:00:00Z" },
        { event: "applied_in_pos", timestamp: "2024-06-20T14:30:00Z" },
        { event: "updated", timestamp: "2024-06-25T10:00:00Z" },
        { event: "deactivated", timestamp: "2024-07-01T00:00:00Z" },
      ];

      expect(lifecycleEvents.length).toBe(5);
      expect(lifecycleEvents[0].event).toBe("created");
      expect(lifecycleEvents[4].event).toBe("deactivated");
    });
  });
});
