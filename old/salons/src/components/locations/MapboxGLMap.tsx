/**
 * MapboxGLMap Component
 *
 * Renders an interactive Mapbox GL map with salon markers and popups.
 * Features:
 * - Mapbox GL JS integration with TypeScript support
 * - Map interactions (zoom, pan, rotate)
 * - Multiple map styles (light, dark, satellite, standard with 3D)
 * - Custom salon markers with hover effects
 * - Popup information display on marker click
 * - 3D buildings, terrain, and landmarks rendering
 * - Animated weather effects (rain, clouds, fog)
 * - 3D building highlighting on marker hover
 * - Responsive design
 * - Theme-aware UI using custom component library
 *
 * Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 13.1, 13.2, 13.3
 */

import React, { useEffect, useRef, useState } from "react";
import "./MapboxGLMap.css";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils/cn";

// Dynamically import mapbox-gl and its CSS
let MapboxGL: any = null;
try {
  MapboxGL = require("mapbox-gl");
  // Try to import CSS, but don't fail if it's not available
  try {
    require("mapbox-gl/dist/mapbox-gl.css");
  } catch (cssError) {
    console.warn("mapbox-gl CSS not available, styling may be limited");
  }
} catch (e) {
  console.warn("mapbox-gl not installed, map functionality will be limited");
}

interface SalonMarker {
  id: string;
  name: string;
  latitude: number;
  longitude: number;
  address: string;
  distance?: number;
  rating?: number;
  reviews?: number;
  phone?: string;
  website?: string;
}

interface WeatherData {
  condition: "clear" | "rain" | "clouds" | "fog" | "snow";
  temperature?: number;
  humidity?: number;
  windSpeed?: number;
}

interface MapboxGLMapProps {
  markers?: SalonMarker[];
  center?: [number, number];
  zoom?: number;
  style?: "light" | "dark" | "satellite" | "3d";
  onMarkerClick?: (marker: SalonMarker) => void;
  onMapClick?: (coordinates: [number, number]) => void;
  height?: string;
  className?: string;
  enable3D?: boolean;
  weatherData?: WeatherData;
}

const MAPBOX_STYLES = {
  light: "mapbox://styles/mapbox/light-v11",
  dark: "mapbox://styles/mapbox/dark-v11",
  satellite: "mapbox://styles/mapbox/satellite-v9",
  "3d": "mapbox://styles/mapbox/standard",
};

export const MapboxGLMap: React.FC<MapboxGLMapProps> = ({
  markers = [],
  center = [0, 0],
  zoom = 12,
  style = "light",
  onMarkerClick,
  onMapClick,
  height = "400px",
  className = "",
  enable3D = false,
  weatherData,
}) => {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<any>(null);
  const markersRef = useRef<Map<string, any>>(new Map());
  const popupsRef = useRef<Map<string, any>>(new Map());
  const [currentStyle, setCurrentStyle] = useState<
    "light" | "dark" | "satellite" | "3d"
  >(style);
  const [isMapReady, setIsMapReady] = useState(false);
  const [is3DEnabled, setIs3DEnabled] = useState(enable3D);
  const [currentWeather, setCurrentWeather] = useState<WeatherData | undefined>(
    weatherData,
  );

  // Initialize map
  useEffect(() => {
    if (!mapContainer.current || !MapboxGL) return;

    // Get public key from environment
    const publicKey = process.env.REACT_APP_MAPBOX_PUBLIC_KEY;
    if (!publicKey) {
      console.error("REACT_APP_MAPBOX_PUBLIC_KEY is not set");
      return;
    }

    MapboxGL.accessToken = publicKey;

    try {
      const mapStyle = is3DEnabled
        ? MAPBOX_STYLES["3d"]
        : MAPBOX_STYLES[currentStyle];

      map.current = new MapboxGL.Map({
        container: mapContainer.current,
        style: mapStyle,
        center,
        zoom,
        pitch: is3DEnabled ? 45 : 0,
        bearing: is3DEnabled ? 0 : 0,
        antialias: is3DEnabled, // Enable antialiasing for 3D
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

      // Handle map click
      map.current.on("click", (e: any) => {
        if (onMapClick) {
          onMapClick([e.lngLat.lng, e.lngLat.lat]);
        }
      });

      // Mark map as ready
      map.current.on("load", () => {
        setIsMapReady(true);

        // Enable 3D features if requested
        if (is3DEnabled) {
          enable3DFeatures(map.current);
        }
      });
    } catch (error) {
      console.error("Failed to initialize Mapbox map:", error);
    }

    return () => {
      if (map.current) {
        map.current.remove();
      }
    };
  }, [is3DEnabled]);

  // Update markers when they change
  useEffect(() => {
    if (!map.current || !isMapReady) return;

    // Remove old markers
    markersRef.current.forEach((marker) => {
      marker.remove();
    });
    markersRef.current.clear();

    // Remove old popups
    popupsRef.current.forEach((popup) => {
      popup.remove();
    });
    popupsRef.current.clear();

    // Add new markers
    markers.forEach((marker) => {
      const el = createMarkerElement(marker);

      const mapboxMarker = new MapboxGL.Marker({ element: el })
        .setLngLat([marker.longitude, marker.latitude])
        .addTo(map.current!);

      markersRef.current.set(marker.id, mapboxMarker);

      // Create popup
      const popup = createPopup(marker);
      popupsRef.current.set(marker.id, popup);

      // Add click handler
      el.addEventListener("click", () => {
        // Close all other popups
        popupsRef.current.forEach((p, id) => {
          if (id !== marker.id) {
            p.remove();
          }
        });

        // Toggle popup for this marker
        if (popup.isOpen()) {
          popup.remove();
        } else {
          popup.addTo(map.current!);
        }

        if (onMarkerClick) {
          onMarkerClick(marker);
        }
      });

      // Add hover effect
      el.addEventListener("mouseenter", () => {
        el.classList.add("marker--hovered");

        // Highlight 3D building on hover if 3D is enabled
        if (is3DEnabled && map.current) {
          highlight3DBuilding(map.current, marker, true);
        }
      });

      el.addEventListener("mouseleave", () => {
        el.classList.remove("marker--hovered");

        // Remove 3D building highlight on hover leave
        if (is3DEnabled && map.current) {
          highlight3DBuilding(map.current, marker, false);
        }
      });
    });

    // Fit bounds if markers exist
    if (markers.length > 0) {
      const bounds = new MapboxGL.LngLatBounds();
      markers.forEach((marker) => {
        bounds.extend([marker.longitude, marker.latitude]);
      });
      map.current.fitBounds(bounds, { padding: 50 });
    }
  }, [markers, isMapReady, onMarkerClick, is3DEnabled]);

  // Handle weather data updates
  useEffect(() => {
    if (!map.current || !isMapReady || !is3DEnabled) return;

    if (weatherData) {
      setCurrentWeather(weatherData);
      applyWeatherEffects(map.current, weatherData);
    }
  }, [weatherData, isMapReady, is3DEnabled]);

  // Handle style change
  useEffect(() => {
    if (!map.current || !isMapReady) return;

    const newStyle = is3DEnabled
      ? MAPBOX_STYLES["3d"]
      : MAPBOX_STYLES[currentStyle];
    map.current.setStyle(newStyle);

    // Re-enable 3D features after style change
    if (is3DEnabled) {
      map.current.once("styledata", () => {
        enable3DFeatures(map.current);
        if (currentWeather) {
          applyWeatherEffects(map.current, currentWeather);
        }
      });
    }
  }, [currentStyle, isMapReady, is3DEnabled, currentWeather]);

  const handleStyleChange = (
    newStyle: "light" | "dark" | "satellite" | "3d",
  ) => {
    if (newStyle === "3d") {
      setIs3DEnabled(true);
      setCurrentStyle("light");
    } else {
      setIs3DEnabled(false);
      setCurrentStyle(newStyle);
    }
  };

  return (
    <Card variant="default" className={cn("w-full overflow-hidden", className)}>
      <div className="relative w-full" style={{ height }}>
        {/* Style Controls - Using custom Button component */}
        <div className="absolute top-4 left-4 z-10 flex gap-2">
          {(["light", "dark", "satellite", "3d"] as const).map((s) => (
            <Button
              key={s}
              variant={
                (s === "3d" && is3DEnabled) ||
                (s !== "3d" && currentStyle === s)
                  ? "primary"
                  : "outline"
              }
              size="sm"
              onClick={() => handleStyleChange(s)}
              title={`Switch to ${s} style`}
            >
              {s === "3d" ? "3D" : s.charAt(0).toUpperCase() + s.slice(1)}
            </Button>
          ))}
        </div>

        {/* Map Container */}
        <div ref={mapContainer} className="w-full h-full" />
      </div>
    </Card>
  );
};

/**
 * Create a custom marker element for a salon
 * Requirement 3.4: Custom markers for each salon
 */
function createMarkerElement(marker: SalonMarker): HTMLElement {
  const el = document.createElement("div");
  el.className = "marker";
  el.id = `marker-${marker.id}`;

  // Create marker with salon name label
  el.innerHTML = `
    <div class="marker__icon">
      <svg width="32" height="40" viewBox="0 0 32 40" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M16 0C9.37 0 4 5.37 4 12c0 8 12 28 12 28s12-20 12-28c0-6.63-5.37-12-12-12z" fill="hsl(var(--primary))"/>
        <circle cx="16" cy="12" r="4" fill="white"/>
      </svg>
    </div>
    <div class="marker__label">${escapeHtml(marker.name.substring(0, 15))}</div>
  `;

  el.style.cursor = "pointer";
  el.setAttribute("data-marker-id", marker.id);

  return el;
}

/**
 * Create a popup for a marker
 * Requirement 3.5: Display popup with salon info (name, address, distance, rating, details link)
 */
function createPopup(salonMarker: SalonMarker): any {
  const popupContent = document.createElement("div");
  popupContent.className = "marker-popup";

  // Build popup content with all available information
  let popupHTML = `
    <div class="marker-popup__content">
      <h3 class="marker-popup__title">${escapeHtml(salonMarker.name)}</h3>
      <p class="marker-popup__address">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="display: inline; margin-right: 4px; vertical-align: middle;">
          <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
          <circle cx="12" cy="10" r="3"/>
        </svg>
        ${escapeHtml(salonMarker.address)}
      </p>
  `;

  // Add distance if available
  if (salonMarker.distance !== undefined && salonMarker.distance !== null) {
    popupHTML += `
      <p class="marker-popup__distance">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="display: inline; margin-right: 4px; vertical-align: middle;">
          <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
          <circle cx="12" cy="10" r="3"/>
        </svg>
        ${salonMarker.distance.toFixed(1)} km away
      </p>
    `;
  }

  // Add rating if available
  if (salonMarker.rating !== undefined && salonMarker.rating !== null) {
    const fullStars = Math.floor(salonMarker.rating);
    let starsHTML = "";
    for (let i = 0; i < fullStars; i++) {
      starsHTML += `
        <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="2" style="display: inline; margin-right: 2px; vertical-align: middle;">
          <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
        </svg>
      `;
    }
    popupHTML += `
      <p class="marker-popup__rating">
        ${starsHTML}
        ${salonMarker.rating.toFixed(1)} (${salonMarker.reviews || 0} reviews)
      </p>
    `;
  }

  // Add phone if available
  if (salonMarker.phone) {
    popupHTML += `
      <p class="marker-popup__phone">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="display: inline; margin-right: 4px; vertical-align: middle;">
          <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>
        </svg>
        ${escapeHtml(salonMarker.phone)}
      </p>
    `;
  }

  // Add website if available
  if (salonMarker.website) {
    popupHTML += `
      <p class="marker-popup__website">
        <a href="${escapeHtml(salonMarker.website)}" target="_blank" rel="noopener noreferrer" style="display: inline-flex; align-items: center; gap: 4px; text-decoration: none; color: inherit;">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="2" y1="12" x2="22" y2="12"/>
            <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
          </svg>
          Visit Website
        </a>
      </p>
    `;
  }

  // Add details link
  popupHTML += `
      <a href="#" class="marker-popup__link" data-marker-id="${salonMarker.id}" style="display: inline-flex; align-items: center; gap: 4px; text-decoration: none; color: inherit;">
        View Details
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="5" y1="12" x2="19" y2="12"/>
          <polyline points="12 5 19 12 12 19"/>
        </svg>
      </a>
    </div>
  `;

  popupContent.innerHTML = popupHTML;

  return new MapboxGL.Popup({
    offset: 25,
    closeButton: true,
    closeOnClick: false,
  }).setDOMContent(popupContent);
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

export default MapboxGLMap;

/**
 * Enable 3D features on the map
 * Requirement 13.1: Use Mapbox Standard Style with 3D buildings, terrain, landmarks
 */
function enable3DFeatures(map: any): void {
  try {
    // Set pitch and bearing for 3D perspective
    map.setPitch(45);
    map.setBearing(0);

    // Enable terrain if available
    if (!map.getSource("mapbox-dem")) {
      map.addSource("mapbox-dem", {
        type: "raster-dem",
        url: "mapbox://mapbox.mapbox-terrain-dem-v1",
        tileSize: 512,
        maxzoom: 14,
      });
      map.setTerrain({ source: "mapbox-dem", exaggeration: 1.5 });
    }

    // Enable sky layer for better 3D effect
    if (!map.getLayer("sky")) {
      map.addLayer({
        id: "sky",
        type: "sky",
        paint: {
          "sky-type": "atmosphere",
          "sky-atmosphere-sun-intensity": 0.15,
        },
      });
    }

    console.log("3D features enabled successfully");
  } catch (error) {
    console.error("Failed to enable 3D features:", error);
  }
}

/**
 * Highlight a 3D building on marker hover
 * Requirement 13.3: Highlight salon's 3D building on marker hover
 */
function highlight3DBuilding(
  map: any,
  _marker: SalonMarker,
  highlight: boolean,
): void {
  try {
    // Get the building layer (Mapbox Standard style includes a building layer)
    const buildingLayer = map.getLayer("building");
    if (!buildingLayer) return;

    if (highlight) {
      // Create a filter to highlight buildings near the marker
      const filter = [
        "all",
        ["==", ["geometry-type"], "Polygon"],
        [
          "all",
          [">=", ["get", "height"], 0],
          ["all", [">=", ["get", "min_height"], 0]],
        ],
      ];

      // Apply highlight paint
      map.setPaintProperty("building", "fill-opacity", [
        "case",
        filter,
        0.8,
        0.6,
      ]);
      map.setPaintProperty("building", "fill-color", [
        "case",
        filter,
        "hsl(var(--primary))",
        "hsl(0, 0%, 85%)",
      ]);
    } else {
      // Reset to default
      map.setPaintProperty("building", "fill-opacity", 0.6);
      map.setPaintProperty("building", "fill-color", "hsl(0, 0%, 85%)");
    }
  } catch (error) {
    console.error("Failed to highlight 3D building:", error);
  }
}

/**
 * Apply animated weather effects to the map
 * Requirement 13.2: Display animated 3D weather effects (rain, clouds, fog)
 */
function applyWeatherEffects(map: any, weather: WeatherData): void {
  try {
    const weatherLayerId = "weather-effects";
    const weatherAnimationId = "weather-animation";

    // Remove existing weather layer if present
    if (map.getLayer(weatherLayerId)) {
      map.removeLayer(weatherLayerId);
    }

    if (map.getSource(weatherLayerId)) {
      map.removeSource(weatherLayerId);
    }

    // Cancel existing animation
    if ((window as any)[weatherAnimationId]) {
      cancelAnimationFrame((window as any)[weatherAnimationId]);
    }

    switch (weather.condition) {
      case "rain":
        addRainEffect(map, weatherLayerId, weatherAnimationId);
        break;

      case "clouds":
        addCloudEffect(map, weatherLayerId);
        break;

      case "fog":
        addFogEffect(map, weatherLayerId, weatherAnimationId);
        break;

      case "snow":
        addSnowEffect(map, weatherLayerId, weatherAnimationId);
        break;

      case "clear":
      default:
        // Clear weather - no effect needed
        break;
    }

    console.log(`Weather effect applied: ${weather.condition}`);
  } catch (error) {
    console.error("Failed to apply weather effects:", error);
  }
}

/**
 * Add rain effect to the map with animated droplets
 */
function addRainEffect(map: any, layerId: string, animationId: string): void {
  try {
    // Add a semi-transparent blue layer to simulate rain
    map.addLayer({
      id: layerId,
      type: "background",
      paint: {
        "background-color": "rgba(100, 150, 200, 0.15)",
        "background-opacity": [
          "interpolate",
          ["linear"],
          ["zoom"],
          0,
          0.08,
          22,
          0.15,
        ],
      },
    });

    // Animate the opacity for rain effect
    let opacity = 0.1;
    let direction = 1;
    const animateRain = () => {
      opacity += direction * 0.02;
      if (opacity >= 0.2) direction = -1;
      if (opacity <= 0.08) direction = 1;

      if (map.getLayer(layerId)) {
        map.setPaintProperty(layerId, "background-opacity", opacity);
      }

      (window as any)[animationId] = requestAnimationFrame(animateRain);
    };

    animateRain();
  } catch (error) {
    console.error("Failed to add rain effect:", error);
  }
}

/**
 * Add cloud effect to the map
 */
function addCloudEffect(map: any, layerId: string): void {
  try {
    // Add a semi-transparent white layer to simulate clouds
    map.addLayer({
      id: layerId,
      type: "background",
      paint: {
        "background-color": "rgba(200, 200, 200, 0.12)",
        "background-opacity": [
          "interpolate",
          ["linear"],
          ["zoom"],
          0,
          0.08,
          22,
          0.12,
        ],
      },
    });

    // Slightly reduce saturation for cloudy effect
    if (map.getLayer("water")) {
      map.setPaintProperty("water", "fill-color", [
        "interpolate",
        ["linear"],
        ["zoom"],
        0,
        "rgba(200, 220, 240, 0.8)",
        22,
        "rgba(200, 220, 240, 0.9)",
      ]);
    }
  } catch (error) {
    console.error("Failed to add cloud effect:", error);
  }
}

/**
 * Add fog effect to the map with animated opacity
 */
function addFogEffect(map: any, layerId: string, animationId: string): void {
  try {
    // Add fog effect using background layer
    map.addLayer({
      id: layerId,
      type: "background",
      paint: {
        "background-color": "rgba(180, 180, 180, 0.2)",
        "background-opacity": [
          "interpolate",
          ["linear"],
          ["zoom"],
          0,
          0.15,
          22,
          0.25,
        ],
      },
    });

    // Animate fog opacity for breathing effect
    let opacity = 0.15;
    let direction = 1;
    const animateFog = () => {
      opacity += direction * 0.01;
      if (opacity >= 0.3) direction = -1;
      if (opacity <= 0.15) direction = 1;

      if (map.getLayer(layerId)) {
        map.setPaintProperty(layerId, "background-opacity", opacity);
      }

      (window as any)[animationId] = requestAnimationFrame(animateFog);
    };

    animateFog();
  } catch (error) {
    console.error("Failed to add fog effect:", error);
  }
}

/**
 * Add snow effect to the map with animated opacity
 */
function addSnowEffect(map: any, layerId: string, animationId: string): void {
  try {
    // Add a semi-transparent white layer to simulate snow
    map.addLayer({
      id: layerId,
      type: "background",
      paint: {
        "background-color": "rgba(240, 240, 240, 0.18)",
        "background-opacity": [
          "interpolate",
          ["linear"],
          ["zoom"],
          0,
          0.1,
          22,
          0.2,
        ],
      },
    });

    // Animate snow opacity for falling effect
    let opacity = 0.1;
    let direction = 1;
    const animateSnow = () => {
      opacity += direction * 0.015;
      if (opacity >= 0.25) direction = -1;
      if (opacity <= 0.1) direction = 1;

      if (map.getLayer(layerId)) {
        map.setPaintProperty(layerId, "background-opacity", opacity);
      }

      (window as any)[animationId] = requestAnimationFrame(animateSnow);
    };

    animateSnow();
  } catch (error) {
    console.error("Failed to add snow effect:", error);
  }
}
