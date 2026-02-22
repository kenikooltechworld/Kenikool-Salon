import { useState } from "react";
import { useCreateGroupBooking } from "@/lib/api/hooks/useGroupBookings";
import { useServices } from "@/lib/api/hooks/useServices";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Modal } from "@/components/ui/modal";
import { Select } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Alert } from "@/components/ui/alert";
import { Spinner } from "@/components/ui/spinner";
import { PlusIcon, TrashIcon, AlertTriangleIcon } from "@/components/icons";
import { showToast } from "@/lib/utils/toast";
import type { GroupBookingCreate, GroupBookingMember } from "@/lib/api/types";
import { AxiosError } from "axios";
import { ErrorResponse } from "@/lib/api/types";

interface GroupBookingFormModalProps {
  isOpen: boolean;
  onClose: () => void;
}

interface FormData {
  organizer_name: string;
  organizer_phone: string;
  organizer_email: string;
  booking_date: string;
  notes: string;
}

export function GroupBookingFormModal({
  isOpen,
  onClose,
}: GroupBookingFormModalProps) {
  const { data: services = [] } = useServices();

  const [formData, setFormData] = useState<FormData>({
    organizer_name: "",
    organizer_phone: "",
    organizer_email: "",
    booking_date: "",
    notes: "",
  });

  const [members, setMembers] = useState<GroupBookingMember[]>([
    {
      client_name: "",
      client_phone: "",
      client_email: "",
      service_id: "",
    },
  ]);

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [totalPrice, setTotalPrice] = useState(0);

  const createGroupBooking = useCreateGroupBooking();

  // Calculate total price whenever members change
  const calculateTotalPrice = () => {
    let total = 0;
    members.forEach((member) => {
      if (member.service_id) {
        const service = services.find((s) => s.id === member.service_id);
        if (service) {
          total += service.price;
        }
      }
    });
    setTotalPrice(total);
  };

  const handleChange = (field: keyof FormData, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  const handleMemberChange = (
    index: number,
    field: keyof GroupBookingMember,
    value: string
  ) => {
    const updated = [...members];
    updated[index] = { ...updated[index], [field]: value };
    setMembers(updated);

    // Recalculate price if service changed
    if (field === "service_id") {
      setTimeout(calculateTotalPrice, 0);
    }

    const errorKey = `member_${index}_${field}`;
    if (errors[errorKey]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[errorKey];
        return newErrors;
      });
    }
  };

  const addMember = () => {
    setMembers([
      ...members,
      {
        client_name: "",
        client_phone: "",
        client_email: "",
        service_id: "",
      },
    ]);
  };

  const removeMember = (index: number) => {
    if (members.length > 1) {
      setMembers(members.filter((_, i) => i !== index));
    }
  };

  const validate = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.organizer_name.trim()) {
      newErrors.organizer_name = "Organizer name is required";
    }
    if (!formData.organizer_phone.trim()) {
      newErrors.organizer_phone = "Organizer phone is required";
    }
    if (!formData.booking_date) {
      newErrors.booking_date = "Booking date is required";
    }

    // Check for duplicate phone numbers
    const phoneNumbers = new Set<string>();
    members.forEach((member, index) => {
      if (!member.client_name.trim()) {
        newErrors[`member_${index}_client_name`] = "Name is required";
      }
      if (!member.client_phone.trim()) {
        newErrors[`member_${index}_client_phone`] = "Phone is required";
      } else if (phoneNumbers.has(member.client_phone)) {
        newErrors[`member_${index}_client_phone`] = "Duplicate phone number";
      } else {
        phoneNumbers.add(member.client_phone);
      }
      if (!member.service_id) {
        newErrors[`member_${index}_service_id`] = "Service is required";
      }
    });

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) return;

    const groupBookingData: GroupBookingCreate = {
      organizer_name: formData.organizer_name,
      organizer_phone: formData.organizer_phone,
      organizer_email: formData.organizer_email || undefined,
      booking_date: new Date(formData.booking_date).toISOString(),
      members: members,
      notes: formData.notes || undefined,
    };

    try {
      await createGroupBooking.mutateAsync(groupBookingData);
      showToast("Group booking created successfully!", "success");
      handleReset();
      onClose();
    } catch (error: any) {
      const errorMessage =
        error.response?.data?.message ||
        error.message ||
        "Failed to create group booking";
      setErrors({ submit: errorMessage });
      showToast(errorMessage, "error");
    }
  };

  const handleReset = () => {
    setFormData({
      organizer_name: "",
      organizer_phone: "",
      organizer_email: "",
      booking_date: "",
      notes: "",
    });
    setMembers([
      {
        client_name: "",
        client_phone: "",
        client_email: "",
        service_id: "",
      },
    ]);
    setErrors({});
  };

  const handleClose = () => {
    handleReset();
    onClose();
  };

  return (
    <Modal open={isOpen} onClose={handleClose} size="xl">
      <div className="p-6">
        <h2 className="text-xl font-bold text-foreground mb-4">
          Create Group Booking
        </h2>

        <form onSubmit={handleSubmit} className="space-y-6">
          {errors.submit && (
            <Alert variant="error">
              <AlertTriangleIcon size={20} />
              <div>
                <p className="text-sm">{errors.submit}</p>
              </div>
            </Alert>
          )}

          {/* Organizer Information */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Organizer Information</h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="organizer_name">Organizer Name *</Label>
                <Input
                  id="organizer_name"
                  value={formData.organizer_name}
                  onChange={(e) =>
                    handleChange("organizer_name", e.target.value)
                  }
                  placeholder="Enter organizer name"
                  error={!!errors.organizer_name}
                />
                {errors.organizer_name && (
                  <p className="text-sm text-error mt-1">
                    {errors.organizer_name}
                  </p>
                )}
              </div>

              <div>
                <Label htmlFor="organizer_phone">Organizer Phone *</Label>
                <Input
                  id="organizer_phone"
                  value={formData.organizer_phone}
                  onChange={(e) =>
                    handleChange("organizer_phone", e.target.value)
                  }
                  placeholder="Enter phone number"
                  type="tel"
                  error={!!errors.organizer_phone}
                />
                {errors.organizer_phone && (
                  <p className="text-sm text-error mt-1">
                    {errors.organizer_phone}
                  </p>
                )}
              </div>

              <div>
                <Label htmlFor="organizer_email">Organizer Email</Label>
                <Input
                  id="organizer_email"
                  value={formData.organizer_email}
                  onChange={(e) =>
                    handleChange("organizer_email", e.target.value)
                  }
                  placeholder="Enter email address"
                  type="email"
                />
              </div>

              <div>
                <Label htmlFor="booking_date">Booking Date *</Label>
                <Input
                  id="booking_date"
                  value={formData.booking_date}
                  onChange={(e) => handleChange("booking_date", e.target.value)}
                  type="datetime-local"
                  error={!!errors.booking_date}
                />
                {errors.booking_date && (
                  <p className="text-sm text-error mt-1">
                    {errors.booking_date}
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Group Members */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold">Group Members</h3>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={addMember}
              >
                <PlusIcon className="w-4 h-4 mr-2" />
                Add Member
              </Button>
            </div>

            {members.map((member, index) => (
              <div
                key={index}
                className="p-4 border border-[var(--border)] rounded-lg space-y-3"
              >
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium">Member {index + 1}</h4>
                  {members.length > 1 && (
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => removeMember(index)}
                    >
                      <TrashIcon className="w-4 h-4 text-error" />
                    </Button>
                  )}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div>
                    <Label htmlFor={`member_${index}_name`}>Name *</Label>
                    <Input
                      id={`member_${index}_name`}
                      value={member.client_name}
                      onChange={(e) =>
                        handleMemberChange(index, "client_name", e.target.value)
                      }
                      placeholder="Enter member name"
                      error={!!errors[`member_${index}_client_name`]}
                    />
                    {errors[`member_${index}_client_name`] && (
                      <p className="text-sm text-error mt-1">
                        {errors[`member_${index}_client_name`]}
                      </p>
                    )}
                  </div>

                  <div>
                    <Label htmlFor={`member_${index}_phone`}>Phone *</Label>
                    <Input
                      id={`member_${index}_phone`}
                      value={member.client_phone}
                      onChange={(e) =>
                        handleMemberChange(
                          index,
                          "client_phone",
                          e.target.value
                        )
                      }
                      placeholder="Enter phone number"
                      type="tel"
                      error={!!errors[`member_${index}_client_phone`]}
                    />
                    {errors[`member_${index}_client_phone`] && (
                      <p className="text-sm text-error mt-1">
                        {errors[`member_${index}_client_phone`]}
                      </p>
                    )}
                  </div>

                  <div>
                    <Label htmlFor={`member_${index}_email`}>Email</Label>
                    <Input
                      id={`member_${index}_email`}
                      value={member.client_email || ""}
                      onChange={(e) =>
                        handleMemberChange(
                          index,
                          "client_email",
                          e.target.value
                        )
                      }
                      placeholder="Enter email address"
                      type="email"
                    />
                  </div>

                  <div>
                    <Label htmlFor={`member_${index}_service`}>Service *</Label>
                    <Select
                      id={`member_${index}_service`}
                      value={member.service_id}
                      onChange={(e) =>
                        handleMemberChange(index, "service_id", e.target.value)
                      }
                      error={!!errors[`member_${index}_service_id`]}
                    >
                      <option value="">Select a service</option>
                      {services.map((service) => (
                        <option key={service.id} value={service.id}>
                          {service.name} - ₦{service.price.toLocaleString()}
                        </option>
                      ))}
                    </Select>
                    {errors[`member_${index}_service_id`] && (
                      <p className="text-sm text-error mt-1">
                        {errors[`member_${index}_service_id`]}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Notes */}
          <div>
            <Label htmlFor="notes">Notes</Label>
            <Textarea
              id="notes"
              value={formData.notes}
              onChange={(e) => handleChange("notes", e.target.value)}
              placeholder="Add any special requests or notes..."
              rows={3}
            />
          </div>

          {/* Total Price Preview */}
          {totalPrice > 0 && (
            <div className="p-4 bg-primary/10 border border-primary/20 rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">
                    Estimated Total Price
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    Based on selected services for {members.length} member
                    {members.length !== 1 ? "s" : ""}
                  </p>
                </div>
                <p className="text-3xl font-bold text-primary">
                  ₦{totalPrice.toLocaleString()}
                </p>
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-3 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={handleClose}
              disabled={createGroupBooking.isPending}
              className="flex-1"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={createGroupBooking.isPending}
              className="flex-1"
            >
              {createGroupBooking.isPending ? (
                <>
                  <Spinner size="sm" />
                  Creating...
                </>
              ) : (
                "Create Group Booking"
              )}
            </Button>
          </div>
        </form>
      </div>
    </Modal>
  );
}
