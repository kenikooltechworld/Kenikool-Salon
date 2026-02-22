import React, { useState } from 'react';
import { VoiceAssistantUI } from '../../components/voice/VoiceAssistantUI';

export default function VoiceAssistantPage() {
  const [language, setLanguage] = useState('en');
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [response, setResponse] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);

  const handleLanguageChange = (newLanguage: string) => {
    setLanguage(newLanguage);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 p-8">
      <div className="max-w-4xl mx-auto">
        <VoiceAssistantUI
          isListening={isListening}
          transcript={transcript}
          response={response}
          isProcessing={isProcessing}
          language={language}
          onLanguageChange={handleLanguageChange}
        />
      </div>
    </div>
  );
}
