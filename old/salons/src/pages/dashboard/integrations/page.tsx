import { useState } from "react";
import { useGetIntegrations } from "@/lib/api/hooks/useIntergrations";
import {
  IntegrationCard,
  IntegrationInstallModal,
  IntegrationConfigureModal,
} from "@/components/intergrations";
import { PackageIcon, SearchIcon } from "@/components/icons";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Spinner } from "@/components/ui/spinner";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import type { Integration } from "@/lib/api/hooks/useIntergrations";

export default function IntegrationsPage() {
  const [selectedCategory, setSelectedCategory] = useState<string>("");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedIntegration, setSelectedIntegration] =
    useState<Integration | null>(null);
  const [isInstallModalOpen, setIsInstallModalOpen] = useState(false);
  const [isConfigureModalOpen, setIsConfigureModalOpen] = useState(false);

  const { data, isLoading } = useGetIntegrations(selectedCategory || undefined);

  const integrations = (Array.isArray(data) ? data : []) as Integration[];

  const filteredIntegrations = integrations.filter(
    (integration) =>
      integration.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      integration.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const installedIntegrations = filteredIntegrations.filter(
    (i) => i.is_installed
  );
  const availableIntegrations = filteredIntegrations.filter(
    (i) => !i.is_installed
  );

  const categories = [
    { value: "", label: "All Categories" },
    { value: "payment", label: "Payment" },
    { value: "marketing", label: "Marketing" },
    { value: "accounting", label: "Accounting" },
    { value: "communication", label: "Communication" },
    { value: "analytics", label: "Analytics" },
    { value: "scheduling", label: "Scheduling" },
    { value: "inventory", label: "Inventory" },
    { value: "other", label: "Other" },
  ];

  const handleInstall = (integration: Integration) => {
    setSelectedIntegration(integration);
    setIsInstallModalOpen(true);
  };

  const handleConfigure = (integration: Integration) => {
    setSelectedIntegration(integration);
    setIsConfigureModalOpen(true);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <PackageIcon size={32} className="text-(--primary)" />
            Integrations
          </h1>
          <p className="text-(--muted-foreground) mt-1">
            Connect your salon with powerful third-party tools
          </p>
        </div>
      </div>

      <div className="flex gap-4">
        <div className="flex-1 relative">
          <SearchIcon
            size={20}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-(--muted-foreground)"
          />
          <Input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search integrations..."
            className="pl-10"
          />
        </div>
        <Select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
        >
          {categories.map((category) => (
            <option key={category.value} value={category.value}>
              {category.label}
            </option>
          ))}
        </Select>
      </div>

      <Tabs defaultValue="all" className="space-y-6">
        <TabsList>
          <TabsTrigger value="all">
            All ({filteredIntegrations.length})
          </TabsTrigger>
          <TabsTrigger value="installed">
            Installed ({installedIntegrations.length})
          </TabsTrigger>
          <TabsTrigger value="available">
            Available ({availableIntegrations.length})
          </TabsTrigger>
        </TabsList>

        <TabsContent value="all" className="space-y-4">
          {filteredIntegrations.length === 0 ? (
            <div className="text-center py-12">
              <PackageIcon
                size={48}
                className="mx-auto text-(--muted-foreground) mb-4"
              />
              <h3 className="text-lg font-semibold mb-2">
                No integrations found
              </h3>
              <p className="text-(--muted-foreground)">
                Try adjusting your search or filters
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {filteredIntegrations.map((integration) => (
                <IntegrationCard
                  key={integration._id}
                  integration={integration}
                  onInstall={handleInstall}
                  onConfigure={handleConfigure}
                />
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="installed" className="space-y-4">
          {installedIntegrations.length === 0 ? (
            <div className="text-center py-12">
              <PackageIcon
                size={48}
                className="mx-auto text-(--muted-foreground) mb-4"
              />
              <h3 className="text-lg font-semibold mb-2">
                No installed integrations
              </h3>
              <p className="text-(--muted-foreground)">
                Browse available integrations to get started
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {installedIntegrations.map((integration) => (
                <IntegrationCard
                  key={integration._id}
                  integration={integration}
                  onInstall={handleInstall}
                  onConfigure={handleConfigure}
                />
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="available" className="space-y-4">
          {availableIntegrations.length === 0 ? (
            <div className="text-center py-12">
              <PackageIcon
                size={48}
                className="mx-auto text-(--muted-foreground) mb-4"
              />
              <h3 className="text-lg font-semibold mb-2">
                All integrations installed
              </h3>
              <p className="text-(--muted-foreground)">
                You've installed all available integrations
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {availableIntegrations.map((integration) => (
                <IntegrationCard
                  key={integration._id}
                  integration={integration}
                  onInstall={handleInstall}
                  onConfigure={handleConfigure}
                />
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>

      <IntegrationInstallModal
        isOpen={isInstallModalOpen}
        onClose={() => {
          setIsInstallModalOpen(false);
          setSelectedIntegration(null);
        }}
        integration={selectedIntegration}
      />

      <IntegrationConfigureModal
        isOpen={isConfigureModalOpen}
        onClose={() => {
          setIsConfigureModalOpen(false);
          setSelectedIntegration(null);
        }}
        integration={selectedIntegration}
      />
    </div>
  );
}
