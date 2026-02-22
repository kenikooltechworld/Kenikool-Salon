import { useState } from "react";
import { useRegisterSalon } from "@/lib/api/hooks/useMarketplace";
import { BuildingIcon, CheckCircleIcon } from "@/components/icons";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Spinner } from "@/components/ui/spinner";
import { showToast } from "@/lib/utils/toast";
import { Link } from "react-router-dom";

export default function RegisterSalonPage() {
  const registerMutation = useRegisterSalon();
  const [formData, setFormData] = useState({
    salon_name: "",
    description: "",
    address: "",
    city: "",
    state: "",
    phone: "",
    email: "",
    website: "",
    owner_name: "",
    owner_phone: "",
    owner_email: "",
  });
  const [isSuccess, setIsSuccess] = useState(false);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      await registerMutation.mutateAsync(formData);
      setIsSuccess(true);
      showToast("Salon registered successfully!", "success");
    } catch (error: any) {
      showToast(
        error.response?.data?.detail || "Failed to register salon",
        "error"
      );
    }
  };

  if (isSuccess) {
    return (
      <div className="min-h-screen bg-[var(--background)] flex items-center justify-center p-4">
        <Card className="max-w-2xl w-full p-8 text-center">
          <CheckCircleIcon
            size={64}
            className="mx-auto text-[var(--success)] mb-4"
          />
          <h1 className="text-3xl font-bold mb-4">Registration Successful!</h1>
          <p className="text-[var(--muted-foreground)] mb-6">
            Your salon has been registered successfully. Check your email for
            verification instructions.
          </p>

          <div className="bg-[var(--muted)]/30 rounded-[var(--radius-md)] p-6 mb-6 text-left">
            <h3 className="font-semibold mb-3">Next Steps:</h3>
            <ol className="list-decimal list-inside space-y-2 text-sm">
              <li>Verify your email address</li>
              <li>Complete your salon profile</li>
              <li>Add services and staff members</li>
              <li>Upload photos of your salon</li>
              <li>Publish your salon to the directory</li>
            </ol>
          </div>

          <div className="flex gap-3 justify-center">
            <Link to="/salons">
              <Button variant="outline">Browse Salons</Button>
            </Link>
            <Link to="/dashboard">
              <Button>Go to Dashboard</Button>
            </Link>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[var(--background)]">
      {/* Header */}
      <div className="bg-[var(--primary)] text-white py-12">
        <div className="container mx-auto px-4">
          <h1 className="text-4xl font-bold mb-4 flex items-center gap-3">
            <BuildingIcon size={40} />
            Register Your Salon
          </h1>
          <p className="text-lg opacity-90">
            Join our platform and start accepting online bookings
          </p>
        </div>
      </div>

      {/* Form */}
      <div className="container mx-auto px-4 py-8">
        <Card className="max-w-3xl mx-auto p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Salon Information */}
            <div>
              <h2 className="text-xl font-semibold mb-4">Salon Information</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium mb-2">
                    Salon Name *
                  </label>
                  <Input
                    type="text"
                    name="salon_name"
                    value={formData.salon_name}
                    onChange={handleChange}
                    required
                    placeholder="Enter salon name"
                  />
                </div>

                <div className="md:col-span-2">
                  <label className="block text-sm font-medium mb-2">
                    Description
                  </label>
                  <textarea
                    name="description"
                    value={formData.description}
                    onChange={handleChange}
                    rows={4}
                    placeholder="Tell us about your salon..."
                    className="w-full px-3 py-2 border border-[var(--border)] rounded-[var(--radius-md)] bg-[var(--background)]"
                  />
                </div>

                <div className="md:col-span-2">
                  <label className="block text-sm font-medium mb-2">
                    Address *
                  </label>
                  <Input
                    type="text"
                    name="address"
                    value={formData.address}
                    onChange={handleChange}
                    required
                    placeholder="Street address"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">
                    City *
                  </label>
                  <Input
                    type="text"
                    name="city"
                    value={formData.city}
                    onChange={handleChange}
                    required
                    placeholder="City"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">
                    State *
                  </label>
                  <Input
                    type="text"
                    name="state"
                    value={formData.state}
                    onChange={handleChange}
                    required
                    placeholder="State"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">
                    Phone *
                  </label>
                  <Input
                    type="tel"
                    name="phone"
                    value={formData.phone}
                    onChange={handleChange}
                    required
                    placeholder="+234 XXX XXX XXXX"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">
                    Email *
                  </label>
                  <Input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    required
                    placeholder="salon@example.com"
                  />
                </div>

                <div className="md:col-span-2">
                  <label className="block text-sm font-medium mb-2">
                    Website
                  </label>
                  <Input
                    type="url"
                    name="website"
                    value={formData.website}
                    onChange={handleChange}
                    placeholder="https://www.yoursalon.com"
                  />
                </div>
              </div>
            </div>

            {/* Owner Information */}
            <div>
              <h2 className="text-xl font-semibold mb-4">Owner Information</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium mb-2">
                    Owner Name *
                  </label>
                  <Input
                    type="text"
                    name="owner_name"
                    value={formData.owner_name}
                    onChange={handleChange}
                    required
                    placeholder="Full name"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">
                    Owner Phone *
                  </label>
                  <Input
                    type="tel"
                    name="owner_phone"
                    value={formData.owner_phone}
                    onChange={handleChange}
                    required
                    placeholder="+234 XXX XXX XXXX"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">
                    Owner Email *
                  </label>
                  <Input
                    type="email"
                    name="owner_email"
                    value={formData.owner_email}
                    onChange={handleChange}
                    required
                    placeholder="owner@example.com"
                  />
                </div>
              </div>
            </div>

            {/* Submit */}
            <div className="flex gap-3 justify-end pt-4">
              <Link to="/salons">
                <Button type="button" variant="outline">
                  Cancel
                </Button>
              </Link>
              <Button type="submit" disabled={registerMutation.isPending}>
                {registerMutation.isPending ? (
                  <>
                    <Spinner size="sm" />
                    Registering...
                  </>
                ) : (
                  "Register Salon"
                )}
              </Button>
            </div>
          </form>
        </Card>
      </div>
    </div>
  );
}
