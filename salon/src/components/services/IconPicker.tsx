import { useState } from "react";
import { ChevronDownIcon } from "@/components/icons";
import {
  ScissorsIcon,
  SparklesIcon,
  HeartIcon,
  StarIcon,
  MoonIcon,
  SunIcon,
  EyeIcon,
  GiftIcon,
  TagIcon,
  CreditCardIcon,
  PercentIcon,
  AlertCircleIcon,
  InfoIcon,
  FilterIcon,
  BuildingIcon,
  TrendingUpIcon,
  TrendingDownIcon,
  EditIcon,
  ListIcon,
  TrophyIcon,
  LightbulbIcon,
  MonitorIcon,
  ShoppingCartIcon,
  PrinterIcon,
  ShareIcon,
  ReceiptIcon,
  ArchiveIcon,
  RefreshIcon,
  CopyIcon,
  ShieldIcon,
  MessageSquareIcon,
  FileTextIcon,
  SendIcon,
  ActivityIcon,
  CakeIcon,
  WifiIcon,
  ChairIcon,
  CoffeeIcon,
  HistoryIcon,
  PlayIcon,
  LinkIcon,
  ShoppingBagIcon,
  TicketIcon,
  ThumbsUpIcon,
  WalletIcon,
  BankIcon,
  ScanIcon,
  ServiceIcon,
} from "@/components/icons";

const SALON_SPA_GYM_ICONS = [
  { name: "Scissors", icon: ScissorsIcon, category: "Hair" },
  { name: "Sparkles", icon: SparklesIcon, category: "Beauty" },
  { name: "Heart", icon: HeartIcon, category: "Wellness" },
  { name: "Star", icon: StarIcon, category: "Premium" },
  { name: "Moon", icon: MoonIcon, category: "Relaxation" },
  { name: "Sun", icon: SunIcon, category: "Energy" },
  { name: "Eye", icon: EyeIcon, category: "Facial" },
  { name: "Gift", icon: GiftIcon, category: "Packages" },
  { name: "Tag", icon: TagIcon, category: "Deals" },
  { name: "CreditCard", icon: CreditCardIcon, category: "Payment" },
  { name: "Percent", icon: PercentIcon, category: "Discount" },
  { name: "AlertCircle", icon: AlertCircleIcon, category: "Alert" },
  { name: "Info", icon: InfoIcon, category: "Info" },
  { name: "Filter", icon: FilterIcon, category: "Filter" },
  { name: "Building", icon: BuildingIcon, category: "Facility" },
  { name: "TrendingUp", icon: TrendingUpIcon, category: "Growth" },
  { name: "TrendingDown", icon: TrendingDownIcon, category: "Decline" },
  { name: "Edit", icon: EditIcon, category: "Edit" },
  { name: "List", icon: ListIcon, category: "List" },
  { name: "Trophy", icon: TrophyIcon, category: "Achievement" },
  { name: "Lightbulb", icon: LightbulbIcon, category: "Idea" },
  { name: "Monitor", icon: MonitorIcon, category: "Digital" },
  { name: "ShoppingCart", icon: ShoppingCartIcon, category: "Shop" },
  { name: "Printer", icon: PrinterIcon, category: "Print" },
  { name: "Share", icon: ShareIcon, category: "Share" },
  { name: "Receipt", icon: ReceiptIcon, category: "Invoice" },
  { name: "Archive", icon: ArchiveIcon, category: "Archive" },
  { name: "Refresh", icon: RefreshIcon, category: "Refresh" },
  { name: "Copy", icon: CopyIcon, category: "Copy" },
  { name: "Shield", icon: ShieldIcon, category: "Security" },
  { name: "MessageSquare", icon: MessageSquareIcon, category: "Chat" },
  { name: "FileText", icon: FileTextIcon, category: "Document" },
  { name: "Send", icon: SendIcon, category: "Send" },
  { name: "Activity", icon: ActivityIcon, category: "Fitness" },
  { name: "Cake", icon: CakeIcon, category: "Celebration" },
  { name: "Wifi", icon: WifiIcon, category: "Connection" },
  { name: "Chair", icon: ChairIcon, category: "Furniture" },
  { name: "Coffee", icon: CoffeeIcon, category: "Beverage" },
  { name: "History", icon: HistoryIcon, category: "History" },
  { name: "Play", icon: PlayIcon, category: "Media" },
  { name: "Link", icon: LinkIcon, category: "Link" },
  { name: "ShoppingBag", icon: ShoppingBagIcon, category: "Retail" },
  { name: "Ticket", icon: TicketIcon, category: "Ticket" },
  { name: "ThumbsUp", icon: ThumbsUpIcon, category: "Feedback" },
  { name: "Wallet", icon: WalletIcon, category: "Payment" },
  { name: "Bank", icon: BankIcon, category: "Finance" },
  { name: "Scan", icon: ScanIcon, category: "Scan" },
  { name: "Service", icon: ServiceIcon, category: "Service" },
];

interface IconPickerProps {
  value: string;
  onChange: (iconName: string) => void;
}

export function IconPicker({ value, onChange }: IconPickerProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");

  const selectedIcon = SALON_SPA_GYM_ICONS.find((i) => i.name === value);
  const SelectedIconComponent = selectedIcon?.icon;

  const filteredIcons = SALON_SPA_GYM_ICONS.filter(
    (icon) =>
      icon.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      icon.category.toLowerCase().includes(searchTerm.toLowerCase()),
  );

  return (
    <div className="relative w-full">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary appearance-none cursor-pointer flex items-center justify-between"
      >
        <div className="flex items-center gap-2">
          {SelectedIconComponent && (
            <SelectedIconComponent size={18} className="text-primary" />
          )}
          <span className="text-sm">{selectedIcon?.name || "Select icon"}</span>
        </div>
        <ChevronDownIcon
          size={16}
          className={`text-muted-foreground transition-transform ${
            isOpen ? "rotate-180" : ""
          }`}
        />
      </button>

      {isOpen && (
        <div className="absolute top-full left-0 right-0 mt-1 bg-background border border-border rounded-lg shadow-lg z-50 max-h-64 overflow-hidden flex flex-col">
          <input
            type="text"
            placeholder="Search icons..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="px-3 py-2 border-b border-border bg-background text-foreground placeholder-muted-foreground focus:outline-none"
          />
          <div className="overflow-y-auto flex-1">
            <div className="grid grid-cols-4 gap-1 p-2">
              {filteredIcons.map(({ name, icon: IconComponent, category }) => (
                <button
                  key={name}
                  type="button"
                  onClick={() => {
                    onChange(name);
                    setIsOpen(false);
                    setSearchTerm("");
                  }}
                  className={`flex flex-col items-center gap-1 p-2 rounded-lg transition-colors ${
                    value === name
                      ? "bg-primary/20 border border-primary"
                      : "hover:bg-muted border border-transparent"
                  }`}
                  title={`${name} (${category})`}
                >
                  <IconComponent size={20} className="text-foreground" />
                  <span className="text-xs text-center text-foreground line-clamp-1">
                    {name}
                  </span>
                </button>
              ))}
            </div>
            {filteredIcons.length === 0 && (
              <div className="p-4 text-center text-sm text-muted-foreground">
                No icons found
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
