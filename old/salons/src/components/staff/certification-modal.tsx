"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { toast } from "sonner";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Checkbox } from "@/components/ui/checkbox";
import { Card, CardContent } from "@/components/ui/card";

interface CertificationModalProps {
  staffId: string;
  staffName: string;
  isOpen: boolean;
  onClose: () => void;
  onCertificationCreated?: () => void;
}

export function CertificationModal({
  staffId,
  staffName,
  isOpen,
  onClose,
  onCertificationCreated,
}: CertificationModalProps) {
  const [name, setName] = useState("");
  const [issuingBody, setIssuingBody] = useState("");
  const [certNumber, setCertNumber] = useState("");
  const [issueDate, setIssueDate] = useState("");
  const [expiryDate, setExpiryDate] = useState("");
  const [isRequired, setIsRequired] = useState(false);
  const [ceHours, setCeHours] = useState("");
  const [notes, setNotes] = useState("");

  const createMutation = useMutation({
    mutationFn: async () => {
      if (!name || !issuingBody || !certNumber || !issueDate || !expiryDate) {
        throw new Error("Please fill in all required fields");
      }

      if (new Date(issueDate) >= new Date(expiryDate)) {
        throw new Error("Expiry date must be after issue date");
      }

      const res = await fetch(`/api/staff/certifications`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          staff_id: staffId,
          certification_name: name,
          issuing_body: issuingBody,
          certification_number: certNumber,
          issue_date: new Date(issueDate).toISOString(),
          expiration_date: new Date(expiryDate).toISOString(),
          is_required: isRequired,
          continuing_education_hours: ceHours ? parseFloat(ceHours) : 0,
          notes: notes || undefined,
        }),
      });

      if (!res.ok) throw new Error("Failed to create certification");
      return res.json();
    },
    onSuccess: () => {
      toast.success("Certification created");
      onCertificationCreated?.();
      onClose();
      setName("");
      setIssuingBody("");
      setCertNumber("");
      setIssueDate("");
      setExpiryDate("");
      setIsRequired(false);
      setCeHours("");
      setNotes("");
    },
    onError: (error: any) => {
      toast.error(error.message || "Failed to create certification");
    },
  });

  const daysUntilExpiry = expiryDate
    ? Math.ceil(
        (new Date(expiryDate).getTime() - new Date().getTime()) /
          (1000 * 60 * 60 * 24),
      )
    : null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Add Certification - {staffName}</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {/* Name */}
          <div>
            <Label htmlFor="name">Certification Name</Label>
            <Input
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g., Cosmetology License"
              className="mt-1"
            />
          </div>

          {/* Issuing Body */}
          <div>
            <Label htmlFor="issuing-body">Issuing Body</Label>
            <Input
              id="issuing-body"
              value={issuingBody}
              onChange={(e) => setIssuingBody(e.target.value)}
              placeholder="e.g., State Board of Cosmetology"
              className="mt-1"
            />
          </div>

          {/* Cert Number */}
          <div>
            <Label htmlFor="cert-number">Certification Number</Label>
            <Input
              id="cert-number"
              value={certNumber}
              onChange={(e) => setCertNumber(e.target.value)}
              placeholder="Certification number"
              className="mt-1"
            />
          </div>

          {/* Dates */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <Label htmlFor="issue-date">Issue Date</Label>
              <Input
                id="issue-date"
                type="date"
                value={issueDate}
                onChange={(e) => setIssueDate(e.target.value)}
                className="mt-1"
              />
            </div>
            <div>
              <Label htmlFor="expiry-date">Expiry Date</Label>
              <Input
                id="expiry-date"
                type="date"
                value={expiryDate}
                onChange={(e) => setExpiryDate(e.target.value)}
                className="mt-1"
              />
            </div>
          </div>

          {/* Expiry Warning */}
          {daysUntilExpiry !== null && (
            <Card
              className={
                daysUntilExpiry < 0
                  ? "bg-red-50 border-red-200"
                  : daysUntilExpiry < 30
                    ? "bg-yellow-50 border-yellow-200"
                    : "bg-green-50 border-green-200"
              }
            >
              <CardContent className="pt-4 text-sm">
                {daysUntilExpiry < 0 ? (
                  <p className="text-red-900">
                    ⚠️ This certification has expired
                  </p>
                ) : daysUntilExpiry < 30 ? (
                  <p className="text-yellow-900">
                    ⚠️ Expires in {daysUntilExpiry} days
                  </p>
                ) : (
                  <p className="text-green-900">
                    ✓ Expires in {daysUntilExpiry} days
                  </p>
                )}
              </CardContent>
            </Card>
          )}

          {/* CE Hours */}
          <div>
            <Label htmlFor="ce-hours">
              Continuing Education Hours (Optional)
            </Label>
            <Input
              id="ce-hours"
              type="number"
              value={ceHours}
              onChange={(e) => setCeHours(e.target.value)}
              placeholder="e.g., 40"
              step="0.5"
              min="0"
              className="mt-1"
            />
          </div>

          {/* Required */}
          <div className="flex items-center gap-2">
            <Checkbox
              id="is-required"
              checked={isRequired}
              onCheckedChange={(checked) => setIsRequired(checked as boolean)}
            />
            <Label htmlFor="is-required" className="cursor-pointer">
              This is a required certification
            </Label>
          </div>

          {/* Notes */}
          <div>
            <Label htmlFor="notes">Notes (Optional)</Label>
            <Textarea
              id="notes"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Additional notes..."
              className="mt-1 resize-none"
              rows={2}
            />
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button
            onClick={() => createMutation.mutate()}
            disabled={
              !name ||
              !issuingBody ||
              !certNumber ||
              !issueDate ||
              !expiryDate ||
              createMutation.isPending
            }
          >
            {createMutation.isPending ? "Creating..." : "Add Certification"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
