import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  PlusIcon,
  EditIcon,
  RefreshIcon,
  ListIcon,
  EyeIcon,
  TrashIcon,
  TrendingUpIcon,
  TrendingDownIcon,
  CopyIcon
} from '@/components/icons';
import { 
  useGetBudgets,
  useGetBudget,
  useCreateBudget,
  useUpdateBudget,
  useGetBudgetVariance,
  useCopyBudget,
  useGenerateForecast,
  useGetBudgetSummary,
  useGetAccounts
} from '@/lib/api/hooks/useAccounting';
import { toast } from 'sonner';

const BUDGET_STATUSES = {
  draft: { label: 'Draft', variant: 'secondary' },
  active: { label: 'Active', variant: 'success' },
  closed: { label: 'Closed', variant: 'destructive' }
};

const PERIOD_TYPES = {
  monthly: 'Monthly',
  quarterly: 'Quarterly',
  yearly: 'Yearly'
};

export default function BudgetManagementPage() {
  const [activeTab, setActiveTab] = useState('budgets');
  const [selectedBudget, setSelectedBudget] = useState<any>(null);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [showCopyDialog, setShowCopyDialog] = useState(false);
  const [showVarianceDialog, setShowVarianceDialog] = useState(false);
  const [showForecastDialog, setShowForecastDialog] = useState(false);
  
  // Form states
  const [budgetForm, setBudgetForm] = useState({
    name: '',
    description: '',
    budget_year: new Date().getFullYear(),
    period_type: 'yearly' as 'monthly' | 'quarterly' | 'yearly',
    start_date: new Date().getFullYear() + '-01-01',
    end_date: new Date().getFullYear() + '-12-31',
    line_items: [] as any[]
  });
  
  const [copyForm, setCopyForm] = useState({
    source_budget_id: '',
    new_budget_name: '',
    new_budget_year: new Date().getFullYear() + 1,
    adjustment_percentage: 0,
    start_date: (new Date().getFullYear() + 1) + '-01-01',
    end_date: (new Date().getFullYear() + 1) + '-12-31'
  });
  
  const [forecastForm, setForecastForm] = useState({
    account_id: '',
    forecast_periods: 12,
    forecast_method: 'trend'
  });

  // Queries and mutations
  const { data: budgets } = useGetBudgets();
  const { data: accounts } = useGetAccounts();
  const { data: budgetDetails } = useGetBudget(selectedBudget?.id || '');
  const { data: budgetVariance } = useGetBudgetVariance(selectedBudget?.id || '');
  const { data: budgetSummary } = useGetBudgetSummary();
  
  const createBudget = useCreateBudget();
  const updateBudget = useUpdateBudget();
  const copyBudget = useCopyBudget();
  const generateForecast = useGenerateForecast();

  const handleCreateBudget = async () => {
    try {
      await createBudget.mutateAsync(budgetForm);
      setShowCreateDialog(false);
      resetBudgetForm();
      toast.success('Budget created successfully');
    } catch (error) {
      console.error('Error creating budget:', error);
    }
  };

  const handleUpdateBudget = async () => {
    if (!selectedBudget) return;

    try {
      await updateBudget.mutateAsync({
        budget_id: selectedBudget.id,
        data: budgetForm
      });
      setShowEditDialog(false);
      toast.success('Budget updated successfully');
    } catch (error) {
      console.error('Error updating budget:', error);
    }
  };

  const handleCopyBudget = async () => {
    try {
      await copyBudget.mutateAsync(copyForm);
      setShowCopyDialog(false);
      setCopyForm({
        source_budget_id: '',
        new_budget_name: '',
        new_budget_year: new Date().getFullYear() + 1,
        adjustment_percentage: 0,
        start_date: (new Date().getFullYear() + 1) + '-01-01',
        end_date: (new Date().getFullYear() + 1) + '-12-31'
      });
      toast.success('Budget copied successfully');
    } catch (error) {
      console.error('Error copying budget:', error);
    }
  };

  const handleGenerateForecast = async () => {
    try {
      const forecast = await generateForecast.mutateAsync(forecastForm);
      console.log('Forecast generated:', forecast);
      setShowForecastDialog(false);
      toast.success('Forecast generated successfully');
    } catch (error) {
      console.error('Error generating forecast:', error);
    }
  };

  const resetBudgetForm = () => {
    setBudgetForm({
      name: '',
      description: '',
      budget_year: new Date().getFullYear(),
      period_type: 'yearly',
      start_date: new Date().getFullYear() + '-01-01',
      end_date: new Date().getFullYear() + '-12-31',
      line_items: []
    });
  };

  const addLineItem = () => {
    setBudgetForm(prev => ({
      ...prev,
      line_items: [...prev.line_items, {
        account_id: '',
        budgeted_amount: 0,
        notes: ''
      }]
    }));
  };

  const updateLineItem = (index: number, field: string, value: any) => {
    setBudgetForm(prev => ({
      ...prev,
      line_items: prev.line_items.map((item, i) => 
        i === index ? { ...item, [field]: value } : item
      )
    }));
  };

  const removeLineItem = (index: number) => {
    setBudgetForm(prev => ({
      ...prev,
      line_items: prev.line_items.filter((_, i) => i !== index)
    }));
  };

  const calculateBudgetTotal = () => {
    return budgetForm.line_items.reduce((sum, item) => sum + (item.budgeted_amount || 0), 0);
  };

  const renderBudgetCard = (budget: any) => {
    const status = budget.status || 'draft';
    const statusConfig = BUDGET_STATUSES[status as keyof typeof BUDGET_STATUSES];

    return (
      <Card key={budget.id} className="hover:shadow-md transition-shadow">
        <CardContent className="p-4">
          <div className="flex justify-between items-start mb-3">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="font-semibold">{budget.name}</span>
                <Badge variant={statusConfig.variant}>
                  {statusConfig.label}
                </Badge>
              </div>
              <p className="text-sm text-muted-foreground">{budget.description}</p>
              <p className="text-sm text-muted-foreground">
                {PERIOD_TYPES[budget.period_type as keyof typeof PERIOD_TYPES]} • {budget.budget_year}
              </p>
            </div>
            <div className="text-right">
              <p className="font-medium">${budget.total_budgeted?.toLocaleString()}</p>
              <p className="text-sm text-muted-foreground">
                Actual: ${budget.total_actual?.toLocaleString()}
              </p>
            </div>
          </div>
          
          <div className="flex justify-between items-center text-sm mb-3">
            <span>Variance: ${budget.total_variance?.toLocaleString()}</span>
            <div className="flex items-center gap-1">
              {budget.variance_percentage > 0 ? (
                <TrendingUpIcon className="h-4 w-4" />
              ) : (
                <TrendingDownIcon className="h-4 w-4" />
              )}
              <span>
                {Math.abs(budget.variance_percentage || 0).toFixed(1)}%
              </span>
            </div>
          </div>
          
          <div className="flex justify-between items-center">
            <div className="flex space-x-1">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  setSelectedBudget(budget);
                  setShowVarianceDialog(true);
                }}
                className="h-8 w-8 p-0"
              >
                <EyeIcon className="h-4 w-4" />
              </Button>
              
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  setSelectedBudget(budget);
                  setBudgetForm({
                    name: budget.name,
                    description: budget.description || '',
                    budget_year: budget.budget_year,
                    period_type: budget.period_type,
                    start_date: budget.start_date,
                    end_date: budget.end_date,
                    line_items: budget.line_items || []
                  });
                  setShowEditDialog(true);
                }}
                className="h-8 w-8 p-0"
              >
                <EditIcon className="h-4 w-4" />
              </Button>
              
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  setCopyForm(prev => ({
                    ...prev,
                    source_budget_id: budget.id,
                    new_budget_name: `${budget.name} (Copy)`
                  }));
                  setShowCopyDialog(true);
                }}
                className="h-8 w-8 p-0"
              >
                <CopyIcon className="h-4 w-4" />
              </Button>
            </div>
            
            <span className="text-xs text-muted-foreground">
              {budget.created_by}
            </span>
          </div>
        </CardContent>
      </Card>
    );
  };

  return (
    <div className="container mx-auto py-6">
      <div className="mb-6">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold">Budget Management</h1>
            <p className="text-muted-foreground">
              Create and manage budgets, track variances, and generate forecasts.
            </p>
          </div>
          
          <div className="flex space-x-2">
            <Button variant="outline" onClick={() => setShowForecastDialog(true)}>
              <TrendingUpIcon className="h-4 w-4 mr-2" />
              Generate Forecast
            </Button>
            <Button onClick={() => setShowCreateDialog(true)}>
              <PlusIcon className="h-4 w-4 mr-2" />
              Create Budget
            </Button>
          </div>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6" defaultValue="budgets">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="budgets">Budgets</TabsTrigger>
          <TabsTrigger value="variance">Variance Analysis</TabsTrigger>
          <TabsTrigger value="summary">Summary</TabsTrigger>
        </TabsList>

        {/* Budgets Tab */}
        <TabsContent value="budgets">
          <div className="grid gap-4">
            {budgets && budgets.length > 0 ? (
              budgets.map(renderBudgetCard)
            ) : (
              <Card>
                <CardContent className="text-center py-8">
                  <ListIcon className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                  <p className="text-muted-foreground">No budgets found</p>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>

        {/* Variance Analysis Tab */}
        <TabsContent value="variance">
          <Card>
            <CardHeader>
              <CardTitle>Budget Variance Analysis</CardTitle>
              <CardDescription>
                Compare budgeted vs actual amounts across all active budgets.
              </CardDescription>
            </CardHeader>
            <CardContent>
              {budgets && budgets.filter(b => b.status === 'active').length > 0 ? (
                <div className="space-y-4">
                  {budgets.filter(b => b.status === 'active').map((budget: any) => (
                    <div key={budget.id} className="border rounded-lg p-4">
                      <div className="flex justify-between items-center mb-2">
                        <h4 className="font-semibold">{budget.name}</h4>
                        <Badge variant={budget.variance_percentage > 0 ? 'destructive' : 'success'}>
                          {budget.variance_percentage > 0 ? 'Over Budget' : 'Under Budget'}
                        </Badge>
                      </div>
                      
                      <div className="grid grid-cols-4 gap-4 text-sm">
                        <div>
                          <Label>Budgeted</Label>
                          <p className="font-medium">${budget.total_budgeted?.toLocaleString()}</p>
                        </div>
                        <div>
                          <Label>Actual</Label>
                          <p className="font-medium">${budget.total_actual?.toLocaleString()}</p>
                        </div>
                        <div>
                          <Label>Variance</Label>
                          <p className={`font-medium`}>
                            ${budget.total_variance?.toLocaleString()}
                          </p>
                        </div>
                        <div>
                          <Label>Variance %</Label>
                          <p className={`font-medium`}>
                            {budget.variance_percentage?.toFixed(1)}%
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <TrendingUpIcon className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                  <p className="text-muted-foreground">No active budgets for variance analysis</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Summary Tab */}
        <TabsContent value="summary">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
            <Card>
              <CardHeader>
                <CardTitle>Total Budgets</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{budgetSummary?.active_budgets_count || 0}</div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle>Total Budgeted</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">${budgetSummary?.total_budgeted?.toLocaleString() || '0'}</div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle>Total Actual</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">${budgetSummary?.total_actual?.toLocaleString() || '0'}</div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle>Overall Variance</CardTitle>
              </CardHeader>
              <CardContent>
                <div className={`text-2xl font-bold`}>
                  {(budgetSummary?.variance_percentage || 0).toFixed(1)}%
                </div>
              </CardContent>
            </Card>
          </div>

          {budgetSummary?.budgets && (
            <Card>
              <CardHeader>
                <CardTitle>Budget Performance</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {budgetSummary.budgets.map((budget: any) => (
                    <div key={budget.id} className="flex justify-between items-center p-3 border rounded">
                      <span className="font-medium">{budget.name}</span>
                      <div className="flex items-center space-x-4">
                        <span>${budget.total_budgeted?.toLocaleString()}</span>
                        <span>
                          {budget.variance_percentage?.toFixed(1)}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>

      {/* Create/Edit Budget Dialog */}
      <Dialog open={showCreateDialog || showEditDialog} onOpenChange={(open) => {
        if (!open) {
          setShowCreateDialog(false);
          setShowEditDialog(false);
          resetBudgetForm();
        }
      }}>
        <DialogContent className="max-w-4xl">
          <DialogHeader>
            <DialogTitle>{showEditDialog ? 'Edit Budget' : 'Create Budget'}</DialogTitle>
            <DialogDescription>
              {showEditDialog ? 'Update budget details and line items.' : 'Create a new budget with line items for different accounts.'}
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="budget_name">Budget Name</Label>
                <Input
                  id="budget_name"
                  value={budgetForm.name}
                  onChange={(e) => setBudgetForm(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="Annual Budget 2024"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="budget_year">Budget Year</Label>
                <Input
                  id="budget_year"
                  type="number"
                  value={budgetForm.budget_year}
                  onChange={(e) => setBudgetForm(prev => ({ ...prev, budget_year: parseInt(e.target.value) || new Date().getFullYear() }))}
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="budget_description">Description</Label>
              <Textarea
                id="budget_description"
                value={budgetForm.description}
                onChange={(e) => setBudgetForm(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Budget description"
              />
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="period_type">Period Type</Label>
                <Select
                  value={budgetForm.period_type}
                  onValueChange={(value: any) => setBudgetForm(prev => ({ ...prev, period_type: value }))}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="monthly">Monthly</SelectItem>
                    <SelectItem value="quarterly">Quarterly</SelectItem>
                    <SelectItem value="yearly">Yearly</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="start_date">Start Date</Label>
                <Input
                  id="start_date"
                  type="date"
                  value={budgetForm.start_date}
                  onChange={(e) => setBudgetForm(prev => ({ ...prev, start_date: e.target.value }))}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="end_date">End Date</Label>
                <Input
                  id="end_date"
                  type="date"
                  value={budgetForm.end_date}
                  onChange={(e) => setBudgetForm(prev => ({ ...prev, end_date: e.target.value }))}
                />
              </div>
            </div>

            {/* Line Items */}
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <Label className="text-base font-semibold">Budget Line Items</Label>
                <Button type="button" onClick={addLineItem} size="sm">
                  <PlusIcon className="h-4 w-4 mr-2" />
                  Add Line Item
                </Button>
              </div>
              
              <div className="border rounded-lg overflow-hidden">
                <table className="w-full">
                  <thead className="bg-muted">
                    <tr>
                      <th className="px-4 py-2 text-left">Account</th>
                      <th className="px-4 py-2 text-right">Budgeted Amount</th>
                      <th className="px-4 py-2 text-left">Notes</th>
                      <th className="px-4 py-2"></th>
                    </tr>
                  </thead>
                  <tbody>
                    {budgetForm.line_items.map((item, index) => (
                      <tr key={index} className="border-t">
                        <td className="px-4 py-2">
                          <Select
                            value={item.account_id}
                            onValueChange={(value) => updateLineItem(index, 'account_id', value)}
                          >
                            <SelectTrigger className="w-full">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              {accounts && accounts.map((account: any) => (
                                <SelectItem key={account.id} value={account.id}>
                                  {account.code} - {account.name}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </td>
                        <td className="px-4 py-2">
                          <Input
                            type="number"
                            step="0.01"
                            value={item.budgeted_amount}
                            onChange={(e) => updateLineItem(index, 'budgeted_amount', parseFloat(e.target.value) || 0)}
                            placeholder="0.00"
                          />
                        </td>
                        <td className="px-4 py-2">
                          <Input
                            value={item.notes}
                            onChange={(e) => updateLineItem(index, 'notes', e.target.value)}
                            placeholder="Optional notes"
                          />
                        </td>
                        <td className="px-4 py-2">
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            onClick={() => removeLineItem(index)}
                            className="h-4 w-4"
                          >
                            <TrashIcon className="h-4 w-4" />
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              
              <div className="flex justify-end text-sm">
                <span>Total Budget: ${calculateBudgetTotal().toLocaleString()}</span>
              </div>
            </div>

            <div className="flex justify-end space-x-2">
              <Button variant="outline" onClick={() => {
                setShowCreateDialog(false);
                setShowEditDialog(false);
                resetBudgetForm();
              }}>
                Cancel
              </Button>
              <Button 
                onClick={showEditDialog ? handleUpdateBudget : handleCreateBudget}
                disabled={!budgetForm.name || budgetForm.line_items.length === 0}
              >
                {showEditDialog ? 'Update Budget' : 'Create Budget'}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Copy Budget Dialog */}
      <Dialog open={showCopyDialog} onOpenChange={setShowCopyDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Copy Budget</DialogTitle>
            <DialogDescription>
              Create a new budget based on an existing one with optional adjustments.
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="new_budget_name">New Budget Name</Label>
              <Input
                id="new_budget_name"
                value={copyForm.new_budget_name}
                onChange={(e) => setCopyForm(prev => ({ ...prev, new_budget_name: e.target.value }))}
                placeholder="Budget name"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="new_budget_year">Budget Year</Label>
                <Input
                  id="new_budget_year"
                  type="number"
                  value={copyForm.new_budget_year}
                  onChange={(e) => setCopyForm(prev => ({ ...prev, new_budget_year: parseInt(e.target.value) || new Date().getFullYear() + 1 }))}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="adjustment_percentage">Adjustment %</Label>
                <Input
                  id="adjustment_percentage"
                  type="number"
                  step="0.1"
                  value={copyForm.adjustment_percentage}
                  onChange={(e) => setCopyForm(prev => ({ ...prev, adjustment_percentage: parseFloat(e.target.value) || 0 }))}
                  placeholder="0.0"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="copy_start_date">Start Date</Label>
                <Input
                  id="copy_start_date"
                  type="date"
                  value={copyForm.start_date}
                  onChange={(e) => setCopyForm(prev => ({ ...prev, start_date: e.target.value }))}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="copy_end_date">End Date</Label>
                <Input
                  id="copy_end_date"
                  type="date"
                  value={copyForm.end_date}
                  onChange={(e) => setCopyForm(prev => ({ ...prev, end_date: e.target.value }))}
                />
              </div>
            </div>

            <div className="flex justify-end space-x-2">
              <Button variant="outline" onClick={() => setShowCopyDialog(false)}>
                Cancel
              </Button>
              <Button 
                onClick={handleCopyBudget}
                disabled={!copyForm.new_budget_name || !copyForm.source_budget_id}
              >
                Copy Budget
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Generate Forecast Dialog */}
      <Dialog open={showForecastDialog} onOpenChange={setShowForecastDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Generate Forecast</DialogTitle>
            <DialogDescription>
              Generate financial forecasts based on historical data.
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="forecast_account">Account</Label>
              <Select
                value={forecastForm.account_id}
                onValueChange={(value) => setForecastForm(prev => ({ ...prev, account_id: value }))}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select account" />
                </SelectTrigger>
                <SelectContent>
                  {accounts && accounts.map((account: any) => (
                    <SelectItem key={account.id} value={account.id}>
                      {account.code} - {account.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="forecast_periods">Forecast Periods</Label>
                <Input
                  id="forecast_periods"
                  type="number"
                  value={forecastForm.forecast_periods}
                  onChange={(e) => setForecastForm(prev => ({ ...prev, forecast_periods: parseInt(e.target.value) || 12 }))}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="forecast_method">Method</Label>
                <Select
                  value={forecastForm.forecast_method}
                  onValueChange={(value) => setForecastForm(prev => ({ ...prev, forecast_method: value }))}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="trend">Trend Analysis</SelectItem>
                    <SelectItem value="average">Historical Average</SelectItem>
                    <SelectItem value="seasonal">Seasonal Pattern</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="flex justify-end space-x-2">
              <Button variant="outline" onClick={() => setShowForecastDialog(false)}>
                Cancel
              </Button>
              <Button 
                onClick={handleGenerateForecast}
                disabled={!forecastForm.account_id}
              >
                Generate Forecast
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Budget Variance Dialog */}
      <Dialog open={showVarianceDialog} onOpenChange={setShowVarianceDialog}>
        <DialogContent className="max-w-4xl">
          <DialogHeader>
            <DialogTitle>Budget Variance Analysis - {budgetVariance?.budget_name}</DialogTitle>
            <DialogDescription>
              Detailed variance analysis showing budgeted vs actual amounts.
            </DialogDescription>
          </DialogHeader>
          
          {budgetVariance && (
            <div className="space-y-6">
              {/* Summary */}
              <div className="grid grid-cols-4 gap-4 p-4 rounded-lg">
                <div>
                  <Label className="text-sm font-medium">Total Budgeted</Label>
                  <p className="text-lg font-semibold">${budgetVariance.total_budgeted?.toLocaleString()}</p>
                </div>
                <div>
                  <Label className="text-sm font-medium">Total Actual</Label>
                  <p className="text-lg font-semibold">${budgetVariance.total_actual?.toLocaleString()}</p>
                </div>
                <div>
                  <Label className="text-sm font-medium">Total Variance</Label>
                  <p className={`text-lg font-semibold`}>
                    ${budgetVariance.total_variance?.toLocaleString()}
                  </p>
                </div>
                <div>
                  <Label className="text-sm font-medium">Variance %</Label>
                  <p className={`text-lg font-semibold`}>
                    {budgetVariance.variance_percentage?.toFixed(1)}%
                  </p>
                </div>
              </div>

              {/* Line Items */}
              <div>
                <Label className="text-base font-semibold">Line Item Details</Label>
                <div className="mt-2 border rounded-lg overflow-hidden">
                  <table className="w-full">
                    <thead className="bg-muted">
                      <tr>
                        <th className="px-4 py-2 text-left">Account</th>
                        <th className="px-4 py-2 text-right">Budgeted</th>
                        <th className="px-4 py-2 text-right">Actual</th>
                        <th className="px-4 py-2 text-right">Variance</th>
                        <th className="px-4 py-2 text-right">Variance %</th>
                      </tr>
                    </thead>
                    <tbody>
                      {budgetVariance.line_items?.map((item: any) => (
                        <tr key={item.id} className="border-t">
                          <td className="px-4 py-2">
                            {item.account_code} - {item.account_name}
                          </td>
                          <td className="px-4 py-2 text-right">
                            ${item.budgeted_amount?.toLocaleString()}
                          </td>
                          <td className="px-4 py-2 text-right">
                            ${item.actual_amount?.toLocaleString()}
                          </td>
                          <td className={`px-4 py-2 text-right`}>
                            ${item.variance_amount?.toLocaleString()}
                          </td>
                          <td className={`px-4 py-2 text-right`}>
                            {item.variance_percentage?.toFixed(1)}%
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              <div className="flex justify-end">
                <Button onClick={() => setShowVarianceDialog(false)}>
                  Close
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}