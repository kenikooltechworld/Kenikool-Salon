import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/components/ui/toast";
import {
  PlusIcon,
  SearchIcon,
  TrashIcon,
  EditIcon,
  PhoneIcon,
  DollarSignIcon,
  CalendarIcon,
  StarIcon,
} from "@/components/icons";
import { useStaff, useDeleteStaff, useCreateStaff } from "@/hooks/useStaff";
import { ConfirmationModal } from "@/components/ui/confirmation-modal";
import { AddStaffModal } from "@/components/staff/AddStaffModal";
import type { Staff } from "@/types/staff";

export default function StaffPage() {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const { data: staffList = [], isLoading, error } = useStaff();
  const deleteStaffMutation = useDeleteStaff();
  const createStaffMutation = useCreateStaff();
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState<string | null>(null);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState<{
    isOpen: boolean;
    staffId?: string;
    staffName?: string;
  }>({ isOpen: false });

  const filteredStaff = staffList.filter((member: Staff) => {
    const matchesSearch =
      `${member.firstName} ${member.lastName}`
        .toLowerCase()
        .includes(searchTerm.toLowerCase()) ||
      member.email.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesStatus = !statusFilter || member.status === statusFilter;

    return matchesSearch && matchesStatus;
  });

  const handleDeleteClick = (id: string, name: string) => {
    setDeleteConfirm({ isOpen: true, staffId: id, staffName: name });
  };

  const handleConfirmDelete = async () => {
    if (deleteConfirm.staffId) {
      try {
        await deleteStaffMutation.mutateAsync(deleteConfirm.staffId);
        showToast({
          variant: "success",
          title: "Success",
          description: `${deleteConfirm.staffName} has been deleted successfully`,
        });
        setDeleteConfirm({ isOpen: false });
      } catch (error) {
        showToast({
          variant: "error",
          title: "Error",
          description:
            error instanceof Error
              ? error.message
              : "Failed to delete staff member",
        });
      }
    }
  };

  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case "active":
        return "default";
      case "inactive":
        return "secondary";
      case "on_leave":
        return "outline";
      case "terminated":
        return "destructive";
      default:
        return "secondary";
    }
  };

  const getStatusLabel = (status: string) => {
    return status
      .split("_")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");
  };

  return (
    <div className="w-full space-y-4 px-0 sm:px-0">
      {/* Header */}
      <div className="flex flex-col gap-3 sm:gap-4">
        <div className="flex flex-col gap-2">
          <h2 className="text-2xl font-bold text-foreground">Staff</h2>
          <p className="text-sm text-muted-foreground">
            Manage your salon staff members
          </p>
        </div>
        <Button
          className="gap-2 w-full sm:w-auto cursor-pointer"
          onClick={() => setIsAddModalOpen(true)}
        >
          <PlusIcon size={18} />
          Add Staff Member
        </Button>
      </div>

      {/* Search and Filters */}
      <div className="space-y-3">
        <div className="relative w-full">
          <SearchIcon
            size={16}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground pointer-events-none"
          />
          <input
            type="text"
            placeholder="Search staff..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-3 py-2 sm:py-3 border border-border rounded-lg bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary text-xs sm:text-sm"
          />
        </div>

        {/* Status Filter */}
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setStatusFilter(null)}
            className={`px-3 py-1 rounded-full text-sm font-medium transition cursor-pointer ${
              statusFilter === null
                ? "bg-primary text-primary-foreground"
                : "bg-muted text-muted-foreground hover:bg-muted/80"
            }`}
          >
            All
          </button>
          {["active", "inactive", "on_leave", "terminated"].map((status) => (
            <button
              key={status}
              onClick={() => setStatusFilter(status)}
              className={`px-3 py-1 rounded-full text-sm font-medium transition cursor-pointer ${
                statusFilter === status
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted text-muted-foreground hover:bg-muted/80"
              }`}
            >
              {getStatusLabel(status)}
            </button>
          ))}
        </div>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="text-center py-12 text-muted-foreground">
          Loading staff members...
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-4 text-destructive text-sm">
          Failed to load staff members. Please try again.
        </div>
      )}

      {/* Mobile Card View */}
      {!isLoading && !error && (
        <>
          {/* Cards for mobile/tablet */}
          <div className="grid grid-cols-1 gap-3 md:hidden">
            {filteredStaff.length > 0 ? (
              filteredStaff.map((member: Staff) => (
                <div
                  key={member.id}
                  className="bg-card border border-border rounded-lg overflow-hidden hover:shadow-md transition cursor-pointer"
                  onClick={() => navigate(`/staff/${member.id}`)}
                >
                  {/* Image */}
                  {member.profile_image_url ? (
                    <div className="w-full h-40 overflow-hidden bg-muted">
                      <img
                        src={member.profile_image_url}
                        alt={`${member.firstName} ${member.lastName}`}
                        className="w-full h-full object-cover"
                      />
                    </div>
                  ) : (
                    <div className="w-full h-40 bg-muted flex items-center justify-center">
                      <p className="text-muted-foreground text-sm">No image</p>
                    </div>
                  )}

                  {/* Content */}
                  <div className="p-4 space-y-3">
                    {/* Name and Status */}
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1 min-w-0">
                        <p className="font-semibold text-foreground truncate">
                          {member.firstName} {member.lastName}
                        </p>
                        <p className="text-xs text-muted-foreground truncate">
                          {member.email}
                        </p>
                      </div>
                      <Badge variant={getStatusBadgeVariant(member.status)}>
                        {getStatusLabel(member.status)}
                      </Badge>
                    </div>

                    {/* Details Grid */}
                    <div className="grid grid-cols-2 gap-3 text-sm">
                      <div className="flex items-start gap-2">
                        <PhoneIcon
                          size={16}
                          className="text-muted-foreground mt-0.5 flex-shrink-0"
                        />
                        <div>
                          <p className="text-xs text-muted-foreground">Phone</p>
                          <p className="text-foreground font-medium">
                            {member.phone || "N/A"}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-start gap-2">
                        <DollarSignIcon
                          size={16}
                          className="text-muted-foreground mt-0.5 flex-shrink-0"
                        />
                        <div>
                          <p className="text-xs text-muted-foreground">
                            Payment
                          </p>
                          <p className="text-foreground font-medium text-xs">
                            {member.payment_type === "commission"
                              ? `${member.payment_rate}%`
                              : `₦${member.payment_rate.toLocaleString()}`}
                          </p>
                        </div>
                      </div>
                      {member.specialties.length > 0 && (
                        <div className="col-span-2 flex items-start gap-2">
                          <StarIcon
                            size={16}
                            className="text-muted-foreground mt-0.5 flex-shrink-0"
                          />
                          <div className="flex-1">
                            <p className="text-xs text-muted-foreground mb-1">
                              Specialties
                            </p>
                            <div className="flex flex-wrap gap-1">
                              {member.specialties.map(
                                (spec: string, idx: number) => (
                                  <Badge
                                    key={idx}
                                    variant="outline"
                                    className="text-xs"
                                  >
                                    {spec}
                                  </Badge>
                                ),
                              )}
                            </div>
                          </div>
                        </div>
                      )}
                      {member.hire_date && (
                        <div className="col-span-2 flex items-start gap-2">
                          <CalendarIcon
                            size={16}
                            className="text-muted-foreground mt-0.5 flex-shrink-0"
                          />
                          <div>
                            <p className="text-xs text-muted-foreground">
                              Hire Date
                            </p>
                            <p className="text-foreground font-medium">
                              {new Date(member.hire_date).toLocaleDateString()}
                            </p>
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Actions */}
                    <div className="flex gap-2 pt-2 border-t border-border">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          navigate(`/staff/${member.id}`);
                        }}
                        className="flex-1 flex items-center justify-center gap-2 p-2 hover:bg-muted rounded-lg transition cursor-pointer text-sm font-medium"
                      >
                        <EditIcon size={16} className="text-muted-foreground" />
                        Edit
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteClick(
                            member.id,
                            `${member.firstName} ${member.lastName}`,
                          );
                        }}
                        className="flex-1 flex items-center justify-center gap-2 p-2 hover:bg-destructive/10 rounded-lg transition cursor-pointer text-sm font-medium text-destructive"
                      >
                        <TrashIcon size={16} />
                        Delete
                      </button>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-12 text-muted-foreground">
                No staff members found
              </div>
            )}
          </div>

          {/* Table for desktop */}
          <div className="hidden md:block bg-card border border-border rounded-lg overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-muted border-b border-border">
                  <tr>
                    <th className="px-4 lg:px-6 py-3 text-left text-sm font-semibold text-foreground">
                      Name
                    </th>
                    <th className="px-4 lg:px-6 py-3 text-left text-sm font-semibold text-foreground">
                      Email
                    </th>
                    <th className="hidden lg:table-cell px-4 lg:px-6 py-3 text-left text-sm font-semibold text-foreground">
                      Phone
                    </th>
                    <th className="hidden lg:table-cell px-4 lg:px-6 py-3 text-left text-sm font-semibold text-foreground">
                      Payment
                    </th>
                    <th className="hidden xl:table-cell px-4 lg:px-6 py-3 text-left text-sm font-semibold text-foreground">
                      Specialties
                    </th>
                    <th className="px-4 lg:px-6 py-3 text-left text-sm font-semibold text-foreground">
                      Status
                    </th>
                    <th className="px-4 lg:px-6 py-3 text-left text-sm font-semibold text-foreground">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {filteredStaff.length > 0 ? (
                    filteredStaff.map((member: Staff) => (
                      <tr
                        key={member.id}
                        className="hover:bg-muted/50 transition cursor-pointer"
                        onClick={() => navigate(`/staff/${member.id}`)}
                      >
                        <td className="px-4 lg:px-6 py-4 text-sm text-foreground">
                          <div className="flex items-center gap-3">
                            {member.profile_image_url && (
                              <img
                                src={member.profile_image_url}
                                alt={`${member.firstName} ${member.lastName}`}
                                className="w-10 h-10 rounded-lg object-cover border border-border flex-shrink-0"
                              />
                            )}
                            <p className="font-medium">
                              {member.firstName} {member.lastName}
                            </p>
                          </div>
                        </td>
                        <td className="px-4 lg:px-6 py-4 text-sm text-muted-foreground">
                          {member.email}
                        </td>
                        <td className="hidden lg:table-cell px-4 lg:px-6 py-4 text-sm text-muted-foreground">
                          {member.phone || "N/A"}
                        </td>
                        <td className="hidden lg:table-cell px-4 lg:px-6 py-4 text-sm text-foreground">
                          {member.payment_type === "commission"
                            ? `${member.payment_rate}% commission`
                            : `₦${member.payment_rate.toLocaleString()} / ${member.payment_type}`}
                        </td>
                        <td className="hidden xl:table-cell px-4 lg:px-6 py-4 text-sm">
                          <div className="flex flex-wrap gap-1">
                            {member.specialties.length > 0 ? (
                              member.specialties.map(
                                (spec: string, idx: number) => (
                                  <Badge
                                    key={idx}
                                    variant="outline"
                                    className="text-xs"
                                  >
                                    {spec}
                                  </Badge>
                                ),
                              )
                            ) : (
                              <span className="text-muted-foreground">N/A</span>
                            )}
                          </div>
                        </td>
                        <td className="px-4 lg:px-6 py-4 text-sm">
                          <Badge variant={getStatusBadgeVariant(member.status)}>
                            {getStatusLabel(member.status)}
                          </Badge>
                        </td>
                        <td className="px-4 lg:px-6 py-4 text-sm">
                          <div className="flex items-center gap-1">
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                navigate(`/staff/${member.id}`);
                              }}
                              className="p-2 hover:bg-muted rounded-lg transition cursor-pointer"
                            >
                              <EditIcon
                                size={16}
                                className="text-muted-foreground"
                              />
                            </button>
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                handleDeleteClick(
                                  member.id,
                                  `${member.firstName} ${member.lastName}`,
                                );
                              }}
                              className="p-2 hover:bg-destructive/10 rounded-lg transition cursor-pointer"
                            >
                              <TrashIcon
                                size={16}
                                className="text-destructive"
                              />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td
                        colSpan={7}
                        className="px-4 lg:px-6 py-8 text-center text-muted-foreground"
                      >
                        No staff members found
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}

      {/* Delete Confirmation Modal */}
      <ConfirmationModal
        isOpen={deleteConfirm.isOpen}
        onClose={() => setDeleteConfirm({ isOpen: false })}
        onConfirm={handleConfirmDelete}
        title="Delete Staff Member"
        description={`Are you sure you want to delete ${deleteConfirm.staffName}? This action cannot be undone.`}
        confirmText="Delete"
        cancelText="Cancel"
        variant="destructive"
        isLoading={deleteStaffMutation.isPending}
      />

      {/* Add Staff Modal */}
      <AddStaffModal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        onSubmit={async (data) => {
          try {
            await createStaffMutation.mutateAsync(data);
            showToast({
              variant: "success",
              title: "Success",
              description: `${data.firstName} ${data.lastName} has been added successfully`,
            });
          } catch (error) {
            showToast({
              variant: "error",
              title: "Error",
              description:
                error instanceof Error
                  ? error.message
                  : "Failed to add staff member",
            });
            throw error;
          }
        }}
        isLoading={createStaffMutation.isPending}
      />
    </div>
  );
}
