"use client";

import { useState, useRef, useEffect } from "react";
import { VoiceInput } from "./voice-input";
import { AudioPlayback } from "./audio-playback";
import {
  Loader2Icon,
  MessageSquareIcon,
  Volume2Icon,
  LanguagesIcon,
} from "@/components/icons";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils/cn";

interface Message {
  id: string;
  type: "user" | "assistant";
  text: string;
  timestamp: Date;
  language?: string;
  audioUrl?: string;
}

interface VoiceAssistantUIProps {
  className?: string;
}

const SUPPORTED_LANGUAGES = [
  { code: "en", name: "English" },
  { code: "yo", name: "Yoruba" },
  { code: "ig", name: "Igbo" },
  { code: "ha", name: "Hausa" },
  { code: "pcm", name: "Nigerian Pidgin" },
];

export function VoiceAssistantUI({ className }: VoiceAssistantUIProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentTranscript, setCurrentTranscript] = useState("");
  const [selectedLanguage, setSelectedLanguage] = useState("en");
  const [sessionId] = useState(() => `session_${Date.now()}`);

  const scrollAreaRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Scroll to bottom when new messages arrive
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  const handleTranscript = async (text: string, detectedLanguage: string) => {
    setCurrentTranscript(text);

    // Add user message
    const userMessage: Message = {
      id: `user_${Date.now()}`,
      type: "user",
      text,
      timestamp: new Date(),
      language: detectedLanguage,
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsProcessing(true);

    try {
      const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

      // Get auth token from localStorage
      const token = localStorage.getItem("access_token");

      // Send to voice assistant API
      const response = await fetch(`${API_URL}/api/voice/process`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token && { Authorization: `Bearer ${token}` }),
        },
        body: JSON.stringify({
          text,
          language: detectedLanguage,
          session_id: sessionId,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to process voice command");
      }

      const data = await response.json();

      // Add assistant response
      const assistantMessage: Message = {
        id: `assistant_${Date.now()}`,
        type: "assistant",
        text: data.response_text,
        timestamp: new Date(),
        language: data.detected_language,
        audioUrl: data.audio_url,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Error processing voice command:", error);

      // Add error message
      const errorMessage: Message = {
        id: `error_${Date.now()}`,
        type: "assistant",
        text: "I'm sorry, I encountered an error processing your request. Please try again.",
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsProcessing(false);
      setCurrentTranscript("");
    }
  };

  const handleError = (error: Error) => {
    console.error("Voice input error:", error);

    const errorMessage: Message = {
      id: `error_${Date.now()}`,
      type: "assistant",
      text: `Error: ${error.message}. Please try again.`,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, errorMessage]);
  };

  const clearHistory = () => {
    setMessages([]);
  };

  return (
    <Card className={cn("flex flex-col", className)}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
        <CardTitle className="flex items-center gap-2">
          <Volume2Icon className="h-5 w-5" />
          Voice Assistant
        </CardTitle>

        <div className="flex items-center gap-2">
          <Select value={selectedLanguage} onValueChange={setSelectedLanguage}>
            <SelectTrigger className="w-[180px]">
              <LanguagesIcon className="mr-2 h-4 w-4" />
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {SUPPORTED_LANGUAGES.map((lang) => (
                <SelectItem key={lang.code} value={lang.code}>
                  {lang.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </CardHeader>

      <CardContent className="flex flex-col gap-4">
        {/* Conversation History */}
        <ScrollArea
          className="h-[400px] rounded-md border p-4"
          ref={scrollAreaRef}
        >
          {messages.length === 0 ? (
            <div className="flex h-full items-center justify-center text-center">
              <div className="space-y-2">
                <MessageSquareIcon className="mx-auto h-12 w-12 text-muted-foreground" />
                <p className="text-sm text-muted-foreground">
                  No conversation yet. Click the microphone to start.
                </p>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={cn(
                    "flex flex-col gap-1",
                    message.type === "user" ? "items-end" : "items-start",
                  )}
                >
                  <div
                    className={cn(
                      "max-w-[80%] rounded-lg px-4 py-2",
                      message.type === "user"
                        ? "bg-primary text-primary-foreground"
                        : "bg-muted",
                    )}
                  >
                    <p className="text-sm">{message.text}</p>
                  </div>

                  <div className="flex items-center gap-2">
                    {message.language && (
                      <Badge variant="outline" className="text-xs">
                        {SUPPORTED_LANGUAGES.find(
                          (l) => l.code === message.language,
                        )?.name || message.language}
                      </Badge>
                    )}
                    <span className="text-xs text-muted-foreground">
                      {message.timestamp.toLocaleTimeString()}
                    </span>
                    {message.audioUrl && message.type === "assistant" && (
                      <AudioPlayback audioUrl={message.audioUrl} autoPlay />
                    )}
                  </div>
                </div>
              ))}

              {/* Current transcript (while processing) */}
              {currentTranscript && (
                <div className="flex flex-col items-end gap-1">
                  <div className="max-w-[80%] rounded-lg bg-primary/50 px-4 py-2">
                    <p className="text-sm">{currentTranscript}</p>
                  </div>
                </div>
              )}

              {/* Processing indicator */}
              {isProcessing && (
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Loader2Icon className="h-4 w-4 animate-spin" />
                  <span>Processing...</span>
                </div>
              )}
            </div>
          )}
        </ScrollArea>

        {/* Voice Input */}
        <div className="flex flex-col items-center gap-2">
          <VoiceInput
            onTranscript={handleTranscript}
            onError={handleError}
            language={selectedLanguage}
          />

          {messages.length > 0 && (
            <button
              onClick={clearHistory}
              className="text-xs text-muted-foreground hover:text-foreground"
            >
              Clear history
            </button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
