"use client";

import { useQuery } from "@tanstack/react-query";
import { format } from "date-fns";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

interface TrainingRecord {
  _id: string;
  training_topic: string;
  training_type: string;
  instructor: string;
  training_date: string;
  duration_hours: number;
  skill_level_before: string;
  skill_level_after: string;
}

interface TrainingListProps {
  staffId?: string;
  title?: string;
}

const TYPE_COLORS = {
  internal: "bg-blue-100 text-blue-800",
  external: "bg-purple-100 text-purple-800",
  online: "bg-green-100 text-green-800",
  certification: "bg-orange-100 text-orange-800",
};

const SKILL_LABELS = {
  beginner: "Beginner",
  intermediate: "Intermediate",
  advanced: "Advanced",
  master: "Master",
};

export function TrainingList({
  staffId,
  title = "Training Records",
}: TrainingListProps) {
  const { data: response, isLoading } = useQuery({
    queryKey: ["training-records", staffId],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (staffId) params.append("staff_id", staffId);

      const res = await fetch(`/api/staff/training?${params}`);
      if (!res.ok) throw new Error("Failed to fetch records");
      return res.json();
    },
  });

  const records: TrainingRecord[] = response?.data || [];

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {[...Array(3)].map((_, i) => (
              <Skeleton key={i} className="h-12 w-full" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!records || records.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground text-center py-8">
            No training records found
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Date</TableHead>
                <TableHead>Topic</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Instructor</TableHead>
                <TableHead className="text-right">Hours</TableHead>
                <TableHead>Skill Progress</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {records.map((record) => (
                <TableRow key={record._id}>
                  <TableCell>
                    {format(new Date(record.training_date), "MMM dd, yyyy")}
                  </TableCell>
                  <TableCell className="font-medium">
                    {record.training_topic}
                  </TableCell>
                  <TableCell>
                    <Badge
                      className={
                        TYPE_COLORS[
                          record.training_type as keyof typeof TYPE_COLORS
                        ] || "bg-gray-100 text-gray-800"
                      }
                    >
                      {record.training_type.charAt(0).toUpperCase() +
                        record.training_type.slice(1)}
                    </Badge>
                  </TableCell>
                  <TableCell>{record.instructor}</TableCell>
                  <TableCell className="text-right">
                    {record.duration_hours}h
                  </TableCell>
                  <TableCell className="text-sm">
                    <span className="text-muted-foreground">
                      {
                        SKILL_LABELS[
                          record.skill_level_before as keyof typeof SKILL_LABELS
                        ]
                      }
                    </span>
                    <span className="mx-1">→</span>
                    <span className="font-semibold">
                      {
                        SKILL_LABELS[
                          record.skill_level_after as keyof typeof SKILL_LABELS
                        ]
                      }
                    </span>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}
