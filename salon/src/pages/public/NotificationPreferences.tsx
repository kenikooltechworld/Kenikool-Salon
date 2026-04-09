import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Spinner } from "@/components/ui/spinner";
import { CheckCircle, AlertCircle } from "@/components/icons";

interface NotificationPreferences {
  send_confirmation_email: boolean;
  send_24h_reminder_email: boolean;
  send_1h_reminder_email: boolean;
  send_sms_reminders: boolean;
}

export default function NotificationPreferences() {
  const { bookingId } = useParams<{ bookingId: string }>();
  const navigate = useNavigate();

  const [preferences, setPreferences] = useState<NotificationPreferences>({
    send_confirmation_email: true,
    send_24h_reminder_email: true,
    send_1h_reminder_email: true,
    send_sms_reminders: false,
  });

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Load current preferences
    const loadPreferences = async () => {
      try {
        setLoading(true);
        const response = await fetch(
          `/api/public/bookings/${bookingId}/notification-preferences`,
        );

        if (response.ok) {
          const data = await response.json();
          setPreferences(data);
        } else if (response.status === 404) {
          // Preferences don't exist yet, use defaults
          setPreferences({
            send_confirmation_email: true,
            send_24h_reminder_email: true,
            send_1h_reminder_email: true,
            send_sms_reminders: false,
          });
        } else {
          setError("Failed to load notification preferences");
        }
      } catch (err) {
        console.error("Error loading preferences:", err);
        setError("Failed to load notification preferences");
      } finally {
        setLoading(false);
      }
    };

    if (bookingId) {
      loadPreferences();
    }
  }, [bookingId]);

  const handleToggle = (key: keyof NotificationPreferences) => {
    setPreferences((prev) => ({
      ...prev,
      [key]: !prev[key],
    }));
    setSuccess(false);
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setError(null);
      setSuccess(false);

      const response = await fetch(
        `/api/public/bookings/${bookingId}/notification-preferences`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(preferences),
        },
      );

      if (response.ok) {
        setSuccess(true);
        setTimeout(() => {
          navigate(`/booking/${bookingId}`);
        }, 2000);
      } else {
        const data = await response.json();
        setError(data.detail || "Failed to save preferences");
      }
    } catch (err) {
      console.error("Error saving preferences:", err);
      setError("Failed to save preferences");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Spinner />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4">
      <div className="max-w-2xl mx-auto">
        <Card>
          <CardHeader>
            <CardTitle>Notification Preferences</CardTitle>
            <CardDescription>
              Manage how you receive notifications about your booking
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {error && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            {success && (
              <Alert className="bg-green-50 border-green-200">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <AlertDescription className="text-green-800">
                  Preferences saved successfully! Redirecting...
                </AlertDescription>
              </Alert>
            )}

            <div className="space-y-4">
              {/* Confirmation Email */}
              <div className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition">
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900">
                    Confirmation Email
                  </h3>
                  <p className="text-sm text-gray-600">
                    Receive an email confirming your booking
                  </p>
                </div>
                <Switch
                  checked={preferences.send_confirmation_email}
                  onCheckedChange={() =>
                    handleToggle("send_confirmation_email")
                  }
                  disabled={saving}
                />
              </div>

              {/* 24-Hour Reminder */}
              <div className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition">
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900">
                    24-Hour Reminder
                  </h3>
                  <p className="text-sm text-gray-600">
                    Get reminded 24 hours before your appointment
                  </p>
                </div>
                <Switch
                  checked={preferences.send_24h_reminder_email}
                  onCheckedChange={() =>
                    handleToggle("send_24h_reminder_email")
                  }
                  disabled={saving}
                />
              </div>

              {/* 1-Hour Reminder */}
              <div className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition">
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900">
                    1-Hour Reminder
                  </h3>
                  <p className="text-sm text-gray-600">
                    Get reminded 1 hour before your appointment
                  </p>
                </div>
                <Switch
                  checked={preferences.send_1h_reminder_email}
                  onCheckedChange={() => handleToggle("send_1h_reminder_email")}
                  disabled={saving}
                />
              </div>

              {/* SMS Reminders */}
              <div className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition">
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900">SMS Reminders</h3>
                  <p className="text-sm text-gray-600">
                    Receive SMS reminders in addition to emails
                  </p>
                </div>
                <Switch
                  checked={preferences.send_sms_reminders}
                  onCheckedChange={() => handleToggle("send_sms_reminders")}
                  disabled={saving}
                />
              </div>
            </div>

            <div className="flex gap-3 pt-6">
              <Button onClick={handleSave} disabled={saving} className="flex-1">
                {saving ? (
                  <>
                    <Spinner className="mr-2 h-4 w-4" />
                    Saving...
                  </>
                ) : (
                  "Save Preferences"
                )}
              </Button>
              <Button
                variant="outline"
                onClick={() => navigate(`/booking/${bookingId}`)}
                disabled={saving}
              >
                Cancel
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
