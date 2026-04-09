import {
  useRecommendations,
  useRecommendationFeedback,
} from "@/hooks/useRecommendations";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  SparklesIcon as Sparkles,
  Clock,
  DollarSign,
  TrendingUp,
} from "@/components/icons";
import { useNavigate } from "react-router-dom";

interface ServiceRecommendationsProps {
  limit?: number;
  onServiceSelect?: (serviceId: string) => void;
}

export default function ServiceRecommendations({
  limit = 5,
  onServiceSelect,
}: ServiceRecommendationsProps) {
  const { data: recommendations, isLoading } = useRecommendations(limit);
  const trackFeedback = useRecommendationFeedback();
  const navigate = useNavigate();

  const handleServiceClick = (serviceId: string, recommendationId: string) => {
    trackFeedback.mutate({
      recommendationId,
      action: "clicked",
    });

    if (onServiceSelect) {
      onServiceSelect(serviceId);
    } else {
      navigate(`/public/booking?service=${serviceId}`);
    }
  };

  const getRecommendationIcon = (type: string) => {
    switch (type) {
      case "content_based":
        return <TrendingUp className="h-4 w-4" />;
      case "collaborative":
        return <Sparkles className="h-4 w-4" />;
      case "popular":
        return <TrendingUp className="h-4 w-4" />;
      default:
        return <Sparkles className="h-4 w-4" />;
    }
  };

  const getRecommendationBadgeColor = (type: string) => {
    switch (type) {
      case "content_based":
        return "bg-blue-100 text-blue-800";
      case "collaborative":
        return "bg-purple-100 text-purple-800";
      case "popular":
        return "bg-green-100 text-green-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-blue-600" />
          <h3 className="text-lg font-semibold">Recommended for You</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader>
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                <div className="h-3 bg-gray-200 rounded w-1/2 mt-2"></div>
              </CardHeader>
              <CardContent>
                <div className="h-20 bg-gray-200 rounded"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (!recommendations || recommendations.length === 0) {
    return null;
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <Sparkles className="h-5 w-5 text-blue-600" />
        <h3 className="text-lg font-semibold">Recommended for You</h3>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {recommendations.map((rec) => (
          <Card
            key={rec.id}
            className="hover:shadow-lg transition-shadow cursor-pointer"
            onClick={() => handleServiceClick(rec.service_id, rec.id)}
          >
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <CardTitle className="text-base">
                    {rec.service_name}
                  </CardTitle>
                  <CardDescription className="text-sm mt-1">
                    {rec.service_description}
                  </CardDescription>
                </div>
                {rec.service_image_url && (
                  <img
                    src={rec.service_image_url}
                    alt={rec.service_name}
                    className="w-16 h-16 object-cover rounded ml-2"
                  />
                )}
              </div>
            </CardHeader>

            <CardContent className="space-y-3">
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-1 text-gray-600">
                  <DollarSign className="h-4 w-4" />
                  <span className="font-semibold">${rec.service_price}</span>
                </div>
                <div className="flex items-center gap-1 text-gray-600">
                  <Clock className="h-4 w-4" />
                  <span>{rec.service_duration} min</span>
                </div>
              </div>

              {rec.staff_name && (
                <div className="text-sm text-gray-600">
                  with <span className="font-medium">{rec.staff_name}</span>
                </div>
              )}

              <div className="flex items-center gap-2">
                <Badge
                  className={`text-xs ${getRecommendationBadgeColor(
                    rec.recommendation_type,
                  )}`}
                >
                  <span className="flex items-center gap-1">
                    {getRecommendationIcon(rec.recommendation_type)}
                    {rec.recommendation_type === "content_based" && "For You"}
                    {rec.recommendation_type === "collaborative" &&
                      "Similar Customers"}
                    {rec.recommendation_type === "popular" && "Popular"}
                  </span>
                </Badge>
                <span className="text-xs text-gray-500">
                  {Math.round(rec.confidence_score * 100)}% match
                </span>
              </div>

              <p className="text-xs text-gray-500 italic">{rec.reasoning}</p>

              <Button className="w-full" size="sm">
                Book Now
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
