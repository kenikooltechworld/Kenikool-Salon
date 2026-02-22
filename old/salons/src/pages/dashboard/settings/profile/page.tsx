import { ProfilePictureUpload } from "@/components/settings/profile-picture-upload";
import { EmailChangeFlow } from "@/components/settings/email-change-flow";
import { PhoneVerificationFlow } from "@/components/settings/phone-verification-flow";

// TODO: Get current user data from auth context or API
const currentUser = {
  email: "user@example.com",
  phone: "",
  phoneVerified: false,
  profilePictureUrl: "",
};

export default function ProfileSettingsPage() {
  return (
    <div className="space-y-6 max-w-4xl">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-foreground">Profile Settings</h1>
        <p className="text-muted-foreground">
          Manage your profile information and contact details
        </p>
      </div>

      {/* Profile Picture */}
      <ProfilePictureUpload currentPictureUrl={currentUser.profilePictureUrl} />

      {/* Email */}
      <EmailChangeFlow currentEmail={currentUser.email} />

      {/* Phone */}
      <PhoneVerificationFlow
        isPhoneVerified={currentUser.phoneVerified}
        currentPhone={currentUser.phone}
      />
    </div>
  );
}
