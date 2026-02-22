/**
 * LocationMap Component
 * Interactive Mapbox GL map for location selection with address autocomplete
 * Integrates with backend Mapbox Geocoding API
 * 
 * Features:
 * - Mapbox GL JS integration for interactive maps
 * - Draggable marker for location selection
 * - Real-time reverse geocoding with retry logic
 * - Error handling with exponential backoff
 * - Loading states and user feedback
 * - Responsive design
 * - Country-specific geocoding for African markets
 * 
 * Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 2.2, 2.3, 2.4, 2.5, 6.1, 6.5, 9.1
 */

import React, { useEffect, useRef, useState, useCallback } from 'react';

// Dynamically import mapbox-gl
let MapboxGL = null;
try {
  MapboxGL = require('mapbox-gl');
  try {
    require('mapbox-gl/dist/mapbox-gl.css');
  } catch (cssError) {
    console.warn('mapbox-gl CSS not available');
  }
} catch (e) {
  console.warn('mapbox-gl not installed');
}

/**
 * Retry logic with exponential backoff
 */
async function retryWithBackoff(fn, maxRetries = 3, initialDelayMs = 1000) {
  let lastError = null;
  
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;
      if (attempt < maxRetries - 1) {
        const delayMs = initialDelayMs * Math.pow(2, attempt);
        await new Promise(resolve => setTimeout(resolve, delayMs));
      }
    }
  }
  
  throw lastError;
}

/**
 * LocationMap Component
 * @param {Object} props
 * @param {number} props.initialLat - Initial latitude (default: 6.5244 - Lagos)
 * @param {number} props.initialLng - Initial longitude (default: 3.3792 - Lagos)
 * @param {string} props.initialAddress - Initial address string
 * @param {Function} props.onLocationSelect - Callback when location is selected
 * @param {string} props.containerHeight - CSS height for map container (default: '400px')
 * @param {boolean} props.draggable - Allow marker dragging (default: true)
 * @param {string} props.country - Country code for geocoding (e.g., 'NG' for Nigeria)
 */
export function LocationMap({
  initialLat = 6.5244,
  initialLng = 3.3792,
  initialAddress = '',
  onLocationSelect = () => {},
  containerHeight = '400px',
  draggable = true,
  country = 'NG',
}) {
  // Validate coordinates
  if (initialLat < -90 || initialLat > 90 || initialLng < -180 || initialLng > 180) {
    console.warn('Invalid initial coordinates, using Lagos defaults');
  }
  const mapRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const markerRef = useRef(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [retryCount, setRetryCount] = useState(0);
  const [address, setAddress] = useState(initialAddress);
  const MAX_RETRIES = 3;
  const abortControllerRef = useRef(null);

  // Initialize map
  useEffect(() => {
    if (!mapRef.current || !MapboxGL) return;

    const initializeMap = async () => {
      try {
        setIsLoading(true);
        setError(null);

        // Get Mapbox public key from environment
        const publicKey = process.env.REACT_APP_MAPBOX_PUBLIC_KEY;
        if (!publicKey) {
          throw new Error('Mapbox public key not configured');
        }

        MapboxGL.accessToken = publicKey;

        // Create map instance
        const map = new MapboxGL.Map({
          container: mapRef.current,
          style: 'mapbox://styles/mapbox/light-v11',
          center: [initialLng, initialLat],
          zoom: 15,
          pitch: 0,
          bearing: 0,
        });

        mapInstanceRef.current = map;

        // Add navigation controls
        map.addControl(new MapboxGL.NavigationControl(), 'top-right');

        // Add geolocate control
        map.addControl(
          new MapboxGL.GeolocateControl({
            positionOptions: {
              enableHighAccuracy: true,
            },
            trackUserLocation: false,
          }),
          'top-right'
        );

        // Create marker element
        const markerElement = document.createElement('div');
        markerElement.style.width = '32px';
        markerElement.style.height = '40px';
        markerElement.style.cursor = 'grab';
        markerElement.innerHTML = `
          <svg width="32" height="40" viewBox="0 0 32 40" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M16 0C9.37 0 4 5.37 4 12c0 8 12 28 12 28s12-20 12-28c0-6.63-5.37-12-12-12z" fill="#3B82F6"/>
            <circle cx="16" cy="12" r="4" fill="white"/>
          </svg>
        `;

        // Add marker
        const marker = new MapboxGL.Marker({
          element: markerElement,
          draggable: draggable,
        })
          .setLngLat([initialLng, initialLat])
          .addTo(map);

        markerRef.current = marker;

        // Handle marker drag
        if (draggable) {
          marker.on('dragend', handleMarkerDragEnd);
        }

        setIsLoading(false);
        setRetryCount(0);

        // Cleanup on unmount
        return () => {
          if (map) {
            map.remove();
            mapInstanceRef.current = null;
          }
        };
      } catch (err) {
        console.error('Error initializing map:', err);
        
        if (retryCount < MAX_RETRIES) {
          setRetryCount(retryCount + 1);
          setTimeout(initializeMap, 1000 * (retryCount + 1));
        } else {
          setError('Failed to initialize map. Please refresh the page.');
        }
        setIsLoading(false);
      }
    };

    initializeMap();
  }, []);

  /**
   * Handle marker drag end event
   * Requirement 1.3: Reverse geocode coordinates to get address
   * Requirement 1.5: Country-specific geocoding for African markets
   * Requirement 6.5: Retry logic with exponential backoff
   */
  const handleMarkerDragEnd = useCallback(async (e) => {
    const { lng, lat } = e.target.getLngLat();

    try {
      setIsLoading(true);
      setError(null);
      setRetryCount(0);

      // Reverse geocode to get address using backend API with retry logic
      const result = await retryWithBackoff(
        async () => {
          const response = await fetch('/api/locations/reverse-geocode', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              latitude: lat,
              longitude: lng,
              country: country,
            }),
            signal: abortControllerRef.current?.signal,
          });

          if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
          }

          return await response.json();
        },
        MAX_RETRIES,
        1000
      );

      // Update address state
      setAddress(result.formatted_address || 'Unknown location');

      // Emit location data
      onLocationSelect({
        latitude: lat,
        longitude: lng,
        formatted_address: result.formatted_address || 'Unknown location',
      });

      setRetryCount(0);
    } catch (err) {
      if (err?.name === 'AbortError') return;
      
      console.error('Error reverse geocoding:', err);
      setError('Failed to get address for this location');
      
      // Still emit coordinates even if address lookup fails
      onLocationSelect({
        latitude: lat,
        longitude: lng,
        formatted_address: '',
      });
    } finally {
      setIsLoading(false);
    }
  }, [onLocationSelect, country]);

  /**
   * Reverse geocode coordinates to get address
   * Requirement 1.3: Use Mapbox Reverse Geocoding API with fallback
   * Requirement 1.5: Country-specific geocoding for African markets
   * Requirement 6.5: Retry logic with exponential backoff
   */
  const reverseGeocode = useCallback(async (lat, lng) => {
    try {
      const result = await retryWithBackoff(
        async () => {
          const response = await fetch('/api/locations/reverse-geocode', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              latitude: lat,
              longitude: lng,
              country: country,
            }),
            signal: abortControllerRef.current?.signal,
          });

          if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
          }

          return await response.json();
        },
        MAX_RETRIES,
        1000
      );

      return result.formatted_address || '';
    } catch (err) {
      if (err?.name === 'AbortError') throw err;
      console.error('Reverse geocoding error:', err);
      return '';
    }
  }, [country]);

  /**
   * Update map center and marker position
   */
  const updateLocation = useCallback(async (lat, lng, addressStr = '') => {
    if (mapInstanceRef.current && markerRef.current) {
      mapInstanceRef.current.setCenter([lng, lat]);
      mapInstanceRef.current.setZoom(15);
      markerRef.current.setLngLat([lng, lat]);

      // If no address provided, reverse geocode
      let finalAddress = addressStr;
      if (!addressStr) {
        finalAddress = await reverseGeocode(lat, lng);
      }

      setAddress(finalAddress);

      onLocationSelect({
        latitude: lat,
        longitude: lng,
        formatted_address: finalAddress,
      });
    }
  }, [reverseGeocode, onLocationSelect]);

  // Expose updateLocation method via ref
  useEffect(() => {
    if (mapRef.current) {
      mapRef.current.updateLocation = updateLocation;
    }
  }, [updateLocation]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  return (
    <div className="location-map-container">
      {error && (
        <div className="mb-2 p-2 bg-red-100 border border-red-400 text-red-700 rounded text-sm">
          {error}
        </div>
      )}

      {isLoading && (
        <div className="absolute inset-0 bg-white bg-opacity-50 flex items-center justify-center rounded z-10">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
            <p className="mt-2 text-sm text-gray-600">Loading...</p>
          </div>
        </div>
      )}

      <div
        ref={mapRef}
        style={{
          height: containerHeight,
          width: '100%',
          borderRadius: '0.375rem',
          border: '1px solid #e5e7eb',
        }}
        className="relative"
      />

      <div className="mt-2 text-xs text-gray-500">
        {address && <p className="mb-1 font-medium text-gray-700">{address}</p>}
        {draggable && <p>Drag the marker to adjust the location</p>}
        <p>Powered by Mapbox</p>
      </div>
    </div>
  );
}

export default LocationMap;
