import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Slider } from "@/components/ui/slider";
import { StarIcon } from "@/components/icons";

interface SearchFilters {
  query: string;
  minRating: number;
  maxRating: number;
  specialty?: string;
}

interface StylistResult {
  _id: string;
  name: string;
  bio: string;
  specialty: string;
  rating: number;
  total_reviews: number;
  photo_url?: string;
  available: boolean;
}

interface StylistSearchProps {
  onStylistSelect?: (stylist: StylistResult) => void;
}

export function StylistSearch({ onStylistSelect }: StylistSearchProps) {
  const [filters, setFilters] = useState<SearchFilters>({
    query: "",
    minRating: 0,
    maxRating: 5,
    specialty: undefined,
  });

  const [showFilters, setShowFilters] = useState(false);

  const { data: specialties } = useQuery({
    queryKey: ["stylist-specialties"],
    queryFn: async () => {
      const response = await apiClient.get("/api/advanced-search/specialties");
      return response.data.specialties || [];
    },
  });

  const { data: searchResults = [], isLoading } = useQuery({
    queryKey: ["stylist-search", filters],
    queryFn: async () => {
      const response = await apiClient.get("/api/advanced-search/stylists", {
        params: {
          q: filters.query,
          min_rating: filters.minRating,
          max_rating: filters.maxRating,
          specialty: filters.specialty,
        },
      });

      return response.data.results || [];
    },
    enabled: filters.query.length > 0,
  });

  const handleSearch = (query: string) => {
    setFilters((prev) => ({ ...prev, query }));
  };

  const handleSpecialtyChange = (specialty: string) => {
    setFilters((prev) => ({
      ...prev,
      specialty: prev.specialty === specialty ? undefined : specialty,
    }));
  };

  const handleRatingChange = (value: number[]) => {
    setFilters((prev) => ({
      ...prev,
      minRating: value[0],
      maxRating: value[1],
    }));
  };

  return (
    <div className="space-y-4">
      {/* Search Input */}
      <div>
        <Label className="text-[var(--foreground)]">Search Stylists</Label>
        <Input
          value={filters.query}
          onChange={(e) => handleSearch(e.target.value)}
          placeholder="Search by name or specialty..."
          className="mt-2"
        />
      </div>

      {/* Filter Toggle */}
      <Button
        variant="outline"
        onClick={() => setShowFilters(!showFilters)}
        className="w-full"
      >
        {showFilters ? "Hide Filters" : "Show Filters"}
      </Button>

      {/* Filters */}
      {showFilters && (
        <Card className="border border-[var(--border)]">
          <CardContent className="pt-6 space-y-6">
            {/* Specialties */}
            {specialties && specialties.length > 0 && (
              <div>
                <Label className="text-[var(--foreground)] mb-3 block">
                  Specialty
                </Label>
                <div className="flex flex-wrap gap-2">
                  {specialties.map((specialty: string) => (
                    <Badge
                      key={specialty}
                      variant={
                        filters.specialty === specialty ? "accent" : "outline"
                      }
                      className="cursor-pointer"
                      onClick={() => handleSpecialtyChange(specialty)}
                    >
                      {specialty}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {/* Rating Range */}
            <div>
              <Label className="text-[var(--foreground)] mb-3 block">
                Minimum Rating: {filters.minRating.toFixed(1)} - {filters.maxRating.toFixed(1)} stars
              </Label>
              <Slider
                min={0}
                max={5}
                step={0.5}
                value={[filters.minRating, filters.maxRating]}
                onValueChange={handleRatingChange}
              />
            </div>
          </CardContent>
        </Card>
      )}

      {/* Results */}
      {filters.query && (
        <div className="space-y-2">
          <p className="text-sm text-[var(--muted-foreground)]">
            {isLoading
              ? "Searching..."
              : `Found ${searchResults.length} stylist${searchResults.length !== 1 ? "s" : ""}`}
          </p>
          {searchResults.length > 0 && (
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {searchResults.map((stylist: StylistResult) => (
                <Card
                  key={stylist._id}
                  className="border border-[var(--border)] cursor-pointer hover:bg-[var(--muted)]"
                  onClick={() => onStylistSelect?.(stylist)}
                >
                  <CardContent className="pt-4">
                    <div className="flex items-start gap-3">
                      {stylist.photo_url && (
                        <div className="relative w-12 h-12 rounded-full overflow-hidden flex-shrink-0">
                          <img
                            src={stylist.photo_url}
                            alt={stylist.name}
                            className="object-cover w-full h-full"
                          />
                        </div>
                      )}
                      <div className="flex-1">
                        <h4 className="font-medium text-[var(--foreground)]">
                          {stylist.name}
                        </h4>
                        {stylist.bio && (
                          <p className="text-sm text-[var(--muted-foreground)] mt-1">
                            {stylist.bio}
                          </p>
                        )}
                        <div className="flex items-center gap-2 mt-2">
                          <div className="flex gap-1">
                            {[...Array(5)].map((_, i) => (
                              <StarIcon
                                key={i}
                                size={14}
                                className={
                                  i < Math.round(stylist.rating)
                                    ? "text-[var(--warning)] fill-[var(--warning)]"
                                    : "text-[var(--muted)]"
                                }
                              />
                            ))}
                          </div>
                          <span className="text-xs text-[var(--muted-foreground)]">
                            {stylist.rating.toFixed(1)} ({stylist.total_reviews} reviews)
                          </span>
                        </div>
                        {stylist.specialty && (
                          <Badge variant="secondary" className="mt-2">
                            {stylist.specialty}
                          </Badge>
                        )}
                        {stylist.available && (
                          <Badge variant="accent" className="mt-2 ml-2">
                            Available
                          </Badge>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
