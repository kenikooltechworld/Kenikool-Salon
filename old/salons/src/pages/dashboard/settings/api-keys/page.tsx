import { APIKeyList } from "@/components/settings/api-key-list";

export default function APIKeysPage() {
  return (
    <div className="space-y-6 max-w-4xl">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-foreground">API Keys</h1>
        <p className="text-muted-foreground">
          Create and manage API keys for external integrations
        </p>
      </div>

      {/* API Keys List */}
      <APIKeyList />
    </div>
  );
}
