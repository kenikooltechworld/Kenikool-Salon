import { useState, useEffect, useCallback } from "react";
import {
  isPushNotificationSupported,
  getNotificationPermission,
  requestNotificationPermission,
  subscribeToPushNotifications,
  unsubscribeFromPushNotifications,
  shouldShowNotificationPrompt,
  markNotificationPromptDismissed,
} from "@/lib/pwa/notifications";

interface UsePushNotificationsReturn {
  isSupported: boolean;
  permission: NotificationPermission;
  isSubscribed: boolean;
  shouldShowPrompt: boolean;
  requestPermission: () => Promise<NotificationPermission>;
  subscribe: (vapidKey: string) => Promise<boolean>;
  unsubscribe: () => Promise<boolean>;
  dismissPrompt: () => void;
}

/**
 * Hook for push notification functionality
 */
export function usePushNotifications(): UsePushNotificationsReturn {
  const [isSupported] = useState(isPushNotificationSupported());
  const [permission, setPermission] = useState<NotificationPermission>(
    getNotificationPermission(),
  );
  const [isSubscribed, setIsSubscribed] = useState(false);
  const [shouldShowPrompt, setShouldShowPrompt] = useState(false);

  useEffect(() => {
    // Check if should show prompt
    setShouldShowPrompt(shouldShowNotificationPrompt());

    // Check if already subscribed
    const checkSubscription = async () => {
      if (!isSupported) return;

      try {
        const registration = await navigator.serviceWorker.ready;
        const subscription = await registration.pushManager.getSubscription();
        setIsSubscribed(!!subscription);
      } catch (error) {
        console.error("Error checking push subscription:", error);
      }
    };

    checkSubscription();
  }, [isSupported]);

  const handleRequestPermission =
    useCallback(async (): Promise<NotificationPermission> => {
      const newPermission = await requestNotificationPermission();
      setPermission(newPermission);

      if (newPermission === "granted") {
        setShouldShowPrompt(false);
      }

      return newPermission;
    }, []);

  const subscribe = useCallback(
    async (vapidKey: string): Promise<boolean> => {
      try {
        // Request permission if not granted
        if (permission !== "granted") {
          const newPermission = await handleRequestPermission();
          if (newPermission !== "granted") {
            return false;
          }
        }

        // Subscribe to push notifications
        const subscription = await subscribeToPushNotifications(vapidKey);

        if (subscription) {
          setIsSubscribed(true);

          // Send subscription to backend
          // await apiClient.post('/api/push-subscriptions', subscription.toJSON());

          return true;
        }

        return false;
      } catch (error) {
        console.error("Error subscribing to push notifications:", error);
        return false;
      }
    },
    [permission, handleRequestPermission],
  );

  const unsubscribe = useCallback(async (): Promise<boolean> => {
    try {
      const success = await unsubscribeFromPushNotifications();

      if (success) {
        setIsSubscribed(false);

        // Remove subscription from backend
        // await apiClient.delete('/api/push-subscriptions');
      }

      return success;
    } catch (error) {
      console.error("Error unsubscribing from push notifications:", error);
      return false;
    }
  }, []);

  const dismissPrompt = useCallback(() => {
    markNotificationPromptDismissed();
    setShouldShowPrompt(false);
  }, []);

  return {
    isSupported,
    permission,
    isSubscribed,
    shouldShowPrompt,
    requestPermission: handleRequestPermission,
    subscribe,
    unsubscribe,
    dismissPrompt,
  };
}
