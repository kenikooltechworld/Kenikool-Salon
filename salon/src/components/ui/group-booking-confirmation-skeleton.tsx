import { Skeleton } from "@/components/ui/skeleton";
import { Card } from "@/components/ui/card";

export function GroupBookingConfirmationSkeleton() {
  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-3xl mx-auto space-y-6">
        {/* Success Header Skeleton */}
        <div className="text-center mb-8">
          <Skeleton className="h-16 w-16 rounded-full mx-auto mb-4" />
          <Skeleton className="h-8 w-80 mx-auto mb-2" />
          <Skeleton className="h-4 w-96 mx-auto" />
        </div>

        {/* Booking Status Card Skeleton */}
        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <Skeleton className="h-6 w-40" />
            <Skeleton className="h-6 w-24 rounded-full" />
          </div>
          <Skeleton className="h-4 w-48" />
        </Card>

        {/* Group Details Card Skeleton */}
        <Card className="p-6">
          <Skeleton className="h-6 w-40 mb-4" />
          <div className="space-y-3">
            <div className="flex items-start gap-3">
              <Skeleton className="h-5 w-5 mt-0.5" />
              <div className="space-y-2 flex-1">
                <Skeleton className="h-5 w-48" />
                <Skeleton className="h-4 w-32" />
              </div>
            </div>
            <div className="flex items-start gap-3">
              <Skeleton className="h-5 w-5 mt-0.5" />
              <div className="space-y-2 flex-1">
                <Skeleton className="h-5 w-40" />
                <Skeleton className="h-4 w-56" />
              </div>
            </div>
          </div>
        </Card>

        {/* Organizer Card Skeleton */}
        <Card className="p-6">
          <Skeleton className="h-6 w-40 mb-4" />
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <Skeleton className="h-5 w-5" />
              <div className="space-y-2 flex-1">
                <Skeleton className="h-5 w-36" />
                <Skeleton className="h-4 w-48" />
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Skeleton className="h-5 w-5" />
              <Skeleton className="h-4 w-32" />
            </div>
          </div>
        </Card>

        {/* Pricing Card Skeleton */}
        <Card className="p-6 bg-blue-50">
          <Skeleton className="h-6 w-40 mb-4" />
          <div className="space-y-3">
            <div className="flex justify-between">
              <Skeleton className="h-4 w-24" />
              <Skeleton className="h-4 w-20" />
            </div>
            <Skeleton className="h-4 w-full" />
            <div className="flex justify-between pt-2 border-t">
              <Skeleton className="h-5 w-24" />
              <Skeleton className="h-5 w-20" />
            </div>
          </div>
        </Card>

        {/* Next Steps Card Skeleton */}
        <Card className="p-6 bg-yellow-50">
          <Skeleton className="h-6 w-40 mb-4" />
          <div className="space-y-3">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="flex items-start gap-2">
                <Skeleton className="h-5 w-5 rounded-full shrink-0" />
                <Skeleton className="h-4 w-full" />
              </div>
            ))}
          </div>
        </Card>

        {/* Action Buttons Skeleton */}
        <div className="flex gap-4">
          <Skeleton className="h-10 flex-1" />
          <Skeleton className="h-10 flex-1" />
        </div>
      </div>
    </div>
  );
}
