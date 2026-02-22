import React, { useState } from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Slider } from '@/components/ui/slider';
import { Loader2, Plus, Trash2 } from 'lucide-react';

interface Variant {
  id: string;
  name: string;
  message_content: string;
  traffic_percentage: number;
}

interface ABTestManagerProps {
  campaignId: string;
  onSave: (test: any) => Promise<void>;
  onCancel: () => void;
}

export const ABTestManager: React.FC<ABTestManagerProps> = ({
  campaignId,
  onSave,
  onCancel,
}) => {
  const [testName, setTestName] = useState('');
  const [variants, setVariants] = useState<Variant[]>([
    { id: '1', name: 'Variant A', message_content: '', traffic_percentage: 50 },
    { id: '2', name: 'Variant B', message_content: '', traffic_percentage: 50 },
  ]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAddVariant = () => {
    const newId = String(Math.max(...variants.map(v => parseInt(v.id)), 0) + 1);
    setVariants(prev => [
      ...prev,
      { id: newId, name: `Variant ${String.fromCharCode(65 + prev.length)}`, message_content: '', traffic_percentage: 0 },
    ]);
  };

  const handleRemoveVariant = (id: string) => {
    if (variants.length > 2) {
      setVariants(prev => prev.filter(v => v.id !== id));
    }
  };

  const handleVariantChange = (id: string, field: string, value: any) => {
    setVariants(prev =>
      prev.map(v => v.id === id ? { ...v, [field]: value } : v)
    );
  };

  const handleTrafficChange = (id: string, percentage: number) => {
    const remaining = 100 - percentage;
    const otherVariants = variants.filter(v => v.id !== id);
    
    if (otherVariants.length === 1) {
      handleVariantChange(id, 'traffic_percentage', percentage);
      handleVariantChange(otherVariants[0].id, 'traffic_percentage', remaining);
    } else {
      handleVariantChange(id, 'traffic_percentage', percentage);
    }
  };

  const totalTraffic = variants.reduce((sum, v) => sum + v.traffic_percentage, 0);
  const isValid = totalTraffic === 100 && testName.trim() && variants.every(v => v.message_content.trim());

  const handleSave = async () => {
    try {
      setLoading(true);
      setError(null);

      if (!testName.trim()) {
        setError('Test name is required');
        return;
      }

      if (variants.length < 2) {
        setError('At least 2 variants are required');
        return;
      }

      if (totalTraffic !== 100) {
        setError(`Traffic split must equal 100% (currently ${totalTraffic}%)`);
        return;
      }

      if (variants.some(v => !v.message_content.trim())) {
        setError('All variants must have message content');
        return;
      }

      const traffic_split = variants.reduce((acc, v) => {
        acc[v.id] = v.traffic_percentage;
        return acc;
      }, {} as Record<string, number>);

      await onSave({
        name: testName,
        variants: variants.map(({ traffic_percentage, ...rest }) => rest),
        traffic_split,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save A/B test');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>A/B Test Configuration</CardTitle>
          <CardDescription>
            Create variants and configure traffic split for testing
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
              {error}
            </div>
          )}

          {/* Test Name */}
          <div>
            <label className="text-sm font-medium">Test Name</label>
            <Input
              value={testName}
              onChange={e => setTestName(e.target.value)}
              placeholder="e.g., Subject Line Test"
            />
          </div>

          {/* Variants */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold">Variants</h3>
              <Button
                size="sm"
                variant="outline"
                onClick={handleAddVariant}
                disabled={variants.length >= 3}
              >
                <Plus className="h-4 w-4 mr-2" />
                Add Variant
              </Button>
            </div>

            <div className="space-y-4">
              {variants.map((variant, index) => (
                <Card key={variant.id} className="p-4">
                  <div className="space-y-4">
                    {/* Variant Header */}
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <Input
                          value={variant.name}
                          onChange={e => handleVariantChange(variant.id, 'name', e.target.value)}
                          placeholder="Variant name"
                          className="font-medium"
                        />
                      </div>
                      {variants.length > 2 && (
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleRemoveVariant(variant.id)}
                          className="ml-2"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      )}
                    </div>

                    {/* Message Content */}
                    <div>
                      <label className="text-sm font-medium">Message Content</label>
                      <Textarea
                        value={variant.message_content}
                        onChange={e => handleVariantChange(variant.id, 'message_content', e.target.value)}
                        placeholder="Enter message content for this variant"
                        rows={3}
                      />
                    </div>

                    {/* Traffic Split */}
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <label className="text-sm font-medium">Traffic Split</label>
                        <Badge variant="outline">{variant.traffic_percentage}%</Badge>
                      </div>
                      <Slider
                        value={[variant.traffic_percentage]}
                        onValueChange={([value]) => handleTrafficChange(variant.id, value)}
                        min={0}
                        max={100}
                        step={5}
                        className="w-full"
                      />
                    </div>
                  </div>
                </Card>
              ))}
            </div>

            {/* Traffic Summary */}
            <div className="p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center justify-between">
                <span className="font-medium">Total Traffic Split</span>
                <Badge variant={totalTraffic === 100 ? 'default' : 'destructive'}>
                  {totalTraffic}%
                </Badge>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-2 pt-4">
            <Button
              onClick={handleSave}
              disabled={loading || !isValid}
              className="flex-1"
            >
              {loading && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
              Create A/B Test
            </Button>
            <Button
              onClick={onCancel}
              variant="outline"
              disabled={loading}
            >
              Cancel
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
