import { useResourceUtilizationStats } from "@/hooks/useResourceOperations";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { BarChart3Icon } from "@/components/icons";

interface ResourceUtilizationProps {
  resourceId?: string;
}

export default function ResourceUtilization({ resourceId }: ResourceUtilizationProps) {
  const { data: stats, isLoading } = useResourceUtilizationStats(resourceId);

  if (isLoading) {
    return <div className="space-y-3">Loading utilization stats...</div>;
  }

  if (!stats || stats.total_records === 0) {
    return (
      <Card>
        <CardContent className="py-8 text-center text-muted-foreground">
          <BarChart3Icon className="w-12 h-12 mx-auto mb-2 opacity-50" />
          <p>No utilization data available</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium text-muted-foreground">
            Total Records
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-2xl font-bold">{stats.total_records}</p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium text-muted-foreground">
            Average Utilization
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-2xl font-bold">{stats.average_utilization.toFixed(1)}%</p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium text-muted-foreground">
            Peak Utilization
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-2xl font-bold">{stats.peak_utilization.toFixed(1)}%</p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium text-muted-foreground">
            Min Utilization
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-2xl font-bold">{stats.min_utilization.toFixed(1)}%</p>
        </CardContent>
      </Card>
    </div>
  );
}
