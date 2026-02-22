import { Link, useLocation } from "react-router-dom";
import { ChevronRightIcon } from "@/components/icons";
import { showToast } from "@/lib/utils/toast";
import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api/client";

export function Breadcrumb() {
  const location = useLocation();
  const pathname = location.pathname;
  const segments = pathname.split("/").filter(Boolean);
  const [names, setNames] = useState<Record<string, string>>({});

  // Fetch names for service IDs and stylist IDs in the breadcrumb
  useEffect(() => {
    const fetchNames = async () => {
      const fetchedNames: Record<string, string> = {};

      for (let i = 0; i < segments.length; i++) {
        const segment = segments[i];
        // Check if this segment is an ID (24-character hex string or starts with temp_)
        if (
          (segment.length === 24 && /^[0-9a-f]{24}$/i.test(segment)) ||
          segment.startsWith("temp_")
        ) {
          // Check if previous segment is "services"
          if (i > 0 && segments[i - 1] === "services") {
            try {
              const response = await apiClient.get(
                `/api/services/${segment}/details`,
              );
              if (response.data?.service?.name) {
                fetchedNames[segment] = response.data.service.name;
              }
            } catch (error) {
              console.error(
                `Failed to fetch service name for ${segment}:`,
                error,
              );
            }
          }
          // Check if previous segment is "staff"
          else if (i > 0 && segments[i - 1] === "staff") {
            try {
              const response = await apiClient.get(`/api/stylists/${segment}`);
              if (response.data?.name) {
                fetchedNames[segment] = response.data.name;
              }
            } catch (error) {
              console.error(
                `Failed to fetch stylist name for ${segment}:`,
                error,
              );
            }
          }
        }
      }

      if (Object.keys(fetchedNames).length > 0) {
        setNames(fetchedNames);
      }
    };

    fetchNames();
  }, [segments]);

  const breadcrumbs = segments.map((segment, index) => {
    const href = "/" + segments.slice(0, index + 1).join("/");

    // Use fetched name if available, otherwise format the segment
    let label = names[segment];
    if (!label) {
      label = segment
        .split("-")
        .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
        .join(" ");
    }

    return { label, href, isLast: index === segments.length - 1 };
  });

  if (breadcrumbs.length <= 1) return null;

  const handleBreadcrumbClick = (label: string) => {
    showToast(`Navigating to ${label}`, "info");
  };

  return (
    <nav className="flex items-center gap-2 text-sm mb-6">
      {breadcrumbs.map((crumb, index) => (
        <div key={crumb.href} className="flex items-center gap-2">
          {index > 0 && (
            <ChevronRightIcon size={16} className="text-muted-foreground" />
          )}
          {crumb.isLast ? (
            <span className="text-foreground font-medium">{crumb.label}</span>
          ) : (
            <Link
              to={crumb.href}
              onClick={() => handleBreadcrumbClick(crumb.label)}
              className="text-muted-foreground hover:text-foreground transition-colors"
            >
              {crumb.label}
            </Link>
          )}
        </div>
      ))}
    </nav>
  );
}
