"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { MicIcon, SquareIcon } from "@/components/icons";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils/cn";

interface VoiceInputProps {
  onTranscript: (text: string, language: string) => void;
  onError: (error: Error) => void;
  language?: string;
  className?: string;
}

export function VoiceInput({
  onTranscript,
  onError,
  language = "en",
  className,
}: VoiceInputProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const silenceTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setAudioLevel(0);

      if (silenceTimeoutRef.current) {
        clearTimeout(silenceTimeoutRef.current);
      }

      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }

      if (
        audioContextRef.current &&
        audioContextRef.current.state !== "closed"
      ) {
        audioContextRef.current.close();
      }
    }
  }, [isRecording]);

  useEffect(() => {
    // Optional: Check permission status but don't block the button
    checkMicrophonePermission();

    return () => {
      stopRecording();
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      if (silenceTimeoutRef.current) {
        clearTimeout(silenceTimeoutRef.current);
      }
    };
  }, [stopRecording]);

  const checkMicrophonePermission = async () => {
    try {
      const result = await navigator.permissions.query({
        name: "microphone" as PermissionName,
      });

      result.addEventListener("change", () => {
        // Permission state changed
      });
    } catch {
      // Permission API not supported, that's okay
      console.log("Permission API not supported, will request on click");
    }
  };

  const processAudio = async (audioBlob: Blob) => {
    try {
      const formData = new FormData();
      formData.append("audio", audioBlob);
      formData.append("language", language);

      const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

      // Get auth token from localStorage
      const token = localStorage.getItem("access_token");

      const headers: HeadersInit = {};
      if (token) {
        headers.Authorization = `Bearer ${token}`;
      }

      const response = await fetch(`${API_URL}/api/voice/transcribe`, {
        method: "POST",
        headers,
        body: formData,
      });

      if (!response.ok) {
        if (response.status === 401 || response.status === 403) {
          throw new Error("Authentication required. Please log in again.");
        }
        throw new Error("Transcription failed");
      }

      const data = await response.json();
      onTranscript(data.text, data.language);
    } catch (error) {
      console.error("Error processing audio:", error);
      onError(error as Error);
    }
  };

  const visualizeAudio = () => {
    if (!analyserRef.current) return;

    const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);

    const updateLevel = () => {
      if (!analyserRef.current || !isRecording) return;

      analyserRef.current.getByteFrequencyData(dataArray);
      const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
      const normalizedLevel = Math.min(100, (average / 255) * 100);

      setAudioLevel(normalizedLevel);
      animationFrameRef.current = requestAnimationFrame(updateLevel);
    };

    updateLevel();
  };

  const startSilenceDetection = () => {
    const checkSilence = () => {
      if (audioLevel < 5) {
        silenceTimeoutRef.current = setTimeout(() => {
          if (audioLevel < 5) {
            stopRecording();
          }
        }, 3000);
      } else {
        if (silenceTimeoutRef.current) {
          clearTimeout(silenceTimeoutRef.current);
        }
        silenceTimeoutRef.current = setTimeout(checkSilence, 100);
      }
    };

    checkSilence();
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

      audioContextRef.current = new AudioContext();
      const source = audioContextRef.current.createMediaStreamSource(stream);
      analyserRef.current = audioContextRef.current.createAnalyser();
      analyserRef.current.fftSize = 256;
      source.connect(analyserRef.current);

      visualizeAudio();

      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, {
          type: "audio/wav",
        });
        await processAudio(audioBlob);
        stream.getTracks().forEach((track) => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);

      startSilenceDetection();
    } catch (err) {
      console.error("Error starting recording:", err);
      onError(err as Error);
    }
  };

  const handleToggleRecording = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  return (
    <div className={cn("flex flex-col items-center gap-4", className)}>
      <Button
        onClick={handleToggleRecording}
        size="lg"
        variant={isRecording ? "destructive" : "primary"}
        className={cn(
          "relative h-16 w-16 rounded-full transition-all",
          isRecording && "animate-pulse",
        )}
      >
        {isRecording ? (
          <SquareIcon className="h-6 w-6" />
        ) : (
          <MicIcon className="h-6 w-6" />
        )}
      </Button>

      {isRecording && (
        <div className="flex items-center gap-1">
          {[...Array(10)].map((_, i) => (
            <div
              key={i}
              className={cn(
                "h-8 w-1 rounded-full bg-primary transition-all",
                audioLevel > i * 10 ? "opacity-100" : "opacity-20",
              )}
              style={{
                height:
                  audioLevel > i * 10
                    ? `${Math.min(32, (audioLevel / 100) * 32)}px`
                    : "8px",
              }}
            />
          ))}
        </div>
      )}

      <p className="text-sm text-muted-foreground">
        {isRecording
          ? "Recording... (Stop or pause for 3 seconds)"
          : "Click to start recording"}
      </p>
    </div>
  );
}
