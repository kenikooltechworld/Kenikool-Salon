import { useState, lazy, Suspense } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import {
  PlusIcon,
  SearchIcon,
  AlertTriangleIcon,
  MessageIcon,
  BellIcon,
} from "@/components/icons";
import { useStylists } from "@/lib/api/hooks/useStylists";
import { Stylist } from "@/lib/api/types";

const MessageBoard = lazy(() =>
  import("@/components/staff").then((mod) => ({
    default: mod.MessageBoard,
  })),
);
const DirectMessageModal = lazy(() =>
  import("@/components/staff").then((mod) => ({
    default: mod.DirectMessageModal,
  })),
);
const ShiftNotes = lazy(() =>
  import("@/components/staff").then((mod) => ({
    default: mod.ShiftNotes,
  })),
);

export default function CommunicationPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [isDirectMessageOpen, setIsDirectMessageOpen] = useState(false);
  const [selectedStylist, setSelectedStylist] = useState<Stylist>();
  const [activeTab, setActiveTab] = useState<
    "announcements" | "messages" | "shift-notes"
  >("announcements");

  const { data: stylists = [], isLoading, error, refetch } = useStylists();

  const stylistsArray = Array.isArray(stylists) ? stylists : [];
  const filteredStylists = stylistsArray.filter((stylist: Stylist) =>
    stylist.name?.toLowerCase().includes(searchQuery.toLowerCase()),
  );

  const handleOpenDirectMessage = (stylist: Stylist) => {
    setSelectedStylist(stylist);
    setIsDirectMessageOpen(true);
  };

  if (error) {
    return (
      <Alert variant="error">
        <AlertTriangleIcon size={20} />
        <div>
          <h3 className="font-semibold">Error loading staff</h3>
          <p className="text-sm">{error.message}</p>
        </div>
      </Alert>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">
            Staff Communication
          </h1>
          <p className="text-muted-foreground">
            Manage announcements, messages, and shift notes
          </p>
        </div>
      </div>

      <div className="flex gap-2 border-b">
        <button
          onClick={() => setActiveTab("announcements")}
          className={`px-4 py-2 font-medium border-b-2 transition-colors ${
            activeTab === "announcements"
              ? "border-primary text-primary"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          <BellIcon size={16} className="inline mr-2" />
          Announcements
        </button>
        <button
          onClick={() => setActiveTab("messages")}
          className={`px-4 py-2 font-medium border-b-2 transition-colors ${
            activeTab === "messages"
              ? "border-primary text-primary"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          <MessageIcon size={16} className="inline mr-2" />
          Direct Messages
        </button>
        <button
          onClick={() => setActiveTab("shift-notes")}
          className={`px-4 py-2 font-medium border-b-2 transition-colors ${
            activeTab === "shift-notes"
              ? "border-primary text-primary"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          <MessageIcon size={16} className="inline mr-2" />
          Shift Notes
        </button>
      </div>

      {activeTab === "announcements" && (
        <Suspense fallback={<Spinner />}>
          <MessageBoard />
        </Suspense>
      )}

      {activeTab === "messages" && (
        <div className="space-y-4">
          <Card className="p-4">
            <div className="relative">
              <SearchIcon
                size={20}
                className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
              />
              <Input
                placeholder="Search staff..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
          </Card>

          {isLoading ? (
            <div className="flex justify-center py-12">
              <Spinner />
            </div>
          ) : filteredStylists.length === 0 ? (
            <Card className="p-12">
              <div className="text-center">
                <MessageIcon
                  size={48}
                  className="mx-auto text-muted-foreground mb-4"
                />
                <h3 className="text-lg font-semibold text-foreground mb-2">
                  No staff members found
                </h3>
              </div>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {filteredStylists.map((stylist: Stylist) => (
                <Card key={stylist.id} className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-semibold text-foreground">
                        {stylist.name}
                      </h3>
                      <p className="text-sm text-muted-foreground">
                        {stylist.email}
                      </p>
                    </div>
                    <Button
                      size="sm"
                      onClick={() => handleOpenDirectMessage(stylist)}
                    >
                      <MessageIcon size={16} />
                      Message
                    </Button>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === "shift-notes" && (
        <Suspense fallback={<Spinner />}>
          <ShiftNotes />
        </Suspense>
      )}

      {selectedStylist && (
        <Suspense fallback={null}>
          <DirectMessageModal
            isOpen={isDirectMessageOpen}
            onClose={() => {
              setIsDirectMessageOpen(false);
              setSelectedStylist(undefined);
            }}
            recipientId={selectedStylist.id}
            recipientName={selectedStylist.name}
          />
        </Suspense>
      )}
    </div>
  );
}
