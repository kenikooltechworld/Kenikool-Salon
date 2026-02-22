import { VoiceAssistantUI } from "@/components/voice/voice-assistant-ui";
import { Card } from "@/components/ui/card";
import { MicIcon, SparklesIcon } from "@/components/icons";

export default function VoiceAssistantPage() {
  return (
    <div className="p-8 space-y-6">
      {/* Page Header */}
      <div className="flex items-center space-x-3">
        <div className="p-3 bg-gradient-to-br from-blue-500 to-purple-500 rounded-lg">
          <MicIcon className="h-6 w-6 text-white" />
        </div>
        <div>
          <h1 className="text-3xl font-bold">Voice Assistant</h1>
          <p className="text-gray-600">
            Manage your salon with voice commands in multiple languages
          </p>
        </div>
      </div>

      {/* Features Info */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="p-4">
          <div className="flex items-center space-x-3">
            <SparklesIcon className="h-8 w-8 text-blue-500" />
            <div>
              <h3 className="font-semibold">Multilingual</h3>
              <p className="text-sm text-gray-600">
                English, Yoruba, Igbo, Hausa, Pidgin
              </p>
            </div>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center space-x-3">
            <MicIcon className="h-8 w-8 text-green-500" />
            <div>
              <h3 className="font-semibold">Natural Commands</h3>
              <p className="text-sm text-gray-600">
                Speak naturally, no memorization needed
              </p>
            </div>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center space-x-3">
            <SparklesIcon className="h-8 w-8 text-purple-500" />
            <div>
              <h3 className="font-semibold">100% Private</h3>
              <p className="text-sm text-gray-600">
                All processing happens locally
              </p>
            </div>
          </div>
        </Card>
      </div>

      {/* Voice Assistant UI */}
      <VoiceAssistantUI />

      {/* Quick Commands Guide */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">Quick Commands</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <h4 className="font-medium text-sm mb-2">Bookings</h4>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• "Show today's appointments"</li>
              <li>• "Book [client] for [service]"</li>
              <li>• "Who's my next appointment?"</li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium text-sm mb-2">Clients</h4>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• "Show [client]'s history"</li>
              <li>• "Add new client [name]"</li>
              <li>• "How many clients do I have?"</li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium text-sm mb-2">Revenue</h4>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• "Show today's revenue"</li>
              <li>• "How much did I make this week?"</li>
              <li>• "Show top performing services"</li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium text-sm mb-2">Inventory</h4>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• "What products are low?"</li>
              <li>• "How much [product] do I have?"</li>
              <li>• "Which products need reordering?"</li>
            </ul>
          </div>
        </div>
      </Card>
    </div>
  );
}
