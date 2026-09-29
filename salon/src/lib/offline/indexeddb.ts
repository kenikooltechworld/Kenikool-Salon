/**
 * IndexedDB utilities for offline storage
 */

const DB_NAME = "salon_pos_db";
const DB_VERSION = 1;

export interface OfflineTransaction {
  id: string;
  customerId: string;
  staffId: string;
  items: any[];
  subtotal: number;
  taxAmount: number;
  discountAmount: number;
  total: number;
  paymentMethod: string;
  paymentStatus: "pending" | "synced";
  createdAt: number;
  updatedAt: number;
}

export interface OfflineCart {
  id: string;
  customerId?: string;
  staffId: string;
  items: any[];
  subtotal: number;
  taxAmount: number;
  discountAmount: number;
  total: number;
  status: "active" | "completed" | "abandoned";
  createdAt: number;
  updatedAt: number;
}

export interface OfflineInventory {
  productId: string;
  quantityOnHand: number;
  quantityReserved: number;
  quantityAvailable: number;
  reorderPoint: number;
  lastUpdated: number;
}

class OfflineDB {
  private db: IDBDatabase | null = null;

  async init(): Promise<void> {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(DB_NAME, DB_VERSION);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        this.db = request.result;
        resolve();
      };

      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;

        // Create transactions store
        if (!db.objectStoreNames.contains("transactions")) {
          const transStore = db.createObjectStore("transactions", {
            keyPath: "id",
          });
          transStore.createIndex("status", "paymentStatus", {
            unique: false,
          });
          transStore.createIndex("createdAt", "createdAt", {
            unique: false,
          });
        }

        // Create carts store
        if (!db.objectStoreNames.contains("carts")) {
          const cartStore = db.createObjectStore("carts", { keyPath: "id" });
          cartStore.createIndex("status", "status", { unique: false });
        }

        // Create inventory store
        if (!db.objectStoreNames.contains("inventory")) {
          db.createObjectStore("inventory", { keyPath: "productId" });
        }
      };
    });
  }

  async saveTransaction(transaction: OfflineTransaction): Promise<void> {
    if (!this.db) throw new Error("Database not initialized");

    return new Promise((resolve, reject) => {
      const store = this.db!.transaction(
        "transactions",
        "readwrite",
      ).objectStore("transactions");
      const request = store.put(transaction);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve();
    });
  }

  async getTransaction(id: string): Promise<OfflineTransaction | undefined> {
    if (!this.db) throw new Error("Database not initialized");

    return new Promise((resolve, reject) => {
      const store = this.db!.transaction(
        "transactions",
        "readonly",
      ).objectStore("transactions");
      const request = store.get(id);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve(request.result);
    });
  }

  async getPendingTransactions(): Promise<OfflineTransaction[]> {
    if (!this.db) throw new Error("Database not initialized");

    return new Promise((resolve, reject) => {
      const store = this.db!.transaction(
        "transactions",
        "readonly",
      ).objectStore("transactions");
      const index = store.index("status");
      const request = index.getAll("pending");

      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve(request.result);
    });
  }

  async deleteTransaction(id: string): Promise<void> {
    if (!this.db) throw new Error("Database not initialized");

    return new Promise((resolve, reject) => {
      const store = this.db!.transaction(
        "transactions",
        "readwrite",
      ).objectStore("transactions");
      const request = store.delete(id);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve();
    });
  }

  async saveCart(cart: OfflineCart): Promise<void> {
    if (!this.db) throw new Error("Database not initialized");

    return new Promise((resolve, reject) => {
      const store = this.db!.transaction("carts", "readwrite").objectStore(
        "carts",
      );
      const request = store.put(cart);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve();
    });
  }

  async getCart(id: string): Promise<OfflineCart | undefined> {
    if (!this.db) throw new Error("Database not initialized");

    return new Promise((resolve, reject) => {
      const store = this.db!.transaction("carts", "readonly").objectStore(
        "carts",
      );
      const request = store.get(id);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve(request.result);
    });
  }

  async saveInventory(inventory: OfflineInventory): Promise<void> {
    if (!this.db) throw new Error("Database not initialized");

    return new Promise((resolve, reject) => {
      const store = this.db!.transaction("inventory", "readwrite").objectStore(
        "inventory",
      );
      const request = store.put(inventory);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve();
    });
  }

  async getInventory(productId: string): Promise<OfflineInventory | undefined> {
    if (!this.db) throw new Error("Database not initialized");

    return new Promise((resolve, reject) => {
      const store = this.db!.transaction("inventory", "readonly").objectStore(
        "inventory",
      );
      const request = store.get(productId);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve(request.result);
    });
  }

  async clearAll(): Promise<void> {
    if (!this.db) throw new Error("Database not initialized");

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(
        ["transactions", "carts", "inventory"],
        "readwrite",
      );

      transaction.objectStore("transactions").clear();
      transaction.objectStore("carts").clear();
      transaction.objectStore("inventory").clear();

      transaction.onerror = () => reject(transaction.error);
      transaction.oncomplete = () => resolve();
    });
  }
}

export const offlineDB = new OfflineDB();
