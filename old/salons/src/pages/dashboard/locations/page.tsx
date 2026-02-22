import { useState } from "react";
import {
  useGetLocations,
  useDeleteLocation,
  Location,
} from "@/lib/api/hooks/useLocations";
import { LocationList, LocationFormModal } from "@/components/locations";
import { PlusIcon, MapPinIcon } from "@/components/icons";
import { showToast } from "@/lib/utils/toast";

export default function LocationsPage() {
  const { data: locations, isLoading, refetch } = useGetLocations();
  const deleteMutation = useDeleteLocation();

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedLocation, setSelectedLocation] = useState<Location | null>(
    null,
  );
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const handleEdit = (location: Location) => {
    setSelectedLocation(location);
    setIsModalOpen(true);
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this location?")) return;

    setDeletingId(id);
    try {
      await deleteMutation.mutateAsync(id);
      showToast("Location deleted successfully", "success");
    } catch (error: any) {
      console.error("Delete error:", error);
      const errorMessage =
        error.response?.data?.detail ||
        error.message ||
        "Failed to delete location";
      showToast(errorMessage, "error");
    } finally {
      setDeletingId(null);
    }
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedLocation(null);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <MapPinIcon size={32} className="text-primary" />
            Locations
          </h1>
          <p className="text-muted-foreground mt-1">
            Manage your salon locations and business hours
          </p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-[var(--radius-md)] hover:bg-primary/90 transition-colors font-medium cursor-pointer"
        >
          <PlusIcon size={20} />
          Add Location
        </button>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-3">
        <div className="bg-card border border-border rounded-[var(--radius-lg)] p-6">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-primary/10 rounded-[var(--radius-md)]">
              <MapPinIcon size={20} className="text-primary" />
            </div>
            <h3 className="font-semibold text-muted-foreground">
              Total Locations
            </h3>
          </div>
          <p className="text-3xl font-bold">{locations?.length || 0}</p>
        </div>

        <div className="bg-card border border-border rounded-[var(--radius-lg)] p-6">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-green-500/10 rounded-[var(--radius-md)]">
              <MapPinIcon size={20} className="text-green-500" />
            </div>
            <h3 className="font-semibold text-muted-foreground">
              Active Locations
            </h3>
          </div>
          <p className="text-3xl font-bold">{locations?.length || 0}</p>
        </div>

        <div className="bg-card border border-border rounded-[var(--radius-lg)] p-6">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-blue-500/10 rounded-[var(--radius-md)]">
              <MapPinIcon size={20} className="text-blue-500" />
            </div>
            <h3 className="font-semibold text-muted-foreground">
              Primary Location
            </h3>
          </div>
          <p className="text-3xl font-bold">
            {locations?.filter((l) => l.is_primary).length || 0}
          </p>
        </div>
      </div>

      {/* Location List */}
      <div className="bg-card border border-border rounded-[var(--radius-lg)] p-6">
        <LocationList
          locations={locations || []}
          onEdit={handleEdit}
          onDelete={handleDelete}
          deletingId={deletingId}
        />
      </div>

      {/* Modal */}
      <LocationFormModal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        location={selectedLocation}
      />
    </div>
  );
}
