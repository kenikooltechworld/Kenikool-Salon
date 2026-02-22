import { useState } from "react";
import { useServices } from "@/hooks/useServices";
import { useCheckout } from "@/hooks/useCheckout";
import { useCustomers } from "@/hooks/useCustomers";
import { useStaff } from "@/hooks/useStaff";
import { useInventory } from "@/hooks/useInventory";
import { usePOSStore } from "@/stores/pos";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Spinner } from "@/components/ui/spinner";
import type { Service } from "@/types/service";
import type { Staff } from "@/types/staff";
import type { Customer } from "@/hooks/useCustomers";
import type { Inventory } from "@/hooks/useInventory";
import CartItems from "./CartItems";
import ItemSelector from "./ItemSelector";
import PaymentProcessor from "./PaymentProcessor";

export default function TransactionEntry() {
  const [showPayment, setShowPayment] = useState(false);
  const [customerId, setCustomerId] = useState("");
  const [staffId, setStaffId] = useState("");
  const [paymentMethod, setPaymentMethod] = useState<
    "cash" | "card" | "mobile_money" | "check"
  >("cash");

  // Fetch data from backend
  const { data: servicesData, isLoading: servicesLoading } = useServices();
  const customersQuery = useCustomers();
  const staffQuery = useStaff();
  const inventoryQuery = useInventory();

  const { mutate: checkout, isPending: isCheckingOut } = useCheckout();
  const {
    cartItems,
    cartSubtotal,
    cartTaxAmount,
    cartTotal,
    clearCart,
    calculateCartTotals,
  } = usePOSStore();

  // Extract data from queries
  const services = (servicesData as Service[]) || [];
  const customers = customersQuery.data?.customers || [];
  const staff = staffQuery.data || [];
  const inventory = inventoryQuery.inventory || [];

  const isLoadingCustomers = customersQuery.isLoading;
  const isLoadingStaff = staffQuery.isLoading;
  const isLoadingInventory = inventoryQuery.isLoadingInventory;

  const handleCheckout = async () => {
    if (!customerId || !staffId || cartItems.length === 0) {
      alert("Please fill in all required fields and add items to cart");
      return;
    }

    // For cash and check payments, create transaction immediately
    if (paymentMethod === "cash" || paymentMethod === "check") {
      const transactionItems = cartItems.map((item: any) => ({
        item_type: item.itemType || "service",
        item_id: item.itemId,
        item_name: item.itemName,
        quantity: item.quantity,
        unit_price: item.unitPrice,
        tax_rate: 0.1, // 10% tax rate
        discount_rate: 0,
      }));

      checkout(
        {
          customer_id: customerId,
          staff_id: staffId,
          items: transactionItems,
          payment_method: paymentMethod,
        },
        {
          onSuccess: () => {
            setShowPayment(true);
            calculateCartTotals();
          },
        },
      );
    } else {
      // For card and mobile money, show payment processor WITHOUT creating transaction first
      setShowPayment(true);
    }
  };

  const handleClearCart = () => {
    if (confirm("Clear cart?")) {
      clearCart();
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
      {/* Item Selection */}
      <div className="md:col-span-2 space-y-4 md:space-y-6">
        {/* Customer & Staff Selection */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4 text-foreground">
            Customer & Staff
          </h3>
          <div className="space-y-4">
            {/* Customer Dropdown */}
            <div>
              <Label htmlFor="customer-select" className="mb-2 block">
                Customer
              </Label>
              {isLoadingCustomers ? (
                <div className="flex items-center justify-center py-2">
                  <Spinner className="w-4 h-4" />
                </div>
              ) : (
                <select
                  id="customer-select"
                  value={customerId}
                  onChange={(e) => setCustomerId(e.target.value)}
                  className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground"
                >
                  <option value="">Select a customer...</option>
                  {customers.map((customer: Customer) => (
                    <option key={customer.id} value={customer.id}>
                      {customer.firstName} {customer.lastName}
                    </option>
                  ))}
                </select>
              )}
            </div>

            {/* Staff Dropdown */}
            <div>
              <Label htmlFor="staff-select" className="mb-2 block">
                Staff Member
              </Label>
              {isLoadingStaff ? (
                <div className="flex items-center justify-center py-2">
                  <Spinner className="w-4 h-4" />
                </div>
              ) : (
                <select
                  id="staff-select"
                  value={staffId}
                  onChange={(e) => setStaffId(e.target.value)}
                  className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground"
                >
                  <option value="">Select a staff member...</option>
                  {staff.map((member: Staff) => (
                    <option key={member.id} value={member.id}>
                      {member.firstName} {member.lastName}
                    </option>
                  ))}
                </select>
              )}
            </div>
          </div>
        </Card>

        {/* Services Card */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4 text-foreground">
            Available Services
          </h3>
          {servicesLoading ? (
            <div className="flex justify-center py-8">
              <Spinner />
            </div>
          ) : services.length === 0 ? (
            <p className="text-muted-foreground text-center py-4">
              No services available
            </p>
          ) : (
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {services.map((service: Service) => (
                <div
                  key={service.id}
                  className="p-3 border border-border rounded-lg hover:bg-muted cursor-pointer transition"
                >
                  <div className="flex justify-between items-start gap-3">
                    <div className="flex-1">
                      <p className="font-medium text-foreground">
                        {service.name}
                      </p>
                      <p className="text-xs text-muted-foreground mt-1">
                        {service.duration_minutes} mins • {service.category}
                      </p>
                      {service.description && (
                        <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
                          {service.description}
                        </p>
                      )}
                    </div>
                    <div className="text-right">
                      <p className="font-semibold text-primary">
                        ₦
                        {service.price.toLocaleString("en-NG", {
                          maximumFractionDigits: 2,
                        })}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>

        {/* Staff Card */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4 text-foreground">
            Available Staff
          </h3>
          {isLoadingStaff ? (
            <div className="flex justify-center py-8">
              <Spinner />
            </div>
          ) : staff.length === 0 ? (
            <p className="text-muted-foreground text-center py-4">
              No staff available
            </p>
          ) : (
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {staff.map((member: Staff) => (
                <div
                  key={member.id}
                  className="p-3 border border-border rounded-lg hover:bg-muted transition"
                >
                  <div className="flex items-start gap-3">
                    {member.profile_image_url && (
                      <img
                        src={member.profile_image_url}
                        alt={`${member.firstName} ${member.lastName}`}
                        className="w-10 h-10 rounded-full object-cover flex-shrink-0"
                      />
                    )}
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-foreground">
                        {member.firstName} {member.lastName}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {member.specialties?.join(", ") || "General"}
                      </p>
                      <p className="text-xs text-muted-foreground mt-1">
                        {member.status}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>

        {/* Inventory Card */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4 text-foreground">
            Inventory Items
          </h3>
          {isLoadingInventory ? (
            <div className="flex justify-center py-8">
              <Spinner />
            </div>
          ) : inventory.length === 0 ? (
            <p className="text-muted-foreground text-center py-4">
              No inventory items
            </p>
          ) : (
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {inventory.map((item: Inventory) => (
                <div
                  key={item.id}
                  className="p-3 border border-border rounded-lg hover:bg-muted transition"
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="font-medium text-foreground">{item.name}</p>
                      <p className="text-xs text-muted-foreground">
                        SKU: {item.sku}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold text-primary">
                        ₦
                        {item.unit_cost.toLocaleString("en-NG", {
                          maximumFractionDigits: 2,
                        })}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        Stock: {item.quantity}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>

        {/* Item Selector */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4 text-foreground">
            Select Items
          </h3>
          {servicesLoading ? (
            <div className="flex justify-center py-8">
              <Spinner />
            </div>
          ) : (
            <ItemSelector services={services} />
          )}
        </Card>
      </div>

      {/* Cart Summary */}
      <div className="space-y-4 md:space-y-6">
        <Card className="p-4 md:p-6 sticky top-6">
          <h3 className="text-lg font-semibold mb-4 text-foreground">Cart</h3>

          {cartItems.length === 0 ? (
            <p className="text-muted-foreground text-center py-8">
              Cart is empty
            </p>
          ) : (
            <>
              <CartItems />

              <div className="border-t border-border mt-4 pt-4 space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Subtotal</span>
                  <span className="font-medium text-foreground">
                    ₦
                    {cartSubtotal.toLocaleString("en-NG", {
                      maximumFractionDigits: 2,
                    })}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Tax (10%)</span>
                  <span className="font-medium text-foreground">
                    ₦
                    {cartTaxAmount.toLocaleString("en-NG", {
                      maximumFractionDigits: 2,
                    })}
                  </span>
                </div>
                <div className="border-t border-border pt-2 flex justify-between">
                  <span className="font-semibold text-foreground">Total</span>
                  <span className="text-xl font-bold text-primary">
                    ₦
                    {cartTotal.toLocaleString("en-NG", {
                      maximumFractionDigits: 2,
                    })}
                  </span>
                </div>
              </div>

              <div className="space-y-4 mt-6">
                <div>
                  <Label htmlFor="payment-method" className="mb-2 block">
                    Payment Method
                  </Label>
                  <select
                    id="payment-method"
                    value={paymentMethod}
                    onChange={(e) => setPaymentMethod(e.target.value as any)}
                    className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground"
                  >
                    <option value="cash">Cash</option>
                    <option value="card">Card (Paystack)</option>
                    <option value="mobile_money">
                      Mobile Money (Paystack)
                    </option>
                    <option value="check">Check</option>
                  </select>
                </div>

                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    onClick={handleClearCart}
                    className="flex-1"
                  >
                    Clear
                  </Button>
                  <Button
                    onClick={handleCheckout}
                    disabled={isCheckingOut}
                    className="flex-1"
                  >
                    {isCheckingOut ? (
                      <Spinner className="w-4 h-4" />
                    ) : (
                      "Checkout"
                    )}
                  </Button>
                </div>
              </div>
            </>
          )}
        </Card>

        {showPayment && (
          <PaymentProcessor
            customerId={customerId}
            staffId={staffId}
            paymentMethod={paymentMethod}
            onClose={() => setShowPayment(false)}
          />
        )}
      </div>
    </div>
  );
}
