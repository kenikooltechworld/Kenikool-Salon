"use client";

import { useState, useEffect, useMemo } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import {
  useClientReviews,
  useModerateReview,
  useRatingAggregation,
  useFilterCounts,
  useBulkModerateReviews,
  type ReviewFiltersParams,
} from "@/lib/api/hooks/useClientReviews";
import {
  ReviewModerationList,
  ReviewStats,
  ReviewFilters,
  BulkActionsToolbar,
  ExportButton,
  type ReviewFilters as ReviewFiltersType,
} from "@/components/reviews";
import { StarIcon } from "@/components/icons";
import { Card } from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";
import { showToast } from "@/lib/utils/toast";
import type { Review } from "@/lib/api/types";

export default function ReviewsPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [filters, setFilters] = useState<ReviewFiltersType>({});
  const [pageSize, setPageSize] = useState(20);
  const [currentPage, setCurrentPage] = useState(0);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());

  // Parse URL params on mount
  useEffect(() => {
    const urlFilters: ReviewFiltersType = {};

    const status = searchParams.get("status");
    if (status) urlFilters.status = status as "pending" | "approved" | "rejected";

    const rating = searchParams.getAll("rating");
    if (rating.length > 0) urlFilters.rating = rating.map(Number);

    const serviceId = searchParams.get("service_id");
    if (serviceId) urlFilters.serviceId = serviceId;

    const stylistId = searchParams.get("stylist_id");
    if (stylistId) urlFilters.stylistId = stylistId;

    const startDate = searchParams.get("start_date");
    const endDate = searchParams.get("end_date");
    if (startDate || endDate) {
      urlFilters.dateRange = {
        start: startDate || "",
        end: endDate || "",
      };
    }

    const hasResponse = searchParams.get("has_response");
    if (hasResponse === "true") urlFilters.hasResponse = true;

    const hasPhotos = searchParams.get("has_photos");
    if (hasPhotos === "true") urlFilters.hasPhotos = true;

    const isFlagged = searchParams.get("is_flagged");
    if (isFlagged === "true") urlFilters.isFlagged = true;

    setFilters(urlFilters);
    setCurrentPage(0);
  }, [searchParams]);

  // Build API params from filters
  const apiParams: ReviewFiltersParams = useMemo(() => {
    const params: ReviewFiltersParams = {
      skip: currentPage * pageSize,
      limit: pageSize,
      sort_by: "created_at",
      sort_order: "desc",
    };

    if (filters.status) params.status = filters.status;
    if (filters.rating?.length) params.rating = filters.rating;
    if (filters.serviceId) params.service_id = filters.serviceId;
    if (filters.stylistId) params.stylist_id = filters.stylistId;
    if (filters.dateRange?.start) params.start_date = filters.dateRange.start;
    if (filters.dateRange?.end) params.end_date = filters.dateRange.end;
    if (filters.hasResponse) params.has_response = true;
    if (filters.hasPhotos) params.has_photos = true;
    if (filters.isFlagged) params.is_flagged = true;

    return params;
  }, [filters, currentPage, pageSize]);

  const { data: reviewsData, isLoading } = useClientReviews(apiParams);
  const { data: aggregation } = useRatingAggregation();
  const { data: filterCounts } = useFilterCounts();
  const moderateMutation = useModerateReview();
  const bulkModerateMutation = useBulkModerateReviews();

  const reviews: Review[] = reviewsData?.reviews || [];
  const totalCount = reviewsData?.total || 0;

  const handleFilterChange = (newFilters: ReviewFiltersType) => {
    setFilters(newFilters);
    setCurrentPage(0);

    // Update URL params
    const params = new URLSearchParams();

    if (newFilters.status) params.set("status", newFilters.status);
    if (newFilters.rating?.length) {
      newFilters.rating.forEach((r) => params.append("rating", r.toString()));
    }
    if (newFilters.serviceId) params.set("service_id", newFilters.serviceId);
    if (newFilters.stylistId) params.set("stylist_id", newFilters.stylistId);
    if (newFilters.dateRange?.start)
      params.set("start_date", newFilters.dateRange.start);
    if (newFilters.dateRange?.end)
      params.set("end_date", newFilters.dateRange.end);
    if (newFilters.hasResponse) params.set("has_response", "true");
    if (newFilters.hasPhotos) params.set("has_photos", "true");
    if (newFilters.isFlagged) params.set("is_flagged", "true");

    const queryString = params.toString();
    router.push(`/dashboard/reviews${queryString ? `?${queryString}` : ""}`);
  };

  const handleApprove = async (id: string) => {
    try {
      await moderateMutation.mutateAsync({
        id,
        data: { status: "approved" },
      });
      showToast("Review approved successfully", "success");
    } catch (error: any) {
      showToast(
        error.message || "Failed to approve review",
        "error"
      );
    }
  };

  const handleReject = async (id: string) => {
    if (!confirm("Reject this review?")) return;
    try {
      await moderateMutation.mutateAsync({
        id,
        data: { status: "rejected" },
      });
      showToast("Review rejected successfully", "success");
    } catch (error: any) {
      showToast(
        error.message || "Failed to reject review",
        "error"
      );
    }
  };

  const handleBulkApprove = async (ids: string[]) => {
    try {
      await bulkModerateMutation.mutateAsync({
        reviewIds: ids,
        action: "approved",
      });
      showToast(`${ids.length} review(s) approved successfully`, "success");
      setSelectedIds(new Set());
    } catch (error: any) {
      showToast(
        error.message || "Failed to approve reviews",
        "error"
      );
    }
  };

  const handleBulkReject = async (ids: string[]) => {
    try {
      await bulkModerateMutation.mutateAsync({
        reviewIds: ids,
        action: "rejected",
      });
      showToast(`${ids.length} review(s) rejected successfully`, "success");
      setSelectedIds(new Set());
    } catch (error: any) {
      showToast(
        error.message || "Failed to reject reviews",
        "error"
      );
    }
  };

  const handleBulkDelete = async (ids: string[]) => {
    try {
      await bulkModerateMutation.mutateAsync({
        reviewIds: ids,
        action: "deleted",
      });
      showToast(`${ids.length} review(s) deleted successfully`, "success");
      setSelectedIds(new Set());
    } catch (error: any) {
      showToast(
        error.message || "Failed to delete reviews",
        "error"
      );
    }
  };

  const handleClearSelection = () => {
    setSelectedIds(new Set());
  };

  // Convert filter counts to stats format
  const filterStats = useMemo(() => {
    if (!filterCounts) {
      return {
        totalReviews: 0,
        byStatus: {},
        byRating: {},
        byService: {},
        byStylist: {},
        withResponse: 0,
        withPhotos: 0,
        flagged: 0,
      };
    }

    return {
      totalReviews: filterCounts.total || 0,
      byStatus: filterCounts.status || {},
      byRating: filterCounts.rating || {},
      byService: filterCounts.services || {},
      byStylist: filterCounts.stylists || {},
      withResponse: filterCounts.has_response || 0,
      withPhotos: filterCounts.has_photos || 0,
      flagged: filterCounts.is_flagged || 0,
    };
  }, [filterCounts]);

  if (isLoading && !reviews.length) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="lg" />
      </div>
    );
  }

  const totalPages = Math.ceil(totalCount / pageSize);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-3">
          <StarIcon size={32} className="text-[var(--primary)]" />
          Reviews
        </h1>
        <p className="text-[var(--muted-foreground)] mt-1">
          Moderate and manage client reviews
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <Card className="p-6">
            <h2 className="text-lg font-semibold mb-4">Pending Reviews</h2>
            <ReviewModerationList
              reviews={reviews.filter(
                (r: Review) => r.status === "pending"
              ) as Review[]}
              onApprove={handleApprove}
              onReject={handleReject}
            />
          </Card>
        </div>

        <div className="lg:col-span-1">
          <ReviewStats aggregation={aggregation || null} />
        </div>
      </div>

      {/* Filters Section */}
      <ReviewFilters
        onFilterChange={handleFilterChange}
        stats={filterStats}
        currentFilters={filters}
      />

      {/* All Reviews Section */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">
            All Reviews ({totalCount})
          </h2>
          <div className="flex items-center gap-4">
            <ExportButton filters={apiParams} />
            <div className="text-sm text-muted-foreground">
              Page {currentPage + 1} of {totalPages || 1}
            </div>
          </div>
        </div>

        {reviews.length > 0 ? (
          <>
            <ReviewModerationList
              reviews={reviews as Review[]}
              onApprove={handleApprove}
              onReject={handleReject}
              onSelectionChange={setSelectedIds}
            />

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-between mt-6 pt-6 border-t">
                <button
                  onClick={() => setCurrentPage(Math.max(0, currentPage - 1))}
                  disabled={currentPage === 0}
                  className="px-4 py-2 rounded-md bg-muted text-muted-foreground hover:bg-muted/80 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Previous
                </button>

                <div className="flex gap-2">
                  {Array.from({ length: totalPages }).map((_, i) => (
                    <button
                      key={i}
                      onClick={() => setCurrentPage(i)}
                      className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                        currentPage === i
                          ? "bg-primary text-primary-foreground"
                          : "bg-muted text-muted-foreground hover:bg-muted/80"
                      }`}
                    >
                      {i + 1}
                    </button>
                  ))}
                </div>

                <button
                  onClick={() =>
                    setCurrentPage(Math.min(totalPages - 1, currentPage + 1))
                  }
                  disabled={currentPage === totalPages - 1}
                  className="px-4 py-2 rounded-md bg-muted text-muted-foreground hover:bg-muted/80 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                </button>
              </div>
            )}
          </>
        ) : (
          <div className="text-center py-12">
            <p className="text-muted-foreground">No reviews found</p>
          </div>
        )}
      </Card>

      {/* Bulk Actions Toolbar */}
      <BulkActionsToolbar
        selectedIds={selectedIds}
        onApprove={handleBulkApprove}
        onReject={handleBulkReject}
        onDelete={handleBulkDelete}
        onClear={handleClearSelection}
        isLoading={bulkModerateMutation.isPending}
      />
    </div>
  );
}
