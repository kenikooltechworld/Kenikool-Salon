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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface TrainingRecordModalProps {
  staffId: string;
  staffName: string;
  isOpen: boolean;
  onClose: () => void;
  onRecordCreated?: () => void;
}

const TRAINING_TYPES = [
  { value: "internal", label: "Internal" },
  { value: "external", label: "External" },
  { value: "online", label: "Online" },
  { value: "certification", label: "Certification" },
];

const SKILL_LEVELS = [
  { value: "beginner", label: "Beginner" },
  { value: "intermediate", label: "Intermediate" },
  { value: "advanced", label: "Advanced" },
  { value: "master", label: "Master" },
];

export function TrainingRecordModal({
  staffId,
  staffName,
  isOpen,
  onClose,
  onRecordCreated,
}: TrainingRecordModalProps) {
  const [topic, setTopic] = useState("");
  const [type, setType] = useState("internal");
  const [instructor, setInstructor] = useState("");
  const [date, setDate] = useState("");
  const [hours, setHours] = useState("");
  const [skillBefore, setSkillBefore] = useState("beginner");
  const [skillAfter, setSkillAfter] = useState("intermediate");
  const [notes, setNotes] = useState("");

  const createMutation = useMutation({
    mutationFn: async () => {
      if (!topic || !instructor || !date || !hours) {
        throw new Error("Please fill in all required fields");
      }

      const res = await fetch(`/api/staff/training`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          staff_id: staffId,
          training_topic: topic,
          training_type: type,
          instructor,
          training_date: new Date(date).toISOString(),
          duration_hours: parseFloat(hours),
          skill_level_before: skillBefore,
          skill_level_after: skillAfter,
          notes: notes || undefined,
        }),
      });

      if (!res.ok) throw new Error("Failed to create training record");
      return res.json();
    },
    onSuccess: () => {
      toast.success("Training record created");
      onRecordCreated?.();
      onClose();
      setTopic("");
      setType("internal");
      setInstructor("");
      setDate("");
      setHours("");
      setSkillBefore("beginner");
      setSkillAfter("intermediate");
      setNotes("");
    },
    onError: (error: any) => {
      toast.error(error.message || "Failed to create record");
    },
  });

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Record Training - {staffName}</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {/* Topic */}
          <div>
            <Label htmlFor="topic">Training Topic</Label>
            <Input
              id="topic"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g., Advanced Hair Coloring"
              className="mt-1"
            />
          </div>

          {/* Type */}
          <div>
            <Label htmlFor="type">Training Type</Label>
            <Select value={type} onValueChange={setType}>
              <SelectTrigger id="type" className="mt-1">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {TRAINING_TYPES.map((t) => (
                  <SelectItem key={t.value} value={t.value}>
                    {t.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Instructor */}
          <div>
            <Label htmlFor="instructor">Instructor</Label>
            <Input
              id="instructor"
              value={instructor}
              onChange={(e) => setInstructor(e.target.value)}
              placeholder="Instructor name"
              className="mt-1"
            />
          </div>

          {/* Date and Hours */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <Label htmlFor="date">Training Date</Label>
              <Input
                id="date"
                type="date"
                value={date}
                onChange={(e) => setDate(e.target.value)}
                className="mt-1"
              />
            </div>
            <div>
              <Label htmlFor="hours">Duration (hours)</Label>
              <Input
                id="hours"
                type="number"
                value={hours}
                onChange={(e) => setHours(e.target.value)}
                placeholder="e.g., 8"
                step="0.5"
                min="0"
                className="mt-1"
              />
            </div>
          </div>

          {/* Skill Levels */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <Label htmlFor="skill-before">Skill Level Before</Label>
              <Select value={skillBefore} onValueChange={setSkillBefore}>
                <SelectTrigger id="skill-before" className="mt-1">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {SKILL_LEVELS.map((s) => (
                    <SelectItem key={s.value} value={s.value}>
                      {s.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="skill-after">Skill Level After</Label>
              <Select value={skillAfter} onValueChange={setSkillAfter}>
                <SelectTrigger id="skill-after" className="mt-1">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {SKILL_LEVELS.map((s) => (
                    <SelectItem key={s.value} value={s.value}>
                      {s.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Notes */}
          <div>
            <Label htmlFor="notes">Notes (Optional)</Label>
            <Textarea
              id="notes"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Additional notes about the training..."
              className="mt-1 resize-none"
              rows={3}
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
              !topic ||
              !instructor ||
              !date ||
              !hours ||
              createMutation.isPending
            }
          >
            {createMutation.isPending ? "Creating..." : "Create Record"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
