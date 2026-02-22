import { create } from "zustand";

export interface CartItem {
  itemType: "service" | "product" | "package";
  itemId: string;
  itemName: string;
  quantity: number;
  unitPrice: number;
  lineTotal: number;
}

export interface POSState {
  // Cart state
  cartItems: CartItem[];
  cartSubtotal: number;
  cartTaxAmount: number;
  cartDiscountAmount: number;
  cartTotal: number;

  // Transaction state
  currentTransactionId?: string;
  transactionHistory: string[];

  // Payment state
  paymentMethod: "cash" | "card" | "mobile_money" | "check" | "bank_transfer";
  paymentStatus: "pending" | "completed" | "failed" | "refunded";

  // Offline state
  isOffline: boolean;
  pendingTransactions: string[];
  syncStatus: "idle" | "syncing" | "error";

  // UI state
  showCart: boolean;
  showPayment: boolean;
  showReceipt: boolean;

  // Actions
  addToCart: (item: CartItem) => void;
  removeFromCart: (itemId: string) => void;
  updateCartItem: (itemId: string, quantity: number) => void;
  clearCart: () => void;
  calculateCartTotals: () => void;

  setPaymentMethod: (method: string) => void;
  setPaymentStatus: (status: string) => void;

  setOfflineStatus: (isOffline: boolean) => void;
  addPendingTransaction: (transactionId: string) => void;
  removePendingTransaction: (transactionId: string) => void;
  setSyncStatus: (status: "idle" | "syncing" | "error") => void;

  setShowCart: (show: boolean) => void;
  setShowPayment: (show: boolean) => void;
  setShowReceipt: (show: boolean) => void;

  setCurrentTransactionId: (id: string) => void;
  addToTransactionHistory: (id: string) => void;
}

export const usePOSStore = create<POSState>((set) => ({
  // Initial state
  cartItems: [],
  cartSubtotal: 0,
  cartTaxAmount: 0,
  cartDiscountAmount: 0,
  cartTotal: 0,

  currentTransactionId: undefined,
  transactionHistory: [],

  paymentMethod: "cash",
  paymentStatus: "pending",

  isOffline: false,
  pendingTransactions: [],
  syncStatus: "idle",

  showCart: true,
  showPayment: false,
  showReceipt: false,

  // Cart actions
  addToCart: (item: CartItem) =>
    set((state) => {
      const existingItem = state.cartItems.find(
        (i) => i.itemId === item.itemId,
      );

      let newItems: CartItem[];
      if (existingItem) {
        newItems = state.cartItems.map((i) =>
          i.itemId === item.itemId
            ? {
                ...i,
                quantity: i.quantity + item.quantity,
                lineTotal: (i.quantity + item.quantity) * i.unitPrice,
              }
            : i,
        );
      } else {
        newItems = [...state.cartItems, item];
      }

      const newState = { cartItems: newItems };
      // Recalculate totals
      const subtotal = newItems.reduce((sum, i) => sum + i.lineTotal, 0);
      return {
        ...newState,
        cartSubtotal: subtotal,
      };
    }),

  removeFromCart: (itemId: string) =>
    set((state) => {
      const newItems = state.cartItems.filter((i) => i.itemId !== itemId);
      const subtotal = newItems.reduce((sum, i) => sum + i.lineTotal, 0);
      return {
        cartItems: newItems,
        cartSubtotal: subtotal,
      };
    }),

  updateCartItem: (itemId: string, quantity: number) =>
    set((state) => {
      const newItems = state.cartItems.map((i) =>
        i.itemId === itemId
          ? {
              ...i,
              quantity,
              lineTotal: quantity * i.unitPrice,
            }
          : i,
      );
      const subtotal = newItems.reduce((sum, i) => sum + i.lineTotal, 0);
      return {
        cartItems: newItems,
        cartSubtotal: subtotal,
      };
    }),

  clearCart: () =>
    set({
      cartItems: [],
      cartSubtotal: 0,
      cartTaxAmount: 0,
      cartDiscountAmount: 0,
      cartTotal: 0,
    }),

  calculateCartTotals: () =>
    set((state) => {
      const subtotal = state.cartItems.reduce((sum, i) => sum + i.lineTotal, 0);
      const taxAmount = subtotal * 0.1; // 10% tax
      const total = subtotal + taxAmount - state.cartDiscountAmount;

      return {
        cartSubtotal: subtotal,
        cartTaxAmount: taxAmount,
        cartTotal: total,
      };
    }),

  // Payment actions
  setPaymentMethod: (method: string) => set({ paymentMethod: method as any }),

  setPaymentStatus: (status: string) => set({ paymentStatus: status as any }),

  // Offline actions
  setOfflineStatus: (isOffline: boolean) => set({ isOffline }),

  addPendingTransaction: (transactionId: string) =>
    set((state) => ({
      pendingTransactions: [...state.pendingTransactions, transactionId],
    })),

  removePendingTransaction: (transactionId: string) =>
    set((state) => ({
      pendingTransactions: state.pendingTransactions.filter(
        (id) => id !== transactionId,
      ),
    })),

  setSyncStatus: (status: "idle" | "syncing" | "error") =>
    set({ syncStatus: status }),

  // UI actions
  setShowCart: (show: boolean) => set({ showCart: show }),
  setShowPayment: (show: boolean) => set({ showPayment: show }),
  setShowReceipt: (show: boolean) => set({ showReceipt: show }),

  // Transaction actions
  setCurrentTransactionId: (id: string) => set({ currentTransactionId: id }),

  addToTransactionHistory: (id: string) =>
    set((state) => ({
      transactionHistory: [...state.transactionHistory, id],
    })),
}));
