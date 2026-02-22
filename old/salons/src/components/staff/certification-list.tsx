"use client";

import { useQuery } from "@tanstack/react-query";
import { format, differenceInDays } from "date-fns";
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

interface Certification {
  _id: string;
  certification_name: string;
  issuing_body: string;
  certification_number: string;
  issue_date: string;
  expiration_date: string;
  is_expired: boolean;
  is_required: boolean;
  continuing_education_hours: number;
}

interface CertificationListProps {
  staffId?: string;
  title?: string;
}

export function CertificationList({
  staffId,
  title = "Certifications",
}: CertificationListProps) {
  const { data: response, isLoading } = useQuery({
    queryKey: ["certifications", staffId],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (staffId) params.append("staff_id", staffId);

      const res = await fetch(`/api/staff/certifications?${params}`);
      if (!res.ok) throw new Error("Failed to fetch certifications");
      return res.json();
    },
  });

  const certs: Certification[] = response?.data || [];

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

  if (!certs || certs.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground text-center py-8">
            No certifications found
          </p>
        </CardContent>
      </Card>
    );
  }

  const getStatusBadge = (cert: Certification) => {
    if (cert.is_expired) {
      return <Badge className="bg-red-100 text-red-800">Expired</Badge>;
    }

    const daysUntilExpiry = differenceInDays(
      new Date(cert.expiration_date),
      new Date(),
    );

    if (daysUntilExpiry < 30) {
      return (
        <Badge className="bg-yellow-100 text-yellow-800">
          Expires in {daysUntilExpiry}d
        </Badge>
      );
    }

    return <Badge className="bg-green-100 text-green-800">Active</Badge>;
  };

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
                <TableHead>Certification</TableHead>
                <TableHead>Issuing Body</TableHead>
                <TableHead>Number</TableHead>
                <TableHead>Issue Date</TableHead>
                <TableHead>Expiry Date</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Required</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {certs.map((cert) => (
                <TableRow key={cert._id}>
                  <TableCell className="font-medium">
                    {cert.certification_name}
                  </TableCell>
                  <TableCell>{cert.issuing_body}</TableCell>
                  <TableCell className="text-sm text-muted-foreground">
                    {cert.certification_number}
                  </TableCell>
                  <TableCell>
                    {format(new Date(cert.issue_date), "MMM dd, yyyy")}
                  </TableCell>
                  <TableCell>
                    {format(new Date(cert.expiration_date), "MMM dd, yyyy")}
                  </TableCell>
                  <TableCell>{getStatusBadge(cert)}</TableCell>
                  <TableCell>
                    {cert.is_required ? (
                      <Badge className="bg-blue-100 text-blue-800">
                        Required
                      </Badge>
                    ) : (
                      <span className="text-sm text-muted-foreground">-</span>
                    )}
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
