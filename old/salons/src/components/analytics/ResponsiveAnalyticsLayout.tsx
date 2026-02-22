import React, { ReactNode } from 'react';

interface ResponsiveAnalyticsLayoutProps {
  title: string;
  children: ReactNode;
  subtitle?: string;
}

export const ResponsiveAnalyticsLayout: React.FC<ResponsiveAnalyticsLayoutProps> = ({
  title,
  subtitle,
  children,
}) => {
  return (
    <div className="min-h-screen bg-gray-50 p-2 sm:p-4 md:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-6 md:mb-8">
          <h1 className="text-2xl sm:text-3xl md:text-4xl font-bold text-gray-900">{title}</h1>
          {subtitle && <p className="text-sm sm:text-base text-gray-600 mt-2">{subtitle}</p>}
        </div>
        {children}
      </div>
    </div>
  );
};

interface ResponsiveGridProps {
  children: ReactNode;
  columns?: 'auto' | 2 | 3 | 4;
}

export const ResponsiveGrid: React.FC<ResponsiveGridProps> = ({ children, columns = 'auto' }) => {
  const gridClass = {
    auto: 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 md:gap-6',
    2: 'grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6',
    3: 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6',
    4: 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6',
  }[columns];

  return <div className={gridClass}>{children}</div>;
};

interface ResponsiveCardProps {
  children: ReactNode;
  title?: string;
  className?: string;
}

export const ResponsiveCard: React.FC<ResponsiveCardProps> = ({ children, title, className = '' }) => {
  return (
    <div className={`bg-white rounded-lg shadow p-4 md:p-6 ${className}`}>
      {title && <h3 className="text-lg md:text-xl font-bold text-gray-900 mb-4">{title}</h3>}
      {children}
    </div>
  );
};

interface ResponsiveChartContainerProps {
  children: ReactNode;
  title?: string;
  height?: 'sm' | 'md' | 'lg';
}

export const ResponsiveChartContainer: React.FC<ResponsiveChartContainerProps> = ({
  children,
  title,
  height = 'md',
}) => {
  const heightClass = {
    sm: 'h-64 sm:h-80',
    md: 'h-80 sm:h-96 md:h-[500px]',
    lg: 'h-96 sm:h-[500px] md:h-[600px]',
  }[height];

  return (
    <ResponsiveCard title={title}>
      <div className={`w-full ${heightClass} overflow-auto`}>{children}</div>
    </ResponsiveCard>
  );
};

interface ResponsiveMetricProps {
  label: string;
  value: string | number;
  unit?: string;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
}

export const ResponsiveMetric: React.FC<ResponsiveMetricProps> = ({
  label,
  value,
  unit,
  trend,
  trendValue,
}) => {
  const trendColor = {
    up: 'text-green-600',
    down: 'text-red-600',
    neutral: 'text-gray-600',
  }[trend || 'neutral'];

  const trendIcon = {
    up: '↑',
    down: '↓',
    neutral: '→',
  }[trend || 'neutral'];

  return (
    <div className="bg-white rounded-lg shadow p-4 md:p-6">
      <p className="text-xs sm:text-sm font-medium text-gray-600 truncate">{label}</p>
      <div className="mt-2 flex items-baseline justify-between">
        <p className="text-xl sm:text-2xl md:text-3xl font-bold text-gray-900">
          {value}
          {unit && <span className="text-sm ml-1">{unit}</span>}
        </p>
        {trendValue && (
          <span className={`text-xs sm:text-sm font-semibold ${trendColor}`}>
            {trendIcon} {trendValue}
          </span>
        )}
      </div>
    </div>
  );
};

interface ResponsiveFilterBarProps {
  children: ReactNode;
}

export const ResponsiveFilterBar: React.FC<ResponsiveFilterBarProps> = ({ children }) => {
  return (
    <div className="bg-white rounded-lg shadow p-4 md:p-6 mb-6 overflow-x-auto">
      <div className="flex flex-col sm:flex-row gap-2 sm:gap-4 min-w-min sm:min-w-0">{children}</div>
    </div>
  );
};
