/**
 * Staff Selector Component - Display available staff for public booking
 * Shows staff specialties and ratings
 */

import { useState, useEffect } from "react";
import { Card, Button, Spinner, Avatar, Badge } from "@/components/ui";
import { usePublicStaff } from "@/hooks/usePublicBooking";
import {
  CheckIcon,
  AlertCircleIcon,
  InfoIcon,
  StarIcon,
} from "@/components/icons";
import { useToast } from "@/components/ui/toast";

interface StaffSelectorProps {
  serviceId: string;
  onSelect: (staffId: string) => void;
  onNoStaffAvailable?: () => void;
}

export default function StaffSelector({
  serviceId,
  onSelect,
  onNoStaffAvailable,
}: StaffSelectorProps) {
  const [selectedStaffId, setSelectedStaffId] = useState<string | null>(null);
  const { addToast } = useToast();

  const { data: staff, isLoading, error } = usePublicStaff(serviceId);

  // Show toast notification when no staff are available
  useEffect(() => {
    if (!isLoading && !error && (!staff || staff.length === 0)) {
      addToast({
        title: "No Staff Available",
        description:
          "Unfortunately, no staff members are currently assigned to this service. Please select a different service or contact the salon.",
        variant: "warning",
      });
      onNoStaffAvailable?.();
    }
  }, [staff, isLoading, error, addToast, onNoStaffAvailable]);

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-12">
        <Spinner className="mb-4" />
        <p className="text-muted-foreground">Loading staff members...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-6">
        <div className="flex gap-3">
          <AlertCircleIcon className="text-destructive shrink-0 mt-0.5" />
          <div>
            <h3 className="font-semibold text-destructive mb-1">
              Failed to Load Staff
            </h3>
            <p className="text-sm text-destructive/80 mb-4">
              We encountered an error while loading available staff members.
              Please try again or contact support if the problem persists.
            </p>
            <Button
              variant="outline"
              size="sm"
              onClick={() => window.location.reload()}
            >
              Retry
            </Button>
          </div>
        </div>
      </div>
    );
  }

  if (!staff || staff.length === 0) {
    return (
      <div className="bg-amber-50 border border-amber-200 rounded-lg p-8">
        <div className="flex gap-4">
          <InfoIcon className="text-amber-600 shrink-0 mt-1" size={24} />
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-amber-900 mb-2">
              No Staff Available
            </h3>
            <p className="text-amber-800 mb-4">
              Unfortunately, no staff members are currently assigned to this
              service. This could mean:
            </p>
            <ul className="list-disc list-inside text-amber-800 text-sm space-y-1 mb-4">
              <li>The salon is still setting up staff assignments</li>
              <li>All staff are currently unavailable</li>
              <li>This service is temporarily unavailable</li>
            </ul>
            <div className="flex gap-2">
              <Button variant="outline" onClick={() => window.history.back()}>
                ← Go Back
              </Button>
              <Button
                variant="outline"
                onClick={() => {
                  const contactEmail = "contact@salon.com";
                  window.location.href = `mailto:${contactEmail}?subject=Staff%20Availability%20Question`;
                }}
              >
                Contact Salon
              </Button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const handleSelect = (staffId: string) => {
    setSelectedStaffId(staffId);
    onSelect(staffId);
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Select a Staff Member</h2>
        <p className="text-sm text-muted-foreground mt-1">
          Choose who you'd like to book with
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {staff.map((member) => (
          <Card
            key={member.id}
            className={`p-4 cursor-pointer transition-all ${
              selectedStaffId === member.id
                ? "ring-2 ring-primary bg-primary/5"
                : "hover:shadow-lg"
            }`}
            onClick={() => handleSelect(member.id)}
          >
            <div className="flex items-start gap-4">
              <Avatar
                src={member.profile_image_url}
                alt={`${member.first_name} ${member.last_name}`}
                className="w-16 h-16 shrink-0"
              />

              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold">
                      {member.first_name} {member.last_name}
                    </h3>
                    {member.bio && (
                      <p className="text-muted-foreground text-sm mt-1">
                        {member.bio}
                      </p>
                    )}

                    {/* Specialties */}
                    {member.specialties && member.specialties.length > 0 && (
                      <div className="mt-2 flex flex-wrap gap-1">
                        {member.specialties.map((specialty, idx) => (
                          <Badge
                            key={idx}
                            variant="secondary"
                            className="text-xs"
                          >
                            {specialty}
                          </Badge>
                        ))}
                      </div>
                    )}

                    {/* Rating */}
                    {member.rating !== undefined && (
                      <div className="mt-2 flex items-center gap-1">
                        <div className="flex items-center gap-0.5">
                          {[...Array(5)].map((_, i) => (
                            <StarIcon
                              key={i}
                              size={14}
                              className={
                                i < Math.floor(member.rating ?? 0)
                                  ? "fill-yellow-400 text-yellow-400"
                                  : "text-gray-300"
                              }
                            />
                          ))}
                        </div>
                        <span className="text-sm text-muted-foreground">
                          {member.rating?.toFixed(1)} (
                          {member.review_count || 0} reviews)
                        </span>
                      </div>
                    )}
                  </div>
                  {selectedStaffId === member.id && (
                    <CheckIcon size={20} className="text-primary shrink-0" />
                  )}
                </div>

                <Button
                  variant={
                    selectedStaffId === member.id ? "primary" : "outline"
                  }
                  className="w-full mt-4"
                  onClick={() => handleSelect(member.id)}
                >
                  {selectedStaffId === member.id ? "✓ Selected" : "Select"}
                </Button>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {selectedStaffId && (
        <div className="flex justify-end">
          <Button
            variant="primary"
            onClick={() => handleSelect(selectedStaffId)}
          >
            Continue →
          </Button>
        </div>
      )}
    </div>
  );
}
