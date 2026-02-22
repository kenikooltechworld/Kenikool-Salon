import React, { useState } from 'react';
import { VoiceInputComponent } from './VoiceInputComponent';
import { AudioPlaybackComponent } from './AudioPlaybackComponent';
import { MessageCircle, Loader } from 'lucide-react';

interface VoiceAssistantUIProps {
  isListening: boolean;
  transcript: string;
  response: string;
  isProcessing: boolean;
  language: string;
  onLanguageChange: (language: string) => void;
}

export const VoiceAssistantUI: React.FC<VoiceAssistantUIProps> = ({
  isListening,
  transcript,
  response,
  isProcessing,
  language,
  onLanguageChange
}) => {
  const [conversationHistory, setConversationHistory] = useState<Array<{
    type: 'user' | 'assistant';
    text: string;
    timestamp: Date;
  }>>([]);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);

  const handleTranscript = (text: string, detectedLanguage: string) => {
    setConversationHistory(prev => [...prev, {
      type: 'user',
      text,
      timestamp: new Date()
    }]);
  };

  const handleError = (error: Error) => {
    console.error('Voice error:', error);
  };

  const languages = [
    { code: 'en', name: 'English' },
    { code: 'yo', name: 'Yoruba' },
    { code: 'ig', name: 'Igbo' },
    { code: 'ha', name: 'Hausa' },
    { code: 'pcm', name: 'Nigerian Pidgin' }
  ];

  return (
    <div className="w-full max-w-2xl mx-auto p-6 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg shadow-lg">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <MessageCircle className="text-blue-600" size={28} />
          <h1 className="text-2xl font-bold text-gray-800">Voice Assistant</h1>
        </div>
        
        {/* Language Selector */}
        <select
          value={language}
          onChange={(e) => onLanguageChange(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg bg-white text-gray-700 hover:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {languages.map(lang => (
            <option key={lang.code} value={lang.code}>
              {lang.name}
            </option>
          ))}
        </select>
      </div>

      {/* Voice Input */}
      <div className="mb-6">
        <VoiceInputComponent
          onTranscript={handleTranscript}
          onError={handleError}
          language={language}
        />
      </div>

      {/* Conversation History */}
      <div className="mb-6 bg-white rounded-lg p-4 max-h-96 overflow-y-auto">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">Conversation</h2>
        
        {conversationHistory.length === 0 ? (
          <p className="text-gray-500 text-center py-8">Start speaking to begin...</p>
        ) : (
          <div className="space-y-4">
            {conversationHistory.map((msg, idx) => (
              <div
                key={idx}
                className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-xs px-4 py-2 rounded-lg ${
                    msg.type === 'user'
                      ? 'bg-blue-600 text-white rounded-br-none'
                      : 'bg-gray-200 text-gray-800 rounded-bl-none'
                  }`}
                >
                  <p className="text-sm">{msg.text}</p>
                  <span className="text-xs opacity-70">
                    {msg.timestamp.toLocaleTimeString()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Processing Indicator */}
      {isProcessing && (
        <div className="flex items-center justify-center gap-2 p-4 bg-blue-100 rounded-lg mb-6">
          <Loader className="animate-spin text-blue-600" size={20} />
          <span className="text-blue-700">Processing your command...</span>
        </div>
      )}

      {/* Response Display */}
      {response && (
        <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
          <h3 className="font-semibold text-green-800 mb-2">Response</h3>
          <p className="text-green-700 mb-4">{response}</p>
          
          {audioUrl && (
            <AudioPlaybackComponent
              audioUrl={audioUrl}
              autoPlay={true}
              onComplete={() => {}}
            />
          )}
        </div>
      )}

      {/* Transcript Display */}
      {transcript && (
        <div className="p-4 bg-gray-50 border border-gray-200 rounded-lg">
          <h3 className="font-semibold text-gray-800 mb-2">Transcription</h3>
          <p className="text-gray-700">{transcript}</p>
        </div>
      )}
    </div>
  );
};
