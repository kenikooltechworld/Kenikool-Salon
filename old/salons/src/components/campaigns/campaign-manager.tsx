import { useState } from "react";
import {
  useGetCampaigns,
  useCreateCampaign,
  useSendCampaign,
  useDeleteCampaign,
} from "@/lib/api/hooks/useCampaigns";
import { useGetSMSBalance } from "@/lib/api/hooks/useSMSCredits";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import {
  AlertCircleIcon,
  CheckCircleIcon,
  SendIcon,
  TrashIcon,
  EditIcon,
} from "@/components/icons";
import { toast } from "sonner";
import { format } from "date-fns";

type CampaignType = "birthday" | "seasonal" | "custom" | "win_back";
type ChannelType = "sms" | "whatsapp" | "email";

export function CampaignManager() {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    campaign_type: "custom" as CampaignType,
    message_template: "",
    channels: [] as ChannelType[],
    target_segment: {},
    discount_code: "",
    discount_value: 0,
    auto_send: false,
  });

  const { data: campaigns, isLoading: campaignsLoading } = useGetCampaigns();
  const { data: smsBalance } = useGetSMSBalance();
  const createCampaign = useCreateCampaign();
  const sendCampaign = useSendCampaign();
  const deleteCampaign = useDeleteCampaign();

  const handleChannelToggle = (channel: ChannelType) => {
    setFormData((prev) => ({
      ...prev,
      channels: prev.channels.includes(channel)
        ? prev.channels.filter((c) => c !== channel)
        : [...prev.channels, channel],
    }));
  };

  const handleCreateCampaign = async () => {
    if (
      !formData.name ||
      !formData.message_template ||
      formData.channels.length === 0
    ) {
      toast.error("Please fill in all required fields");
      return;
    }

    try {
      await createCampaign.mutateAsync(formData);
      toast.success("Campaign created successfully");
      setShowCreateForm(false);
      setFormData({
        name: "",
        campaign_type: "custom",
        message_template: "",
        channels: [],
        target_segment: {},
        discount_code: "",
        discount_value: 0,
        auto_send: false,
      });
    } catch (error) {
      toast.error("Failed to create campaign");
    }
  };

  const handleSendCampaign = async (campaignId: string) => {
    try {
      await sendCampaign.mutateAsync(campaignId);
      toast.success("Campaign sent successfully");
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Failed to send campaign");
    }
  };

  const handleDeleteCampaign = async (campaignId: string) => {
    if (!confirm("Are you sure you want to delete this campaign?")) return;

    try {
      await deleteCampaign.mutateAsync(campaignId);
      toast.success("Campaign deleted successfully");
    } catch (error) {
      toast.error("Failed to delete campaign");
    }
  };

  return (
    <div className="space-y-6">
      {/* SMS Balance Alert */}
      {smsBalance &&
        smsBalance.current_balance < smsBalance.low_balance_threshold && (
          <Card className="border-yellow-200 bg-yellow-50">
            <CardContent className="pt-6 flex items-center gap-3">
              <AlertCircleIcon className="h-5 w-5 text-yellow-600" />
              <div>
                <p className="font-semibold text-yellow-900">Low SMS Credits</p>
                <p className="text-sm text-yellow-800">
                  You have {smsBalance.current_balance} SMS credits remaining.
                  Consider purchasing more.
                </p>
              </div>
            </CardContent>
          </Card>
        )}

      {/* Create Campaign Form */}
      {showCreateForm && (
        <Card>
          <CardHeader>
            <CardTitle>Create New Campaign</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium">Campaign Name</label>
              <Input
                placeholder="e.g., Birthday Special Offer"
                value={formData.name}
                onChange={(e) =>
                  setFormData({ ...formData, name: e.target.value })
                }
              />
            </div>

            <div>
              <label className="text-sm font-medium">Campaign Type</label>
              <Select
                value={formData.campaign_type}
                onValueChange={(value) =>
                  setFormData({
                    ...formData,
                    campaign_type: value as CampaignType,
                  })
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="birthday">Birthday</SelectItem>
                  <SelectItem value="seasonal">Seasonal</SelectItem>
                  <SelectItem value="custom">Custom</SelectItem>
                  <SelectItem value="win_back">Win Back</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <label className="text-sm font-medium">Message Template</label>
              <Textarea
                placeholder="Enter your message. Use {{client_name}}, {{salon_name}} for variables"
                value={formData.message_template}
                onChange={(e) =>
                  setFormData({ ...formData, message_template: e.target.value })
                }
                rows={4}
              />
            </div>

            <div>
              <label className="text-sm font-medium mb-2 block">Channels</label>
              <div className="space-y-2">
                {(["sms", "whatsapp", "email"] as ChannelType[]).map(
                  (channel) => (
                    <div key={channel} className="flex items-center gap-2">
                      <Checkbox
                        checked={formData.channels.includes(channel)}
                        onCheckedChange={() => handleChannelToggle(channel)}
                      />
                      <label className="text-sm capitalize">{channel}</label>
                    </div>
                  ),
                )}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium">
                  Discount Code (Optional)
                </label>
                <Input
                  placeholder="e.g., SAVE20"
                  value={formData.discount_code}
                  onChange={(e) =>
                    setFormData({ ...formData, discount_code: e.target.value })
                  }
                />
              </div>
              <div>
                <label className="text-sm font-medium">
                  Discount Value (Optional)
                </label>
                <Input
                  type="number"
                  placeholder="e.g., 20"
                  value={formData.discount_value}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      discount_value: parseFloat(e.target.value),
                    })
                  }
                />
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Checkbox
                checked={formData.auto_send}
                onCheckedChange={(checked) =>
                  setFormData({ ...formData, auto_send: checked as boolean })
                }
              />
              <label className="text-sm">Auto-send to matching clients</label>
            </div>

            <div className="flex gap-2">
              <Button
                onClick={handleCreateCampaign}
                disabled={createCampaign.isPending}
              >
                Create Campaign
              </Button>
              <Button
                variant="outline"
                onClick={() => setShowCreateForm(false)}
              >
                Cancel
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Create Campaign Button */}
      {!showCreateForm && (
        <Button onClick={() => setShowCreateForm(true)}>
          Create New Campaign
        </Button>
      )}

      {/* Campaigns List */}
      <div className="space-y-4">
        <h2 className="text-lg font-semibold">Your Campaigns</h2>

        {campaignsLoading ? (
          <p className="text-muted-foreground">Loading campaigns...</p>
        ) : campaigns && campaigns.length > 0 ? (
          <div className="grid gap-4">
            {campaigns.map((campaign) => (
              <Card key={campaign.id}>
                <CardContent className="pt-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h3 className="font-semibold">{campaign.name}</h3>
                        <span
                          className={`text-xs px-2 py-1 rounded ${
                            campaign.status === "sent"
                              ? "bg-green-100 text-green-800"
                              : campaign.status === "draft"
                                ? "bg-gray-100 text-gray-800"
                                : "bg-blue-100 text-blue-800"
                          }`}
                        >
                          {campaign.status}
                        </span>
                      </div>
                      <p className="text-sm text-muted-foreground mb-2">
                        {campaign.message_template}
                      </p>
                      <div className="flex gap-4 text-sm text-muted-foreground">
                        <span>Type: {campaign.campaign_type}</span>
                        <span>Channels: {campaign.channels.join(", ")}</span>
                        {campaign.sent_at && (
                          <span>
                            Sent:{" "}
                            {format(new Date(campaign.sent_at), "MMM dd, yyyy")}
                          </span>
                        )}
                      </div>
                      {campaign.status === "sent" && (
                        <div className="flex gap-4 text-sm mt-2">
                          <span className="flex items-center gap-1">
                            <CheckCircleIcon className="h-4 w-4 text-green-600" />
                            Delivered: {campaign.delivered_count}
                          </span>
                          {(campaign.failed_count ?? 0) > 0 && (
                            <span className="flex items-center gap-1">
                              <AlertCircleIcon className="h-4 w-4 text-red-600" />
                              Failed: {campaign.failed_count}
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                    <div className="flex gap-2">
                      {campaign.status === "draft" && (
                        <>
                          <Button
                            size="sm"
                            onClick={() => handleSendCampaign(campaign.id)}
                            disabled={sendCampaign.isPending}
                          >
                            <SendIcon className="h-4 w-4 mr-1" />
                            Send
                          </Button>
                          <Button size="sm" variant="outline">
                            <EditIcon className="h-4 w-4" />
                          </Button>
                        </>
                      )}
                      <Button
                        size="sm"
                        variant="destructive"
                        onClick={() => handleDeleteCampaign(campaign.id)}
                        disabled={deleteCampaign.isPending}
                      >
                        <TrashIcon className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : (
          <p className="text-muted-foreground">
            No campaigns yet. Create one to get started!
          </p>
        )}
      </div>
    </div>
  );
}
