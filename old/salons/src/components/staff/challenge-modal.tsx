import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Progress } from "@/components/ui/progress";
import { X, Target, Zap } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface Challenge {
  _id: string;
  title: string;
  description: string;
  challenge_type: string;
  target_value: number;
  reward_points: number;
  start_date: string;
  end_date: string;
}

interface ChallengeProgress {
  rank: number;
  staff_id: string;
  staff_name: string;
  current_value: number;
  target_value: number;
  completion_percent: number;
  completed: boolean;
}

interface ChallengeModalProps {
  isOpen: boolean;
  onClose: () => void;
  userRole: string;
  onCreateChallenge?: (data: any) => Promise<void>;
}

export const ChallengeModal: React.FC<ChallengeModalProps> = ({
  isOpen,
  onClose,
  userRole,
  onCreateChallenge,
}) => {
  const { showToast } = useToast();
  const [challenges, setChallenges] = useState<Challenge[]>([]);
  const [selectedChallenge, setSelectedChallenge] = useState<Challenge | null>(
    null,
  );
  const [progress, setProgress] = useState<ChallengeProgress[]>([]);
  const [isCreating, setIsCreating] = useState(false);
  const [loading, setLoading] = useState(true);

  // Form state
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [challengeType, setChallengeType] = useState("bookings");
  const [targetValue, setTargetValue] = useState("");
  const [rewardPoints, setRewardPoints] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");

  useEffect(() => {
    if (isOpen) {
      fetchChallenges();
    }
  }, [isOpen]);

  useEffect(() => {
    if (selectedChallenge) {
      fetchProgress();
    }
  }, [selectedChallenge]);

  const fetchChallenges = async () => {
    try {
      setLoading(true);
      const response = await fetch("/api/staff/leaderboard/challenges");
      const data = await response.json();
      setChallenges(data.challenges || []);
      if (data.challenges && data.challenges.length > 0) {
        setSelectedChallenge(data.challenges[0]);
      }
    } catch (error) {
      console.error("Failed to fetch challenges:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchProgress = async () => {
    if (!selectedChallenge) return;
    try {
      const response = await fetch(
        `/api/staff/leaderboard/challenges/${selectedChallenge._id}/progress`,
      );
      const data = await response.json();
      setProgress(data.progress || []);
    } catch (error) {
      console.error("Failed to fetch progress:", error);
    }
  };

  const handleCreateChallenge = async () => {
    if (
      !title ||
      !description ||
      !targetValue ||
      !rewardPoints ||
      !startDate ||
      !endDate
    ) {
      showToast({
        title: "Validation Error",
        description: "Please fill in all fields",
        variant: "destructive",
      });
      return;
    }

    try {
      if (onCreateChallenge) {
        await onCreateChallenge({
          title,
          description,
          challenge_type: challengeType,
          target_value: parseFloat(targetValue),
          reward_points: parseInt(rewardPoints),
          start_date: startDate,
          end_date: endDate,
        });
      }
      setTitle("");
      setDescription("");
      setChallengeType("bookings");
      setTargetValue("");
      setRewardPoints("");
      setStartDate("");
      setEndDate("");
      setIsCreating(false);
      await fetchChallenges();
    } catch (error) {
      console.error("Failed to create challenge:", error);
      showToast({
        title: "Error",
        description: "Failed to create challenge",
        variant: "destructive",
      });
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <Card className="w-full max-w-2xl max-h-[80vh] flex flex-col">
        <CardHeader className="flex flex-row items-center justify-between border-b">
          <CardTitle className="flex items-center gap-2">
            <Target className="w-5 h-5" />
            Challenges
          </CardTitle>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="w-4 h-4" />
          </Button>
        </CardHeader>

        <CardContent className="flex-1 overflow-hidden flex flex-col p-4 space-y-4">
          {userRole === "owner" && !isCreating && (
            <Button onClick={() => setIsCreating(true)} className="w-full">
              <Zap className="w-4 h-4 mr-2" />
              Create New Challenge
            </Button>
          )}

          {isCreating && (
            <div className="border rounded-lg p-4 space-y-3 bg-slate-50">
              <Input
                placeholder="Challenge title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
              />
              <Textarea
                placeholder="Challenge description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={2}
              />
              <Select value={challengeType} onValueChange={setChallengeType}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="bookings">Bookings</SelectItem>
                  <SelectItem value="revenue">Revenue</SelectItem>
                  <SelectItem value="rating">Rating</SelectItem>
                </SelectContent>
              </Select>
              <Input
                type="number"
                placeholder="Target value"
                value={targetValue}
                onChange={(e) => setTargetValue(e.target.value)}
              />
              <Input
                type="number"
                placeholder="Reward points"
                value={rewardPoints}
                onChange={(e) => setRewardPoints(e.target.value)}
              />
              <Input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
              />
              <Input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
              />
              <div className="flex gap-2">
                <Button onClick={handleCreateChallenge} className="flex-1">
                  Create
                </Button>
                <Button
                  variant="outline"
                  onClick={() => setIsCreating(false)}
                  className="flex-1"
                >
                  Cancel
                </Button>
              </div>
            </div>
          )}

          {loading ? (
            <p className="text-center text-slate-500 py-8">
              Loading challenges...
            </p>
          ) : challenges.length === 0 ? (
            <p className="text-center text-slate-500 py-8">
              No active challenges
            </p>
          ) : (
            <div className="flex-1 overflow-hidden flex flex-col gap-4">
              <div className="flex gap-2 overflow-x-auto pb-2">
                {challenges.map((challenge) => (
                  <button
                    key={challenge._id}
                    onClick={() => setSelectedChallenge(challenge)}
                    className={`px-3 py-2 rounded-lg whitespace-nowrap text-sm transition ${
                      selectedChallenge?._id === challenge._id
                        ? "bg-blue-500 text-white"
                        : "bg-slate-200 hover:bg-slate-300"
                    }`}
                  >
                    {challenge.title}
                  </button>
                ))}
              </div>

              {selectedChallenge && (
                <div className="flex-1 overflow-y-auto space-y-3">
                  <div className="bg-slate-50 rounded-lg p-3">
                    <h3 className="font-semibold">{selectedChallenge.title}</h3>
                    <p className="text-sm text-slate-600 mt-1">
                      {selectedChallenge.description}
                    </p>
                    <div className="flex gap-4 mt-2 text-sm">
                      <span>Target: {selectedChallenge.target_value}</span>
                      <span>Reward: {selectedChallenge.reward_points} pts</span>
                    </div>
                  </div>

                  <div className="space-y-2">
                    {progress.map((p) => (
                      <div key={p.staff_id} className="border rounded-lg p-2">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-sm font-medium">
                            #{p.rank} {p.staff_name}
                          </span>
                          <span className="text-xs text-slate-600">
                            {p.current_value} / {p.target_value}
                          </span>
                        </div>
                        <Progress
                          value={p.completion_percent}
                          className="h-1.5"
                        />
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};
