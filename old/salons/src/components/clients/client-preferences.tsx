import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { X } from "@/components/icons";
import { useToast } from "@/hooks/use-toast";
import { useUpdateClientPreferences } from "@/lib/api/hooks/useClients";
import { useStylists } from "@/lib/api/hooks/useStylists";
import { useServices } from "@/lib/api/hooks/useServices";
import { useInventory } from "@/lib/api/hooks/useInventory";

interface ClientPreferencesProps {
  clientId: string;
  preferences?: {
    preferred_stylist_id?: string;
    preferred_services?: string[];
    preferred_products?: string[];
    communication_channel?: string;
    appointment_reminders?: boolean;
    marketing_consent?: boolean;
  };
  onUpdate: () => void;
}

export function ClientPreferences({
  clientId,
  preferences,
  onUpdate,
}: ClientPreferencesProps) {
  const { toast } = useToast();
  const updatePreferences = useUpdateClientPreferences(clientId, {
    onSuccess: () => {
      toast("Client preferences updated successfully", "success");
      onUpdate();
    },
    onError: () => {
      toast("Failed to update preferences", "error");
    },
  });

  // Fetch available stylists, services, and products
  const { data: stylistsData } = useStylists();
  const { data: servicesData } = useServices();
  const { data: productsData } = useInventory();

  const stylists = Array.isArray(stylistsData) ? stylistsData : [];
  const services = Array.isArray(servicesData) ? servicesData : [];
  const products = Array.isArray(productsData) ? productsData : [];

  const [preferredStylistId, setPreferredStylistId] = useState<string>(
    preferences?.preferred_stylist_id || ""
  );
  const [preferredServices, setPreferredServices] = useState<string[]>(
    preferences?.preferred_services || []
  );
  const [preferredProducts, setPreferredProducts] = useState<string[]>(
    preferences?.preferred_products || []
  );
  const [communicationChannel, setCommunicationChannel] = useState<string>(
    preferences?.communication_channel || "sms"
  );
  const [appointmentReminders, setAppointmentReminders] = useState<boolean>(
    preferences?.appointment_reminders ?? true
  );
  const [marketingConsent, setMarketingConsent] = useState<boolean>(
    preferences?.marketing_consent ?? false
  );

  const [selectedService, setSelectedService] = useState<string>("");
  const [selectedProduct, setSelectedProduct] = useState<string>("");

  const handleAddService = (serviceId: string) => {
    if (serviceId && !preferredServices.includes(serviceId)) {
      setPreferredServices([...preferredServices, serviceId]);
      setSelectedService("");
    }
  };

  const handleRemoveService = (serviceId: string) => {
    setPreferredServices(preferredServices.filter((s) => s !== serviceId));
  };

  const handleAddProduct = (productId: string) => {
    if (productId && !preferredProducts.includes(productId)) {
      setPreferredProducts([...preferredProducts, productId]);
      setSelectedProduct("");
    }
  };

  const handleRemoveProduct = (productId: string) => {
    setPreferredProducts(preferredProducts.filter((p) => p !== productId));
  };

  const getServiceName = (serviceId: string) => {
    const service = services.find((s) => s.id === serviceId);
    return service?.name || serviceId;
  };

  const getProductName = (productId: string) => {
    const product = products.find((p) => p.id === productId);
    return product?.name || productId;
  };

  const getStylistName = (stylistId: string) => {
    const stylist = stylists.find((s) => s.id === stylistId);
    return stylist?.name || stylistId;
  };

  const handleSave = () => {
    updatePreferences.mutate({
      preferred_stylist_id: preferredStylistId || undefined,
      preferred_services: preferredServices,
      preferred_products: preferredProducts,
      communication_channel: communicationChannel,
      appointment_reminders: appointmentReminders,
      marketing_consent: marketingConsent,
    });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Client Preferences</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Preferred Stylist */}
        <div className="space-y-2">
          <Label htmlFor="stylist">Preferred Stylist</Label>
          <Select
            value={preferredStylistId}
            onValueChange={setPreferredStylistId}
          >
            <SelectTrigger id="stylist">
              <SelectValue>
                {preferredStylistId
                  ? getStylistName(preferredStylistId)
                  : "Select a stylist"}
              </SelectValue>
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">None</SelectItem>
              {stylists.map((stylist) => (
                <SelectItem key={stylist.id} value={stylist.id}>
                  {stylist.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          {preferredStylistId && (
            <p className="text-sm text-muted-foreground">
              Selected: {getStylistName(preferredStylistId)}
            </p>
          )}
        </div>

        {/* Preferred Services */}
        <div className="space-y-2">
          <Label>Preferred Services</Label>
          <Select value={selectedService} onValueChange={handleAddService}>
            <SelectTrigger>
              <SelectValue>
                {selectedService
                  ? "Select another service"
                  : "Select services to add"}
              </SelectValue>
            </SelectTrigger>
            <SelectContent>
              {services
                .filter((service) => !preferredServices.includes(service.id))
                .map((service) => (
                  <SelectItem key={service.id} value={service.id}>
                    {service.name}
                  </SelectItem>
                ))}
            </SelectContent>
          </Select>
          <div className="flex flex-wrap gap-2 mt-2">
            {preferredServices.map((serviceId) => (
              <Badge key={serviceId} variant="secondary">
                {getServiceName(serviceId)}
                <button
                  onClick={() => handleRemoveService(serviceId)}
                  className="ml-2 hover:text-destructive"
                >
                  <X className="h-3 w-3" />
                </button>
              </Badge>
            ))}
          </div>
        </div>

        {/* Preferred Products */}
        <div className="space-y-2">
          <Label>Preferred Products</Label>
          <Select value={selectedProduct} onValueChange={handleAddProduct}>
            <SelectTrigger>
              <SelectValue>
                {selectedProduct
                  ? "Select another product"
                  : "Select products to add"}
              </SelectValue>
            </SelectTrigger>
            <SelectContent>
              {products
                .filter((product) => !preferredProducts.includes(product.id))
                .map((product) => (
                  <SelectItem key={product.id} value={product.id}>
                    {product.name}
                  </SelectItem>
                ))}
            </SelectContent>
          </Select>
          <div className="flex flex-wrap gap-2 mt-2">
            {preferredProducts.map((productId) => (
              <Badge key={productId} variant="secondary">
                {getProductName(productId)}
                <button
                  onClick={() => handleRemoveProduct(productId)}
                  className="ml-2 hover:text-destructive"
                >
                  <X className="h-3 w-3" />
                </button>
              </Badge>
            ))}
          </div>
        </div>

        {/* Communication Channel */}
        <div className="space-y-2">
          <Label htmlFor="channel">Preferred Communication Channel</Label>
          <Select
            value={communicationChannel}
            onValueChange={setCommunicationChannel}
          >
            <SelectTrigger id="channel">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="sms">SMS</SelectItem>
              <SelectItem value="email">Email</SelectItem>
              <SelectItem value="whatsapp">WhatsApp</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Appointment Reminders */}
        <div className="flex items-center justify-between">
          <Label htmlFor="reminders">Appointment Reminders</Label>
          <Switch
            id="reminders"
            checked={appointmentReminders}
            onCheckedChange={setAppointmentReminders}
          />
        </div>

        {/* Marketing Consent */}
        <div className="flex items-center justify-between">
          <Label htmlFor="marketing">Marketing Consent</Label>
          <Switch
            id="marketing"
            checked={marketingConsent}
            onCheckedChange={setMarketingConsent}
          />
        </div>

        <Button
          onClick={handleSave}
          disabled={updatePreferences.isPending}
          className="w-full"
        >
          {updatePreferences.isPending ? "Saving..." : "Save Preferences"}
        </Button>
      </CardContent>
    </Card>
  );
}
