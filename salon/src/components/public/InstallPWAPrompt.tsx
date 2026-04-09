import { useState, useEffect } from "react";
import { usePWA } from "@/hooks/usePWA";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { X, Download, Smartphone } from "@/components/icons";

interface InstallPWAPromptProps {
  /**
   * Delay before showing prompt (in milliseconds)
   * Default: 30 seconds
   */
  delay?: number;

  /**
   * Position of the prompt
   * Default: 'bottom'
   */
  position?: "top" | "bottom";

  /**
   * Custom className
   */
  className?: string;
}

export default function InstallPWAPrompt({
  delay = 30000,
  position = "bottom",
  className = "",
}: InstallPWAPromptProps) {
  const {
    isInstallable,
    isInstalled,
    isIOS,
    shouldShowPrompt,
    installInstructions,
    install,
    dismissInstall,
  } = usePWA();

  const [isVisible, setIsVisible] = useState(false);
  const [isInstalling, setIsInstalling] = useState(false);

  useEffect(() => {
    // Don't show if already installed or shouldn't show
    if (isInstalled || !shouldShowPrompt) {
      return;
    }

    // Show prompt after delay
    const timer = setTimeout(() => {
      if (isInstallable || isIOS) {
        setIsVisible(true);
      }
    }, delay);

    return () => clearTimeout(timer);
  }, [isInstalled, shouldShowPrompt, isInstallable, isIOS, delay]);

  const handleInstall = async () => {
    setIsInstalling(true);

    try {
      const accepted = await install();

      if (accepted) {
        setIsVisible(false);
      }
    } catch (error) {
      console.error("Error installing PWA:", error);
    } finally {
      setIsInstalling(false);
    }
  };

  const handleDismiss = () => {
    setIsVisible(false);
    dismissInstall();
  };

  if (!isVisible) {
    return null;
  }

  const positionClasses =
    position === "top"
      ? "top-4 animate-slide-down"
      : "bottom-4 animate-slide-up";

  return (
    <div
      className={`fixed left-4 right-4 z-50 ${positionClasses} ${className}`}
      role="dialog"
      aria-labelledby="pwa-install-title"
      aria-describedby="pwa-install-description"
    >
      <Card className="mx-auto max-w-md shadow-lg border-2 border-blue-500">
        <div className="p-4">
          <div className="flex items-start gap-4">
            {/* Icon */}
            <div className="flex-shrink-0">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                <Smartphone className="w-6 h-6 text-blue-600" />
              </div>
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0">
              <h3
                id="pwa-install-title"
                className="text-lg font-semibold text-gray-900 mb-1"
              >
                Install Our App
              </h3>
              <p
                id="pwa-install-description"
                className="text-sm text-gray-600 mb-3"
              >
                {isIOS
                  ? installInstructions
                  : "Get quick access and a better experience with our app!"}
              </p>

              {/* Benefits */}
              <ul className="text-xs text-gray-500 space-y-1 mb-4">
                <li className="flex items-center gap-2">
                  <span className="w-1 h-1 bg-blue-500 rounded-full" />
                  Faster booking experience
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1 h-1 bg-blue-500 rounded-full" />
                  Works offline
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1 h-1 bg-blue-500 rounded-full" />
                  Get instant notifications
                </li>
              </ul>

              {/* Actions */}
              <div className="flex items-center gap-2">
                {!isIOS && (
                  <Button
                    onClick={handleInstall}
                    disabled={isInstalling}
                    size="sm"
                    className="flex-1"
                  >
                    <Download className="w-4 h-4 mr-2" />
                    {isInstalling ? "Installing..." : "Install"}
                  </Button>
                )}
                <Button
                  onClick={handleDismiss}
                  variant="outline"
                  size="sm"
                  className={isIOS ? "flex-1" : ""}
                >
                  {isIOS ? "Got it" : "Maybe later"}
                </Button>
              </div>
            </div>

            {/* Close button */}
            <button
              onClick={handleDismiss}
              className="flex-shrink-0 text-gray-400 hover:text-gray-600 transition-colors"
              aria-label="Dismiss install prompt"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>
      </Card>
    </div>
  );
}
