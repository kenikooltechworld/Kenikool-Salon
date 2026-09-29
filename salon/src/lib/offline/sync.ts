/**
 * Offline sync utilities for POS system
 */

import { offlineDB, type OfflineTransaction } from "./indexeddb";
import { apiClient } from "@/lib/utils/api";

export interface SyncResult {
  success: boolean;
  synced: number;
  failed: number;
  errors: string[];
}

class OfflineSyncManager {
  private isSyncing = false;
  private syncInterval: NodeJS.Timeout | null = null;

  async syncTransactions(): Promise<SyncResult> {
    if (this.isSyncing) {
      return {
        success: false,
        synced: 0,
        failed: 0,
        errors: ["Sync already in progress"],
      };
    }

    this.isSyncing = true;
    const result: SyncResult = {
      success: true,
      synced: 0,
      failed: 0,
      errors: [],
    };

    try {
      const pendingTransactions = await offlineDB.getPendingTransactions();

      for (const transaction of pendingTransactions) {
        try {
          // Send to server
          await apiClient.post("/transactions", transaction);

          // Mark as synced
          transaction.paymentStatus = "synced";
          await offlineDB.saveTransaction(transaction);

          result.synced++;
        } catch (error) {
          result.failed++;
          result.errors.push(
            `Failed to sync transaction ${transaction.id}: ${error}`,
          );
        }
      }

      result.success = result.failed === 0;
    } catch (error) {
      result.success = false;
      result.errors.push(`Sync failed: ${error}`);
    } finally {
      this.isSyncing = false;
    }

    return result;
  }

  async handleConflict(
    localTransaction: OfflineTransaction,
    serverTransaction: any,
  ): Promise<OfflineTransaction> {
    // Compare timestamps - use the newer version
    const localTime = new Date(localTransaction.updatedAt).getTime();
    const serverTime = new Date(serverTransaction.updatedAt).getTime();

    if (localTime > serverTime) {
      // Local is newer, use local version
      return localTransaction;
    } else {
      // Server is newer, use server version
      return {
        ...localTransaction,
        ...serverTransaction,
        updatedAt: serverTransaction.updatedAt,
      };
    }
  }

  startAutoSync(intervalMs: number = 30000): void {
    if (this.syncInterval) {
      clearInterval(this.syncInterval);
    }

    this.syncInterval = setInterval(() => {
      this.syncTransactions().catch((error) => {
        console.error("Auto sync error:", error);
      });
    }, intervalMs);
  }

  stopAutoSync(): void {
    if (this.syncInterval) {
      clearInterval(this.syncInterval);
      this.syncInterval = null;
    }
  }

  async clearSyncedTransactions(): Promise<void> {
    const pendingTransactions = await offlineDB.getPendingTransactions();

    for (const transaction of pendingTransactions) {
      if (transaction.paymentStatus === "synced") {
        await offlineDB.deleteTransaction(transaction.id);
      }
    }
  }
}

export const offlineSyncManager = new OfflineSyncManager();
