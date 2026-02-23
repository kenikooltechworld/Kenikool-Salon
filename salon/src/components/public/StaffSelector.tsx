/**
 * Staff Selector Component - Display available staff for public booking
 */

import { useState } from "react";
import { Card, Button, Spinner, Avatar } from "@/components/ui";
import { usePublicStaff } from "@/hooks/usePublicBooking";
import { CheckIcon } from "@/components/icons";

interface StaffSelectorProps {
  serviceId: string;
  onSelect: (staffId: string) => void;
}

export default function StaffSelector({
  serviceId,
  onSelect,
}: StaffSelectorProps) {
  const [selectedStaffId, setSelectedStaffId] = useState<string | null>(null);

  const { data: staff, isLoading, error } = usePublicStaff(serviceId);

  if (isLoading) {
    return (
      <div className="flex justify-center py-8">
        <Spinner />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <p className="text-destructive">
          Failed to load staff. Please try again.
        </p>
      </div>
    );
  }

  if (!staff || staff.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-muted-foreground">
          No staff available for this service.
        </p>
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
                className="w-16 h-16 flex-shrink-0"
              />

              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <h3 className="text-lg font-semibold">
                      {member.first_name} {member.last_name}
                    </h3>
                    {member.bio && (
                      <p className="text-muted-foreground text-sm mt-1">
                        {member.bio}
                      </p>
                    )}
                    {member.specialties && member.specialties.length > 0 && (
                      <div className="mt-2 flex flex-wrap gap-1">
                        {member.specialties.map((specialty, idx) => (
                          <span
                            key={idx}
                            className="inline-block bg-primary/10 text-primary text-xs px-2 py-1 rounded"
                          >
                            {specialty}
                          </span>
                        ))}
                      </div>
                    )}
                    {member.rating && (
                      <div className="mt-2 text-sm">
                        <span className="text-yellow-500">★</span>
                        <span className="ml-1 font-semibold">
                          {member.rating.toFixed(1)}
                        </span>
                        <span className="text-muted-foreground ml-1">
                          ({member.review_count} reviews)
                        </span>
                      </div>
                    )}
                  </div>
                  {selectedStaffId === member.id && (
                    <CheckIcon
                      size={20}
                      className="text-primary flex-shrink-0"
                    />
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
          <Button variant="primary">Continue →</Button>
        </div>
      )}
    </div>
  );
}
