import { Card } from "@/components/ui/card";
import { StarIcon } from "@/components/icons";

interface ReviewCardProps {
  id: string;
  clientName: string;
  rating: number;
  comment: string;
  date: string;
  service: string;
}

export function ReviewCard({
  clientName,
  rating,
  comment,
  date,
  service,
}: ReviewCardProps) {
  return (
    <Card className="p-4">
      <div className="flex items-start justify-between mb-3">
        <div>
          <p className="font-semibold">{clientName}</p>
          <p className="text-sm text-muted-foreground">{service}</p>
        </div>
        <div className="flex items-center gap-1">
          {[...Array(5)].map((_, i) => (
            <StarIcon
              key={i}
              size={16}
              className={i < rating ? "fill-accent text-accent" : "text-muted"}
            />
          ))}
        </div>
      </div>
      <p className="text-sm mb-3">{comment}</p>
      <p className="text-xs text-muted-foreground">
        {new Date(date).toLocaleDateString()}
      </p>
    </Card>
  );
}
