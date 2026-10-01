import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/components/ui/toast";
import { useSendCustomerMessage } from "@/hooks/useMessages";
import { MessageSquareIcon } from "@/components/icons";

export default function CustomerContactForm() {
  const { showToast } = useToast();
  const sendMessage = useSendCustomerMessage();

  const [subject, setSubject] = useState("");
  const [content, setContent] = useState("");
  const [sendEmail, setSendEmail] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!content.trim()) {
      showToast({
        title: "Error",
        description: "Please enter a message",
        variant: "error",
      });
      return;
    }

    try {
      await sendMessage.mutateAsync({
        recipient_type: "staff",
        notification_type: "custom",
        content: content.trim(),
        subject: subject.trim() || undefined,
        channel: "in_app",
        send_email: sendEmail,
      });

      showToast({
        title: "Success",
        description: "Your message has been sent to the salon team",
        variant: "success",
      });

      setSubject("");
      setContent("");
      setSendEmail(false);
    } catch (error: any) {
      showToast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to send message",
        variant: "error",
      });
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
          <MessageSquareIcon className="w-6 h-6" />
          Contact Us
        </h2>
        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
          Have a question or feedback? Send us a message and we&apos;ll get back to you.
        </p>
      </div>

      <Card className="p-6">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Subject
            </label>
            <Input
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              placeholder="What is this about?"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Message *
            </label>
            <Textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Enter your message..."
              rows={6}
              required
            />
          </div>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="sendEmail"
              checked={sendEmail}
              onChange={(e) => setSendEmail(e.target.checked)}
              className="rounded border-gray-300"
            />
            <label htmlFor="sendEmail" className="text-sm text-gray-700 dark:text-gray-300">
              Also send via email
            </label>
          </div>

          <Button
            type="submit"
            disabled={sendMessage.isPending}
            className="w-full"
          >
            {sendMessage.isPending ? "Sending..." : "Send Message"}
          </Button>
        </form>
      </Card>
    </div>
  );
}
