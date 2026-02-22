import { useState, useEffect } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  useGetReceiptTemplate,
  useSaveReceiptTemplate,
} from "@/lib/api/hooks/usePOS";
import { toast } from "sonner";
import {
  ImageIcon,
  MessageSquareIcon,
  ShareIcon,
  QrCodeIcon,
  EyeIcon,
} from "@/components/icons";

interface ReceiptCustomizationModalProps {
  open: boolean;
  onClose: () => void;
}

export function ReceiptCustomizationModal({
  open,
  onClose,
}: ReceiptCustomizationModalProps) {
  const { data: template } = useGetReceiptTemplate();
  const saveTemplate = useSaveReceiptTemplate();

  const [showLogo, setShowLogo] = useState(true);
  const [logoUrl, setLogoUrl] = useState("");
  const [headerText, setHeaderText] = useState("Thank you for your business!");
  const [footerText, setFooterText] = useState("Please visit us again");
  const [showSocialMedia, setShowSocialMedia] = useState(true);
  const [facebook, setFacebook] = useState("");
  const [instagram, setInstagram] = useState("");
  const [twitter, setTwitter] = useState("");
  const [showQrCode, setShowQrCode] = useState(true);
  const [promotionalMessage, setPromotionalMessage] = useState("");
  const [showLoyaltyInfo, setShowLoyaltyInfo] = useState(true);
  const [showPreview, setShowPreview] = useState(false);

  // Load template data
  useEffect(() => {
    if (template) {
      setShowLogo(template.show_logo);
      setLogoUrl(template.logo_url || "");
      setHeaderText(template.header_text);
      setFooterText(template.footer_text);
      setShowSocialMedia(template.show_social_media);
      setFacebook(template.social_media.facebook || "");
      setInstagram(template.social_media.instagram || "");
      setTwitter(template.social_media.twitter || "");
      setShowQrCode(template.show_qr_code);
      setPromotionalMessage(template.promotional_message || "");
      setShowLoyaltyInfo(template.show_loyalty_info);
    }
  }, [template]);

  const handleSave = async () => {
    try {
      await saveTemplate.mutateAsync({
        show_logo: showLogo,
        logo_url: logoUrl || undefined,
        header_text: headerText,
        footer_text: footerText,
        show_social_media: showSocialMedia,
        social_media: {
          facebook: facebook || undefined,
          instagram: instagram || undefined,
          twitter: twitter || undefined,
        },
        show_qr_code: showQrCode,
        promotional_message: promotionalMessage || undefined,
        show_loyalty_info: showLoyaltyInfo,
      });

      toast.success("Receipt template saved successfully!");
      onClose();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Failed to save template");
    }
  };

  const renderPreview = () => (
    <div className="border rounded-lg p-6 bg-white text-black max-w-sm mx-auto">
      {/* Logo */}
      {showLogo && logoUrl && (
        <div className="text-center mb-4">
          <img src={logoUrl} alt="Logo" className="h-16 mx-auto" />
        </div>
      )}

      {/* Header */}
      <div className="text-center mb-4">
        <h3 className="font-bold text-lg">Your Salon Name</h3>
        <p className="text-sm text-gray-600">{headerText}</p>
      </div>

      {/* Transaction Details */}
      <div className="border-t border-b py-3 my-3 space-y-1">
        <div className="flex justify-between text-sm">
          <span>Haircut</span>
          <span>$50.00</span>
        </div>
        <div className="flex justify-between text-sm">
          <span>Hair Color</span>
          <span>$120.00</span>
        </div>
        <div className="flex justify-between text-sm font-bold mt-2 pt-2 border-t">
          <span>Total</span>
          <span>$170.00</span>
        </div>
      </div>

      {/* Loyalty Info */}
      {showLoyaltyInfo && (
        <div className="bg-blue-50 p-2 rounded text-sm text-center my-3">
          <p className="font-medium">You earned 170 points!</p>
          <p className="text-xs text-gray-600">Total balance: 500 points</p>
        </div>
      )}

      {/* Promotional Message */}
      {promotionalMessage && (
        <div className="bg-yellow-50 p-2 rounded text-sm text-center my-3">
          <p>{promotionalMessage}</p>
        </div>
      )}

      {/* QR Code */}
      {showQrCode && (
        <div className="text-center my-3">
          <div className="inline-block p-2 bg-gray-100 rounded">
            <QrCodeIcon className="h-16 w-16" />
          </div>
          <p className="text-xs text-gray-600 mt-1">Scan to leave a review</p>
        </div>
      )}

      {/* Social Media */}
      {showSocialMedia && (facebook || instagram || twitter) && (
        <div className="text-center my-3">
          <p className="text-xs font-medium mb-1">Follow us:</p>
          <div className="flex justify-center gap-2 text-xs">
            {facebook && <span>Facebook: {facebook}</span>}
            {instagram && <span>Instagram: @{instagram}</span>}
            {twitter && <span>Twitter: @{twitter}</span>}
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="text-center mt-4 pt-3 border-t">
        <p className="text-sm">{footerText}</p>
      </div>
    </div>
  );

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Customize Receipt Template</DialogTitle>
        </DialogHeader>

        <Tabs defaultValue="branding" className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="branding">
              <ImageIcon className="h-4 w-4 mr-2" />
              Branding
            </TabsTrigger>
            <TabsTrigger value="messages">
              <MessageSquareIcon className="h-4 w-4 mr-2" />
              Messages
            </TabsTrigger>
            <TabsTrigger value="social">
              <ShareIcon className="h-4 w-4 mr-2" />
              Social
            </TabsTrigger>
            <TabsTrigger value="preview">
              <EyeIcon className="h-4 w-4 mr-2" />
              Preview
            </TabsTrigger>
          </TabsList>

          <TabsContent value="branding" className="space-y-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label>Show Logo</Label>
                <Switch checked={showLogo} onCheckedChange={setShowLogo} />
              </div>
            </div>

            {showLogo && (
              <div className="space-y-2">
                <Label>Logo URL</Label>
                <Input
                  value={logoUrl}
                  onChange={(e) => setLogoUrl(e.target.value)}
                  placeholder="https://example.com/logo.png"
                />
                <p className="text-xs text-muted-foreground">
                  Upload your logo and paste the URL here
                </p>
              </div>
            )}

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label>Show QR Code</Label>
                <Switch checked={showQrCode} onCheckedChange={setShowQrCode} />
              </div>
              <p className="text-xs text-muted-foreground">
                QR code links to review/feedback page
              </p>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label>Show Loyalty Points Info</Label>
                <Switch
                  checked={showLoyaltyInfo}
                  onCheckedChange={setShowLoyaltyInfo}
                />
              </div>
            </div>
          </TabsContent>

          <TabsContent value="messages" className="space-y-4">
            <div className="space-y-2">
              <Label>Header Text</Label>
              <Input
                value={headerText}
                onChange={(e) => setHeaderText(e.target.value)}
                placeholder="Thank you for your business!"
              />
            </div>

            <div className="space-y-2">
              <Label>Footer Text</Label>
              <Input
                value={footerText}
                onChange={(e) => setFooterText(e.target.value)}
                placeholder="Please visit us again"
              />
            </div>

            <div className="space-y-2">
              <Label>Promotional Message (Optional)</Label>
              <Textarea
                value={promotionalMessage}
                onChange={(e) => setPromotionalMessage(e.target.value)}
                placeholder="Get 20% off your next visit! Show this receipt."
                rows={3}
              />
              <p className="text-xs text-muted-foreground">
                Add special offers or promotions
              </p>
            </div>
          </TabsContent>

          <TabsContent value="social" className="space-y-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label>Show Social Media Links</Label>
                <Switch
                  checked={showSocialMedia}
                  onCheckedChange={setShowSocialMedia}
                />
              </div>
            </div>

            {showSocialMedia && (
              <>
                <div className="space-y-2">
                  <Label>Facebook Page</Label>
                  <Input
                    value={facebook}
                    onChange={(e) => setFacebook(e.target.value)}
                    placeholder="YourSalonPage"
                  />
                </div>

                <div className="space-y-2">
                  <Label>Instagram Handle</Label>
                  <div className="flex items-center gap-2">
                    <span className="text-muted-foreground">@</span>
                    <Input
                      value={instagram}
                      onChange={(e) => setInstagram(e.target.value)}
                      placeholder="yoursalon"
                      className="flex-1"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label>Twitter Handle</Label>
                  <div className="flex items-center gap-2">
                    <span className="text-muted-foreground">@</span>
                    <Input
                      value={twitter}
                      onChange={(e) => setTwitter(e.target.value)}
                      placeholder="yoursalon"
                      className="flex-1"
                    />
                  </div>
                </div>
              </>
            )}
          </TabsContent>

          <TabsContent value="preview">
            <div className="py-4">
              <h3 className="text-lg font-medium mb-4 text-center">
                Receipt Preview
              </h3>
              {renderPreview()}
              <p className="text-xs text-muted-foreground text-center mt-4">
                This is a preview. Actual receipts will include real transaction
                data.
              </p>
            </div>
          </TabsContent>
        </Tabs>

        <div className="flex gap-2 pt-4">
          <Button variant="outline" onClick={onClose} className="flex-1">
            Cancel
          </Button>
          <Button
            onClick={handleSave}
            disabled={saveTemplate.isPending}
            className="flex-1"
          >
            {saveTemplate.isPending ? "Saving..." : "Save Template"}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
