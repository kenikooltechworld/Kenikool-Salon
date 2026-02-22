import { useState, useMemo, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { POSCart, POSPayment, POSReceipt } from "@/components/pos";
import { CashDropModal } from "@/components/pos/cash-drop-modal";
import { QuickKeysModal } from "@/components/pos/quick-keys-modal";
import { DiscountModal } from "@/components/pos/discount-modal";
import { ParkTransactionModal } from "@/components/pos/park-transaction-modal";
import { ParkedTransactionsModal } from "@/components/pos/parked-transactions-modal";
import { StartShiftModal } from "@/components/pos/start-shift-modal";
import { EndShiftModal } from "@/components/pos/end-shift-modal";
import { ShiftIndicator } from "@/components/pos/shift-indicator";
import { BookAppointmentModal } from "@/components/pos/book-appointment-modal";
import { BarcodeScanner } from "@/components/pos/barcode-scanner";
import { ReceiptCustomizationModal } from "@/components/pos/receipt-customization-modal";
import { InventoryAlert } from "@/components/pos/inventory-alert";
import { GiftCardModal } from "@/components/pos/gift-card-modal";
import { GiftCardRedeemModal } from "@/components/pos/gift-card-redeem-modal";
import { CurrencySelector } from "@/components/pos/currency-selector";
import { CustomerNotesPanel } from "@/components/pos/customer-notes-panel";
import { ReceiptOptionsModal } from "@/components/pos/receipt-options-modal";
import { KeyboardShortcuts } from "@/components/pos/keyboard-shortcuts";
import { SplitPaymentCalculator } from "@/components/pos/split-payment-calculator";
import { TransactionSearchModal } from "@/components/pos/transaction-search-modal";
import { ServiceTicketsModal } from "@/components/pos/service-tickets-modal";
import { POSHeader } from "@/components/pos/pos-header";
import { OfflineStatusBanner } from "@/components/pos/offline-status-banner";
import { CashDrawerStatus } from "@/components/pos/cash-drawer-status";
import { LoyaltyPointsCard } from "@/components/pos/loyalty-points-card";
import { ClientStylistSelector } from "@/components/pos/client-stylist-selector";
import { ProductServiceTabs } from "@/components/pos/product-service-tabs";
import { QuickKeysGrid } from "@/components/pos/quick-keys-grid";
import { useServices } from "@/lib/api/hooks/useServices";
import { useInventory } from "@/lib/api/hooks/useInventory";
import { useStylists } from "@/lib/api/hooks/useStylists";
import { useClients } from "@/lib/api/hooks/useClients";
import {
  useGetBalance,
  useEarnPoints,
  useRedeemPoints,
} from "@/lib/api/hooks/useLoyalty";
import {
  useCreateTransaction,
  useProcessPayment,
  useGetCashDrawer,
  useOpenCashDrawer,
  useCloseCashDrawer,
  useGetCurrentShift,
  useCheckInventoryAlert,
  type POSCartItem,
  type POSPaymentMethod,
  type POSTransaction,
} from "@/lib/api/hooks/usePOS";
import { SearchIcon } from "@/components/icons";
import { toast } from "sonner";
import { offlineDB } from "@/lib/offline/db";
import { syncEngine } from "@/lib/offline/sync-engine";
import { apiClient } from "@/lib/api/client";

interface Service {
  id: string;
  name: string;
  duration: number;
  price: number;
  image_url?: string;
}

interface Product {
  id: string;
  name: string;
  quantity: number;
  price: number;
  image_url?: string;
}

interface Client {
  id: string;
  name: string;
  email?: string;
  phone?: string;
}

interface Stylist {
  id: string;
  name: string;
}

interface QuickKey {
  id: string;
  type: "service" | "product";
  name: string;
  price: number;
}

export default function POSPage() {
  // Load quick keys from localStorage
  const loadQuickKeys = (): QuickKey[] => {
    if (typeof window === "undefined") return [];
    const savedQuickKeys = localStorage.getItem("pos_quick_keys");
    if (savedQuickKeys) {
      try {
        const parsed = JSON.parse(savedQuickKeys);
        if (Array.isArray(parsed)) {
          return parsed;
        }
      } catch (e) {
        console.error("Failed to load quick keys:", e);
      }
    }
    return [];
  };

  // Load saved stylist from localStorage
  const loadSavedStylist = (): string => {
    if (typeof window === "undefined") return "";
    const savedStylist = localStorage.getItem("pos_selected_stylist");
    return savedStylist || "";
  };

  // State
  const [cartItems, setCartItems] = useState<POSCartItem[]>([]);
  const [selectedClientId, setSelectedClientId] = useState<string>("");
  const [selectedStylistId, setSelectedStylistId] =
    useState<string>(loadSavedStylist);
  const [discount, setDiscount] = useState<number>(0);
  const [tax, setTax] = useState<number>(0);
  const [tip, setTip] = useState<number>(0);
  const [notes, setNotes] = useState<string>("");
  const [searchQuery, setSearchQuery] = useState("");
  const [currentTransaction, setCurrentTransaction] =
    useState<POSTransaction | null>(null);
  const [showReceipt, setShowReceipt] = useState(false);
  const [showPayment, setShowPayment] = useState(false);
  const [showCashDrop, setShowCashDrop] = useState(false);
  const [showQuickKeys, setShowQuickKeys] = useState(false);
  const [showDiscount, setShowDiscount] = useState(false);
  const [showParkTransaction, setShowParkTransaction] = useState(false);
  const [showParkedTransactions, setShowParkedTransactions] = useState(false);
  const [showStartShift, setShowStartShift] = useState(false);
  const [showEndShift, setShowEndShift] = useState(false);
  const [showBookAppointment, setShowBookAppointment] = useState(false);
  const [showReceiptCustomization, setShowReceiptCustomization] =
    useState(false);
  const [showGiftCard, setShowGiftCard] = useState(false);
  const [showGiftCardRedeem, setShowGiftCardRedeem] = useState(false);
  const [showCurrencySelector, setShowCurrencySelector] = useState(false);
  const [showReceiptOptions, setShowReceiptOptions] = useState(false);
  const [showTransactionSearch, setShowTransactionSearch] = useState(false);
  const [showSplitCalculator, setShowSplitCalculator] = useState(false);
  const [showServiceTickets, setShowServiceTickets] = useState(false);
  const [inventoryAlert, setInventoryAlert] = useState<any>(null);
  const [lastServiceId, setLastServiceId] = useState<string>("");
  const [quickKeys, setQuickKeys] = useState<QuickKey[]>(loadQuickKeys);
  const [isOnline, setIsOnline] = useState(true);
  const [pendingSync, setPendingSync] = useState(0);
  const [pointsToRedeem, setPointsToRedeem] = useState<number>(0);
  const [discountReason, setDiscountReason] = useState<string>("");
  const [membershipDiscount, setMembershipDiscount] = useState<number>(0);
  const [membershipPlanName, setMembershipPlanName] = useState<string>("");
  const [membershipDiscountPercentage, setMembershipDiscountPercentage] = useState<number>(0);

  // Queries
  const { data: servicesData } = useServices();
  // Map backend service data to component interface
  const services: Service[] = Array.isArray(servicesData)
    ? servicesData.map((s) => ({
        id: s.id,
        name: s.name,
        duration: s.duration_minutes,
        price: s.price,
        image_url: s.photo_url,
      }))
    : [];
  const { data: productsData } = useInventory();
  const products: Product[] = Array.isArray(productsData) ? productsData : [];
  const { data: stylistsData } = useStylists();
  const stylists: Stylist[] = Array.isArray(stylistsData) ? stylistsData : [];
  const { data: clientsData } = useClients();
  // Extract clients from paginated response
  const clients: Client[] = clientsData?.items ? clientsData.items : [];
  const { data: cashDrawer } = useGetCashDrawer();
  const { data: currentShift } = useGetCurrentShift();

  // Mutations
  const createTransaction = useCreateTransaction();
  const processPayment = useProcessPayment();
  const openCashDrawer = useOpenCashDrawer();
  const closeCashDrawer = useCloseCashDrawer();
  const earnPoints = useEarnPoints();
  const redeemPoints = useRedeemPoints();
  const checkInventoryAlert = useCheckInventoryAlert();

  // Get loyalty balance for selected client
  const { data: loyaltyBalance } = useGetBalance(selectedClientId || null);

  // Fetch membership discount when client changes
  useEffect(() => {
    const fetchMembershipDiscount = async () => {
      if (!selectedClientId) {
        setMembershipDiscount(0);
        setMembershipPlanName("");
        setMembershipDiscountPercentage(0);
        return;
      }

      try {
        const response = await apiClient.get(
          `/api/pos/client-discount/${selectedClientId}`
        );
        if (response.data) {
          const { has_discount, discount_percentage, plan_name } = response.data;
          setMembershipDiscountPercentage(discount_percentage);
          setMembershipPlanName(plan_name || "");
          
          // Calculate discount on services only
          if (has_discount && cartItems.length > 0) {
            const serviceTotal = cartItems
              .filter((item) => item.type === "service")
              .reduce((sum, item) => sum + item.price * item.quantity, 0);
            const discount = serviceTotal * (discount_percentage / 100);
            setMembershipDiscount(discount);
          } else {
            setMembershipDiscount(0);
          }
        }
      } catch (error) {
        console.error("Failed to fetch membership discount:", error);
        setMembershipDiscount(0);
        setMembershipPlanName("");
        setMembershipDiscountPercentage(0);
      }
    };

    fetchMembershipDiscount();
  }, [selectedClientId, cartItems]);

  // Calculate totals
  const subtotal = useMemo(() => {
    return cartItems.reduce(
      (sum, item) => sum + item.price * item.quantity - (item.discount || 0),
      0
    );
  }, [cartItems]);

  const total = useMemo(() => {
    const loyaltyDiscount = pointsToRedeem * 0.01;
    return subtotal - discount - loyaltyDiscount - membershipDiscount + tax + tip;
  }, [subtotal, discount, tax, tip, pointsToRedeem, membershipDiscount]);

  // Monitor online/offline status
  useEffect(() => {
    const updateOnlineStatus = () => {
      setIsOnline(navigator.onLine);
    };

    const updatePendingCount = async () => {
      const count = await syncEngine.getPendingCount();
      setPendingSync(count);
    };

    updateOnlineStatus();
    updatePendingCount();

    window.addEventListener("online", updateOnlineStatus);
    window.addEventListener("offline", updateOnlineStatus);

    const interval = setInterval(updatePendingCount, 5000);

    return () => {
      window.removeEventListener("online", updateOnlineStatus);
      window.removeEventListener("offline", updateOnlineStatus);
      clearInterval(interval);
    };
  }, []);

  // Save selected stylist to localStorage whenever it changes
  useEffect(() => {
    if (selectedStylistId) {
      localStorage.setItem("pos_selected_stylist", selectedStylistId);
    }
  }, [selectedStylistId]);

  // Update customer display whenever cart changes
  useEffect(() => {
    const displayData = {
      items: cartItems.map((item) => ({
        name: item.item_name,
        quantity: item.quantity,
        price: item.price,
      })),
      subtotal,
      discount: discount + pointsToRedeem * 0.01,
      tax,
      tip,
      total,
      status: showPayment
        ? "payment"
        : cartItems.length > 0
        ? "checkout"
        : "idle",
    };
    localStorage.setItem("pos_customer_display", JSON.stringify(displayData));
  }, [
    cartItems,
    subtotal,
    discount,
    tax,
    tip,
    total,
    pointsToRedeem,
    showPayment,
  ]);

  // Filter services and products
  const filteredServices = useMemo(() => {
    const servicesList = Array.isArray(services) ? services : [];
    if (!searchQuery) return servicesList;
    return servicesList.filter((s) =>
      s.name?.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [services, searchQuery]);

  const filteredProducts = useMemo(() => {
    const productsList = Array.isArray(products) ? products : [];
    if (!searchQuery) return productsList;
    return productsList.filter((p) =>
      p.name?.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [products, searchQuery]);

  // Handlers
  const addServiceToCart = (service: Service) => {
    const item: POSCartItem = {
      type: "service",
      item_id: service.id,
      item_name: service.name,
      quantity: 1,
      price: service.price,
      discount: 0,
    };
    setCartItems([...cartItems, item]);
    toast.success(`Added ${service.name} to cart`);
  };

  const addProductToCart = async (product: Product) => {
    if (product.quantity <= 0) {
      toast.error("Product out of stock");
      return;
    }

    // Check inventory alert
    try {
      const alert = await checkInventoryAlert.mutateAsync({
        product_id: product.id,
        quantity: 1,
      });

      if (!alert.available) {
        setInventoryAlert(alert);
        return;
      }

      if (alert.alert_type === "low_stock") {
        setInventoryAlert(alert);
        // Still allow adding to cart
      }
    } catch (error) {
      console.error("Failed to check inventory:", error);
    }

    const item: POSCartItem = {
      type: "product",
      item_id: product.id,
      item_name: product.name,
      quantity: 1,
      price: product.price,
      discount: 0,
    };
    setCartItems([...cartItems, item]);
    toast.success(`Added ${product.name} to cart`);
  };

  const updateCartItem = (index: number, item: POSCartItem) => {
    const newItems = [...cartItems];
    newItems[index] = item;
    setCartItems(newItems);
  };

  const removeCartItem = (index: number) => {
    setCartItems(cartItems.filter((_, i) => i !== index));
  };

  const handleCreateTransaction = async () => {
    if (cartItems.length === 0) {
      toast.error("Cart is empty");
      return;
    }

    if (!selectedStylistId) {
      toast.error("Please select a stylist before proceeding");
      return;
    }

    if (!currentShift) {
      toast.error("Please start a shift before processing transactions");
      setShowStartShift(true);
      return;
    }

    const loyaltyDiscount = pointsToRedeem * 0.01;

    try {
      if (isOnline) {
        const transaction = await createTransaction.mutateAsync({
          items: cartItems,
          client_id: selectedClientId || undefined,
          stylist_id: selectedStylistId || undefined,
          discount_total: discount + loyaltyDiscount,
          tax,
          tip,
          notes: notes || undefined,
        });

        setCurrentTransaction(transaction);
        setShowPayment(true);
        toast.success("Transaction created");
      } else {
        const mockTransaction: POSTransaction = {
          id: `offline_${Date.now()}`,
          tenant_id: "offline",
          transaction_number: `POS-OFFLINE-${Date.now()}`,
          items: cartItems,
          subtotal,
          discount_total: discount + loyaltyDiscount,
          tax,
          tip,
          total,
          payments: [],
          client_id: selectedClientId || undefined,
          stylist_id: selectedStylistId || undefined,
          created_by: "offline",
          created_at: new Date().toISOString(),
          status: "pending",
          notes: notes || undefined,
        };

        setCurrentTransaction(mockTransaction);
        setShowPayment(true);
        toast.success("Transaction created (offline mode)");
      }
    } catch (error: unknown) {
      const err = error as { response?: { data?: { detail?: string } } };
      toast.error(err.response?.data?.detail || "Failed to create transaction");
    }
  };

  const handleProcessPayment = async (payments: POSPaymentMethod[]) => {
    if (!currentTransaction) return;

    const totalPaid = payments.reduce((sum, p) => sum + p.amount, 0);
    const change = totalPaid - currentTransaction.total;

    // Update customer display with payment info
    const displayData = {
      items: cartItems.map((item) => ({
        name: item.item_name,
        quantity: item.quantity,
        price: item.price,
      })),
      subtotal,
      discount: discount + pointsToRedeem * 0.01,
      tax,
      tip,
      total,
      payment: {
        amount: totalPaid,
        change: change > 0 ? change : 0,
      },
      status: "complete",
    };
    localStorage.setItem("pos_customer_display", JSON.stringify(displayData));

    try {
      if (isOnline) {
        await processPayment.mutateAsync({
          transaction_id: currentTransaction.id,
          payments,
        });

        // Fetch the updated transaction with payments
        const updatedTransaction = await apiClient.get<POSTransaction>(
          `/api/pos/transactions/${currentTransaction.id}`
        );

        // Update current transaction with the payments
        setCurrentTransaction(updatedTransaction.data);

        if (selectedClientId) {
          if (pointsToRedeem > 0) {
            try {
              await redeemPoints.mutateAsync({
                client_id: selectedClientId,
                points: pointsToRedeem,
                reference_type: "pos_transaction",
                reference_id: currentTransaction.id,
                description: `Redeemed ${pointsToRedeem} points for $${(
                  pointsToRedeem * 0.01
                ).toFixed(2)} discount`,
              });
            } catch (error) {
              console.error("Failed to redeem points:", error);
            }
          }

          const pointsToEarn = Math.floor(currentTransaction.total);
          if (pointsToEarn > 0) {
            try {
              await earnPoints.mutateAsync({
                client_id: selectedClientId,
                points: pointsToEarn,
                reference_type: "pos_transaction",
                reference_id: currentTransaction.id,
                description: `Earned ${pointsToEarn} points from purchase`,
              });
              toast.success(`${pointsToEarn} loyalty points earned!`, {
                duration: 3000,
              });
            } catch (error) {
              console.error("Failed to earn points:", error);
            }
          }
        }

        setShowPayment(false);
        setShowReceipt(true);
        // Optionally show receipt options after a delay
        setTimeout(() => {
          if (selectedClientId) {
            setShowReceiptOptions(true);
          }
        }, 1000);
        toast.success("Payment processed successfully");
      } else {
        await offlineDB.addTransaction({
          type: "pos_transaction",
          action: "create",
          data: {
            items: currentTransaction.items,
            client_id: currentTransaction.client_id,
            stylist_id: currentTransaction.stylist_id,
            discount_total: currentTransaction.discount_total,
            tax: currentTransaction.tax,
            tip: currentTransaction.tip,
            notes: currentTransaction.notes,
            payments,
          },
        });

        const updatedTransaction = {
          ...currentTransaction,
          payments,
          status: "completed" as const,
        };

        await offlineDB.addCachedItem("pos_transactions", updatedTransaction);

        setCurrentTransaction(updatedTransaction);
        setShowPayment(false);
        setShowReceipt(true);
        toast.success("Payment saved (will sync when online)");

        const count = await syncEngine.getPendingCount();
        setPendingSync(count);
      }
    } catch (error: unknown) {
      const err = error as { response?: { data?: { detail?: string } } };
      toast.error(err.response?.data?.detail || "Failed to process payment");
    }
  };

  const handleNewTransaction = () => {
    setCartItems([]);
    setSelectedClientId("");
    // Keep the stylist selected - don't clear it
    // setSelectedStylistId("");
    setDiscount(0);
    setDiscountReason("");
    setTax(0);
    setTip(0);
    setNotes("");
    setPointsToRedeem(0);
    setCurrentTransaction(null);
    setShowReceipt(false);
    setShowPayment(false);

    // Reset customer display
    localStorage.setItem(
      "pos_customer_display",
      JSON.stringify({
        items: [],
        subtotal: 0,
        discount: 0,
        tax: 0,
        tip: 0,
        total: 0,
        status: "idle",
      })
    );
  };

  const handleOpenCashDrawer = async () => {
    const balance = prompt("Enter opening balance:");
    if (balance) {
      try {
        await openCashDrawer.mutateAsync({
          opening_balance: parseFloat(balance),
        });
        toast.success("Cash drawer opened");
      } catch (error: unknown) {
        const err = error as { response?: { data?: { detail?: string } } };
        toast.error(err.response?.data?.detail || "Failed to open cash drawer");
      }
    }
  };

  const handleCloseCashDrawer = async () => {
    const balance = prompt("Enter actual cash counted:");
    if (balance) {
      try {
        const result = await closeCashDrawer.mutateAsync({
          actual_balance: parseFloat(balance),
        });
        toast.success(
          `Cash drawer closed. Variance: $${
            result.variance?.toFixed(2) || "0.00"
          }`
        );
      } catch (error: unknown) {
        const err = error as { response?: { data?: { detail?: string } } };
        toast.error(
          err.response?.data?.detail || "Failed to close cash drawer"
        );
      }
    }
  };

  const handleSyncNow = async () => {
    toast.info("Syncing offline transactions...");
    const result = await syncEngine.sync();
    if (result.status === "success") {
      toast.success(`Synced ${result.completed} transactions`);
      setPendingSync(0);
    } else {
      toast.error(`Sync failed: ${result.failed} transactions`);
    }
  };

  const handleOpenCustomerDisplay = () => {
    const width = 800;
    const height = 600;
    const left = window.screen.width - width;
    const top = 0;
    window.open(
      "/dashboard/pos/customer-display",
      "CustomerDisplay",
      `width=${width},height=${height},left=${left},top=${top}`
    );
    toast.success("Customer display opened in new window");
  };

  const handleQuickKeyClick = (key: QuickKey) => {
    if (key.type === "service") {
      const service = services.find((s) => s.id === key.id);
      if (service) addServiceToCart(service);
    } else {
      const product = products.find((p) => p.id === key.id);
      if (product) addProductToCart(product);
    }
  };

  const handleClientChange = (clientId: string) => {
    setSelectedClientId(clientId);
    setPointsToRedeem(0);
  };

  const handleApplyDiscount = (discountData: {
    amount: number;
    type: string;
    reason: string;
  }) => {
    setDiscount(discountData.amount);
    setDiscountReason(discountData.reason);
  };

  const handleSplitPayment = (payments: POSPaymentMethod[]) => {
    if (!currentTransaction) return;
    handleProcessPayment(payments);
    setShowSplitCalculator(false);
  };

  // Get service IDs from cart
  const serviceIdsInCart = cartItems
    .filter((item) => item.type === "service")
    .map((item) => item.item_id);

  return (
    <div className="container mx-auto p-6 space-y-6 max-w-full overflow-x-hidden">
      {/* Keyboard Shortcuts Handler */}
      <KeyboardShortcuts
        onNewTransaction={handleNewTransaction}
        onSearch={() => setShowTransactionSearch(true)}
        onPayment={() => {
          if (cartItems.length > 0) {
            handleCreateTransaction();
          }
        }}
        onDiscount={() => {
          if (cartItems.length > 0) {
            setShowDiscount(true);
          }
        }}
        onPark={() => {
          if (cartItems.length > 0) {
            setShowParkTransaction(true);
          }
        }}
        onQuickKeys={() => setShowQuickKeys(true)}
      />

      <POSHeader
        cashDrawerStatus={cashDrawer?.status}
        onOpenQuickKeys={() => setShowQuickKeys(true)}
        onOpenCashDrop={() => setShowCashDrop(true)}
        onOpenCashDrawer={handleOpenCashDrawer}
        onCloseCashDrawer={handleCloseCashDrawer}
        onOpenParkedTransactions={() => setShowParkedTransactions(true)}
        onOpenCustomerDisplay={handleOpenCustomerDisplay}
        onOpenReceiptCustomization={() => setShowReceiptCustomization(true)}
        onOpenGiftCards={() => setShowGiftCard(true)}
        onOpenTransactionSearch={() => setShowTransactionSearch(true)}
        onOpenServiceTickets={() => setShowServiceTickets(true)}
      />

      <OfflineStatusBanner
        isOnline={isOnline}
        pendingSync={pendingSync}
        onSyncNow={handleSyncNow}
      />

      <ShiftIndicator
        currentShift={currentShift || null}
        onStartShift={() => setShowStartShift(true)}
        onEndShift={() => setShowEndShift(true)}
      />

      {cashDrawer?.status === "open" && (
        <CashDrawerStatus expectedBalance={cashDrawer.expected_balance} />
      )}

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <div className="xl:col-span-2 space-y-4">
          <QuickKeysGrid
            quickKeys={quickKeys}
            onEditQuickKeys={() => setShowQuickKeys(true)}
            onQuickKeyClick={handleQuickKeyClick}
          />

          <div className="relative">
            <SearchIcon className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search services or products..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>

          <ClientStylistSelector
            clients={clients}
            stylists={stylists}
            selectedClientId={selectedClientId}
            selectedStylistId={selectedStylistId}
            onClientChange={handleClientChange}
            onStylistChange={setSelectedStylistId}
          />

          {selectedClientId && loyaltyBalance && (
            <LoyaltyPointsCard
              loyaltyBalance={loyaltyBalance}
              pointsToRedeem={pointsToRedeem}
              onPointsChange={setPointsToRedeem}
            />
          )}

          {selectedClientId && (
            <CustomerNotesPanel clientId={selectedClientId} />
          )}

          <ProductServiceTabs
            services={filteredServices}
            products={filteredProducts}
            onAddService={addServiceToCart}
            onAddProduct={addProductToCart}
          />
        </div>

        <div className="space-y-4">
          <POSCart
            items={cartItems}
            onUpdateItem={updateCartItem}
            onRemoveItem={removeCartItem}
            onAddItem={(item) => setCartItems([...cartItems, item])}
            subtotal={subtotal}
            discount={discount}
            tax={tax}
            tip={tip}
            total={total}
            notes={notes}
            loyaltyDiscount={pointsToRedeem * 0.01}
            discountReason={discountReason}
            membershipDiscount={membershipDiscount}
            membershipPlanName={membershipPlanName}
            membershipDiscountPercentage={membershipDiscountPercentage}
            onUpdateDiscount={setDiscount}
            onUpdateTax={setTax}
            onUpdateTip={setTip}
            onUpdateNotes={setNotes}
          />

          <Button
            onClick={() => setShowDiscount(true)}
            variant="outline"
            className="w-full"
            disabled={cartItems.length === 0}
          >
            Apply Discount / Promo Code
          </Button>

          <Button
            onClick={() => setShowGiftCardRedeem(true)}
            variant="outline"
            className="w-full"
            disabled={cartItems.length === 0}
          >
            Redeem Gift Card
          </Button>

          <Button
            onClick={() => setShowCurrencySelector(true)}
            variant="outline"
            className="w-full"
            disabled={cartItems.length === 0}
          >
            Multi-Currency Payment
          </Button>

          <div className="flex gap-2">
            <Button
              onClick={() => setShowParkTransaction(true)}
              variant="outline"
              className="flex-1"
              disabled={cartItems.length === 0}
            >
              Park
            </Button>
            <Button
              onClick={handleCreateTransaction}
              disabled={cartItems.length === 0 || createTransaction.isPending}
              className="flex-1"
              size="lg"
            >
              {createTransaction.isPending
                ? "Processing..."
                : "Proceed to Payment"}
            </Button>
          </div>

          <Button
            onClick={() => setShowSplitCalculator(true)}
            variant="outline"
            className="w-full"
            disabled={cartItems.length === 0}
          >
            Split Payment Calculator
          </Button>
        </div>
      </div>

      {showPayment && currentTransaction && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-background rounded-lg max-w-md w-full">
            <POSPayment
              total={currentTransaction.total}
              clientId={selectedClientId}
              onProcessPayment={handleProcessPayment}
              isProcessing={processPayment.isPending}
              membershipDiscount={membershipDiscount}
              membershipPlanName={membershipPlanName}
            />
          </div>
        </div>
      )}

      <POSReceipt
        transaction={currentTransaction}
        open={showReceipt}
        onClose={handleNewTransaction}
      />

      {currentTransaction && (
        <ReceiptOptionsModal
          open={showReceiptOptions}
          onClose={() => setShowReceiptOptions(false)}
          transactionId={currentTransaction.id}
        />
      )}

      {currentTransaction && (
        <GiftCardRedeemModal
          open={showGiftCardRedeem}
          onClose={() => setShowGiftCardRedeem(false)}
          transactionId={currentTransaction.id}
          onRedeemed={(amount) => {
            setDiscount(discount + amount);
            toast.success(`Gift card redeemed: $${amount.toFixed(2)}`);
          }}
        />
      )}

      <CashDropModal
        open={showCashDrop}
        onClose={() => setShowCashDrop(false)}
      />

      <QuickKeysModal
        open={showQuickKeys}
        onClose={() => setShowQuickKeys(false)}
        services={services}
        products={products}
        quickKeys={quickKeys}
        onUpdateQuickKeys={setQuickKeys}
      />

      <DiscountModal
        open={showDiscount}
        onClose={() => setShowDiscount(false)}
        cartSubtotal={subtotal}
        clientId={selectedClientId}
        serviceIds={serviceIdsInCart}
        onApplyDiscount={handleApplyDiscount}
      />

      <ParkTransactionModal
        open={showParkTransaction}
        onClose={() => {
          setShowParkTransaction(false);
          handleNewTransaction();
        }}
        items={cartItems}
        clientId={selectedClientId}
        stylistId={selectedStylistId}
        discountTotal={discount}
        tax={tax}
        tip={tip}
        notes={notes}
      />

      <ParkedTransactionsModal
        open={showParkedTransactions}
        onClose={() => setShowParkedTransactions(false)}
        onResume={(transactionId) => {
          // Transaction is already created, just show payment
          setShowPayment(true);
        }}
      />

      <StartShiftModal
        open={showStartShift}
        onClose={() => setShowStartShift(false)}
      />

      <EndShiftModal
        open={showEndShift}
        onClose={() => setShowEndShift(false)}
        currentShift={currentShift || null}
      />

      {/* Inventory Alert */}
      {inventoryAlert && (
        <div className="fixed bottom-4 right-4 max-w-md z-50">
          <InventoryAlert
            alert={inventoryAlert}
            onSelectAlternative={(alt) => {
              const item: POSCartItem = {
                type: "product",
                item_id: alt.id,
                item_name: alt.name,
                quantity: 1,
                price: alt.price,
                discount: 0,
              };
              setCartItems([...cartItems, item]);
              setInventoryAlert(null);
              toast.success(`Added ${alt.name} to cart`);
            }}
            onDismiss={() => setInventoryAlert(null)}
          />
        </div>
      )}

      {/* Barcode Scanner */}
      <div className="mt-4">
        <BarcodeScanner
          onItemScanned={(item) => {
            const cartItem: POSCartItem = {
              type: item.type === "service" ? "service" : "product",
              item_id: item.id,
              item_name: item.name,
              quantity: 1,
              price: item.price,
              discount: 0,
            };
            setCartItems([...cartItems, cartItem]);
          }}
        />
      </div>

      {/* Book Appointment Modal */}
      <BookAppointmentModal
        open={showBookAppointment}
        onClose={() => setShowBookAppointment(false)}
        clientId={selectedClientId}
        clientName={clients.find((c: any) => c.id === selectedClientId)?.name}
        clientPhone={clients.find((c: any) => c.id === selectedClientId)?.phone}
        stylistId={selectedStylistId}
        lastServiceId={lastServiceId}
      />

      {/* Receipt Customization Modal */}
      <ReceiptCustomizationModal
        open={showReceiptCustomization}
        onClose={() => setShowReceiptCustomization(false)}
      />

      {/* Gift Card Modal */}
      <GiftCardModal
        open={showGiftCard}
        onClose={() => setShowGiftCard(false)}
        onRedeemSuccess={(amount, cardNumber) => {
          setDiscount(discount + amount);
          setDiscountReason(`Gift Card: ${cardNumber}`);
          toast.success(`Gift card redeemed: $${amount.toFixed(2)}`);
        }}
      />

      {/* Currency Selector Modal */}
      <CurrencySelector
        open={showCurrencySelector}
        onClose={() => setShowCurrencySelector(false)}
        amount={total}
        onCurrencySelected={(convertedAmount, currency) => {
          toast.info(
            `Payment will be processed in ${currency}: ${convertedAmount.toFixed(
              2
            )}`
          );
        }}
      />

      {/* Receipt Options Modal */}
      {currentTransaction && (
        <ReceiptOptionsModal
          open={showReceiptOptions}
          onClose={() => setShowReceiptOptions(false)}
          transactionId={currentTransaction.id}
          clientEmail={clients.find((c) => c.id === selectedClientId)?.email}
          clientPhone={clients.find((c) => c.id === selectedClientId)?.phone}
        />
      )}

      {/* Transaction Search Modal */}
      <TransactionSearchModal
        open={showTransactionSearch}
        onOpenChange={setShowTransactionSearch}
        onSelectTransaction={(transaction) => {
          setShowTransactionSearch(false);
          toast.info(`Selected transaction: ${transaction.transaction_number}`);
        }}
      />

      {/* Split Payment Calculator */}
      {currentTransaction && (
        <SplitPaymentCalculator
          open={showSplitCalculator}
          onOpenChange={setShowSplitCalculator}
          totalAmount={currentTransaction.total}
          onSplitCalculated={(splits) => {
            const payments = splits.map((split) => ({
              method: split.method as "cash" | "card" | "transfer",
              amount: split.amount,
              reference: undefined,
            }));
            handleSplitPayment(payments);
          }}
        />
      )}

      {/* Service Tickets Modal */}
      <ServiceTicketsModal
        open={showServiceTickets}
        onClose={() => setShowServiceTickets(false)}
      />
    </div>
  );
}
