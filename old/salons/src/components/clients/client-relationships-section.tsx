import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import {
  AlertTriangleIcon,
  LinkIcon,
  TrashIcon,
  UsersIcon,
} from "@/components/icons";
import {
  useGetClientRelationships,
  useGetClientReferrals,
} from "@/lib/api/hooks/useClients";
import { useState } from "react";
import { LinkClientModal } from "./link-client-modal";

interface ClientRelationshipsSectionProps {
  clientId: string;
}

export function ClientRelationshipsSection({
  clientId,
}: ClientRelationshipsSectionProps) {
  const {
    data: relationships,
    isLoading: relationshipsLoading,
    error: relationshipsError,
  } = useGetClientRelationships(clientId);
  const { data: referrals, isLoading: referralsLoading } =
    useGetClientReferrals(clientId);
  const [showLinkModal, setShowLinkModal] = useState(false);

  if (relationshipsLoading || referralsLoading) {
    return (
      <Card className="p-6">
        <div className="flex justify-center py-8">
          <Spinner />
        </div>
      </Card>
    );
  }

  if (relationshipsError || !relationships) {
    return (
      <Card className="p-6">
        <Alert variant="error">
          <AlertTriangleIcon size={20} />
          <div>
            <h3 className="font-semibold">Error loading relationships</h3>
            <p className="text-sm">
              {relationshipsError?.message || "Relationships not available"}
            </p>
          </div>
        </Alert>
      </Card>
    );
  }

  const getRelationshipColor = (type: string) => {
    switch (type) {
      case "family":
        return "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200";
      case "friend":
        return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200";
      case "referral":
        return "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200";
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200";
    }
  };

  const handleUnlink = async (relatedClientId: string) => {
    if (confirm("Are you sure you want to unlink this client?")) {
      try {
        await unlinkClient.mutateAsync(relatedClientId);
      } catch (error) {
        console.error("Failed to unlink client:", error);
      }
    }
  };

  return (
    <div className="space-y-6">
      {/* Linked Clients */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold text-foreground">
            Linked Clients
          </h2>
          <Button
            onClick={() => setShowLinkModal(true)}
            variant="outline"
            size="sm"
          >
            <LinkIcon size={16} className="mr-2" />
            Link Client
          </Button>
        </div>

        {relationships.relationships &&
        relationships.relationships.length > 0 ? (
          <div className="space-y-3">
            {relationships.relationships.map((rel) => (
              <div
                key={rel.id}
                className="p-4 border border-border rounded-lg flex items-center justify-between hover:bg-muted/50 transition"
              >
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <p className="font-medium text-foreground">
                      {rel.related_client_name}
                    </p>
                    <span
                      className={`px-2 py-1 text-xs font-medium rounded-full ${getRelationshipColor(
                        rel.relationship_type,
                      )}`}
                    >
                      {rel.relationship_type}
                    </span>
                  </div>
                  {rel.notes && (
                    <p className="text-sm text-muted-foreground">{rel.notes}</p>
                  )}
                  <p className="text-xs text-muted-foreground mt-1">
                    Linked {new Date(rel.created_at).toLocaleDateString()}
                  </p>
                </div>
                <button
                  onClick={() => handleUnlink(rel.related_client_id)}
                  disabled={unlinkClient.isPending}
                  className="p-2 text-muted-foreground hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-950 rounded transition"
                >
                  <TrashIcon size={18} />
                </button>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <UsersIcon
              size={32}
              className="mx-auto text-muted-foreground mb-2"
            />
            <p className="text-muted-foreground">No linked clients</p>
            <p className="text-sm text-muted-foreground">
              Link clients to track family, friends, or referral relationships
            </p>
          </div>
        )}
      </Card>

      {/* Referral Information */}
      {referrals && referrals.total_referral_value !== undefined && (
        <Card className="p-6">
          <h2 className="text-lg font-semibold text-foreground mb-6">
            Referral Information
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            {/* Total Referral Value */}
            <div className="p-4 bg-muted/50 rounded-lg">
              <p className="text-sm text-muted-foreground mb-2">
                Total Referral Value
              </p>
              <p className="text-2xl font-bold text-foreground">
                ₦{(referrals.total_referral_value || 0).toLocaleString()}
              </p>
            </div>

            {/* Referred Clients Count */}
            <div className="p-4 bg-muted/50 rounded-lg">
              <p className="text-sm text-muted-foreground mb-2">
                Referred Clients
              </p>
              <p className="text-2xl font-bold text-foreground">
                {(referrals.referred_clients || []).length}
              </p>
            </div>
          </div>

          {/* Referred Clients List */}
          {referrals.referred_clients &&
          referrals.referred_clients.length > 0 ? (
            <div>
              <h3 className="text-sm font-semibold text-foreground mb-3">
                Clients Referred by {referrals.referrer_name}
              </h3>
              <div className="space-y-2">
                {referrals.referred_clients.map((client) => (
                  <div
                    key={client.id}
                    className="p-3 bg-muted/30 rounded-lg flex items-center justify-between"
                  >
                    <p className="font-medium text-foreground">{client.name}</p>
                    <p className="text-sm font-semibold text-primary">
                      ₦{(client.referral_value || 0).toLocaleString()}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="text-center py-8">
              <p className="text-muted-foreground">No referrals yet</p>
              <p className="text-sm text-muted-foreground">
                Referral value will be tracked when referred clients make
                purchases
              </p>
            </div>
          )}
        </Card>
      )}

      {/* Link Client Modal */}
      {showLinkModal && (
        <LinkClientModal
          isOpen={showLinkModal}
          clientId={clientId}
          onClose={() => setShowLinkModal(false)}
        />
      )}
    </div>
  );
}
