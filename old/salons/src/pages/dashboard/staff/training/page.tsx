import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import { PlusIcon, SearchIcon, AlertTriangleIcon } from "@/components/icons";
import { useStylists } from "@/lib/api/hooks/useStylists";
import { Stylist } from "@/lib/api/types";
import {
  TrainingList,
  TrainingRecordModal,
  CertificationList,
  CertificationModal,
} from "@/components/staff";

const TrainingList = lazy(() =>
  import("@/components/staff").then((mod) => ({
    default: mod.TrainingList,
  })),
);
const TrainingRecordModal = lazy(() =>
  import("@/components/staff").then((mod) => ({
    default: mod.TrainingRecordModal,
  })),
);
const CertificationList = lazy(() =>
  import("@/components/staff").then((mod) => ({
    default: mod.CertificationList,
  })),
);
const CertificationModal = lazy(() =>
  import("@/components/staff").then((mod) => ({
    default: mod.CertificationModal,
  })),
);

export default function TrainingPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [isTrainingModalOpen, setIsTrainingModalOpen] = useState(false);
  const [isCertificationModalOpen, setIsCertificationModalOpen] =
    useState(false);
  const [selectedStylist, setSelectedStylist] = useState<Stylist>();
  const [activeTab, setActiveTab] = useState<"training" | "certifications">(
    "training",
  );

  const { data: stylists = [], isLoading, error, refetch } = useStylists();

  const stylistsArray = Array.isArray(stylists) ? stylists : [];
  const filteredStylists = stylistsArray.filter((stylist: Stylist) =>
    stylist.name?.toLowerCase().includes(searchQuery.toLowerCase()),
  );

  const handleOpenTrainingModal = (stylist: Stylist) => {
    setSelectedStylist(stylist);
    setIsTrainingModalOpen(true);
  };

  const handleOpenCertificationModal = (stylist: Stylist) => {
    setSelectedStylist(stylist);
    setIsCertificationModalOpen(true);
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
            Training & Certifications
          </h1>
          <p className="text-muted-foreground">
            Manage staff training records and certifications
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

      <div className="flex gap-2 border-b">
        <button
          onClick={() => setActiveTab("training")}
          className={`px-4 py-2 font-medium border-b-2 transition-colors ${
            activeTab === "training"
              ? "border-primary text-primary"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          <BookIcon size={16} className="inline mr-2" />
          Training Records
        </button>
        <button
          onClick={() => setActiveTab("certifications")}
          className={`px-4 py-2 font-medium border-b-2 transition-colors ${
            activeTab === "certifications"
              ? "border-primary text-primary"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          <AwardIcon size={16} className="inline mr-2" />
          Certifications
        </button>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-12">
          <Spinner />
        </div>
      ) : filteredStylists.length === 0 ? (
        <Card className="p-12">
          <div className="text-center">
            <BookIcon
              size={48}
              className="mx-auto text-muted-foreground mb-4"
            />
            <h3 className="text-lg font-semibold text-foreground mb-2">
              No staff members found
            </h3>
            <p className="text-muted-foreground">
              {searchQuery
                ? "Try adjusting your search"
                : "No staff members to manage"}
            </p>
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
                <div className="flex gap-2">
                  {activeTab === "training" && (
                    <Button
                      size="sm"
                      onClick={() => handleOpenTrainingModal(stylist)}
                    >
                      <PlusIcon size={16} />
                      Add Training
                    </Button>
                  )}
                  {activeTab === "certifications" && (
                    <Button
                      size="sm"
                      onClick={() => handleOpenCertificationModal(stylist)}
                    >
                      <PlusIcon size={16} />
                      Add Certification
                    </Button>
                  )}
                </div>
              </div>

              {activeTab === "training" && (
                <Suspense fallback={<Spinner />}>
                  <TrainingList staffId={stylist.id} />
                </Suspense>
              )}

              {activeTab === "certifications" && (
                <Suspense fallback={<Spinner />}>
                  <CertificationList staffId={stylist.id} />
                </Suspense>
              )}
            </Card>
          ))}
        </div>
      )}

      {selectedStylist && (
        <Suspense fallback={null}>
          <TrainingRecordModal
            isOpen={isTrainingModalOpen}
            onClose={() => {
              setIsTrainingModalOpen(false);
              setSelectedStylist(undefined);
            }}
            staffId={selectedStylist.id}
            staffName={selectedStylist.name}
            onSuccess={refetch}
          />
        </Suspense>
      )}

      {selectedStylist && (
        <Suspense fallback={null}>
          <CertificationModal
            isOpen={isCertificationModalOpen}
            onClose={() => {
              setIsCertificationModalOpen(false);
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
