import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Checkbox } from '@/components/ui/checkbox';
import { 
  PlusIcon,
  CheckCircleIcon,
  RefreshIcon,
  ListIcon,
  EyeIcon
} from '@/components/icons';
import { 
  useGetReconciliations,
  useGetReconciliation,
  useCreateReconciliation,
  useUpdateReconciliation,
  useCompleteReconciliation,
  useAddReconciliationAdjustment,
  useGetAccounts
} from '@/lib/api/hooks/useAccounting';
import { toast } from 'sonner';

const RECONCILIATION_STATUSES = {
  in_progress: { label: 'In Progress', variant: 'warning' },
  completed: { label: 'Completed', variant: 'success' },
  cancelled: { label: 'Cancelled', variant: 'destructive' }
};

export default function BankReconciliationPage() {
  const [activeTab, setActiveTab] = useState('reconciliations');
  const [selectedReconciliation, setSelectedReconciliation] = useState<any>(null);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showReconcileDialog, setShowReconcileDialog] = useState(false);
  const [showAdjustmentDialog, setShowAdjustmentDialog] = useState(false);
  
  // Form states
  const [createForm, setCreateForm] = useState({
    account_id: '',
    reconciliation_date: new Date().toISOString().split('T')[0],
    statement_date: new Date().toISOString().split('T')[0],
    statement_balance: 0
  });
  
  const [adjustmentForm, setAdjustmentForm] = useState({
    description: '',
    amount: 0,
    account_id: '',
    reference: ''
  });
  
  const [matchedTransactions, setMatchedTransactions] = useState<string[]>([]);

  // Queries and mutations
  const { data: reconciliations } = useGetReconciliations();
  const { data: accounts } = useGetAccounts();
  const { data: reconciliationDetails } = useGetReconciliation(selectedReconciliation?.id || '');
  
  const createReconciliation = useCreateReconciliation();
  const updateReconciliation = useUpdateReconciliation();
  const completeReconciliation = useCompleteReconciliation();
  const addAdjustment = useAddReconciliationAdjustment();

  const handleCreateReconciliation = async () => {
    try {
      const reconciliation = await createReconciliation.mutateAsync(createForm);
      setSelectedReconciliation(reconciliation);
      setShowCreateDialog(false);
      setShowReconcileDialog(true);
      toast.success('Reconciliation started successfully');
    } catch (error) {
      console.error('Error creating reconciliation:', error);
    }
  };

  const handleMatchTransaction = (transactionId: string, checked: boolean) => {
    if (checked) {
      setMatchedTransactions(prev => [...prev, transactionId]);
    } else {
      setMatchedTransactions(prev => prev.filter(id => id !== transactionId));
    }
  };

  const handleUpdateMatches = async () => {
    if (!selectedReconciliation) return;

    try {
      const transactions = reconciliationDetails?.transactions || [];
      const matched = transactions.filter(t => matchedTransactions.includes(t.id));
      
      await updateReconciliation.mutateAsync({
        reconciliation_id: selectedReconciliation.id,
        data: { matched_transactions: matched }
      });
      
      toast.success('Transaction matches updated');
    } catch (error) {
      console.error('Error updating matches:', error);
    }
  };

  const handleAddAdjustment = async () => {
    if (!selectedReconciliation) return;

    try {
      await addAdjustment.mutateAsync({
        reconciliation_id: selectedReconciliation.id,
        adjustment: adjustmentForm
      });
      
      setShowAdjustmentDialog(false);
      setAdjustmentForm({
        description: '',
        amount: 0,
        account_id: '',
        reference: ''
      });
      
      toast.success('Adjustment added successfully');
    } catch (error) {
      console.error('Error adding adjustment:', error);
    }
  };

  const handleCompleteReconciliation = async () => {
    if (!selectedReconciliation) return;

    try {
      await completeReconciliation.mutateAsync(selectedReconciliation.id);
      setShowReconcileDialog(false);
      toast.success('Reconciliation completed successfully');
    } catch (error) {
      console.error('Error completing reconciliation:', error);
    }
  };

  const calculateReconciliationBalance = () => {
    if (!reconciliationDetails) return 0;
    
    const matchedAmount = reconciliationDetails.transactions
      ?.filter(t => matchedTransactions.includes(t.id))
      .reduce((sum, t) => sum + t.amount, 0) || 0;
    
    const adjustmentAmount = reconciliationDetails.adjustments
      ?.reduce((sum, adj) => sum + adj.amount, 0) || 0;
    
    return reconciliationDetails.beginning_balance + matchedAmount + adjustmentAmount;
  };

  const renderReconciliationCard = (reconciliation: any) => {
    const status = reconciliation.status || 'in_progress';
    const statusConfig = RECONCILIATION_STATUSES[status as keyof typeof RECONCILIATION_STATUSES];

    return (
      <Card key={reconciliation.id} className="hover:shadow-md transition-shadow">
        <CardContent className="p-4">
          <div className="flex justify-between items-start mb-3">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="font-semibold">{reconciliation.account_name}</span>
                <Badge className={statusConfig.color}>
                  {statusConfig.label}
                </Badge>
              </div>
              <p className="text-sm text-muted-foreground">
                Statement Date: {reconciliation.statement_date}
              </p>
              <p className="text-sm text-muted-foreground">
                Reconciliation Date: {reconciliation.reconciliation_date}
              </p>
            </div>
            <div className="text-right">
              <p className="font-medium">${reconciliation.statement_balance?.toLocaleString()}</p>
              <p className="text-sm text-muted-foreground">
                Difference: ${reconciliation.difference?.toLocaleString()}
              </p>
            </div>
          </div>
          
          <div className="flex justify-between items-center text-sm mb-3">
            <span>Transactions: {reconciliation.matched_count}/{reconciliation.transaction_count}</span>
            <span>
              {reconciliation.difference === 0 ? 'Balanced' : 'Unbalanced'}
            </span>
          </div>
          
          <div className="flex justify-between items-center">
            <div className="flex space-x-1">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  setSelectedReconciliation(reconciliation);
                  if (reconciliation.status === 'in_progress') {
                    setShowReconcileDialog(true);
                  }
                }}
                className="h-8 w-8 p-0"
              >
                <EyeIcon className="h-4 w-4" />
              </Button>
              
              {reconciliation.status === 'in_progress' && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleCompleteReconciliation()}
                  disabled={reconciliation.difference !== 0}
                  className="h-8 w-8 p-0"
                >
                  <CheckCircleIcon className="h-4 w-4" />
                </Button>
              )}
            </div>
            
            <span className="text-xs text-muted-foreground">
              {reconciliation.created_by}
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
            <h1 className="text-3xl font-bold">Bank Reconciliation</h1>
            <p className="text-muted-foreground">
              Reconcile bank statements with your accounting records.
            </p>
          </div>
          
          <div className="flex space-x-2">
            <Button onClick={() => setShowCreateDialog(true)}>
              <PlusIcon className="h-4 w-4 mr-2" />
              Start Reconciliation
            </Button>
          </div>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6" defaultValue="reconciliations">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="reconciliations">Reconciliations</TabsTrigger>
          <TabsTrigger value="summary">Summary</TabsTrigger>
        </TabsList>

        {/* Reconciliations Tab */}
        <TabsContent value="reconciliations">
          <div className="grid gap-4">
            {reconciliations && reconciliations.length > 0 ? (
              reconciliations.map(renderReconciliationCard)
            ) : (
              <Card>
                <CardContent className="text-center py-8">
                  <ListIcon className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                  <p className="text-muted-foreground">No reconciliations found</p>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>

        {/* Summary Tab */}
        <TabsContent value="summary">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Total Reconciliations</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{reconciliations?.length || 0}</div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle>Completed This Month</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {reconciliations?.filter(r => r.status === 'completed').length || 0}
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle>In Progress</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {reconciliations?.filter(r => r.status === 'in_progress').length || 0}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>

      {/* Create Reconciliation Dialog */}
      <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Start Bank Reconciliation</DialogTitle>
            <DialogDescription>
              Begin a new bank reconciliation for an account.
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="account_id">Bank Account</Label>
              <Select
                value={createForm.account_id}
                onValueChange={(value) => setCreateForm(prev => ({ ...prev, account_id: value }))}
              >
                <SelectTrigger>
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
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="statement_date">Statement Date</Label>
                <Input
                  id="statement_date"
                  type="date"
                  value={createForm.statement_date}
                  onChange={(e) => setCreateForm(prev => ({ ...prev, statement_date: e.target.value }))}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="reconciliation_date">Reconciliation Date</Label>
                <Input
                  id="reconciliation_date"
                  type="date"
                  value={createForm.reconciliation_date}
                  onChange={(e) => setCreateForm(prev => ({ ...prev, reconciliation_date: e.target.value }))}
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="statement_balance">Statement Ending Balance</Label>
              <Input
                id="statement_balance"
                type="number"
                step="0.01"
                value={createForm.statement_balance}
                onChange={(e) => setCreateForm(prev => ({ ...prev, statement_balance: parseFloat(e.target.value) || 0 }))}
                placeholder="0.00"
              />
            </div>

            <div className="flex justify-end space-x-2">
              <Button variant="outline" onClick={() => setShowCreateDialog(false)}>
                Cancel
              </Button>
              <Button 
                onClick={handleCreateReconciliation}
                disabled={!createForm.account_id || createReconciliation.isPending}
              >
                {createReconciliation.isPending ? (
                  <>
                    <RefreshIcon className="mr-2 h-4 w-4 animate-spin" />
                    Starting...
                  </>
                ) : (
                  'Start Reconciliation'
                )}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Reconcile Dialog */}
      <Dialog open={showReconcileDialog} onOpenChange={setShowReconcileDialog}>
        <DialogContent className="max-w-6xl">
          <DialogHeader>
            <DialogTitle>Bank Reconciliation - {reconciliationDetails?.account_name}</DialogTitle>
            <DialogDescription>
              Match transactions and add adjustments to balance the reconciliation.
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-6">
            {/* Reconciliation Summary */}
            <div className="grid grid-cols-4 gap-4 p-4 rounded-lg">
              <div>
                <Label className="text-sm font-medium">Beginning Balance</Label>
                <p className="text-lg font-semibold">${reconciliationDetails?.beginning_balance?.toLocaleString()}</p>
              </div>
              <div>
                <Label className="text-sm font-medium">Statement Balance</Label>
                <p className="text-lg font-semibold">${reconciliationDetails?.statement_balance?.toLocaleString()}</p>
              </div>
              <div>
                <Label className="text-sm font-medium">Reconciled Balance</Label>
                <p className="text-lg font-semibold">${calculateReconciliationBalance().toLocaleString()}</p>
              </div>
              <div>
                <Label className="text-sm font-medium">Difference</Label>
                <p className={`text-lg font-semibold ${
                  Math.abs((reconciliationDetails?.statement_balance || 0) - calculateReconciliationBalance()) < 0.01 
                    ? 'text-green-600' : 'text-red-600'
                }`}>
                  ${((reconciliationDetails?.statement_balance || 0) - calculateReconciliationBalance()).toLocaleString()}
                </p>
              </div>
            </div>

            {/* Transactions */}
            <div>
              <div className="flex justify-between items-center mb-4">
                <Label className="text-base font-semibold">Unreconciled Transactions</Label>
                <div className="flex space-x-2">
                  <Button variant="outline" size="sm" onClick={handleUpdateMatches}>
                    Update Matches
                  </Button>
                  <Button variant="outline" size="sm" onClick={() => setShowAdjustmentDialog(true)}>
                    Add Adjustment
                  </Button>
                </div>
              </div>
              
              <div className="border rounded-lg overflow-hidden max-h-96 overflow-y-auto">
                <table className="w-full">
                  <thead className="bg-muted sticky top-0">
                    <tr>
                      <th className="px-4 py-2 text-left">Match</th>
                      <th className="px-4 py-2 text-left">Date</th>
                      <th className="px-4 py-2 text-left">Description</th>
                      <th className="px-4 py-2 text-left">Reference</th>
                      <th className="px-4 py-2 text-right">Amount</th>
                    </tr>
                  </thead>
                  <tbody>
                    {reconciliationDetails?.transactions?.map((transaction: any) => (
                      <tr key={transaction.id} className="border-t">
                        <td className="px-4 py-2">
                          <Checkbox
                            checked={matchedTransactions.includes(transaction.id)}
                            onCheckedChange={(checked) => handleMatchTransaction(transaction.id, checked as boolean)}
                          />
                        </td>
                        <td className="px-4 py-2">{transaction.date}</td>
                        <td className="px-4 py-2">{transaction.description}</td>
                        <td className="px-4 py-2">{transaction.reference || '-'}</td>
                        <td className="px-4 py-2 text-right">
                          <span>
                            ${Math.abs(transaction.amount).toLocaleString()}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Adjustments */}
            {reconciliationDetails?.adjustments && reconciliationDetails.adjustments.length > 0 && (
              <div>
                <Label className="text-base font-semibold">Adjustments</Label>
                <div className="mt-2 space-y-2">
                  {reconciliationDetails.adjustments.map((adjustment: any) => (
                    <div key={adjustment.id} className="flex justify-between items-center p-2 border rounded">
                      <span>{adjustment.description}</span>
                      <span>
                        ${adjustment.amount.toLocaleString()}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="flex justify-end space-x-2">
              <Button variant="outline" onClick={() => setShowReconcileDialog(false)}>
                Close
              </Button>
              <Button 
                onClick={handleCompleteReconciliation}
                disabled={Math.abs((reconciliationDetails?.statement_balance || 0) - calculateReconciliationBalance()) >= 0.01}
                className="bg-primary hover:bg-primary/90"
              >
                Complete Reconciliation
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Add Adjustment Dialog */}
      <Dialog open={showAdjustmentDialog} onOpenChange={setShowAdjustmentDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add Reconciliation Adjustment</DialogTitle>
            <DialogDescription>
              Add an adjustment entry to balance the reconciliation.
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="adj_description">Description</Label>
              <Input
                id="adj_description"
                value={adjustmentForm.description}
                onChange={(e) => setAdjustmentForm(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Bank fees, interest, etc."
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="adj_amount">Amount</Label>
              <Input
                id="adj_amount"
                type="number"
                step="0.01"
                value={adjustmentForm.amount}
                onChange={(e) => setAdjustmentForm(prev => ({ ...prev, amount: parseFloat(e.target.value) || 0 }))}
                placeholder="0.00"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="adj_reference">Reference</Label>
              <Input
                id="adj_reference"
                value={adjustmentForm.reference}
                onChange={(e) => setAdjustmentForm(prev => ({ ...prev, reference: e.target.value }))}
                placeholder="Optional reference"
              />
            </div>

            <div className="flex justify-end space-x-2">
              <Button variant="outline" onClick={() => setShowAdjustmentDialog(false)}>
                Cancel
              </Button>
              <Button 
                onClick={handleAddAdjustment}
                disabled={!adjustmentForm.description || adjustmentForm.amount === 0}
              >
                Add Adjustment
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}