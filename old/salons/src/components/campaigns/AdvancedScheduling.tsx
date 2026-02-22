import React, { useState } from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Clock, Zap } from 'lucide-react';

interface AdvancedSchedulingProps {
  onSave: (config: any) => Promise<void>;
}

const DAYS_OF_WEEK = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
const TRIGGER_EVENTS = [
  { id: 'post_booking', label: 'Post-Booking', description: 'Send after booking confirmation' },
  { id: 'post_visit', label: 'Post-Visit', description: 'Send after service completion' },
  { id: 'anniversary', label: 'Anniversary', description: 'Send on client anniversary' },
];

export const RecurrenceSelector: React.FC<{
  value?: any;
  onChange: (value: any) => void;
}> = ({ value, onChange }) => {
  const [recurrenceType, setRecurrenceType] = useState(value?.type || 'none');
  const [dayOfWeek, setDayOfWeek] = useState(value?.day_of_week || 0);
  const [dayOfMonth, setDayOfMonth] = useState(value?.day_of_month || 1);

  const handleChange = () => {
    if (recurrenceType === 'none') {
      onChange(null);
    } else if (recurrenceType === 'daily') {
      onChange({ type: 'daily' });
    } else if (recurrenceType === 'weekly') {
      onChange({ type: 'weekly', day_of_week: dayOfWeek });
    } else if (recurrenceType === 'monthly') {
      onChange({ type: 'monthly', day_of_month: dayOfMonth });
    }
  };

  React.useEffect(() => {
    handleChange();
  }, [recurrenceType, dayOfWeek, dayOfMonth]);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Clock className="h-5 w-5" />
          Recurrence
        </CardTitle>
        <CardDescription>Set up recurring campaign execution</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <label className="text-sm font-medium">Recurrence Type</label>
          <Select value={recurrenceType} onValueChange={setRecurrenceType}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="none">No Recurrence</SelectItem>
              <SelectItem value="daily">Daily</SelectItem>
              <SelectItem value="weekly">Weekly</SelectItem>
              <SelectItem value="monthly">Monthly</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {recurrenceType === 'weekly' && (
          <div>
            <label className="text-sm font-medium">Day of Week</label>
            <Select value={String(dayOfWeek)} onValueChange={v => setDayOfWeek(parseInt(v))}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {DAYS_OF_WEEK.map((day, idx) => (
                  <SelectItem key={idx} value={String(idx)}>
                    {day}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        )}

        {recurrenceType === 'monthly' && (
          <div>
            <label className="text-sm font-medium">Day of Month</label>
            <Select value={String(dayOfMonth)} onValueChange={v => setDayOfMonth(parseInt(v))}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {Array.from({ length: 31 }, (_, i) => i + 1).map(day => (
                  <SelectItem key={day} value={String(day)}>
                    Day {day}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        )}

        {recurrenceType !== 'none' && (
          <div className="p-3 bg-blue-50 rounded-lg">
            <p className="text-sm text-blue-700">
              {recurrenceType === 'daily' && 'Campaign will run every day'}
              {recurrenceType === 'weekly' && `Campaign will run every ${DAYS_OF_WEEK[dayOfWeek]}`}
              {recurrenceType === 'monthly' && `Campaign will run on day ${dayOfMonth} of each month`}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export const TriggerSelector: React.FC<{
  value?: any;
  onChange: (value: any) => void;
}> = ({ value, onChange }) => {
  const [selectedTrigger, setSelectedTrigger] = useState(value?.event || null);
  const [delayDays, setDelayDays] = useState(value?.delay_days || 0);

  const handleChange = () => {
    if (selectedTrigger) {
      onChange({ event: selectedTrigger, delay_days: delayDays });
    } else {
      onChange(null);
    }
  };

  React.useEffect(() => {
    handleChange();
  }, [selectedTrigger, delayDays]);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Zap className="h-5 w-5" />
          Trigger Events
        </CardTitle>
        <CardDescription>Send campaign when specific events occur</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-3">
          {TRIGGER_EVENTS.map(trigger => (
            <div key={trigger.id} className="flex items-start space-x-3 p-3 border rounded-lg hover:bg-gray-50">
              <Checkbox
                id={trigger.id}
                checked={selectedTrigger === trigger.id}
                onCheckedChange={() => setSelectedTrigger(selectedTrigger === trigger.id ? null : trigger.id)}
              />
              <div className="flex-1">
                <label htmlFor={trigger.id} className="font-medium cursor-pointer">
                  {trigger.label}
                </label>
                <p className="text-sm text-gray-600">{trigger.description}</p>
              </div>
            </div>
          ))}
        </div>

        {selectedTrigger && (
          <div>
            <label className="text-sm font-medium">Delay (days)</label>
            <Select value={String(delayDays)} onValueChange={v => setDelayDays(parseInt(v))}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {Array.from({ length: 31 }, (_, i) => i).map(day => (
                  <SelectItem key={day} value={String(day)}>
                    {day === 0 ? 'Immediately' : `${day} day${day > 1 ? 's' : ''} later`}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        )}

        {selectedTrigger && (
          <div className="p-3 bg-green-50 rounded-lg">
            <p className="text-sm text-green-700">
              Campaign will send {delayDays === 0 ? 'immediately' : `${delayDays} days`} after {TRIGGER_EVENTS.find(t => t.id === selectedTrigger)?.label.toLowerCase()}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export const OptimalSendTime: React.FC<{
  value?: boolean;
  onChange: (value: boolean) => void;
}> = ({ value, onChange }) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Optimal Send Time</CardTitle>
        <CardDescription>Send at the best time for each client</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex items-center space-x-3 p-3 border rounded-lg">
          <Checkbox
            id="optimal-time"
            checked={value || false}
            onCheckedChange={onChange}
          />
          <div className="flex-1">
            <label htmlFor="optimal-time" className="font-medium cursor-pointer">
              Use Optimal Send Time
            </label>
            <p className="text-sm text-gray-600">
              Analyze client engagement patterns and send at their most active time
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export const AdvancedScheduling: React.FC<AdvancedSchedulingProps> = ({ onSave }) => {
  const [recurrence, setRecurrence] = useState<any>(null);
  const [trigger, setTrigger] = useState<any>(null);
  const [useOptimalTime, setUseOptimalTime] = useState(false);

  const handleSave = async () => {
    await onSave({
      recurrence,
      trigger,
      use_optimal_send_time: useOptimalTime,
    });
  };

  return (
    <div className="space-y-4">
      <Tabs defaultValue="recurrence" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="recurrence">Recurrence</TabsTrigger>
          <TabsTrigger value="trigger">Triggers</TabsTrigger>
          <TabsTrigger value="timing">Timing</TabsTrigger>
        </TabsList>

        <TabsContent value="recurrence" className="space-y-4">
          <RecurrenceSelector value={recurrence} onChange={setRecurrence} />
        </TabsContent>

        <TabsContent value="trigger" className="space-y-4">
          <TriggerSelector value={trigger} onChange={setTrigger} />
        </TabsContent>

        <TabsContent value="timing" className="space-y-4">
          <OptimalSendTime value={useOptimalTime} onChange={setUseOptimalTime} />
        </TabsContent>
      </Tabs>

      <Button onClick={handleSave} className="w-full">
        Save Advanced Scheduling
      </Button>
    </div>
  );
};
