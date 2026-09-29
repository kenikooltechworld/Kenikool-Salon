/**
 * Service Worker Registration
 * Handles service worker registration and updates
 */

/**
 * Register service worker
 */
export async function registerServiceWorker(): Promise<ServiceWorkerRegistration | null> {
  if (!("serviceWorker" in navigator)) {
    console.warn("Service workers not supported");
    return null;
  }

  try {
    const registration = await navigator.serviceWorker.register(
      "/service-worker.js",
      {
        scope: "/",
      },
    );

    console.log("[SW] Service worker registered:", registration.scope);

    // Check for updates periodically
    setInterval(
      () => {
        registration.update();
      },
      60 * 60 * 1000,
    ); // Check every hour

    // Handle updates
    registration.addEventListener("updatefound", () => {
      const newWorker = registration.installing;
      if (!newWorker) return;

      newWorker.addEventListener("statechange", () => {
        if (
          newWorker.state === "installed" &&
          navigator.serviceWorker.controller
        ) {
          // New service worker available
          console.log("[SW] New service worker available");

          // Dispatch custom event
          window.dispatchEvent(new Event("sw-update-available"));

          // Show update notification
          showUpdateNotification();
        }
      });
    });

    return registration;
  } catch (error) {
    console.error("[SW] Service worker registration failed:", error);
    return null;
  }
}

/**
 * Unregister service worker
 */
export async function unregisterServiceWorker(): Promise<boolean> {
  if (!("serviceWorker" in navigator)) {
    return false;
  }

  try {
    const registration = await navigator.serviceWorker.getRegistration();
    if (registration) {
      await registration.unregister();
      console.log("[SW] Service worker unregistered");
      return true;
    }
    return false;
  } catch (error) {
    console.error("[SW] Service worker unregistration failed:", error);
    return false;
  }
}

/**
 * Skip waiting and activate new service worker
 */
export function skipWaiting(): void {
  if (!("serviceWorker" in navigator)) {
    return;
  }

  navigator.serviceWorker.controller?.postMessage({ type: "SKIP_WAITING" });
}

/**
 * Show update notification to user
 */
function showUpdateNotification(): void {
  // Create a custom event with update details
  const event = new CustomEvent("pwa-update-available", {
    detail: {
      message: "A new version is available!",
      action: "Refresh to update",
    },
  });

  window.dispatchEvent(event);
}

/**
 * Check if service worker is registered
 */
export async function isServiceWorkerRegistered(): Promise<boolean> {
  if (!("serviceWorker" in navigator)) {
    return false;
  }

  try {
    const registration = await navigator.serviceWorker.getRegistration();
    return !!registration;
  } catch {
    return false;
  }
}

/**
 * Get service worker registration
 */
export async function getServiceWorkerRegistration(): Promise<ServiceWorkerRegistration | null> {
  if (!("serviceWorker" in navigator)) {
    return null;
  }

  try {
    const registration = await navigator.serviceWorker.getRegistration();
    return registration || null;
  } catch (error) {
    console.error("[SW] Error getting service worker registration:", error);
    return null;
  }
}
