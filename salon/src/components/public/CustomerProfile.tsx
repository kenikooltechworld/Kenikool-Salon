import { useState } from "react";
import {
  Card,
  Button,
  Input,
  Label,
  Alert,
  Spinner,
  Switch,
} from "@/components/ui";
import {
  useCustomerProfile,
  useUpdateCustomerProfile,
} from "@/hooks/useCustomerAuth";
import {
  UserIcon,
  MailIcon,
  PhoneIcon,
  MapPinIcon,
  CalendarIcon,
  BellIcon,
} from "@/components/icons";

export default function CustomerProfile() {
  const { data: profile, isLoading } = useCustomerProfile();
  const updateProfile = useUpdateCustomerProfile();

  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    first_name: "",
    last_name: "",
    phone: "",
    address: "",
    date_of_birth: "",
  });

  const [notificationPrefs, setNotificationPrefs] = useState<{
    email_reminders: boolean;
    sms_reminders: boolean;
    marketing_emails: boolean;
  }>({
    email_reminders: true,
    sms_reminders: true,
    marketing_emails: false,
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [successMessage, setSuccessMessage] = useState("");

  // Initialize form data when profile loads
  useState(() => {
    if (profile) {
      setFormData({
        first_name: profile.first_name || "",
        last_name: profile.last_name || "",
        phone: profile.phone || "",
        address: profile.address || "",
        date_of_birth: profile.date_of_birth || "",
      });
      setNotificationPrefs(
        profile.notification_preferences || notificationPrefs,
      );
    }
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  const handleNotificationChange = (key: string, value: boolean) => {
    setNotificationPrefs((prev) => ({ ...prev, [key]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSuccessMessage("");
    setErrors({});

    try {
      await updateProfile.mutateAsync({
        ...formData,
        notification_preferences: notificationPrefs,
      });

      setSuccessMessage("Profile updated successfully!");
      setIsEditing(false);

      // Clear success message after 3 seconds
      setTimeout(() => setSuccessMessage(""), 3000);
    } catch (error: any) {
      setErrors({
        submit:
          error.response?.data?.detail ||
          "Failed to update profile. Please try again.",
      });
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner />
      </div>
    );
  }

  if (!profile) {
    return (
      <Alert variant="error">Failed to load profile. Please try again.</Alert>
    );
  }

  return (
    <div className="space-y-6">
      {/* Profile Information Card */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold">Profile Information</h2>
          {!isEditing && (
            <Button onClick={() => setIsEditing(true)}>Edit Profile</Button>
          )}
        </div>

        {successMessage && (
          <Alert className="mb-6 bg-green-50 text-green-800 border-green-200">
            {successMessage}
          </Alert>
        )}

        {errors.submit && (
          <Alert variant="error" className="mb-6">
            {errors.submit}
          </Alert>
        )}

        {!isEditing ? (
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <UserIcon size={20} className="text-gray-400" />
              <div>
                <p className="text-sm text-gray-500">Name</p>
                <p className="font-medium">
                  {profile.first_name} {profile.last_name}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <MailIcon size={20} className="text-gray-400" />
              <div>
                <p className="text-sm text-gray-500">Email</p>
                <p className="font-medium">{profile.email}</p>
                {profile.email_verified && (
                  <span className="text-xs text-green-600">✓ Verified</span>
                )}
              </div>
            </div>

            <div className="flex items-center gap-3">
              <PhoneIcon size={20} className="text-gray-400" />
              <div>
                <p className="text-sm text-gray-500">Phone</p>
                <p className="font-medium">{profile.phone || "Not provided"}</p>
                {profile.phone_verified && (
                  <span className="text-xs text-green-600">✓ Verified</span>
                )}
              </div>
            </div>

            {profile.address && (
              <div className="flex items-center gap-3">
                <MapPinIcon size={20} className="text-gray-400" />
                <div>
                  <p className="text-sm text-gray-500">Address</p>
                  <p className="font-medium">{profile.address}</p>
                </div>
              </div>
            )}

            {profile.date_of_birth && (
              <div className="flex items-center gap-3">
                <CalendarIcon size={20} className="text-gray-400" />
                <div>
                  <p className="text-sm text-gray-500">Date of Birth</p>
                  <p className="font-medium">{profile.date_of_birth}</p>
                </div>
              </div>
            )}
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="first_name">First Name</Label>
                <Input
                  id="first_name"
                  name="first_name"
                  value={formData.first_name}
                  onChange={handleChange}
                />
              </div>

              <div>
                <Label htmlFor="last_name">Last Name</Label>
                <Input
                  id="last_name"
                  name="last_name"
                  value={formData.last_name}
                  onChange={handleChange}
                />
              </div>
            </div>

            <div>
              <Label htmlFor="phone">Phone Number</Label>
              <Input
                id="phone"
                name="phone"
                type="tel"
                value={formData.phone}
                onChange={handleChange}
              />
            </div>

            <div>
              <Label htmlFor="address">Address</Label>
              <Input
                id="address"
                name="address"
                value={formData.address}
                onChange={handleChange}
              />
            </div>

            <div>
              <Label htmlFor="date_of_birth">Date of Birth</Label>
              <Input
                id="date_of_birth"
                name="date_of_birth"
                type="date"
                value={formData.date_of_birth}
                onChange={handleChange}
              />
            </div>

            <div className="flex gap-2 pt-4">
              <Button type="submit" disabled={updateProfile.isPending}>
                {updateProfile.isPending ? (
                  <>
                    <Spinner className="mr-2" />
                    Saving...
                  </>
                ) : (
                  "Save Changes"
                )}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => setIsEditing(false)}
              >
                Cancel
              </Button>
            </div>
          </form>
        )}
      </Card>

      {/* Notification Preferences Card */}
      <Card className="p-6">
        <div className="flex items-center gap-2 mb-6">
          <BellIcon size={20} />
          <h2 className="text-xl font-bold">Notification Preferences</h2>
        </div>

        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Email Reminders</p>
              <p className="text-sm text-gray-500">
                Receive appointment reminders via email
              </p>
            </div>
            <Switch
              checked={notificationPrefs.email_reminders}
              onCheckedChange={(checked) =>
                handleNotificationChange("email_reminders", checked)
              }
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">SMS Reminders</p>
              <p className="text-sm text-gray-500">
                Receive appointment reminders via SMS
              </p>
            </div>
            <Switch
              checked={notificationPrefs.sms_reminders}
              onCheckedChange={(checked) =>
                handleNotificationChange("sms_reminders", checked)
              }
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Marketing Emails</p>
              <p className="text-sm text-gray-500">
                Receive promotional offers and updates
              </p>
            </div>
            <Switch
              checked={notificationPrefs.marketing_emails}
              onCheckedChange={(checked) =>
                handleNotificationChange("marketing_emails", checked)
              }
            />
          </div>
        </div>

        {isEditing && (
          <div className="mt-6 pt-6 border-t border-gray-200">
            <p className="text-sm text-gray-500">
              Notification preferences will be saved when you save your profile
              changes.
            </p>
          </div>
        )}
      </Card>

      {/* Account Status Card */}
      <Card className="p-6">
        <h2 className="text-xl font-bold mb-4">Account Status</h2>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm">Outstanding Balance</span>
            <span className="font-semibold">
              ${profile.outstanding_balance.toFixed(2)}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm">Member Since</span>
            <span className="font-medium">
              {new Date(profile.created_at).toLocaleDateString()}
            </span>
          </div>
        </div>
      </Card>
    </div>
  );
}
