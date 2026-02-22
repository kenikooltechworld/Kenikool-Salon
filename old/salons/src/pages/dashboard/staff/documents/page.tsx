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
  FileIcon,
} from "@/components/icons";
import { useStylists } from "@/lib/api/hooks/useStylists";
import { Stylist } from "@/lib/api/types";

const DocumentList = lazy(() =>
  import("@/components/staff").then((mod) => ({
    default: mod.DocumentList,
  })),
);
const DocumentUploadModal = lazy(() =>
  import("@/components/staff").then((mod) => ({
    default: mod.DocumentUploadModal,
  })),
);

export default function DocumentsPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [selectedStylist, setSelectedStylist] = useState<Stylist>();

  const { data: stylists = [], isLoading, error, refetch } = useStylists();

  const stylistsArray = Array.isArray(stylists) ? stylists : [];
  const filteredStylists = stylistsArray.filter((stylist: Stylist) =>
    stylist.name?.toLowerCase().includes(searchQuery.toLowerCase()),
  );

  const handleOpenUploadModal = (stylist: Stylist) => {
    setSelectedStylist(stylist);
    setIsUploadModalOpen(true);
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
            Staff Documents
          </h1>
          <p className="text-muted-foreground">
            Manage staff documents and certifications
          </p>
        </div>
      </div>

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
            <FileIcon
              size={48}
              className="mx-auto text-muted-foreground mb-4"
            />
            <h3 className="text-lg font-semibold text-foreground mb-2">
              No staff members found
            </h3>
          </div>
        </Card>
      ) : (
        <div className="space-y-4">
          {filteredStylists.map((stylist: Stylist) => (
            <Card key={stylist.id} className="p-4">
              <div className="flex items-center justify-between mb-4">
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
                  onClick={() => handleOpenUploadModal(stylist)}
                >
                  <PlusIcon size={16} />
                  Upload Document
                </Button>
              </div>

              <Suspense fallback={<Spinner />}>
                <DocumentList staffId={stylist.id} />
              </Suspense>
            </Card>
          ))}
        </div>
      )}

      {selectedStylist && (
        <Suspense fallback={null}>
          <DocumentUploadModal
            isOpen={isUploadModalOpen}
            onClose={() => {
              setIsUploadModalOpen(false);
              setSelectedStylist(undefined);
            }}
            staffId={selectedStylist.id}
            staffName={selectedStylist.name}
            onSuccess={refetch}
          />
        </Suspense>
      )}
    </div>
  );
}
