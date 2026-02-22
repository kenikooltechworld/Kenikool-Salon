import React, { useState, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert';
import { 
  Search,
  Download, 
  Upload, 
  Plus,
  Edit,
  Trash2,
  ChevronRight,
  ChevronDown,
  Filter,
  FileText,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Merge,
  Eye,
  RefreshCw
} from 'lucide-react';
import { 
  useGetAccounts,
  useGetAccountHierarchy,
  useSearchAccounts,
  useExportAccountsCSV,
  useValidateAccountsImport,
  useImportAccountsCSV,
  useMergeAccounts,
  useGetAccountUsageStats,
  useCreateAccount,
  useUpdateAccount
} from '@/lib/api/hooks/useAccounting';
import { toast } from 'sonner';

const ACCOUNT_TYPES = [
  { value: 'asset', label: 'Asset' },
  { value: 'liability', label: 'Liability' },
  { value: 'equity', label: 'Equity' },
  { value: 'revenue', label: 'Revenue' },
  { value: 'expense', label: 'Expense' }
];

const SUB_TYPES = {
  asset: [
    { value: 'cash', label: 'Cash' },
    { value: 'bank', label: 'Bank' },
    { value: 'accounts_receivable', label: 'Accounts Receivable' },
    { value: 'inventory', label: 'Inventory' },
    { value: 'fixed_assets', label: 'Fixed Assets' }
  ],
  liability: [
    { value: 'accounts_payable', label: 'Accounts Payable' },
    { value: 'credit_card', label: 'Credit Card' },
    { value: 'loans', label: 'Loans' }
  ],
  equity: [
    { value: 'owners_equity', label: 'Owner\'s Equity' },
    { value: 'retained_earnings', label: 'Retained Earnings' }
  ],
  revenue: [
    { value: 'service_revenue', label: 'Service Revenue' },
    { value: 'product_revenue', label: 'Product Revenue' },
    { value: 'other_revenue', label: 'Other Revenue' }
  ],
  expense: [
    { value: 'cost_of_goods', label: 'Cost of Goods' },
    { value: 'operating_expenses', label: 'Operating Expenses' },
    { value: 'payroll', label: 'Payroll' },
    { value: 'rent', label: 'Rent' },
    { value: 'utilities', label: 'Utilities' },
    { value: 'marketing', label: 'Marketing' }
  ]
};

interface AccountTreeItemProps {
  account: any;
  level: number;
  onEdit: (account: any) => void;
  onDelete: (account: any) => void;
  onViewUsage: (account: any) => void;
  onMerge: (account: any) => void;
}

const AccountTreeItem: React.FC<AccountTreeItemProps> = ({ 
  account, 
  level, 
  onEdit, 
  onDelete, 
  onViewUsage, 
  onMerge 
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const getTypeVariant = (type: string) => {
    const variants = {
      asset: 'default',
      liability: 'destructive',
      equity: 'success',
      revenue: 'accent',
      expense: 'warning'
    };
    return variants[type as keyof typeof variants] || 'secondary';
  };

  return (
    <div className="space-y-1">
      <div 
        className={`flex items-center justify-between p-3 rounded-lg border hover:bg-muted ${
          level > 0 ? 'ml-' + (level * 4) : ''
        }`}
        style={{ marginLeft: level * 20 }}
      >
        <div className="flex items-center space-x-3 flex-1">
          {account.has_children && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsExpanded(!isExpanded)}
              className="p-0 h-6 w-6"
            >
              {isExpanded ? (
                <ChevronDown className="h-4 w-4" />
              ) : (
                <ChevronRight className="h-4 w-4" />
              )}
            </Button>
          )}
          
          <div className="flex-1">
            <div className="flex items-center space-x-2">
              <span className="font-medium">{account.code}</span>
              <span>{account.name}</span>
              <Badge variant={getTypeVariant(account.account_type)}>
                {account.account_type}
              </Badge>
              {!account.active && (
                <Badge variant="secondary">Inactive</Badge>
              )}
            </div>
            {account.description && (
              <p className="text-sm text-muted-foreground mt-1">{account.description}</p>
            )}
          </div>

          <div className="flex items-center space-x-2">
            <span className="text-sm font-medium">
              ${account.balance?.toLocaleString() || '0.00'}
            </span>
            
            <div className="flex space-x-1">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onViewUsage(account)}
                className="h-8 w-8 p-0"
              >
                <Eye className="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onEdit(account)}
                className="h-8 w-8 p-0"
              >
                <Edit className="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onMerge(account)}
                className="h-8 w-8 p-0"
              >
                <Merge className="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onDelete(account)}
                className="h-8 w-8 p-0"
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </div>

      {isExpanded && account.children && account.children.length > 0 && (
        <div className="space-y-1">
          {account.children.map((child: any) => (
            <AccountTreeItem
              key={child.id}
              account={child}
              level={level + 1}
              onEdit={onEdit}
              onDelete={onDelete}
              onViewUsage={onViewUsage}
              onMerge={onMerge}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default function ChartOfAccountsPage() {
  const [activeTab, setActiveTab] = useState('hierarchy');
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('');
  const [filterSubType, setFilterSubType] = useState('');
  const [showActiveOnly, setShowActiveOnly] = useState(true);
  
  // Dialog states
  const [showImportDialog, setShowImportDialog] = useState(false);
  const [showMergeDialog, setShowMergeDialog] = useState(false);
  const [showUsageDialog, setShowUsageDialog] = useState(false);
  const [showAccountForm, setShowAccountForm] = useState(false);
  
  // Selected items
  const [selectedAccount, setSelectedAccount] = useState<any>(null);
  const [mergeSource, setMergeSource] = useState<any>(null);
  const [mergeTarget, setMergeTarget] = useState<any>(null);
  
  // Import states
  const [importFile, setImportFile] = useState<File | null>(null);
  const [validationResult, setValidationResult] = useState<any>(null);
  const [importResult, setImportResult] = useState<any>(null);
  
  // Form state
  const [accountForm, setAccountForm] = useState({
    code: '',
    name: '',
    account_type: '',
    sub_type: '',
    description: '',
    parent_account_id: ''
  });

  const fileInputRef = useRef<HTMLInputElement>(null);

  // Queries and mutations
  const { data: accounts } = useGetAccounts();
  const { data: hierarchy } = useGetAccountHierarchy();
  const { data: searchResults } = useSearchAccounts({
    search: searchTerm,
    account_type: filterType,
    sub_type: filterSubType,
    active_only: showActiveOnly
  });
  const { data: usageStats } = useGetAccountUsageStats(selectedAccount?.id || '');
  
  const exportCSV = useExportAccountsCSV();
  const validateImport = useValidateAccountsImport();
  const importCSV = useImportAccountsCSV();
  const mergeAccounts = useMergeAccounts();
  const createAccount = useCreateAccount();
  const updateAccount = useUpdateAccount();

  const handleExport = async () => {
    try {
      await exportCSV.mutateAsync();
      toast.success('Chart of accounts exported successfully');
    } catch (error) {
      console.error('Export error:', error);
    }
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setImportFile(file);
      setValidationResult(null);
      setImportResult(null);
    }
  };

  const handleValidateImport = async () => {
    if (!importFile) {
      toast.error('Please select a file first');
      return;
    }

    try {
      const result = await validateImport.mutateAsync(importFile);
      setValidationResult(result);
      
      if (result.valid) {
        toast.success('File validation passed');
      } else {
        toast.error('File validation failed');
      }
    } catch (error) {
      console.error('Validation error:', error);
    }
  };

  const handleImport = async () => {
    if (!importFile || !validationResult?.valid) {
      toast.error('Please validate the file first');
      return;
    }

    try {
      const result = await importCSV.mutateAsync(importFile);
      setImportResult(result);
      setShowImportDialog(false);
      toast.success(`Import completed: ${result.imported} imported, ${result.updated} updated`);
    } catch (error) {
      console.error('Import error:', error);
    }
  };

  const handleMergeAccounts = async () => {
    if (!mergeSource || !mergeTarget) {
      toast.error('Please select both source and target accounts');
      return;
    }

    if (mergeSource.id === mergeTarget.id) {
      toast.error('Cannot merge an account with itself');
      return;
    }

    try {
      await mergeAccounts.mutateAsync({
        source_account_id: mergeSource.id,
        target_account_id: mergeTarget.id,
        merge_transactions: true
      });
      setShowMergeDialog(false);
      setMergeSource(null);
      setMergeTarget(null);
      toast.success('Accounts merged successfully');
    } catch (error) {
      console.error('Merge error:', error);
    }
  };

  const handleAccountSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      if (selectedAccount) {
        // Update existing account
        await updateAccount.mutateAsync({
          id: selectedAccount.id,
          data: {
            name: accountForm.name,
            description: accountForm.description,
            active: true
          }
        });
        toast.success('Account updated successfully');
      } else {
        // Create new account
        await createAccount.mutateAsync(accountForm);
        toast.success('Account created successfully');
      }
      
      setShowAccountForm(false);
      setSelectedAccount(null);
      setAccountForm({
        code: '',
        name: '',
        account_type: '',
        sub_type: '',
        description: '',
        parent_account_id: ''
      });
    } catch (error) {
      console.error('Account form error:', error);
    }
  };

  const openAccountForm = (account?: any) => {
    if (account) {
      setSelectedAccount(account);
      setAccountForm({
        code: account.code,
        name: account.name,
        account_type: account.account_type,
        sub_type: account.sub_type,
        description: account.description || '',
        parent_account_id: account.parent_account_id || ''
      });
    } else {
      setSelectedAccount(null);
      setAccountForm({
        code: '',
        name: '',
        account_type: '',
        sub_type: '',
        description: '',
        parent_account_id: ''
      });
    }
    setShowAccountForm(true);
  };

  const openUsageDialog = (account: any) => {
    setSelectedAccount(account);
    setShowUsageDialog(true);
  };

  const openMergeDialog = (account: any) => {
    setMergeSource(account);
    setShowMergeDialog(true);
  };

  return (
    <div className="container mx-auto py-6">
      <div className="mb-6">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold">Chart of Accounts</h1>
            <p className="text-muted-foreground">
              Manage your chart of accounts with hierarchical structure, search, import/export, and merging capabilities.
            </p>
          </div>
          
          <div className="flex space-x-2">
            <Button onClick={() => openAccountForm()} className="flex items-center gap-2">
              <Plus className="h-4 w-4" />
              Add Account
            </Button>
            <Button variant="outline" onClick={handleExport} disabled={exportCSV.isPending}>
              <Download className="h-4 w-4 mr-2" />
              Export CSV
            </Button>
            <Button variant="outline" onClick={() => setShowImportDialog(true)}>
              <Upload className="h-4 w-4 mr-2" />
              Import CSV
            </Button>
          </div>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="hierarchy">Hierarchy View</TabsTrigger>
          <TabsTrigger value="search">Search & Filter</TabsTrigger>
          <TabsTrigger value="list">List View</TabsTrigger>
        </TabsList>

        {/* Hierarchy View */}
        <TabsContent value="hierarchy">
          <Card>
            <CardHeader>
              <CardTitle>Account Hierarchy</CardTitle>
              <CardDescription>
                View accounts in a hierarchical tree structure with parent-child relationships.
              </CardDescription>
            </CardHeader>
            <CardContent>
              {hierarchy && hierarchy.length > 0 ? (
                <div className="space-y-2">
                  {hierarchy.map((account: any) => (
                    <AccountTreeItem
                      key={account.id}
                      account={account}
                      level={0}
                      onEdit={openAccountForm}
                      onDelete={(account) => console.log('Delete:', account)}
                      onViewUsage={openUsageDialog}
                      onMerge={openMergeDialog}
                    />
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <FileText className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                  <p className="text-muted-foreground">No accounts found</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Search & Filter */}
        <TabsContent value="search">
          <Card>
            <CardHeader>
              <CardTitle>Search & Filter Accounts</CardTitle>
              <CardDescription>
                Search accounts by code, name, or description and filter by type.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {/* Search and Filter Controls */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="search">Search</Label>
                    <div className="relative">
                      <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                      <Input
                        id="search"
                        placeholder="Search accounts..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="pl-10"
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="filter_type">Account Type</Label>
                    <Select value={filterType} onValueChange={setFilterType}>
                      <SelectTrigger>
                        <SelectValue placeholder="All types" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="">All types</SelectItem>
                        {ACCOUNT_TYPES.map(type => (
                          <SelectItem key={type.value} value={type.value}>
                            {type.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="filter_sub_type">Sub Type</Label>
                    <Select value={filterSubType} onValueChange={setFilterSubType}>
                      <SelectTrigger>
                        <SelectValue placeholder="All sub types" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="">All sub types</SelectItem>
                        {filterType && SUB_TYPES[filterType as keyof typeof SUB_TYPES]?.map(subType => (
                          <SelectItem key={subType.value} value={subType.value}>
                            {subType.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="active_only">Status</Label>
                    <Select 
                      value={showActiveOnly ? 'active' : 'all'} 
                      onValueChange={(value) => setShowActiveOnly(value === 'active')}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="active">Active only</SelectItem>
                        <SelectItem value="all">All accounts</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                {/* Search Results */}
                {searchResults && searchResults.length > 0 && (
                  <div className="space-y-2">
                    <h4 className="font-semibold">Search Results ({searchResults.length})</h4>
                    <div className="space-y-2">
                      {searchResults.map((account: any) => (
                        <AccountTreeItem
                          key={account.id}
                          account={account}
                          level={0}
                          onEdit={openAccountForm}
                          onDelete={(account) => console.log('Delete:', account)}
                          onViewUsage={openUsageDialog}
                          onMerge={openMergeDialog}
                        />
                      ))}
                    </div>
                  </div>
                )}

                {searchTerm && searchResults && searchResults.length === 0 && (
                  <div className="text-center py-8">
                    <Search className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                    <p className="text-muted-foreground">No accounts found matching your search</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* List View */}
        <TabsContent value="list">
          <Card>
            <CardHeader>
              <CardTitle>All Accounts</CardTitle>
              <CardDescription>
                Complete list of all accounts in your chart of accounts.
              </CardDescription>
            </CardHeader>
            <CardContent>
              {accounts && accounts.length > 0 ? (
                <div className="space-y-2">
                  {accounts.map((account: any) => (
                    <AccountTreeItem
                      key={account.id}
                      account={account}
                      level={0}
                      onEdit={openAccountForm}
                      onDelete={(account) => console.log('Delete:', account)}
                      onViewUsage={openUsageDialog}
                      onMerge={openMergeDialog}
                    />
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <FileText className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                  <p className="text-muted-foreground">No accounts found</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Import Dialog */}
      <Dialog open={showImportDialog} onOpenChange={setShowImportDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Import Chart of Accounts</DialogTitle>
            <DialogDescription>
              Import accounts from a CSV file. The file should have columns: Code, Name, Account Type, Sub Type, Description, Parent Account Code, Active, Balance.
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="import_file">Select CSV File</Label>
              <Input
                id="import_file"
                type="file"
                accept=".csv"
                onChange={handleFileSelect}
                ref={fileInputRef}
              />
            </div>

            {importFile && (
              <div className="space-y-4">
                <div className="flex space-x-2">
                  <Button 
                    onClick={handleValidateImport}
                    disabled={validateImport.isPending}
                    variant="outline"
                  >
                    {validateImport.isPending ? (
                      <>
                        <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                        Validating...
                      </>
                    ) : (
                      <>
                        <CheckCircle className="mr-2 h-4 w-4" />
                        Validate File
                      </>
                    )}
                  </Button>

                  {validationResult?.valid && (
                    <Button 
                      onClick={handleImport}
                      disabled={importCSV.isPending}
                    >
                      {importCSV.isPending ? (
                        <>
                          <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                          Importing...
                        </>
                      ) : (
                        <>
                          <Upload className="mr-2 h-4 w-4" />
                          Import Accounts
                        </>
                      )}
                    </Button>
                  )}
                </div>

                {validationResult && (
                  <div className="border rounded-lg p-4">
                    <div className="flex items-center space-x-2 mb-2">
                      {validationResult.valid ? (
                        <CheckCircle className="h-5 w-5" />
                      ) : (
                        <XCircle className="h-5 w-5" />
                      )}
                      <span className="font-semibold">
                        {validationResult.valid ? 'Validation Passed' : 'Validation Failed'}
                      </span>
                    </div>
                    
                    <p className="text-sm text-muted-foreground mb-2">
                      Total rows: {validationResult.total_rows}
                    </p>

                    {validationResult.errors && validationResult.errors.length > 0 && (
                      <div className="space-y-2">
                        <h5 className="font-medium">Errors:</h5>
                        <div className="max-h-32 overflow-y-auto space-y-1">
                          {validationResult.errors.map((error: any, index: number) => (
                            <div key={index} className="text-sm">
                              Row {error.row}: {error.error}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {validationResult.warnings && validationResult.warnings.length > 0 && (
                      <div className="space-y-2 mt-2">
                        <h5 className="font-medium">Warnings:</h5>
                        <div className="max-h-32 overflow-y-auto space-y-1">
                          {validationResult.warnings.map((warning: any, index: number) => (
                            <div key={index} className="text-sm">
                              {warning.account}: {warning.warning}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>

      {/* Merge Dialog */}
      <Dialog open={showMergeDialog} onOpenChange={setShowMergeDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Merge Accounts</DialogTitle>
            <DialogDescription>
              Merge one account into another. All transactions from the source account will be transferred to the target account.
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>Source Account (will be deactivated)</Label>
              <div className="p-3 border rounded-lg bg-destructive/10">
                {mergeSource ? (
                  <div>
                    <span className="font-medium">{mergeSource.code}</span> - {mergeSource.name}
                    <Badge variant="destructive" className="ml-2">{mergeSource.account_type}</Badge>
                  </div>
                ) : (
                  <span className="text-muted-foreground">No source account selected</span>
                )}
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="merge_target">Target Account</Label>
              <Select 
                value={mergeTarget?.id || ''} 
                onValueChange={(value) => {
                  const target = accounts?.find(acc => acc.id === value);
                  setMergeTarget(target);
                }}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select target account" />
                </SelectTrigger>
                <SelectContent>
                  {accounts?.filter(acc => 
                    acc.id !== mergeSource?.id && 
                    acc.account_type === mergeSource?.account_type
                  ).map(account => (
                    <SelectItem key={account.id} value={account.id}>
                      {account.code} - {account.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {mergeSource && mergeTarget && (
              <Alert variant="warning">
                <AlertTriangle className="h-4 w-4" />
                <AlertTitle>Warning</AlertTitle>
                <AlertDescription>
                  This action cannot be undone. All transactions from "{mergeSource.name}" will be moved to "{mergeTarget.name}" 
                  and the source account will be deactivated.
                </AlertDescription>
              </Alert>
            )}

            <div className="flex justify-end space-x-2">
              <Button variant="outline" onClick={() => setShowMergeDialog(false)}>
                Cancel
              </Button>
              <Button 
                onClick={handleMergeAccounts}
                disabled={!mergeSource || !mergeTarget || mergeAccounts.isPending}
                variant="destructive"
              >
                {mergeAccounts.isPending ? (
                  <>
                    <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                    Merging...
                  </>
                ) : (
                  <>
                    <Merge className="mr-2 h-4 w-4" />
                    Merge Accounts
                  </>
                )}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Usage Stats Dialog */}
      <Dialog open={showUsageDialog} onOpenChange={setShowUsageDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Account Usage Statistics</DialogTitle>
            <DialogDescription>
              View usage statistics and transaction history for this account.
            </DialogDescription>
          </DialogHeader>
          
          {usageStats && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Account Code</Label>
                  <p className="font-medium">{usageStats.account_code}</p>
                </div>
                <div className="space-y-2">
                  <Label>Account Name</Label>
                  <p className="font-medium">{usageStats.account_name}</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Current Balance</Label>
                  <p className="font-medium">${usageStats.current_balance?.toLocaleString()}</p>
                </div>
                <div className="space-y-2">
                  <Label>Total Transactions</Label>
                  <p className="font-medium">{usageStats.total_transactions}</p>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label>Journal Entries</Label>
                  <p className="font-medium">{usageStats.journal_entries}</p>
                </div>
                <div className="space-y-2">
                  <Label>Invoices</Label>
                  <p className="font-medium">{usageStats.invoices}</p>
                </div>
                <div className="space-y-2">
                  <Label>Bills</Label>
                  <p className="font-medium">{usageStats.bills}</p>
                </div>
              </div>

              {usageStats.first_transaction_date && (
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>First Transaction</Label>
                    <p className="font-medium">{usageStats.first_transaction_date}</p>
                  </div>
                  <div className="space-y-2">
                    <Label>Last Transaction</Label>
                    <p className="font-medium">{usageStats.last_transaction_date}</p>
                  </div>
                </div>
              )}

              <div className="space-y-2">
                <Label>Can be deleted?</Label>
                <div className="flex items-center space-x-2">
                  {usageStats.can_be_deleted ? (
                    <CheckCircle className="h-5 w-5" />
                  ) : (
                    <XCircle className="h-5 w-5" />
                  )}
                  <span>
                    {usageStats.can_be_deleted ? 'Yes' : 'No'}
                  </span>
                </div>
              </div>

              {usageStats.deletion_blockers && usageStats.deletion_blockers.length > 0 && (
                <div className="space-y-2">
                  <Label>Deletion Blockers</Label>
                  <ul className="list-disc list-inside space-y-1">
                    {usageStats.deletion_blockers.map((blocker: string, index: number) => (
                      <li key={index} className="text-sm">{blocker}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Account Form Dialog */}
      <Dialog open={showAccountForm} onOpenChange={setShowAccountForm}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{selectedAccount ? 'Edit Account' : 'Create Account'}</DialogTitle>
            <DialogDescription>
              {selectedAccount ? 'Update account information' : 'Add a new account to your chart of accounts'}
            </DialogDescription>
          </DialogHeader>
          
          <form onSubmit={handleAccountSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="account_code">Account Code *</Label>
                <Input
                  id="account_code"
                  value={accountForm.code}
                  onChange={(e) => setAccountForm(prev => ({ ...prev, code: e.target.value }))}
                  placeholder="e.g., 1000"
                  required
                  disabled={!!selectedAccount}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="account_name">Account Name *</Label>
                <Input
                  id="account_name"
                  value={accountForm.name}
                  onChange={(e) => setAccountForm(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="e.g., Cash"
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="account_type">Account Type *</Label>
                <Select
                  value={accountForm.account_type}
                  onValueChange={(value) => setAccountForm(prev => ({ ...prev, account_type: value, sub_type: '' }))}
                  disabled={!!selectedAccount}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select type" />
                  </SelectTrigger>
                  <SelectContent>
                    {ACCOUNT_TYPES.map(type => (
                      <SelectItem key={type.value} value={type.value}>
                        {type.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="sub_type">Sub Type</Label>
                <Select
                  value={accountForm.sub_type}
                  onValueChange={(value) => setAccountForm(prev => ({ ...prev, sub_type: value }))}
                  disabled={!accountForm.account_type || !!selectedAccount}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select sub type" />
                  </SelectTrigger>
                  <SelectContent>
                    {accountForm.account_type && SUB_TYPES[accountForm.account_type as keyof typeof SUB_TYPES]?.map(subType => (
                      <SelectItem key={subType.value} value={subType.value}>
                        {subType.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="parent_account">Parent Account</Label>
              <Select
                value={accountForm.parent_account_id}
                onValueChange={(value) => setAccountForm(prev => ({ ...prev, parent_account_id: value }))}
                disabled={!!selectedAccount}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select parent account (optional)" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">No parent account</SelectItem>
                  {accounts?.filter(acc => 
                    acc.account_type === accountForm.account_type && 
                    acc.id !== selectedAccount?.id
                  ).map(account => (
                    <SelectItem key={account.id} value={account.id}>
                      {account.code} - {account.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Input
                id="description"
                value={accountForm.description}
                onChange={(e) => setAccountForm(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Optional description"
              />
            </div>

            <div className="flex justify-end space-x-2">
              <Button type="button" variant="outline" onClick={() => setShowAccountForm(false)}>
                Cancel
              </Button>
              <Button 
                type="submit" 
                disabled={createAccount.isPending || updateAccount.isPending}
              >
                {(createAccount.isPending || updateAccount.isPending) ? (
                  <>
                    <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                    {selectedAccount ? 'Updating...' : 'Creating...'}
                  </>
                ) : (
                  <>
                    {selectedAccount ? 'Update Account' : 'Create Account'}
                  </>
                )}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}