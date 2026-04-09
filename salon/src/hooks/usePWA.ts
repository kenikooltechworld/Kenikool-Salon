import { useState, useEffect, useCallback } from "react";
import {
  initPWAInstall,
  showInstallPrompt,
  isPWAInstallable,
  isPWAInstalled,
  shouldShowInstallPrompt,
  markInstallDismissed,
  isIOS,
  isAndroid,
  getInstallInstructions,
} from "@/lib/pwa/install";
import { registerServiceWorker } from "@/lib/pwa/register";

interface UsePWAReturn {
  isInstallable: boolean;
  isInstalled: boolean;
  isIOS: boolean;
  isAndroid: boolean;
  shouldShowPrompt: boolean;
  installInstructions: string;
  install: () => Promise<boolean>;
  dismissInstall: () => void;
}

/**
 * Hook for PWA installation functionality
 */
export function usePWA(): UsePWAReturn {
  const [isInstallable, setIsInstallable] = useState(false);
  const [isInstalled, setIsInstalled] = useState(isPWAInstalled());
  const [shouldShowPrompt, setShouldShowPrompt] = useState(false);

  useEffect(() => {
    // Initialize PWA install
    initPWAInstall();

    // Register service worker
    registerServiceWorker();

    // Check if should show prompt
    setShouldShowPrompt(shouldShowInstallPrompt());

    // Listen for install availability
    const handleInstallAvailable = () => {
      setIsInstallable(true);
      setShouldShowPrompt(shouldShowInstallPrompt());
    };

    // Listen for install completion
    const handleInstalled = () => {
      setIsInstalled(true);
      setIsInstallable(false);
      setShouldShowPrompt(false);
    };

    window.addEventListener("pwa-install-available", handleInstallAvailable);
    window.addEventListener("pwa-installed", handleInstalled);

    // Check initial state
    setIsInstallable(isPWAInstallable());

    return () => {
      window.removeEventListener(
        "pwa-install-available",
        handleInstallAvailable,
      );
      window.removeEventListener("pwa-installed", handleInstalled);
    };
  }, []);

  const install = useCallback(async (): Promise<boolean> => {
    const accepted = await showInstallPrompt();

    if (accepted) {
      setIsInstalled(true);
      setIsInstallable(false);
      setShouldShowPrompt(false);
    }

    return accepted;
  }, []);

  const dismissInstall = useCallback(() => {
    markInstallDismissed();
    setShouldShowPrompt(false);
  }, []);

  return {
    isInstallable,
    isInstalled,
    isIOS: isIOS(),
    isAndroid: isAndroid(),
    shouldShowPrompt,
    installInstructions: getInstallInstructions(),
    install,
    dismissInstall,
  };
}
