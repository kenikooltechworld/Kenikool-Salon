import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { useToast } from "@/components/ui/toast";
import {
  useLocations,
  useCreateLocation,
  useUpdateLocation,
  useDeleteLocation,
  type Location,
} from "@/hooks/useLocations";
import { PlusIcon, EditIcon, TrashIcon } from "@/components/icons";

export default function LocationsSettings() {
  const { data: locations = [], isLoading } = useLocations({ isActive: true });
  const createLocation = useCreateLocation();
  const updateLocation = useUpdateLocation();
  const deleteLocation = useDeleteLocation();
  const { showToast } = useToast();

  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingLocation, setEditingLocation] = useState<Location | null>(null);
  const [name, setName] = useState("");
  const [address, setAddress] = useState("");
  const [phone, setPhone] = useState("");
  const [email, setEmail] = useState("");
  const [timezone, setTimezone] = useState("");

  const resetForm = () => {
    setName("");
    setAddress("");
    setPhone("");
    setEmail("");
    setTimezone("");
    setEditingLocation(null);
    setIsFormOpen(false);
  };

  const handleEdit = (location: Location) => {
    setEditingLocation(location);
    setName(location.name);
    setAddress(location.address || "");
    setPhone(location.phone || "");
    setEmail(location.email || "");
    setTimezone(location.timezone || "");
    setIsFormOpen(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      showToast({
        title: "Error",
        description: "Location name is required",
        variant: "error",
      });
      return;
    }

    const input = {
      name: name.trim(),
      address: address.trim() || undefined,
      phone: phone.trim() || undefined,
      email: email.trim() || undefined,
      timezone: timezone.trim() || undefined,
      isActive: true,
    };

    try {
      if (editingLocation) {
        await updateLocation.mutateAsync({ id: editingLocation.id, input });
        showToast({
          title: "Success",
          description: "Location updated successfully",
          variant: "success",
        });
      } else {
        await createLocation.mutateAsync(input);
        showToast({
          title: "Success",
          description: "Location created successfully",
          variant: "success",
        });
      }
      resetForm();
    } catch (error: any) {
      showToast({
        title: "Error",
        description: error?.response?.data?.detail || "Failed to save location",
        variant: "error",
      });
    }
  };

  const handleDelete = async (location: Location) => {
    if (!confirm(`Deactivate location "${location.name}"?`)) return;
    try {
      await deleteLocation.mutateAsync(location.id);
      showToast({
        title: "Success",
        description: "Location deactivated",
        variant: "success",
      });
    } catch (error: any) {
      showToast({
        title: "Error",
        description: error?.response?.data?.detail || "Failed to deactivate location",
        variant: "error",
      });
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-foreground">Locations</h2>
          <p className="text-sm text-muted-foreground mt-1">
            Manage salon locations for bookings and resources
          </p>
        </div>
        {!isFormOpen && (
          <Button onClick={() => setIsFormOpen(true)} className="gap-2 cursor-pointer">
            <PlusIcon size={18} />
            Add Location
          </Button>
        )}
      </div>

      {isFormOpen && (
        <form
          onSubmit={handleSubmit}
          className="bg-card border border-border rounded-lg p-4 md:p-6 space-y-4"
        >
          <h3 className="text-lg font-semibold text-foreground">
            {editingLocation ? "Edit Location" : "New Location"}
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                Name *
              </label>
              <Input
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Main Salon"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                Address
              </label>
              <Input
                value={address}
                onChange={(e) => setAddress(e.target.value)}
                placeholder="123 Main Street"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                Phone
              </label>
              <Input
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="+234 801 234 5678"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                Email
              </label>
              <Input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="location@salon.com"
              />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-foreground mb-2">
                Timezone
              </label>
              <select
                value={timezone}
                onChange={(e) => setTimezone(e.target.value)}
                className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
              >
                <option value="">Select timezone</option>
                <option value="Africa/Lagos">Africa/Lagos (WAT)</option>
                <option value="Africa/Johannesburg">Africa/Johannesburg (SAST)</option>
                <option value="Africa/Cairo">Africa/Cairo (EET)</option>
                <option value="Africa/Nairobi">Africa/Nairobi (EAT)</option>
                <option value="Africa/Accra">Africa/Accra (GMT)</option>
                <option value="UTC">UTC</option>
              </select>
            </div>
          </div>
          <div className="flex gap-3 pt-2">
            <Button
              type="submit"
              disabled={createLocation.isPending || updateLocation.isPending}
              className="cursor-pointer"
            >
              {editingLocation ? "Update" : "Create"} Location
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={resetForm}
              className="cursor-pointer"
            >
              Cancel
            </Button>
          </div>
        </form>
      )}

      <div className="bg-card border border-border rounded-lg overflow-hidden">
        {isLoading ? (
          <div className="p-4 space-y-3">
            {[...Array(3)].map((_, i) => (
              <Skeleton key={i} className="h-16 w-full" />
            ))}
          </div>
        ) : locations.length === 0 ? (
          <div className="p-8 text-center text-sm text-muted-foreground">
            No locations configured. Add your first location above.
          </div>
        ) : (
          <div className="divide-y divide-border">
            {locations.map((location) => (
              <div
                key={location.id}
                className="flex items-center justify-between p-4 hover:bg-muted/50 transition-colors"
              >
                <div className="flex-1">
                  <p className="font-medium text-foreground">{location.name}</p>
                  <p className="text-xs text-muted-foreground mt-1">
                    {location.address || "No address"} • {location.phone || "No phone"} •{" "}
                    {location.email || "No email"}
                  </p>
                </div>
                <div className="flex gap-2 ml-4">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleEdit(location)}
                    className="cursor-pointer"
                  >
                    <EditIcon size={16} />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDelete(location)}
                    disabled={deleteLocation.isPending}
                    className="cursor-pointer"
                  >
                    <TrashIcon size={16} />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
