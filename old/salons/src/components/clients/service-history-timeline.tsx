import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import {
  CalendarIcon,
  DollarIcon,
  UserIcon,
  AlertTriangleIcon,
  FilterIcon,
  XIcon,
} from "@/components/icons";
import { useServiceHistory } from "@/lib/api/hooks/useClients";
// Image removed;

interface ServiceHistoryTimelineProps {
  clientId: string;
}

export function ServiceHistoryTimeline({
  clientId,
}: ServiceHistoryTimelineProps) {
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState<{
    start_date?: string;
    end_date?: string;
    service_type?: string;
    stylist_id?: string;
  }>({});
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 10;

  const { data, isLoading, error } = useServiceHistory(clientId, {
    ...filters,
    offset: (currentPage - 1) * pageSize,
    limit: pageSize,
  });

  const history = data?.items || [];
  const hasMore = data?.has_more || false;

  const handleApplyFilters = () => {
    setCurrentPage(1);
  };

  const handleClearFilters = () => {
    setFilters({});
    setCurrentPage(1);
  };

  const hasActiveFilters = Object.keys(filters).some(
    (key) => filters[key as keyof typeof filters] !== undefined
  );

  if (error) {
    return (
      <Alert variant="error">
        <AlertTriangleIcon size={20} />
        <div>
          <h3 className="font-semibold">Error loading service history</h3>
          <p className="text-sm">{error.message}</p>
        </div>
      </Alert>
    );
  }

  return (
    <div className="space-y-4">
      {/* Filter Toggle */}
      <div className="flex justify-between items-center">
        <h2 className="text-lg font-semibold text-foreground">
          Service History
        </h2>
        <Button
          variant="outline"
          size="sm"
          onClick={() => setShowFilters(!showFilters)}
        >
          <FilterIcon size={16} />
          {showFilters ? "Hide" : "Show"} Filters
        </Button>
      </div>

      {/* Filters */}
      {showFilters && (
        <Card className="p-4 space-y-4 bg-muted/30">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-foreground">Filters</h3>
            {hasActiveFilters && (
              <Button variant="ghost" size="sm" onClick={handleClearFilters}>
                <XIcon size={16} />
                Clear All
              </Button>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="start_date">From Date</Label>
              <Input
                id="start_date"
                type="date"
                value={filters.start_date || ""}
                onChange={(e) =>
                  setFilters({
                    ...filters,
                    start_date: e.target.value || undefined,
                  })
                }
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="end_date">To Date</Label>
              <Input
                id="end_date"
                type="date"
                value={filters.end_date || ""}
                onChange={(e) =>
                  setFilters({
                    ...filters,
                    end_date: e.target.value || undefined,
                  })
                }
              />
            </div>
          </div>

          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={handleClearFilters}>
              Clear
            </Button>
            <Button onClick={handleApplyFilters}>Apply Filters</Button>
          </div>
        </Card>
      )}

      {/* Timeline */}
      {isLoading ? (
        <div className="flex justify-center py-12">
          <Spinner />
        </div>
      ) : history.length === 0 ? (
        <Card className="p-12">
          <div className="text-center">
            <CalendarIcon
              size={48}
              className="mx-auto text-muted-foreground mb-4"
            />
            <h3 className="text-lg font-semibold text-foreground mb-2">
              No service history
            </h3>
            <p className="text-muted-foreground">
              {hasActiveFilters
                ? "No services found matching your filters"
                : "This client hasn't had any services yet"}
            </p>
          </div>
        </Card>
      ) : (
        <>
          <div className="space-y-4">
            {history.map((item, index) => (
              <Card key={index} className="p-4">
                <div className="flex items-start gap-4">
                  {/* Timeline Dot */}
                  <div className="flex flex-col items-center">
                    <div className="w-3 h-3 rounded-full bg-primary mt-2" />
                    {index < history.length - 1 && (
                      <div className="w-0.5 h-full bg-border mt-2" />
                    )}
                  </div>

                  {/* Content */}
                  <div className="flex-1 space-y-3">
                    {/* Header */}
                    <div className="flex items-start justify-between">
                      <div>
                        <h3 className="font-semibold text-foreground">
                          {item.service_name}
                        </h3>
                        <div className="flex items-center gap-4 mt-1 text-sm text-muted-foreground">
                          <div className="flex items-center gap-1">
                            <CalendarIcon size={14} />
                            {new Date(item.date).toLocaleDateString("en-US", {
                              year: "numeric",
                              month: "long",
                              day: "numeric",
                            })}
                          </div>
                          {item.stylist_name && (
                            <div className="flex items-center gap-1">
                              <UserIcon size={14} />
                              {item.stylist_name}
                            </div>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center gap-1 text-lg font-semibold text-foreground">
                        <DollarIcon size={18} />₦{item.cost.toLocaleString()}
                      </div>
                    </div>

                    {/* Photos */}
                    {item.photos && item.photos.length > 0 && (
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                        {item.photos.map((photo, photoIndex) => (
                          <div
                            key={photoIndex}
                            className="relative aspect-square rounded-lg overflow-hidden bg-muted"
                          >
                            <img                               src={photo.photo_url}
                              alt={
                                photo.description || `${photo.photo_type} photo`
                              } className="object-cover"
                              sizes="(max-width: 768px) 50vw, 25vw"
                            />
                            <div className="absolute top-2 left-2">
                              <span className="px-2 py-1 text-xs font-medium bg-black/70 text-white rounded">
                                {photo.photo_type}
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Notes */}
                    {item.notes && (
                      <p className="text-sm text-muted-foreground">
                        {item.notes}
                      </p>
                    )}
                  </div>
                </div>
              </Card>
            ))}
          </div>

          {/* Pagination */}
          {(hasMore || currentPage > 1) && (
            <div className="flex items-center justify-center gap-2">
              <Button
                variant="outline"
                disabled={currentPage === 1}
                onClick={() => setCurrentPage((p) => p - 1)}
              >
                Previous
              </Button>
              <span className="text-sm text-muted-foreground">
                Page {currentPage}
              </span>
              <Button
                variant="outline"
                disabled={!hasMore}
                onClick={() => setCurrentPage((p) => p + 1)}
              >
                Next
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
