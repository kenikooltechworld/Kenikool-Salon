import { useState } from "react";
import {
  useInstallIntegration,
  useUpdateInstallation,
  useUninstallIntegration,
  useTestIntegration,
  type Integration,
  type IntegrationInstallationCreate,
} from "@/lib/api/hooks/useIntergrations";
import {
  Modal,
  ModalHeader,
  ModalTitle,
  ModalBody,
  ModalFooter,
  ModalDescription,
} from "@/components/ui/modal";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";
import {
  CheckIcon,
  XIcon,
  SettingsIcon,
  ExternalLinkIcon,
  PackageIcon,
} from "@/components/icons";
import { showToast } from "@/lib/utils/toast";

interface IntegrationCardProps {
  integration: Integration;
  onInstall: (integration: Integration) => void;
  onConfigure: (integration: Integration) => void;
}

export function IntegrationCard({
  integration,
  onInstall,
  onConfigure,
}: IntegrationCardProps) {
  const uninstallMutation = useUninstallIntegration();
  const testMutation = useTestIntegration();

  const handleUninstall = async () => {
    if (!confirm(`Uninstall ${integration.name}?`)) return;

    try {
      await uninstallMutation.mutateAsync(integration._id);
      showToast("Integration uninstalled successfully", "success");
    } catch (error) {
      const err = error as { response?: { data?: { detail?: string } } };
      showToast(
        err.response?.data?.detail || "Failed to uninstall integration",
        "error"
      );
    }
  };

  const handleTest = async () => {
    try {
      const result = await testMutation.mutateAsync(integration._id);
      if (result.success) {
        showToast(result.message, "success");
      } else {
        showToast(result.message, "error");
      }
    } catch (error) {
      const err = error as { response?: { data?: { detail?: string } } };
      showToast(
        err.response?.data?.detail || "Failed to test integration",
        "error"
      );
    }
  };

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      payment: "bg-green-500",
      marketing: "bg-blue-500",
      accounting: "bg-purple-500",
      communication: "bg-yellow-500",
      analytics: "bg-pink-500",
      scheduling: "bg-indigo-500",
      inventory: "bg-orange-500",
      other: "bg-gray-500",
    };
    return colors[category] || colors.other;
  };

  return (
    <Card hover>
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            {integration.icon_url ? (
              <img
                src={integration.icon_url}
                alt={integration.name}
                className="w-12 h-12 rounded-lg"
              />
            ) : (
              <div className="w-12 h-12 rounded-lg bg-(--muted) flex items-center justify-center">
                <PackageIcon size={24} />
              </div>
            )}
            <div>
              <CardTitle className="text-lg">{integration.name}</CardTitle>
              <div className="flex items-center gap-2 mt-1">
                <Badge
                  variant="outline"
                  className={`${getCategoryColor(
                    integration.category
                  )} text-white border-0`}
                >
                  {integration.category}
                </Badge>
                {integration.is_premium && (
                  <Badge variant="accent">Premium</Badge>
                )}
                {integration.is_installed && (
                  <Badge variant="default">
                    <CheckIcon size={12} />
                    Installed
                  </Badge>
                )}
              </div>
            </div>
          </div>
        </div>
      </CardHeader>

      <CardContent>
        <CardDescription className="mb-4">
          {integration.description}
        </CardDescription>

        {integration.features.length > 0 && (
          <div className="space-y-2">
            <p className="text-sm font-medium">Features:</p>
            <ul className="space-y-1">
              {integration.features.slice(0, 3).map((feature, index) => (
                <li
                  key={index}
                  className="text-sm text-(--muted-foreground) flex items-start gap-2"
                >
                  <CheckIcon
                    size={16}
                    className="mt-0.5 text-green-500 shrink-0"
                  />
                  <span>{feature}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {integration.pricing && (
          <div className="mt-4 p-3 bg-(--muted) rounded-lg">
            <p className="text-sm">
              <span className="font-medium">Pricing:</span>{" "}
              {integration.pricing}
            </p>
          </div>
        )}

        {integration.installation?.status === "error" && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-600">
              {integration.installation.error_message}
            </p>
          </div>
        )}
      </CardContent>

      <CardFooter className="flex gap-2">
        {!integration.is_installed ? (
          <Button onClick={() => onInstall(integration)} className="flex-1">
            Install
          </Button>
        ) : (
          <>
            <Button
              variant="outline"
              onClick={() => onConfigure(integration)}
              className="flex-1"
            >
              <SettingsIcon size={16} />
              Configure
            </Button>
            <Button
              variant="outline"
              onClick={handleTest}
              disabled={testMutation.isPending}
            >
              {testMutation.isPending ? <Spinner size="sm" /> : "Test"}
            </Button>
            <Button
              variant="ghost"
              onClick={handleUninstall}
              disabled={uninstallMutation.isPending}
            >
              <XIcon size={16} />
            </Button>
          </>
        )}
        {integration.documentation_url && (
          <Button
            variant="ghost"
            onClick={() => window.open(integration.documentation_url, "_blank")}
          >
            <ExternalLinkIcon size={16} />
          </Button>
        )}
      </CardFooter>
    </Card>
  );
}

interface IntegrationInstallModalProps {
  isOpen: boolean;
  onClose: () => void;
  integration: Integration | null;
}

export function IntegrationInstallModal({
  isOpen,
  onClose,
  integration,
}: IntegrationInstallModalProps) {
  const installMutation = useInstallIntegration();
  const [configuration, setConfiguration] = useState<Record<string, string>>(
    {}
  );

  if (!integration) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      const data: IntegrationInstallationCreate = {
        integration_id: integration._id,
        configuration,
        is_active: true,
      };

      await installMutation.mutateAsync(data);
      showToast("Integration installed successfully", "success");
      onClose();
      setConfiguration({});
    } catch (error) {
      const err = error as { response?: { data?: { detail?: string } } };
      showToast(
        err.response?.data?.detail || "Failed to install integration",
        "error"
      );
    }
  };

  return (
    <Modal open={isOpen} onClose={onClose} size="lg">
      <form onSubmit={handleSubmit}>
        <ModalHeader>
          <ModalTitle>Install {integration.name}</ModalTitle>
          <ModalDescription>{integration.description}</ModalDescription>
        </ModalHeader>

        <ModalBody className="space-y-4">
          {integration.required_fields.length > 0 ? (
            <>
              <p className="text-sm text-(--muted-foreground)">
                Please provide the following configuration details:
              </p>
              {integration.required_fields.map((field) => (
                <div key={field}>
                  <label className="block text-sm font-medium mb-2">
                    {field
                      .replace(/_/g, " ")
                      .replace(/\b\w/g, (l) => l.toUpperCase())}
                    <span className="text-red-500">*</span>
                  </label>
                  <Input
                    value={configuration[field] || ""}
                    onChange={(e) =>
                      setConfiguration({
                        ...configuration,
                        [field]: e.target.value,
                      })
                    }
                    placeholder={`Enter ${field}`}
                    type={
                      field.includes("secret") || field.includes("password")
                        ? "password"
                        : "text"
                    }
                    required
                  />
                </div>
              ))}
            </>
          ) : (
            <p className="text-sm text-(--muted-foreground)">
              This integration doesn't require any configuration. Click install
              to proceed.
            </p>
          )}

          {integration.documentation_url && (
            <div className="p-4 bg-(--muted) rounded-lg">
              <p className="text-sm mb-2">Need help with configuration?</p>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() =>
                  window.open(integration.documentation_url, "_blank")
                }
              >
                <ExternalLinkIcon size={16} />
                View Documentation
              </Button>
            </div>
          )}
        </ModalBody>

        <ModalFooter>
          <Button type="button" variant="ghost" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" disabled={installMutation.isPending}>
            {installMutation.isPending ? <Spinner size="sm" /> : "Install"}
          </Button>
        </ModalFooter>
      </form>
    </Modal>
  );
}

interface IntegrationConfigureModalProps {
  isOpen: boolean;
  onClose: () => void;
  integration: Integration | null;
}

export function IntegrationConfigureModal({
  isOpen,
  onClose,
  integration,
}: IntegrationConfigureModalProps) {
  const updateMutation = useUpdateInstallation();
  const [configuration, setConfiguration] = useState<Record<string, string>>(
    integration?.installation?.configuration || {}
  );
  const [isActive, setIsActive] = useState(
    integration?.installation?.is_active ?? true
  );

  if (!integration || !integration.installation) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      await updateMutation.mutateAsync({
        integrationId: integration._id,
        data: { configuration, is_active: isActive },
      });
      showToast("Integration updated successfully", "success");
      onClose();
    } catch (error) {
      const err = error as { response?: { data?: { detail?: string } } };
      showToast(
        err.response?.data?.detail || "Failed to update integration",
        "error"
      );
    }
  };

  return (
    <Modal open={isOpen} onClose={onClose} size="lg">
      <form onSubmit={handleSubmit}>
        <ModalHeader>
          <ModalTitle>Configure {integration.name}</ModalTitle>
          <ModalDescription>Update integration settings</ModalDescription>
        </ModalHeader>

        <ModalBody className="space-y-4">
          {integration.required_fields.map((field) => (
            <div key={field}>
              <label className="block text-sm font-medium mb-2">
                {field
                  .replace(/_/g, " ")
                  .replace(/\b\w/g, (l) => l.toUpperCase())}
              </label>
              <Input
                value={configuration[field] || ""}
                onChange={(e) =>
                  setConfiguration({
                    ...configuration,
                    [field]: e.target.value,
                  })
                }
                placeholder={`Enter ${field}`}
                type={
                  field.includes("secret") || field.includes("password")
                    ? "password"
                    : "text"
                }
              />
            </div>
          ))}

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="is_active"
              checked={isActive}
              onChange={(e) => setIsActive(e.target.checked)}
              className="w-4 h-4"
            />
            <label htmlFor="is_active" className="text-sm font-medium">
              Active
            </label>
          </div>

          {integration.installation.last_sync && (
            <div className="p-3 bg-(--muted) rounded-lg">
              <p className="text-sm text-(--muted-foreground)">
                Last synced:{" "}
                {new Date(integration.installation.last_sync).toLocaleString()}
              </p>
            </div>
          )}
        </ModalBody>

        <ModalFooter>
          <Button type="button" variant="ghost" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" disabled={updateMutation.isPending}>
            {updateMutation.isPending ? <Spinner size="sm" /> : "Update"}
          </Button>
        </ModalFooter>
      </form>
    </Modal>
  );
}
