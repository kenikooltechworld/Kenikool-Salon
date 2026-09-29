/**
 * PWA Installation Utilities
 * Handles PWA installation prompts and detection
 */

interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: "accepted" | "dismissed" }>;
}

let deferredPrompt: BeforeInstallPromptEvent | null = null;

/**
 * Initialize PWA install prompt listener
 */
export function initPWAInstall(): void {
  window.addEventListener("beforeinstallprompt", (e: Event) => {
    // Prevent the mini-infobar from appearing on mobile
    e.preventDefault();
    // Stash the event so it can be triggered later
    deferredPrompt = e as BeforeInstallPromptEvent;

    // Dispatch custom event to notify app
    window.dispatchEvent(new Event("pwa-install-available"));
  });

  window.addEventListener("appinstalled", () => {
    // Clear the deferredPrompt
    deferredPrompt = null;

    // Track installation
    trackPWAInstall();

    // Dispatch custom event
    window.dispatchEvent(new Event("pwa-installed"));
  });
}

/**
 * Show PWA install prompt
 * @returns Promise resolving to true if user accepted, false if dismissed
 */
export async function showInstallPrompt(): Promise<boolean> {
  if (!deferredPrompt) {
    console.warn("PWA install prompt not available");
    return false;
  }

  try {
    // Show the install prompt
    await deferredPrompt.prompt();

    // Wait for the user to respond to the prompt
    const { outcome } = await deferredPrompt.userChoice;

    // Clear the deferredPrompt
    deferredPrompt = null;

    return outcome === "accepted";
  } catch (error) {
    console.error("Error showing install prompt:", error);
    return false;
  }
}

/**
 * Check if PWA is installable
 */
export function isPWAInstallable(): boolean {
  return deferredPrompt !== null;
}

/**
 * Check if app is running as PWA (standalone mode)
 */
export function isPWAInstalled(): boolean {
  // Check if running in standalone mode
  if (window.matchMedia("(display-mode: standalone)").matches) {
    return true;
  }

  // Check for iOS standalone mode
  if ((window.navigator as any).standalone === true) {
    return true;
  }

  return false;
}

/**
 * Check if device is iOS
 */
export function isIOS(): boolean {
  return (
    /iPad|iPhone|iPod/.test(navigator.userAgent) && !(window as any).MSStream
  );
}

/**
 * Check if device is Android
 */
export function isAndroid(): boolean {
  return /Android/.test(navigator.userAgent);
}

/**
 * Get install instructions based on device
 */
export function getInstallInstructions(): string {
  if (isIOS()) {
    return 'Tap the Share button and then "Add to Home Screen"';
  }

  if (isAndroid()) {
    return 'Tap the menu button and then "Add to Home Screen" or "Install App"';
  }

  return "Click the install button in your browser's address bar";
}

/**
 * Track PWA installation (send to analytics)
 */
function trackPWAInstall(): void {
  try {
    // Send to analytics if available
    if (typeof window !== "undefined" && (window as any).gtag) {
      (window as any).gtag("event", "pwa_install", {
        event_category: "engagement",
        event_label: "PWA Installed",
      });
    }

    // Store installation timestamp
    localStorage.setItem("pwa_installed_at", new Date().toISOString());
  } catch (error) {
    console.error("Error tracking PWA install:", error);
  }
}

/**
 * Check if user has dismissed install prompt recently
 */
export function hasRecentlyDismissedInstall(): boolean {
  try {
    const dismissedAt = localStorage.getItem("pwa_install_dismissed_at");
    if (!dismissedAt) return false;

    const dismissedDate = new Date(dismissedAt);
    const daysSinceDismissed =
      (Date.now() - dismissedDate.getTime()) / (1000 * 60 * 60 * 24);

    // Show again after 7 days
    return daysSinceDismissed < 7;
  } catch {
    return false;
  }
}

/**
 * Mark install prompt as dismissed
 */
export function markInstallDismissed(): void {
  try {
    localStorage.setItem("pwa_install_dismissed_at", new Date().toISOString());
  } catch (error) {
    console.error("Error marking install dismissed:", error);
  }
}

/**
 * Check if should show install prompt
 * Based on various conditions like device, install status, etc.
 */
export function shouldShowInstallPrompt(): boolean {
  // Don't show if already installed
  if (isPWAInstalled()) {
    return false;
  }

  // Don't show if recently dismissed
  if (hasRecentlyDismissedInstall()) {
    return false;
  }

  // Don't show on desktop (optional - remove if you want desktop installs)
  if (
    !isIOS() &&
    !isAndroid() &&
    !window.matchMedia("(max-width: 768px)").matches
  ) {
    return false;
  }

  return true;
}
