import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { Plus, Send } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface ShiftNote {
  _id: string;
  shift_id: string;
  author_id: string;
  author_name?: string;
  content: string;
  created_at: string;
}

interface ShiftNotesProps {
  shiftId: string;
  shiftDate: string;
  currentUserId: string;
  onAddNote?: (shiftId: string, content: string) => Promise<void>;
}

export const ShiftNotes: React.FC<ShiftNotesProps> = ({
  shiftId,
  shiftDate,
  currentUserId,
  onAddNote,
}) => {
  const { showToast } = useToast();
  const [notes, setNotes] = useState<ShiftNote[]>([]);
  const [newNote, setNewNote] = useState("");
  const [loading, setLoading] = useState(false);
  const [isAdding, setIsAdding] = useState(false);

  useEffect(() => {
    fetchNotes();
  }, [shiftId]);

  const fetchNotes = async () => {
    try {
      const response = await fetch(
        `/api/staff/messages/shift-notes/${shiftId}`,
      );
      const data = await response.json();
      setNotes(data.notes || []);
    } catch (error) {
      console.error("Failed to fetch shift notes:", error);
    }
  };

  const handleAddNote = async () => {
    if (!newNote.trim()) {
      return;
    }

    setLoading(true);
    try {
      if (onAddNote) {
        await onAddNote(shiftId, newNote);
      }
      setNewNote("");
      setIsAdding(false);
      await fetchNotes();
    } catch (error) {
      console.error("Failed to add note:", error);
      showToast({
        title: "Error",
        description: "Failed to add note",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">
          Shift Notes - {new Date(shiftDate).toLocaleDateString()}
        </CardTitle>
      </CardHeader>

      <CardContent className="space-y-4">
        {!isAdding && (
          <Button
            onClick={() => setIsAdding(true)}
            variant="outline"
            className="w-full"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Note
          </Button>
        )}

        {isAdding && (
          <div className="border rounded-lg p-3 space-y-2 bg-slate-50">
            <Textarea
              placeholder="Add a shift note for handoff..."
              value={newNote}
              onChange={(e) => setNewNote(e.target.value)}
              rows={3}
            />
            <div className="flex gap-2">
              <Button
                onClick={handleAddNote}
                disabled={loading || !newNote.trim()}
                className="flex-1"
                size="sm"
              >
                <Send className="w-4 h-4 mr-2" />
                Save Note
              </Button>
              <Button
                variant="outline"
                onClick={() => {
                  setIsAdding(false);
                  setNewNote("");
                }}
                className="flex-1"
                size="sm"
              >
                Cancel
              </Button>
            </div>
          </div>
        )}

        <ScrollArea className="h-64">
          <div className="space-y-3 pr-4">
            {notes.length === 0 ? (
              <p className="text-center text-slate-500 py-8">
                No shift notes yet
              </p>
            ) : (
              notes.map((note) => (
                <div
                  key={note._id}
                  className="border rounded-lg p-3 hover:bg-slate-50 transition"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1">
                      <p className="text-xs font-semibold text-slate-600">
                        {note.author_name || "Staff Member"}
                      </p>
                      <p className="text-xs text-slate-500 mt-0.5">
                        {new Date(note.created_at).toLocaleTimeString([], {
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </p>
                    </div>
                    {note.author_id === currentUserId && (
                      <Badge variant="secondary" className="text-xs">
                        You
                      </Badge>
                    )}
                  </div>
                  <p className="text-sm mt-2 text-slate-700">{note.content}</p>
                </div>
              ))
            )}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
};
