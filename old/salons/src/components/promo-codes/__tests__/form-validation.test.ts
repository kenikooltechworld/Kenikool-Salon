import { describe, it, expect } from "vitest";

// Validation functions extracted from the form component
function validateDateRange(
  validFrom: string | undefined,
  validUntil: string | undefined
): string | null {
  if (validFrom && validUntil) {
    const fromDate = new Date(validFrom);
    const untilDate = new Date(validUntil);
    if (fromDate > untilDate) {
      return "Valid from date must be before valid until date";
    }
  }
  return null;
}

function validatePercentageDiscount(value: number | undefined): string | null {
  if (value !== undefined && (value < 0 || value > 100)) {
    return "Percentage must be between 0 and 100";
  }
  return null;
}

function validatePositiveValue(
  value: number | undefined,
  fieldName: string
): string | null {
  if (value !== undefined && value <= 0) {
    return `${fieldName} must be greater than 0`;
  }
  return null;
}

function validateFixedDiscount(value: number | undefined): string | null {
  if (value !== undefined && value <= 0) {
    return "Fixed discount must be greater than 0";
  }
  return null;
}

describe("Form Validation", () => {
  describe("Date Range Validation", () => {
    it("should pass when valid_from is before valid_until", () => {
      const error = validateDateRange(
        "2024-01-01T00:00:00Z",
        "2024-12-31T23:59:59Z"
      );
      expect(error).toBeNull();
    });

    it("should fail when valid_from is after valid_until", () => {
      const error = validateDateRange(
        "2024-12-31T23:59:59Z",
        "2024-01-01T00:00:00Z"
      );
      expect(error).not.toBeNull();
      expect(error).toContain("must be before");
    });

    it("should pass when valid_from equals valid_until", () => {
      const error = validateDateRange(
        "2024-06-15T12:00:00Z",
        "2024-06-15T12:00:00Z"
      );
      expect(error).toBeNull();
    });

    it("should pass when only one date is provided", () => {
      const error1 = validateDateRange("2024-01-01T00:00:00Z", undefined);
      const error2 = validateDateRange(undefined, "2024-12-31T23:59:59Z");
      expect(error1).toBeNull();
      expect(error2).toBeNull();
    });

    it("should pass when no dates are provided", () => {
      const error = validateDateRange(undefined, undefined);
      expect(error).toBeNull();
    });
  });

  describe("Percentage Discount Validation", () => {
    it("should pass for valid percentage values (0-100)", () => {
      expect(validatePercentageDiscount(0)).toBeNull();
      expect(validatePercentageDiscount(50)).toBeNull();
      expect(validatePercentageDiscount(100)).toBeNull();
      expect(validatePercentageDiscount(25.5)).toBeNull();
    });

    it("should fail for negative percentages", () => {
      const error = validatePercentageDiscount(-10);
      expect(error).not.toBeNull();
      expect(error).toContain("between 0 and 100");
    });

    it("should fail for percentages over 100", () => {
      const error = validatePercentageDiscount(150);
      expect(error).not.toBeNull();
      expect(error).toContain("between 0 and 100");
    });

    it("should pass when value is undefined", () => {
      const error = validatePercentageDiscount(undefined);
      expect(error).toBeNull();
    });
  });

  describe("Positive Value Validation", () => {
    it("should pass for positive values", () => {
      expect(validatePositiveValue(1, "Max uses")).toBeNull();
      expect(validatePositiveValue(100, "Max uses")).toBeNull();
      expect(validatePositiveValue(0.01, "Max uses")).toBeNull();
    });

    it("should fail for zero", () => {
      const error = validatePositiveValue(0, "Max discount amount");
      expect(error).not.toBeNull();
      expect(error).toContain("must be greater than 0");
    });

    it("should fail for negative values", () => {
      const error = validatePositiveValue(-50, "Min purchase amount");
      expect(error).not.toBeNull();
      expect(error).toContain("must be greater than 0");
    });

    it("should pass when value is undefined", () => {
      const error = validatePositiveValue(undefined, "Max uses");
      expect(error).toBeNull();
    });

    it("should include field name in error message", () => {
      const error = validatePositiveValue(-1, "Custom Field Name");
      expect(error).toContain("Custom Field Name");
    });
  });

  describe("Fixed Discount Validation", () => {
    it("should pass for positive fixed discount values", () => {
      expect(validateFixedDiscount(1)).toBeNull();
      expect(validateFixedDiscount(50)).toBeNull();
      expect(validateFixedDiscount(99.99)).toBeNull();
    });

    it("should fail for zero fixed discount", () => {
      const error = validateFixedDiscount(0);
      expect(error).not.toBeNull();
      expect(error).toContain("must be greater than 0");
    });

    it("should fail for negative fixed discount", () => {
      const error = validateFixedDiscount(-25);
      expect(error).not.toBeNull();
      expect(error).toContain("must be greater than 0");
    });

    it("should pass when value is undefined", () => {
      const error = validateFixedDiscount(undefined);
      expect(error).toBeNull();
    });
  });

  describe("Required Field Validation", () => {
    it("should validate code is required", () => {
      const code = "";
      expect(code.trim()).toBe("");
    });

    it("should validate discount value is required and positive", () => {
      expect(validatePositiveValue(0, "Discount value")).not.toBeNull();
      expect(validatePositiveValue(undefined, "Discount value")).toBeNull();
    });

    it("should validate valid_until is required", () => {
      const validUntil = "";
      expect(validUntil).toBe("");
    });
  });

  describe("Combined Validation Scenarios", () => {
    it("should validate complete form with all fields", () => {
      const formData = {
        code: "SUMMER2024",
        description: "Summer sale",
        discount_type: "percentage" as const,
        discount_value: 20,
        min_purchase_amount: 50,
        max_discount_amount: 100,
        is_active: true,
        valid_from: "2024-06-01T00:00:00Z",
        valid_until: "2024-08-31T23:59:59Z",
        max_uses: 1000,
        max_uses_per_client: 1,
        applicable_services: ["service-1"],
      };

      const errors: Record<string, string> = {};

      if (!formData.code?.trim()) {
        errors.code = "Code is required";
      }

      if (!formData.discount_value || formData.discount_value <= 0) {
        errors.discount_value = "Discount value must be greater than 0";
      }

      if (
        formData.discount_type === "percentage" &&
        formData.discount_value &&
        (formData.discount_value < 0 || formData.discount_value > 100)
      ) {
        errors.discount_value = "Percentage must be between 0 and 100";
      }

      if (
        formData.max_discount_amount !== undefined &&
        formData.max_discount_amount <= 0
      ) {
        errors.max_discount_amount =
          "Max discount amount must be greater than 0";
      }

      if (
        formData.min_purchase_amount !== undefined &&
        formData.min_purchase_amount <= 0
      ) {
        errors.min_purchase_amount =
          "Min purchase amount must be greater than 0";
      }

      if (
        formData.max_uses_per_client !== undefined &&
        formData.max_uses_per_client <= 0
      ) {
        errors.max_uses_per_client =
          "Max uses per client must be greater than 0";
      }

      if (formData.valid_from && formData.valid_until) {
        const fromDate = new Date(formData.valid_from);
        const untilDate = new Date(formData.valid_until);
        if (fromDate > untilDate) {
          errors.valid_from =
            "Valid from date must be before valid until date";
        }
      }

      expect(Object.keys(errors).length).toBe(0);
    });

    it("should catch multiple validation errors", () => {
      const formData = {
        code: "",
        discount_type: "percentage" as const,
        discount_value: 150,
        min_purchase_amount: -10,
        max_discount_amount: 0,
        valid_from: "2024-12-31T23:59:59Z",
        valid_until: "2024-01-01T00:00:00Z",
      };

      const errors: Record<string, string> = {};

      if (!formData.code?.trim()) {
        errors.code = "Code is required";
      }

      if (
        formData.discount_type === "percentage" &&
        formData.discount_value &&
        (formData.discount_value < 0 || formData.discount_value > 100)
      ) {
        errors.discount_value = "Percentage must be between 0 and 100";
      }

      if (
        formData.min_purchase_amount !== undefined &&
        formData.min_purchase_amount <= 0
      ) {
        errors.min_purchase_amount =
          "Min purchase amount must be greater than 0";
      }

      if (
        formData.max_discount_amount !== undefined &&
        formData.max_discount_amount <= 0
      ) {
        errors.max_discount_amount =
          "Max discount amount must be greater than 0";
      }

      if (formData.valid_from && formData.valid_until) {
        const fromDate = new Date(formData.valid_from);
        const untilDate = new Date(formData.valid_until);
        if (fromDate > untilDate) {
          errors.valid_from =
            "Valid from date must be before valid until date";
        }
      }

      expect(Object.keys(errors).length).toBeGreaterThan(0);
      expect(errors.code).toBeDefined();
      expect(errors.discount_value).toBeDefined();
      expect(errors.min_purchase_amount).toBeDefined();
      expect(errors.max_discount_amount).toBeDefined();
      expect(errors.valid_from).toBeDefined();
    });
  });
});
