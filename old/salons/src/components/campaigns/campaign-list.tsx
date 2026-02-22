import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  TagIcon,
  MailIcon,
  CalendarIcon,
  UsersIcon,
  EditIcon,
  TrashIcon,
  CheckCircleIcon,
} from "@/components/icons";
import { Campaign } from "@/lib/api/hooks/useCampaigns";
import { format } from "date-fns";

interface CampaignListProps {
  campaigns: Campaign[];
  onEdit: (campaign: Campaign) => void;
  onDelete: (id: string) => void;
  onSend: (id: string) => void;
  onViewAnalytics: (id: string) => void;
}

const STATUS_COLORS = {
  draft: "bg-gray-100 text-gray-800",
  scheduled: "bg-blue-100 text-blue-800",
  sent: "bg-green-100 text-green-800",
  cancelled: "bg-red-100 text-red-800",
};

const TYPE_LABELS = {
  birthday: "Birthday",
  seasonal: "Seasonal",
  custom: "Custom",
  win_back: "Win Back",
};

export function CampaignList({
  campaigns,
  onEdit,
  onDelete,
  onSend,
  onViewAnalytics,
}: CampaignListProps) {
  if (campaigns.length === 0) {
    return (
      <Card className="p-12 text-center">
        <TagIcon size={48} className="mx-auto text-muted-foreground mb-4" />
        <h3 className="text-lg font-semibold text-foreground mb-2">
          No campaigns yet
        </h3>
        <p className="text-muted-foreground">
          Create your first marketing campaign to engage with clients
        </p>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {campaigns.map((campaign) => (
        <Card
          key={campaign.id}
          className="p-6 hover:shadow-md transition-shadow"
        >
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <h3 className="text-lg font-semibold text-foreground">
                  {campaign.name}
                </h3>
                <Badge className={STATUS_COLORS[campaign.status]}>
                  {campaign.status}
                </Badge>
                <Badge variant="outline">
                  {TYPE_LABELS[campaign.campaign_type]}
                </Badge>
              </div>

              <p className="text-sm text-muted-foreground mb-4 line-clamp-2">
                {campaign.message_template}
              </p>

              <div className="flex items-center gap-6 text-sm text-muted-foreground">
                {campaign.scheduled_at && (
                  <div className="flex items-center gap-2">
                    <CalendarIcon size={16} />
                    <span>
                      {format(new Date(campaign.scheduled_at), "MMM d, yyyy")}
                    </span>
                  </div>
                )}

                {campaign.recipients_count !== undefined && (
                  <div className="flex items-center gap-2">
                    <UsersIcon size={16} />
                    <span>{campaign.recipients_count} recipients</span>
                  </div>
                )}

                {campaign.delivered_count !== undefined && (
                  <div className="flex items-center gap-2">
                    <CheckCircleIcon size={16} />
                    <span>{campaign.delivered_count} delivered</span>
                  </div>
                )}

                {campaign.discount_code && (
                  <div className="flex items-center gap-2">
                    <TagIcon size={16} />
                    <span>{campaign.discount_code}</span>
                  </div>
                )}
              </div>
            </div>

            <div className="flex items-center gap-2 ml-4">
              {campaign.status === "sent" && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onViewAnalytics(campaign.id)}
                >
                  <MailIcon size={16} />
                  Analytics
                </Button>
              )}

              {campaign.status === "draft" && (
                <>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => onEdit(campaign)}
                  >
                    <EditIcon size={16} />
                  </Button>
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={() => onSend(campaign.id)}
                  >
                    Send Now
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onDelete(campaign.id)}
                  >
                    <TrashIcon size={16} />
                  </Button>
                </>
              )}

              {campaign.status === "scheduled" && (
                <>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => onEdit(campaign)}
                  >
                    <EditIcon size={16} />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onDelete(campaign.id)}
                  >
                    <TrashIcon size={16} />
                  </Button>
                </>
              )}
            </div>
          </div>
        </Card>
      ))}
    </div>
  );
}
