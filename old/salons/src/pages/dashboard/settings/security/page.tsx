import { PasswordChangeForm } from "@/components/settings/password-change-form";
import { TwoFactorSetupWizard } from "@/components/settings/two-factor-setup-wizard";
import { ActiveSessionsList } from "@/components/settings/active-sessions-list";
import { SecurityScoreDashboard } from "@/components/settings/security-score-dashboard";
import { LoginActivityTimeline } from "@/components/settings/login-activity-timeline";

export default function SecuritySettingsPage() {
  return (
    <div className="space-y-6 max-w-4xl">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-foreground">
          Security Settings
        </h1>
        <p className="text-muted-foreground">
          Manage your password, authentication, and account security
        </p>
      </div>

      {/* Security Score */}
      <SecurityScoreDashboard />

      {/* Change Password */}
      <PasswordChangeForm />

      {/* Two-Factor Authentication */}
      <TwoFactorSetupWizard />

      {/* Active Sessions */}
      <ActiveSessionsList />

      {/* Login Activity */}
      <LoginActivityTimeline />
    </div>
  );
}
