import { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import {
  PlusIcon,
  TrashIcon,
  AlertTriangleIcon,
  CheckCircleIcon,
  ScissorsIcon,
  SparklesIcon,
} from "@/components/icons";
import { apiClient } from "@/lib/api/client";
import { useNavigate } from "react-router-dom";

interface Recommendation {
  id: string;
  name: string;
  price: number;
  duration_minutes: number;
  category?: string;
  photo_url?: string;
  is_manual: boolean;
}

interface ServiceRecommendationsProps {
  serviceId: string;
  isEditing?: boolean;
}

export function ServiceRecommendations({
  serviceId,
  isEditing = false,
}: ServiceRecommendationsProps) {
  const navigate = useNavigate();
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isAddingMode, setIsAddingMode] = useState(false);
  const [availableServices, setAvailableServices] = useState<any[]>([]);
  const [selectedServiceId, setSelectedServiceId] = useState<string>("");

  useEffect(() => {
    loadRecommendations();
  }, [serviceId]);

  const loadRecommendations = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await apiClient.get(
        `/api/services/${serviceId}/recommendations`
      );
      setRecommendations(response.data);
    } catch (err) {
      console.error("Error loading recommendations:", err);
      setError("Failed to load recommendations");
    } finally {
      setIsLoading(false);
    }
  };

  const loadAvailableServices = async () => {
    try {
      const response = await apiClient.get("/api/services", {
        params: { is_active: true },
      });
      // Filter out current service and already recommended services
      const recommendedIds = recommendations.map((r) => r.id);
      const filtered = response.data.filter(
        (s: any) => s.id !== serviceId && !recommendedIds.includes(s.id)
      );
      setAvailableServices(filtered);
    } catch (err) {
      console.error("Error loading services:", err);
    }
  };

  const handleAddRecommendation = async () => {
    if (!selectedServiceId) return;

    try {
      await apiClient.post(`/api/services/${serviceId}/recommendations`, {
        recommended_service_id: selectedServiceId,
      });
      setIsAddingMode(false);
      setSelectedServiceId("");
      loadRecommendations();
    } catch (err) {
      console.error("Error adding recommendation:", err);
      setError("Failed to add recommendation");
    }
  };

  const handleRemoveRecommendation = async (recommendedServiceId: string) => {
    if (!confirm("Remove this recommendation?")) return;

    try {
      await apiClient.delete(
        `/api/services/${serviceId}/recommendations/${recommendedServiceId}`
      );
      loadRecommendations();
    } catch (err) {
      console.error("Error removing recommendation:", err);
      setError("Failed to remove recommendation");
    }
  };

  const handleServiceClick = (recommendationId: string) => {
    navigate(`/dashboard/services/${recommendationId}`);
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-12">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-foreground flex items-center gap-2">
            <SparklesIcon size={20} className="text-primary" />
            Recommended Services
          </h3>
          <p className="text-sm text-muted-foreground mt-1">
            Services frequently booked together or manually recommended
          </p>
        </div>
        {isEditing && !isAddingMode && (
          <Button
            onClick={() => {
              setIsAddingMode(true);
              loadAvailableServices();
            }}
            className="cursor-pointer transition-all duration-200"
          >
            <PlusIcon size={16} />
            Add Recommendation
          </Button>
        )}
      </div>

      {error && (
        <Alert variant="error">
          <AlertTriangleIcon size={20} />
          <div>
            <h3 className="font-semibold">Error</h3>
            <p className="text-sm">{error}</p>
          </div>
        </Alert>
      )}

      {/* Add Recommendation Mode */}
      {isAddingMode && (
        <Card className="p-6 bg-blue-50 dark:bg-blue-950 border-blue-200 dark:border-blue-800">
          <h4 className="font-semibold text-foreground mb-4">
            Add Manual Recommendation
          </h4>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                Select Service
              </label>
              <select
                value={selectedServiceId}
                onChange={(e) => setSelectedServiceId(e.target.value)}
                className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground"
              >
                <option value="">Choose a service...</option>
                {availableServices.map((service) => (
                  <option key={service.id} value={service.id}>
                    {service.name} - ₦{service.price.toLocaleString()}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex gap-2">
              <Button
                onClick={handleAddRecommendation}
                disabled={!selectedServiceId}
                className="cursor-pointer transition-all duration-200"
              >
                <CheckCircleIcon size={16} />
                Add
              </Button>
              <Button
                variant="outline"
                onClick={() => {
                  setIsAddingMode(false);
                  setSelectedServiceId("");
                }}
                className="cursor-pointer transition-all duration-200"
              >
                Cancel
              </Button>
            </div>
          </div>
        </Card>
      )}

      {/* Recommendations List */}
      {recommendations.length === 0 ? (
        <Card className="p-12 text-center">
          <SparklesIcon
            size={48}
            className="mx-auto text-muted-foreground mb-4"
          />
          <h3 className="text-lg font-semibold text-foreground mb-2">
            No Recommendations Yet
          </h3>
          <p className="text-sm text-muted-foreground mb-4">
            Recommendations will appear automatically based on booking patterns,
            or you can add them manually.
          </p>
          {isEditing && (
            <Button
              onClick={() => {
                setIsAddingMode(true);
                loadAvailableServices();
              }}
              className="cursor-pointer transition-all duration-200"
            >
              <PlusIcon size={16} />
              Add First Recommendation
            </Button>
          )}
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {recommendations.map((rec) => (
            <Card
              key={rec.id}
              className="p-4 hover:shadow-lg transition-all duration-200 cursor-pointer"
              onClick={() => handleServiceClick(rec.id)}
            >
              <div className="flex gap-4">
                {/* Service Photo */}
                <div className="w-20 h-20 rounded-lg overflow-hidden bg-muted flex-shrink-0">
                  {rec.photo_url ? (
                    <img
                      src={rec.photo_url}
                      alt={rec.name}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center">
                      <ScissorsIcon
                        size={32}
                        className="text-muted-foreground"
                      />
                    </div>
                  )}
                </div>

                {/* Service Info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <h4 className="font-semibold text-foreground truncate">
                      {rec.name}
                    </h4>
                    {isEditing && rec.is_manual && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleRemoveRecommendation(rec.id);
                        }}
                        className="cursor-pointer transition-all duration-200 flex-shrink-0"
                      >
                        <TrashIcon size={14} />
                      </Button>
                    )}
                  </div>

                  <div className="space-y-1">
                    <p className="text-sm font-medium text-foreground">
                      ₦{rec.price.toLocaleString()}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {rec.duration_minutes} mins
                    </p>
                    {rec.category && (
                      <Badge variant="secondary" className="text-xs">
                        {rec.category}
                      </Badge>
                    )}
                  </div>

                  {rec.is_manual && (
                    <Badge
                      variant="outline"
                      className="mt-2 text-xs border-blue-500 text-blue-600"
                    >
                      Manual
                    </Badge>
                  )}
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Info Card */}
      {recommendations.length > 0 && (
        <Card className="p-4 bg-blue-50 dark:bg-blue-950 border-blue-200 dark:border-blue-800">
          <div className="flex gap-3">
            <SparklesIcon
              size={20}
              className="text-blue-600 flex-shrink-0 mt-0.5"
            />
            <div>
              <h4 className="font-semibold text-blue-900 dark:text-blue-100 mb-1">
                How Recommendations Work
              </h4>
              <p className="text-sm text-blue-800 dark:text-blue-200">
                Recommendations are generated automatically based on services
                frequently booked together by your clients. You can also add
                manual recommendations to highlight specific service
                combinations.
              </p>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}
