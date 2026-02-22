import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface Client {
  id: string;
  name: string;
}

interface Stylist {
  id: string;
  name: string;
}

interface ClientStylistSelectorProps {
  clients: Client[];
  stylists: Stylist[];
  selectedClientId: string;
  selectedStylistId: string;
  onClientChange: (clientId: string) => void;
  onStylistChange: (stylistId: string) => void;
}

export function ClientStylistSelector({
  clients,
  stylists,
  selectedClientId,
  selectedStylistId,
  onClientChange,
  onStylistChange,
}: ClientStylistSelectorProps) {
  return (
    <div className="grid grid-cols-2 gap-4">
      <div>
        <Label>Client (Optional)</Label>
        <Select value={selectedClientId} onValueChange={onClientChange}>
          <SelectTrigger>
            <SelectValue>
              {selectedClientId
                ? clients.find((c) => c.id === selectedClientId)?.name
                : "Select client"}
            </SelectValue>
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="">Walk-in</SelectItem>
            {clients.map((client) => (
              <SelectItem key={client.id} value={client.id}>
                {client.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div>
        <Label>Stylist *</Label>
        <Select
          value={selectedStylistId}
          onValueChange={onStylistChange}
          required
        >
          <SelectTrigger className={!selectedStylistId ? "border-red-500" : ""}>
            <SelectValue placeholder="Select stylist (required)">
              {selectedStylistId
                ? stylists.find((s) => s.id === selectedStylistId)?.name
                : "Select stylist (required)"}
            </SelectValue>
          </SelectTrigger>
          <SelectContent>
            {stylists.map((stylist) => (
              <SelectItem key={stylist.id} value={stylist.id}>
                {stylist.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        {!selectedStylistId && (
          <p className="text-xs text-[var(--destructive)] mt-1">Stylist is required</p>
        )}
      </div>
    </div>
  );
}
