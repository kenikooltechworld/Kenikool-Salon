/**
 * Salon Detail Map Component
 *
 * Displays a Mapbox GL map showing the salon location with:
 * - Salon marker at the location
 * - Directions link using backend Directions API
 * - Address information
 * - Error handling and fallback UI
 * - Real-time route visualization
 * - Distance and duration display
 *
 * Requirements: 10.4, 4.1, 4.2, 4.3, 4.4, 4.5, 6.1, 6.2, 6.3, 6.4, 6.5
 */

import { useEffect, useRef, useState, useCallback } from "react";

// Dynamically import mapbox-gl
let MapboxGL: any = null;
try {
  MapboxGL = require("mapbox-gl");
  try {
    require("mapbox-gl/dist/mapbox-gl.css");
  } catch (cssError) {
    console.warn("mapbox-gl CSS not available");
  }
} catch (e) {
  console.warn("mapbox-gl not installed");
}

/**
 * Retry logic with exponential backoff
 */
async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  initialDelayMs: number = 1000,
): Promise<T> {
  let lastError: Error | null = null;

  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error as Error;
      if (attempt < maxRetries - 1) {
        const delayMs = initialDelayMs * Math.pow(2, attempt);
        await new Promise((resolve) => setTimeout(resolve, delayMs));
      }
    }
  }

  throw lastError || new Error("Max retries exceeded");
}

interface SalonLocation {
  latitude: number;
  longitude: number;
  address: string;
  city: string;
  state: string;
}

interface SalonDetailMapProps {
  salon: {
    _id: string;
    name: string;
    location: SalonLocation;
    phone?: string;
    email?: string;
  };
  userLocation?: { latitude: number; longitude: number };
  style?: "light" | "dark" | "satellite";
  zoom?: number;
  height?: string;
}

export function SalonDetailMap({
  salon,
  userLocation,
  style = "light",
  zoom = 15,
  height = "400px",
}: SalonDetailMapProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<any>(null);
  const marker = useRef<any>(null);
  const [mapLoaded, setMapLoaded] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [directions, setDirections] = useState<any>(null);
  const [directionsLoading, setDirectionsLoading] = useState(false);
  const [retryCount, setRetryCount] = useState(0);
  const MAX_RETRIES = 3;

  // Initialize map
  useEffect(() => {
    if (!mapContainer.current || !MapboxGL) return;

    const initializeMap = async () => {
      try {
        setError(null);

        // Get Mapbox public key from environment
        const publicKey = process.env.REACT_APP_MAPBOX_PUBLIC_KEY;
        if (!publicKey) {
          throw new Error("Mapbox public key not configured");
        }

        MapboxGL.accessToken = publicKey;

        // Create map
        map.current = new MapboxGL.Map({
          container: mapContainer.current,
          style: `mapbox://styles/mapbox/${style}-v12`,
          center: [salon.location.longitude, salon.location.latitude],
          zoom: zoom,
          pitch: 0,
          bearing: 0,
        });

        // Add navigation controls
        map.current.addControl(new MapboxGL.NavigationControl(), "top-right");

        // Add geolocate control
        map.current.addControl(
          new MapboxGL.GeolocateControl({
            positionOptions: {
              enableHighAccuracy: true,
            },
            trackUserLocation: false,
          }),
          "top-right",
        );

        // Add marker
        const markerElement = document.createElement("div");
        markerElement.style.width = "32px";
        markerElement.style.height = "40px";
        markerElement.innerHTML = `
          <svg width="32" height="40" viewBox="0 0 32 40" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M16 0C9.37 0 4 5.37 4 12c0 8 12 28 12 28s12-20 12-28c0-6.63-5.37-12-12-12z" fill="#EF4444"/>
            <circle cx="16" cy="12" r="4" fill="white"/>
          </svg>
        `;

        marker.current = new MapboxGL.Marker(markerElement)
          .setLngLat([salon.location.longitude, salon.location.latitude])
          .addTo(map.current);

        // Create popup with salon info
        const popupContent = document.createElement("div");
        popupContent.style.padding = "12px";
        popupContent.style.fontFamily = "system-ui, -apple-system, sans-serif";
        popupContent.innerHTML = `
          <div style="max-width: 250px;">
            <h3 style="margin: 0 0 8px 0; font-size: 16px; font-weight: 600;">${escapeHtml(salon.name)}</h3>
            <p style="margin: 0 0 4px 0; font-size: 14px; color: #666;">
              <strong>Address:</strong> ${escapeHtml(salon.location.address)}
            </p>
            <p style="margin: 0 0 8px 0; font-size: 14px; color: #666;">
              ${escapeHtml(salon.location.city)}, ${escapeHtml(salon.location.state)}
            </p>
            ${salon.phone ? `<p style="margin: 0 0 4px 0; font-size: 14px;"><strong>Phone:</strong> <a href="tel:${escapeHtml(salon.phone)}" style="color: #3B82F6; text-decoration: none;">${escapeHtml(salon.phone)}</a></p>` : ""}
            ${salon.email ? `<p style="margin: 0 0 8px 0; font-size: 14px;"><strong>Email:</strong> <a href="mailto:${escapeHtml(salon.email)}" style="color: #3B82F6; text-decoration: none;">${escapeHtml(salon.email)}</a></p>` : ""}
            <button id="get-directions-btn" style="width: 100%; padding: 8px 12px; background-color: #3B82F6; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; font-weight: 500;">
              Get Directions
            </button>
          </div>
        `;

        const popup = new MapboxGL.Popup({
          offset: 25,
          maxWidth: "300px",
        }).setDOMContent(popupContent);

        marker.current.setPopup(popup);
        popup.addTo(map.current);

        // Add click handler for directions button
        setTimeout(() => {
          const btn = document.getElementById("get-directions-btn");
          if (btn) {
            btn.addEventListener("click", () => {
              handleGetDirections();
            });
          }
        }, 100);

        // Handle map load
        map.current.on("load", () => {
          setMapLoaded(true);
          setRetryCount(0);
        });

        // Handle map errors
        map.current.on("error", (e: any) => {
          console.error("Map error:", e);
          if (retryCount < MAX_RETRIES) {
            setRetryCount(retryCount + 1);
            setTimeout(initializeMap, 1000 * (retryCount + 1));
          } else {
            setError("Failed to load map");
          }
        });

        return () => {
          if (map.current) {
            map.current.remove();
          }
        };
      } catch (err) {
        console.error("Error initializing map:", err);
        if (retryCount < MAX_RETRIES) {
          setRetryCount(retryCount + 1);
          setTimeout(initializeMap, 1000 * (retryCount + 1));
        } else {
          setError(
            err instanceof Error ? err.message : "Failed to initialize map",
          );
        }
      }
    };

    initializeMap();
  }, [salon, style, zoom]);

  // Handle style changes
  useEffect(() => {
    if (map.current && mapLoaded) {
      map.current.setStyle(`mapbox://styles/mapbox/${style}-v12`);
    }
  }, [style, mapLoaded]);

  /**
   * Get directions from user location to salon
   * Requirement 4.1, 4.2, 4.3: Use backend Directions API with retry logic
   * Requirement 6.5: Retry logic with exponential backoff
   */
  const handleGetDirections = useCallback(async () => {
    if (!userLocation) {
      // Fallback to Google Maps if no user location
      window.open(
        `https://www.google.com/maps/search/?api=1&query=${salon.location.latitude},${salon.location.longitude}`,
        "_blank",
      );
      return;
    }

    try {
      setDirectionsLoading(true);
      setError(null);

      // Call backend directions API with retry logic
      const data = await retryWithBackoff(
        async () => {
          const response = await fetch("/api/directions", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              from_latitude: userLocation.latitude,
              from_longitude: userLocation.longitude,
              to_latitude: salon.location.latitude,
              to_longitude: salon.location.longitude,
              profile: "driving",
            }),
          });

          if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
          }

          return await response.json();
        },
        MAX_RETRIES,
        1000,
      );

      setDirections(data);

      // Draw route on map if available
      if (data.routes && data.routes.length > 0 && map.current) {
        const route = data.routes[0];
        if (route.geometry) {
          // Add route layer
          if (!map.current.getSource("route")) {
            map.current.addSource("route", {
              type: "geojson",
              data: {
                type: "Feature",
                properties: {},
                geometry: route.geometry,
              },
            });

            map.current.addLayer({
              id: "route",
              type: "line",
              source: "route",
              layout: {
                "line-join": "round",
                "line-cap": "round",
              },
              paint: {
                "line-color": "#3B82F6",
                "line-width": 4,
              },
            });
          }

          // Fit bounds to show entire route
          const bounds = new MapboxGL.LngLatBounds();
          route.geometry.coordinates.forEach((coord: [number, number]) => {
            bounds.extend(coord);
          });
          map.current.fitBounds(bounds, { padding: 50 });
        }
      }

      setRetryCount(0);
    } catch (err) {
      console.error("Error getting directions:", err);
      setError("Failed to get directions. Opening Google Maps...");
      // Fallback to Google Maps
      setTimeout(() => {
        window.open(
          `https://www.google.com/maps/search/?api=1&query=${salon.location.latitude},${salon.location.longitude}`,
          "_blank",
        );
      }, 1000);
    } finally {
      setDirectionsLoading(false);
    }
  }, [userLocation, salon, retryCount]);

  if (error && !mapLoaded) {
    return (
      <div className="salon-detail-map-error" style={{ height }}>
        <div style={{ padding: "20px", textAlign: "center" }}>
          <p style={{ color: "#DC2626", marginBottom: "12px" }}>{error}</p>
          <p style={{ fontSize: "14px", color: "#666", marginBottom: "16px" }}>
            {salon.location.address}, {salon.location.city},{" "}
            {salon.location.state}
          </p>
          <a
            href={`https://www.google.com/maps/search/?api=1&query=${salon.location.latitude},${salon.location.longitude}`}
            target="_blank"
            rel="noopener noreferrer"
            style={{
              display: "inline-block",
              padding: "8px 16px",
              backgroundColor: "#3B82F6",
              color: "white",
              textDecoration: "none",
              borderRadius: "4px",
              fontSize: "14px",
              fontWeight: "500",
            }}
          >
            📍 Get Directions on Google Maps
          </a>
        </div>
      </div>
    );
  }

  return (
    <div style={{ width: "100%" }}>
      <div
        ref={mapContainer}
        style={{ height, width: "100%", borderRadius: "8px" }}
      />
      {directions && (
        <div
          style={{
            marginTop: "16px",
            padding: "12px",
            backgroundColor: "#F3F4F6",
            borderRadius: "8px",
          }}
        >
          <h4
            style={{ margin: "0 0 8px 0", fontSize: "14px", fontWeight: "600" }}
          >
            Directions
          </h4>
          <p style={{ margin: "0 0 4px 0", fontSize: "14px" }}>
            <strong>Distance:</strong>{" "}
            {directions.routes?.[0]?.distance_km?.toFixed(1)} km
          </p>
          <p style={{ margin: "0", fontSize: "14px" }}>
            <strong>Duration:</strong>{" "}
            {Math.round(directions.routes?.[0]?.duration_minutes || 0)} minutes
          </p>
        </div>
      )}
      {directionsLoading && (
        <div
          style={{
            marginTop: "12px",
            textAlign: "center",
            color: "#666",
            fontSize: "14px",
          }}
        >
          Loading directions...
        </div>
      )}
    </div>
  );
}

/**
 * Escape HTML special characters
 */
function escapeHtml(text: string): string {
  const map: { [key: string]: string } = {
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;",
  };
  return text.replace(/[&<>"']/g, (m) => map[m]);
}

export default SalonDetailMap;
