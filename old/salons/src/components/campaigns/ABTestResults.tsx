import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Loader2, Trophy } from 'lucide-react';

interface VariantPerformance {
  total: number;
  delivered: number;
  opened: number;
  clicked: number;
  conversions: number;
  revenue: number;
  open_rate: number;
  click_rate: number;
  conversion_rate: number;
}

interface ABTestResultsProps {
  campaignId: string;
  testId: string;
  onSelectWinner?: (variantId: string) => Promise<void>;
}

export const ABTestResults: React.FC<ABTestResultsProps> = ({
  campaignId,
  testId,
  onSelectWinner,
}) => {
  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectingWinner, setSelectingWinner] = useState(false);

  useEffect(() => {
    fetchResults();
  }, [campaignId, testId]);

  const fetchResults = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/campaigns/${campaignId}/ab-test/results`);
      if (!response.ok) throw new Error('Failed to fetch results');
      const data = await response.json();
      setResults(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load results');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectWinner = async (variantId: string) => {
    if (!onSelectWinner) return;
    try {
      setSelectingWinner(true);
      await onSelectWinner(variantId);
      await fetchResults();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to select winner');
    } finally {
      setSelectingWinner(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  if (!results) {
    return (
      <Card>
        <CardContent className="pt-6 text-center text-gray-500">
          No test results available
        </CardContent>
      </Card>
    );
  }

  const variants = results.variants || [];
  const performance = results.variant_performance || {};
  const winner = results.winner_variant_id;

  // Find best performing variant
  const bestVariant = variants.reduce((best: any, variant: any) => {
    const perf = performance[variant.id];
    const bestPerf = performance[best.id];
    if (!perf || !bestPerf) return best;
    return (perf.conversion_rate || 0) > (bestPerf.conversion_rate || 0) ? variant : best;
  });

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>A/B Test Results</CardTitle>
          <CardDescription>
            {results.name} - Status: <Badge>{results.status}</Badge>
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
              {error}
            </div>
          )}

          {/* Performance Table */}
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Variant</TableHead>
                  <TableHead className="text-right">Sent</TableHead>
                  <TableHead className="text-right">Delivered</TableHead>
                  <TableHead className="text-right">Opened</TableHead>
                  <TableHead className="text-right">Open Rate</TableHead>
                  <TableHead className="text-right">Clicked</TableHead>
                  <TableHead className="text-right">Click Rate</TableHead>
                  <TableHead className="text-right">Conversions</TableHead>
                  <TableHead className="text-right">Conv. Rate</TableHead>
                  <TableHead className="text-right">Revenue</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {variants.map((variant: any) => {
                  const perf = performance[variant.id] || {};
                  const isBest = bestVariant.id === variant.id;
                  const isWinner = winner === variant.id;

                  return (
                    <TableRow key={variant.id} className={isBest ? 'bg-green-50' : ''}>
                      <TableCell className="font-medium">
                        <div className="flex items-center gap-2">
                          {variant.name}
                          {isWinner && (
                            <Trophy className="h-4 w-4 text-yellow-500" />
                          )}
                          {isBest && !isWinner && (
                            <Badge variant="outline">Best</Badge>
                          )}
                        </div>
                      </TableCell>
                      <TableCell className="text-right">{perf.total || 0}</TableCell>
                      <TableCell className="text-right">{perf.delivered || 0}</TableCell>
                      <TableCell className="text-right">{perf.opened || 0}</TableCell>
                      <TableCell className="text-right">{(perf.open_rate || 0).toFixed(1)}%</TableCell>
                      <TableCell className="text-right">{perf.clicked || 0}</TableCell>
                      <TableCell className="text-right">{(perf.click_rate || 0).toFixed(1)}%</TableCell>
                      <TableCell className="text-right">{perf.conversions || 0}</TableCell>
                      <TableCell className="text-right">{(perf.conversion_rate || 0).toFixed(1)}%</TableCell>
                      <TableCell className="text-right">${(perf.revenue || 0).toFixed(2)}</TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </div>

          {/* Winner Selection */}
          {results.status === 'completed' && !winner && (
            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg space-y-4">
              <div>
                <h4 className="font-semibold text-blue-900">Select Winner</h4>
                <p className="text-sm text-blue-700 mt-1">
                  {bestVariant.name} has the best performance. Select it as the winner to use for future sends.
                </p>
              </div>
              <Button
                onClick={() => handleSelectWinner(bestVariant.id)}
                disabled={selectingWinner}
                className="w-full"
              >
                {selectingWinner && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
                Select {bestVariant.name} as Winner
              </Button>
            </div>
          )}

          {winner && (
            <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
              <div className="flex items-center gap-2">
                <Trophy className="h-5 w-5 text-green-600" />
                <div>
                  <h4 className="font-semibold text-green-900">Winner Selected</h4>
                  <p className="text-sm text-green-700">
                    {variants.find((v: any) => v.id === winner)?.name} is the winning variant
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Traffic Split Info */}
          <div className="p-4 bg-gray-50 rounded-lg">
            <h4 className="font-semibold mb-3">Traffic Split</h4>
            <div className="space-y-2">
              {variants.map((variant: any) => {
                const split = results.traffic_split[variant.id] || 0;
                return (
                  <div key={variant.id} className="flex items-center justify-between">
                    <span className="text-sm">{variant.name}</span>
                    <div className="flex items-center gap-2">
                      <div className="w-32 bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-500 h-2 rounded-full"
                          style={{ width: `${split}%` }}
                        />
                      </div>
                      <span className="text-sm font-medium w-12 text-right">{split}%</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
