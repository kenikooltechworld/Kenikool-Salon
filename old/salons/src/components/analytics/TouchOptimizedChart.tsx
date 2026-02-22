import React, { useRef, useEffect, useState, ReactNode } from 'react';

interface TouchOptimizedChartProps {
  children: ReactNode;
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
  onPinch?: (scale: number) => void;
}

export const TouchOptimizedChart: React.FC<TouchOptimizedChartProps> = ({
  children,
  onSwipeLeft,
  onSwipeRight,
  onPinch,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [touchStart, setTouchStart] = useState<{ x: number; y: number } | null>(null);
  const [touchDistance, setTouchDistance] = useState<number | null>(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const handleTouchStart = (e: TouchEvent) => {
      if (e.touches.length === 1) {
        setTouchStart({ x: e.touches[0].clientX, y: e.touches[0].clientY });
      } else if (e.touches.length === 2) {
        const dx = e.touches[0].clientX - e.touches[1].clientX;
        const dy = e.touches[0].clientY - e.touches[1].clientY;
        setTouchDistance(Math.sqrt(dx * dx + dy * dy));
      }
    };

    const handleTouchMove = (e: TouchEvent) => {
      if (e.touches.length === 2 && touchDistance) {
        const dx = e.touches[0].clientX - e.touches[1].clientX;
        const dy = e.touches[0].clientY - e.touches[1].clientY;
        const newDistance = Math.sqrt(dx * dx + dy * dy);
        const scale = newDistance / touchDistance;
        onPinch?.(scale);
      }
    };

    const handleTouchEnd = (e: TouchEvent) => {
      if (!touchStart || e.touches.length > 0) return;

      const touch = e.changedTouches[0];
      const deltaX = touch.clientX - touchStart.x;
      const deltaY = touch.clientY - touchStart.y;

      // Swipe threshold
      const threshold = 50;

      if (Math.abs(deltaX) > threshold && Math.abs(deltaY) < threshold) {
        if (deltaX > 0) {
          onSwipeRight?.();
        } else {
          onSwipeLeft?.();
        }
      }

      setTouchStart(null);
      setTouchDistance(null);
    };

    container.addEventListener('touchstart', handleTouchStart);
    container.addEventListener('touchmove', handleTouchMove);
    container.addEventListener('touchend', handleTouchEnd);

    return () => {
      container.removeEventListener('touchstart', handleTouchStart);
      container.removeEventListener('touchmove', handleTouchMove);
      container.removeEventListener('touchend', handleTouchEnd);
    };
  }, [touchStart, touchDistance, onSwipeLeft, onSwipeRight, onPinch]);

  return (
    <div
      ref={containerRef}
      className="touch-none select-none"
      style={{ touchAction: 'manipulation' }}
    >
      {children}
    </div>
  );
};

interface TouchOptimizedButtonProps {
  onClick: () => void;
  children: ReactNode;
  className?: string;
}

export const TouchOptimizedButton: React.FC<TouchOptimizedButtonProps> = ({
  onClick,
  children,
  className = '',
}) => {
  return (
    <button
      onClick={onClick}
      className={`min-h-[44px] min-w-[44px] px-4 py-2 rounded-md transition-colors active:opacity-75 ${className}`}
      style={{ WebkitTouchCallout: 'none' }}
    >
      {children}
    </button>
  );
};

interface SwipeNavigationProps {
  children: ReactNode;
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
}

export const SwipeNavigation: React.FC<SwipeNavigationProps> = ({
  children,
  onSwipeLeft,
  onSwipeRight,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [touchStart, setTouchStart] = useState<number | null>(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const handleTouchStart = (e: TouchEvent) => {
      setTouchStart(e.touches[0].clientX);
    };

    const handleTouchEnd = (e: TouchEvent) => {
      if (touchStart === null) return;

      const touchEnd = e.changedTouches[0].clientX;
      const deltaX = touchEnd - touchStart;
      const threshold = 50;

      if (Math.abs(deltaX) > threshold) {
        if (deltaX > 0) {
          onSwipeRight?.();
        } else {
          onSwipeLeft?.();
        }
      }

      setTouchStart(null);
    };

    container.addEventListener('touchstart', handleTouchStart);
    container.addEventListener('touchend', handleTouchEnd);

    return () => {
      container.removeEventListener('touchstart', handleTouchStart);
      container.removeEventListener('touchend', handleTouchEnd);
    };
  }, [touchStart, onSwipeLeft, onSwipeRight]);

  return (
    <div ref={containerRef} className="w-full">
      {children}
    </div>
  );
};

interface TouchOptimizedSelectProps {
  options: Array<{ value: string; label: string }>;
  value: string;
  onChange: (value: string) => void;
  label?: string;
}

export const TouchOptimizedSelect: React.FC<TouchOptimizedSelectProps> = ({
  options,
  value,
  onChange,
  label,
}) => {
  return (
    <div className="flex flex-col">
      {label && <label className="text-sm font-medium text-gray-700 mb-2">{label}</label>}
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="min-h-[44px] px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-base"
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </div>
  );
};
