/**
 * PWA Push Notifications Utilities
 * Handles push notification permissions and subscriptions
 */

/**
 * Check if push notifications are supported
 */
export function isPushNotificationSupported(): boolean {
  return (
    "Notification" in window &&
    "serviceWorker" in navigator &&
    "PushManager" in window
  );
}

/**
 * Get current notification permission status
 */
export function getNotificationPermission(): NotificationPermission {
  if (!isPushNotificationSupported()) {
    return "denied";
  }
  return Notification.permission;
}

/**
 * Request notification permission
 * @returns Promise resolving to the permission status
 */
export async function requestNotificationPermission(): Promise<NotificationPermission> {
  if (!isPushNotificationSupported()) {
    console.warn("Push notifications not supported");
    return "denied";
  }

  try {
    const permission = await Notification.requestPermission();

    // Track permission result
    trackNotificationPermission(permission);

    return permission;
  } catch (error) {
    console.error("Error requesting notification permission:", error);
    return "denied";
  }
}

/**
 * Subscribe to push notifications
 * @param vapidPublicKey - VAPID public key from backend
 * @returns Promise resolving to the push subscription
 */
export async function subscribeToPushNotifications(
  vapidPublicKey: string,
): Promise<PushSubscription | null> {
  if (!isPushNotificationSupported()) {
    console.warn("Push notifications not supported");
    return null;
  }

  try {
    // Get service worker registration
    const registration = await navigator.serviceWorker.ready;

    // Check if already subscribed
    let subscription = await registration.pushManager.getSubscription();

    if (!subscription) {
      // Subscribe to push notifications
      subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(
          vapidPublicKey,
        ) as BufferSource,
      });
    }

    return subscription;
  } catch (error) {
    console.error("Error subscribing to push notifications:", error);
    return null;
  }
}

/**
 * Unsubscribe from push notifications
 */
export async function unsubscribeFromPushNotifications(): Promise<boolean> {
  if (!isPushNotificationSupported()) {
    return false;
  }

  try {
    const registration = await navigator.serviceWorker.ready;
    const subscription = await registration.pushManager.getSubscription();

    if (subscription) {
      await subscription.unsubscribe();
      return true;
    }

    return false;
  } catch (error) {
    console.error("Error unsubscribing from push notifications:", error);
    return false;
  }
}

/**
 * Show a local notification
 * @param title - Notification title
 * @param options - Notification options
 */
export async function showNotification(
  title: string,
  options?: NotificationOptions,
): Promise<void> {
  if (!isPushNotificationSupported()) {
    console.warn("Notifications not supported");
    return;
  }

  // Request permission if not granted
  if (Notification.permission !== "granted") {
    const permission = await requestNotificationPermission();
    if (permission !== "granted") {
      return;
    }
  }

  try {
    const registration = await navigator.serviceWorker.ready;
    await registration.showNotification(title, {
      icon: "/icon-192.png",
      badge: "/icon-72.png",
      ...options,
    });
  } catch (error) {
    console.error("Error showing notification:", error);
  }
}

/**
 * Convert VAPID key from base64 to Uint8Array
 */
function urlBase64ToUint8Array(base64String: string): Uint8Array {
  const padding = "=".repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding).replace(/-/g, "+").replace(/_/g, "/");

  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);

  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }

  return outputArray;
}

/**
 * Track notification permission result
 */
function trackNotificationPermission(permission: NotificationPermission): void {
  try {
    if (typeof window !== "undefined" && (window as any).gtag) {
      (window as any).gtag("event", "notification_permission", {
        event_category: "engagement",
        event_label: permission,
      });
    }

    localStorage.setItem("notification_permission", permission);
    localStorage.setItem(
      "notification_permission_at",
      new Date().toISOString(),
    );
  } catch (error) {
    console.error("Error tracking notification permission:", error);
  }
}

/**
 * Check if should show notification prompt
 */
export function shouldShowNotificationPrompt(): boolean {
  if (!isPushNotificationSupported()) {
    return false;
  }

  // Don't show if already granted or denied
  const permission = getNotificationPermission();
  if (permission !== "default") {
    return false;
  }

  // Don't show if recently dismissed
  try {
    const dismissedAt = localStorage.getItem(
      "notification_prompt_dismissed_at",
    );
    if (dismissedAt) {
      const dismissedDate = new Date(dismissedAt);
      const daysSinceDismissed =
        (Date.now() - dismissedDate.getTime()) / (1000 * 60 * 60 * 24);

      // Show again after 30 days
      if (daysSinceDismissed < 30) {
        return false;
      }
    }
  } catch {
    // Ignore localStorage errors
  }

  return true;
}

/**
 * Mark notification prompt as dismissed
 */
export function markNotificationPromptDismissed(): void {
  try {
    localStorage.setItem(
      "notification_prompt_dismissed_at",
      new Date().toISOString(),
    );
  } catch (error) {
    console.error("Error marking notification prompt dismissed:", error);
  }
}
