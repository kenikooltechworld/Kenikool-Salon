import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { 
  FileText, 
  Download, 
  TrendingUp, 
  BarChart3, 
  PieChart, 
  Calendar,
  Filter,
  Eye,
  RefreshCw
} from 'lucide-react';
import { 
  useGenerateCashFlowStatement,
  useGenerateComparisonReport,
  useGenerateEnhancedReport,
  useGetReportVisualization,
  useGetReportDrillDown
} from '@/lib/api/hooks/useAccounting';
import { toast } from 'sonner';

const DATE_PRESETS = [
  { value: 'today', label: 'Today' },
  { value: 'yesterday', label: 'Yesterday' },
  { value: 'this_week', label: 'This Week' },
  { value: 'last_week', label: 'Last Week' },
  { value: 'this_month', label: 'This Month' },
  { value: 'last_month', label: 'Last Month' },
  { value: 'this_quarter', label: 'This Quarter' },
  { value: 'last_quarter', label: 'Last Quarter' },
  { value: 'this_year', label: 'This Year' },
  { value: 'last_year', label: 'Last Year' },
  { value: 'ytd', label: 'Year to Date' },
  { value: 'qtd', label: 'Quarter to Date' },
  { value: 'custom', label: 'Custom Range' }
];

const REPORT_TYPES = [
  { value: 'balance_sheet', label: 'Balance Sheet' },
  { value: 'income_statement', label: 'Income Statement' },
  { value: 'trial_balance', label: 'Trial Balance' },
  { value: 'cash_flow', label: 'Cash Flow Statement' }
];

const EXPORT_FORMATS = [
  { value: 'json', label: 'View Online' },
  { value: 'pdf', label: 'PDF' },
  { value: 'excel', label: 'Excel' }
];

const CHART_TYPES = [
  { value: 'line', label: 'Line Chart' },
  { value: 'bar', label: 'Bar Chart' },
  { value: 'pie', label: 'Pie Chart' },
  { value: 'area', label: 'Area Chart' }
];

export default function EnhancedReportsPage() {
  const [activeTab, setActiveTab] = useState('enhanced');
  
  // Enhanced Report State
  const [enhancedForm, setEnhancedForm] = useState({
    report_type: '',
    date_preset: 'this_month',
    start_date: '',
    end_date: '',
    comparison_period: false,
    comparison_start_date: '',
    comparison_end_date: '',
    format: 'json',
    include_zero_balances: false,
    account_ids: [] as string[]
  });

  // Cash Flow State
  const [cashFlowForm, setCashFlowForm] = useState({
    start_date: '',
    end_date: '',
    method: 'indirect',
    format: 'json'
  });

  // Comparison Report State
  const [comparisonForm, setComparisonForm] = useState({
    report_type: '',
    current_start_date: '',
    current_end_date: '',
    comparison_start_date: '',
    comparison_end_date: '',
    format: 'json'
  });

  // Visualization State
  const [visualizationForm, setVisualizationForm] = useState({
    report_type: '',
    chart_type: 'bar',
    start_date: '',
    end_date: '',
    group_by: 'month',
    account_ids: [] as string[]
  });

  // Report Results State
  const [reportResults, setReportResults] = useState<any>(null);
  const [visualizationData, setVisualizationData] = useState<any>(null);

  // Mutations
  const generateEnhancedReport = useGenerateEnhancedReport();
  const generateCashFlow = useGenerateCashFlowStatement();
  const generateComparison = useGenerateComparisonReport();
  const getVisualization = useGetReportVisualization();
  const getDrillDown = useGetReportDrillDown();

  const handleEnhancedReportSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!enhancedForm.report_type) {
      toast.error('Please select a report type');
      return;
    }

    try {
      const result = await generateEnhancedReport.mutateAsync(enhancedForm);
      if (enhancedForm.format === 'json') {
        setReportResults(result);
        toast.success('Report generated successfully');
      } else {
        toast.success('Report downloaded successfully');
      }
    } catch (error) {
      console.error('Error generating enhanced report:', error);
    }
  };

  const handleCashFlowSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!cashFlowForm.start_date || !cashFlowForm.end_date) {
      toast.error('Please select start and end dates');
      return;
    }

    try {
      const result = await generateCashFlow.mutateAsync(cashFlowForm);
      if (cashFlowForm.format === 'json') {
        setReportResults(result);
        toast.success('Cash flow statement generated successfully');
      } else {
        toast.success('Cash flow statement downloaded successfully');
      }
    } catch (error) {
      console.error('Error generating cash flow:', error);
    }
  };

  const handleComparisonSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!comparisonForm.report_type || !comparisonForm.current_start_date || 
        !comparisonForm.current_end_date || !comparisonForm.comparison_start_date || 
        !comparisonForm.comparison_end_date) {
      toast.error('Please fill in all required fields');
      return;
    }

    try {
      const result = await generateComparison.mutateAsync(comparisonForm);
      if (comparisonForm.format === 'json') {
        setReportResults(result);
        toast.success('Comparison report generated successfully');
      } else {
        toast.success('Comparison report downloaded successfully');
      }
    } catch (error) {
      console.error('Error generating comparison report:', error);
    }
  };

  const handleVisualizationSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!visualizationForm.report_type || !visualizationForm.start_date || !visualizationForm.end_date) {
      toast.error('Please fill in all required fields');
      return;
    }

    try {
      const result = await getVisualization.mutateAsync(visualizationForm);
      setVisualizationData(result);
      toast.success('Visualization data generated successfully');
    } catch (error) {
      console.error('Error generating visualization:', error);
    }
  };

  const renderReportResults = () => {
    if (!reportResults) return null;

    return (
      <Card className="mt-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Report Results
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Report metadata */}
            <div className="flex flex-wrap gap-2">
              <Badge variant="outline">
                Type: {reportResults.report_type?.replace('_', ' ').toUpperCase()}
              </Badge>
              {reportResults.period && (
                <Badge variant="outline">
                  Period: {reportResults.period.start_date} to {reportResults.period.end_date}
                </Badge>
              )}
              {reportResults.method && (
                <Badge variant="outline">
                  Method: {reportResults.method}
                </Badge>
              )}
            </div>

            {/* Cash Flow Results */}
            {reportResults.cash_flows && (
              <div className="space-y-4">
                {Object.entries(reportResults.cash_flows).map(([key, category]: [string, any]) => (
                  <div key={key} className="border rounded-lg p-4">
                    <h4 className="font-semibold text-lg mb-2">{category.name}</h4>
                    {category.items && category.items.length > 0 ? (
                      <div className="space-y-2">
                        {category.items.map((item: any, index: number) => (
                          <div key={index} className="flex justify-between items-center py-1">
                            <span>{item.description}</span>
                            <span className={`font-medium`}>
                              ${item.amount.toLocaleString()}
                            </span>
                          </div>
                        ))}
                        <Separator />
                        <div className="flex justify-between items-center font-semibold">
                          <span>Total {category.name}</span>
                          <span className={`font-medium`}>
                            ${category.total.toLocaleString()}
                          </span>
                        </div>
                      </div>
                    ) : (
                      <p className="text-muted-foreground">No transactions in this category</p>
                    )}
                  </div>
                ))}
                
                {reportResults.net_cash_flow !== undefined && (
                  <div className="border-2 border-primary rounded-lg p-4 bg-primary/5">
                    <div className="flex justify-between items-center text-lg font-bold">
                      <span>Net Cash Flow</span>
                      <span className={`font-medium`}>
                        ${reportResults.net_cash_flow.toLocaleString()}
                      </span>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Comparison Results */}
            {reportResults.variances && (
              <div className="space-y-4">
                <h4 className="font-semibold text-lg">Variance Analysis</h4>
                <div className="overflow-x-auto">
                  <table className="w-full border-collapse border border-border">
                    <thead>
                      <tr className="bg-muted">
                        <th className="border border-border px-4 py-2 text-left">Account</th>
                        <th className="border border-border px-4 py-2 text-right">Current</th>
                        <th className="border border-border px-4 py-2 text-right">Comparison</th>
                        <th className="border border-border px-4 py-2 text-right">Variance $</th>
                        <th className="border border-border px-4 py-2 text-right">Variance %</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(reportResults.variances).map(([account, variance]: [string, any]) => (
                        <tr key={account}>
                          <td className={`border border-border px-4 py-2`}>
                            {account.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                          </td>
                          <td className={`border border-border px-4 py-2 text-right`}>
                            ${variance.current.toLocaleString()}
                          </td>
                          <td className={`border border-border px-4 py-2 text-right`}>
                            ${variance.comparison.toLocaleString()}
                          </td>
                          <td className={`border border-border px-4 py-2 text-right font-medium`}>
                            ${variance.variance_amount.toLocaleString()}
                          </td>
                          <td className={`border border-border px-4 py-2 text-right font-medium`}>
                            {variance.variance_percent.toFixed(1)}%
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Generic data display */}
            {reportResults.data && typeof reportResults.data === 'object' && (
              <div className="space-y-4">
                <h4 className="font-semibold text-lg">Financial Data</h4>
                <div className="grid gap-4">
                  {Object.entries(reportResults.data).map(([key, value]: [string, any]) => (
                    <div key={key} className="flex justify-between items-center py-2 border-b">
                      <span className="font-medium">
                        {key.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </span>
                      <span className="text-right">
                        {typeof value === 'number' ? `$${value.toLocaleString()}` : value}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    );
  };

  return (
    <div className="container mx-auto py-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Enhanced Financial Reports</h1>
        <p className="text-muted-foreground">
          Generate comprehensive financial reports with advanced features like period comparison, 
          drill-down capabilities, and multiple export formats.
        </p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="enhanced" className="flex items-center gap-2">
            <TrendingUp className="h-4 w-4" />
            Enhanced Reports
          </TabsTrigger>
          <TabsTrigger value="cashflow" className="flex items-center gap-2">
            <BarChart3 className="h-4 w-4" />
            Cash Flow
          </TabsTrigger>
          <TabsTrigger value="comparison" className="flex items-center gap-2">
            <RefreshCw className="h-4 w-4" />
            Comparison
          </TabsTrigger>
          <TabsTrigger value="visualization" className="flex items-center gap-2">
            <PieChart className="h-4 w-4" />
            Visualization
          </TabsTrigger>
        </TabsList>

        {/* Enhanced Reports Tab */}
        <TabsContent value="enhanced">
          <Card>
            <CardHeader>
              <CardTitle>Enhanced Financial Reports</CardTitle>
              <CardDescription>
                Generate financial reports with date presets, comparison periods, and multiple export formats.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleEnhancedReportSubmit} className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="report_type">Report Type *</Label>
                    <Select
                      value={enhancedForm.report_type}
                      onValueChange={(value) => setEnhancedForm(prev => ({ ...prev, report_type: value }))}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select report type" />
                      </SelectTrigger>
                      <SelectContent>
                        {REPORT_TYPES.map(type => (
                          <SelectItem key={type.value} value={type.value}>
                            {type.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="date_preset">Date Range</Label>
                    <Select
                      value={enhancedForm.date_preset}
                      onValueChange={(value) => setEnhancedForm(prev => ({ ...prev, date_preset: value }))}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {DATE_PRESETS.map(preset => (
                          <SelectItem key={preset.value} value={preset.value}>
                            {preset.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                {enhancedForm.date_preset === 'custom' && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="start_date">Start Date</Label>
                      <Input
                        id="start_date"
                        type="date"
                        value={enhancedForm.start_date}
                        onChange={(e) => setEnhancedForm(prev => ({ ...prev, start_date: e.target.value }))}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="end_date">End Date</Label>
                      <Input
                        id="end_date"
                        type="date"
                        value={enhancedForm.end_date}
                        onChange={(e) => setEnhancedForm(prev => ({ ...prev, end_date: e.target.value }))}
                      />
                    </div>
                  </div>
                )}

                <div className="space-y-4">
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="comparison_period"
                      checked={enhancedForm.comparison_period}
                      onCheckedChange={(checked) => 
                        setEnhancedForm(prev => ({ ...prev, comparison_period: checked as boolean }))
                      }
                    />
                    <Label htmlFor="comparison_period">Include comparison period</Label>
                  </div>

                  {enhancedForm.comparison_period && (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pl-6">
                      <div className="space-y-2">
                        <Label htmlFor="comparison_start_date">Comparison Start Date</Label>
                        <Input
                          id="comparison_start_date"
                          type="date"
                          value={enhancedForm.comparison_start_date}
                          onChange={(e) => setEnhancedForm(prev => ({ ...prev, comparison_start_date: e.target.value }))}
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="comparison_end_date">Comparison End Date</Label>
                        <Input
                          id="comparison_end_date"
                          type="date"
                          value={enhancedForm.comparison_end_date}
                          onChange={(e) => setEnhancedForm(prev => ({ ...prev, comparison_end_date: e.target.value }))}
                        />
                      </div>
                    </div>
                  )}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="format">Export Format</Label>
                    <Select
                      value={enhancedForm.format}
                      onValueChange={(value) => setEnhancedForm(prev => ({ ...prev, format: value }))}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {EXPORT_FORMATS.map(format => (
                          <SelectItem key={format.value} value={format.value}>
                            {format.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="flex items-center space-x-2 pt-8">
                    <Checkbox
                      id="include_zero_balances"
                      checked={enhancedForm.include_zero_balances}
                      onCheckedChange={(checked) => 
                        setEnhancedForm(prev => ({ ...prev, include_zero_balances: checked as boolean }))
                      }
                    />
                    <Label htmlFor="include_zero_balances">Include zero balances</Label>
                  </div>
                </div>

                <Button 
                  type="submit" 
                  className="w-full"
                  disabled={generateEnhancedReport.isPending}
                >
                  {generateEnhancedReport.isPending ? (
                    <>
                      <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                      Generating Report...
                    </>
                  ) : (
                    <>
                      <FileText className="mr-2 h-4 w-4" />
                      Generate Enhanced Report
                    </>
                  )}
                </Button>
              </form>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Cash Flow Tab */}
        <TabsContent value="cashflow">
          <Card>
            <CardHeader>
              <CardTitle>Cash Flow Statement</CardTitle>
              <CardDescription>
                Generate detailed cash flow statements with operating, investing, and financing activities.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleCashFlowSubmit} className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="cf_start_date">Start Date *</Label>
                    <Input
                      id="cf_start_date"
                      type="date"
                      value={cashFlowForm.start_date}
                      onChange={(e) => setCashFlowForm(prev => ({ ...prev, start_date: e.target.value }))}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="cf_end_date">End Date *</Label>
                    <Input
                      id="cf_end_date"
                      type="date"
                      value={cashFlowForm.end_date}
                      onChange={(e) => setCashFlowForm(prev => ({ ...prev, end_date: e.target.value }))}
                      required
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="method">Method</Label>
                    <Select
                      value={cashFlowForm.method}
                      onValueChange={(value) => setCashFlowForm(prev => ({ ...prev, method: value }))}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="indirect">Indirect Method</SelectItem>
                        <SelectItem value="direct">Direct Method</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="cf_format">Export Format</Label>
                    <Select
                      value={cashFlowForm.format}
                      onValueChange={(value) => setCashFlowForm(prev => ({ ...prev, format: value }))}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {EXPORT_FORMATS.map(format => (
                          <SelectItem key={format.value} value={format.value}>
                            {format.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <Button 
                  type="submit" 
                  className="w-full"
                  disabled={generateCashFlow.isPending}
                >
                  {generateCashFlow.isPending ? (
                    <>
                      <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                      Generating Cash Flow...
                    </>
                  ) : (
                    <>
                      <BarChart3 className="mr-2 h-4 w-4" />
                      Generate Cash Flow Statement
                    </>
                  )}
                </Button>
              </form>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Comparison Tab */}
        <TabsContent value="comparison">
          <Card>
            <CardHeader>
              <CardTitle>Period Comparison Reports</CardTitle>
              <CardDescription>
                Compare financial data between two periods with variance analysis.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleComparisonSubmit} className="space-y-6">
                <div className="space-y-2">
                  <Label htmlFor="comp_report_type">Report Type *</Label>
                  <Select
                    value={comparisonForm.report_type}
                    onValueChange={(value) => setComparisonForm(prev => ({ ...prev, report_type: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select report type" />
                    </SelectTrigger>
                    <SelectContent>
                      {REPORT_TYPES.map(type => (
                        <SelectItem key={type.value} value={type.value}>
                          {type.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-4">
                  <h4 className="font-semibold">Current Period</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="current_start_date">Start Date *</Label>
                      <Input
                        id="current_start_date"
                        type="date"
                        value={comparisonForm.current_start_date}
                        onChange={(e) => setComparisonForm(prev => ({ ...prev, current_start_date: e.target.value }))}
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="current_end_date">End Date *</Label>
                      <Input
                        id="current_end_date"
                        type="date"
                        value={comparisonForm.current_end_date}
                        onChange={(e) => setComparisonForm(prev => ({ ...prev, current_end_date: e.target.value }))}
                        required
                      />
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <h4 className="font-semibold">Comparison Period</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="comparison_start_date">Start Date *</Label>
                      <Input
                        id="comparison_start_date"
                        type="date"
                        value={comparisonForm.comparison_start_date}
                        onChange={(e) => setComparisonForm(prev => ({ ...prev, comparison_start_date: e.target.value }))}
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="comparison_end_date">End Date *</Label>
                      <Input
                        id="comparison_end_date"
                        type="date"
                        value={comparisonForm.comparison_end_date}
                        onChange={(e) => setComparisonForm(prev => ({ ...prev, comparison_end_date: e.target.value }))}
                        required
                      />
                    </div>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="comp_format">Export Format</Label>
                  <Select
                    value={comparisonForm.format}
                    onValueChange={(value) => setComparisonForm(prev => ({ ...prev, format: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {EXPORT_FORMATS.map(format => (
                        <SelectItem key={format.value} value={format.value}>
                          {format.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <Button 
                  type="submit" 
                  className="w-full"
                  disabled={generateComparison.isPending}
                >
                  {generateComparison.isPending ? (
                    <>
                      <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                      Generating Comparison...
                    </>
                  ) : (
                    <>
                      <RefreshCw className="mr-2 h-4 w-4" />
                      Generate Comparison Report
                    </>
                  )}
                </Button>
              </form>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Visualization Tab */}
        <TabsContent value="visualization">
          <Card>
            <CardHeader>
              <CardTitle>Report Visualizations</CardTitle>
              <CardDescription>
                Generate interactive charts and visualizations for financial data.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleVisualizationSubmit} className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="viz_report_type">Report Type *</Label>
                    <Select
                      value={visualizationForm.report_type}
                      onValueChange={(value) => setVisualizationForm(prev => ({ ...prev, report_type: value }))}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select report type" />
                      </SelectTrigger>
                      <SelectContent>
                        {REPORT_TYPES.map(type => (
                          <SelectItem key={type.value} value={type.value}>
                            {type.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="chart_type">Chart Type</Label>
                    <Select
                      value={visualizationForm.chart_type}
                      onValueChange={(value) => setVisualizationForm(prev => ({ ...prev, chart_type: value }))}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {CHART_TYPES.map(type => (
                          <SelectItem key={type.value} value={type.value}>
                            {type.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="viz_start_date">Start Date *</Label>
                    <Input
                      id="viz_start_date"
                      type="date"
                      value={visualizationForm.start_date}
                      onChange={(e) => setVisualizationForm(prev => ({ ...prev, start_date: e.target.value }))}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="viz_end_date">End Date *</Label>
                    <Input
                      id="viz_end_date"
                      type="date"
                      value={visualizationForm.end_date}
                      onChange={(e) => setVisualizationForm(prev => ({ ...prev, end_date: e.target.value }))}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="group_by">Group By</Label>
                    <Select
                      value={visualizationForm.group_by}
                      onValueChange={(value) => setVisualizationForm(prev => ({ ...prev, group_by: value }))}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="day">Day</SelectItem>
                        <SelectItem value="week">Week</SelectItem>
                        <SelectItem value="month">Month</SelectItem>
                        <SelectItem value="quarter">Quarter</SelectItem>
                        <SelectItem value="year">Year</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <Button 
                  type="submit" 
                  className="w-full"
                  disabled={getVisualization.isPending}
                >
                  {getVisualization.isPending ? (
                    <>
                      <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                      Generating Visualization...
                    </>
                  ) : (
                    <>
                      <PieChart className="mr-2 h-4 w-4" />
                      Generate Visualization
                    </>
                  )}
                </Button>
              </form>

              {visualizationData && (
                <div className="mt-6 p-4 border rounded-lg">
                  <h4 className="font-semibold mb-2">Visualization Data Generated</h4>
                  <p className="text-sm text-muted-foreground">
                    Chart data has been generated. In a production environment, this would be 
                    rendered using a charting library like Chart.js or Recharts.
                  </p>
                  <pre className="mt-2 p-2 bg-muted rounded text-xs overflow-auto max-h-40">
                    {JSON.stringify(visualizationData, null, 2)}
                  </pre>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Render report results */}
      {renderReportResults()}
    </div>
  );
}