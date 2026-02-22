import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { toast } from 'sonner';
import { Plus, Edit, TrendingUp, DollarSign, Globe, RefreshCw } from '@/components/icons';
import {
  useGetCurrencies,
  useCreateCurrency,
  useUpdateCurrency,
  useGetCurrencySummary,
  useCreateExchangeRate,
  useFetchLiveExchangeRates,
  type Currency,
  type CurrencyCreate,
  type CurrencyUpdate,
  type ExchangeRateCreate,
} from '@/lib/api/hooks/useAccounting';

interface CurrencyFormData {
  code: string;
  name: string;
  symbol: string;
  decimal_places: number;
  is_base_currency: boolean;
  active: boolean;
}

interface ExchangeRateFormData {
  from_currency: string;
  to_currency: string;
  rate: number;
  rate_date: string;
  source: string;
}

const CurrencyManagementPage: React.FC = () => {
  const [showCurrencyDialog, setShowCurrencyDialog] = useState(false);
  const [showRateDialog, setShowRateDialog] = useState(false);
  const [editingCurrency, setEditingCurrency] = useState<Currency | null>(null);
  const [currencyForm, setCurrencyForm] = useState<CurrencyFormData>({
    code: '',
    name: '',
    symbol: '',
    decimal_places: 2,
    is_base_currency: false,
    active: true,
  });
  const [rateForm, setRateForm] = useState<ExchangeRateFormData>({
    from_currency: '',
    to_currency: '',
    rate: 1.0,
    rate_date: new Date().toISOString().split('T')[0],
    source: 'manual',
  });

  const { data: currencies = [], isLoading: currenciesLoading } = useGetCurrencies();
  const { data: summary } = useGetCurrencySummary();
  const createCurrencyMutation = useCreateCurrency();
  const updateCurrencyMutation = useUpdateCurrency();
  const createRateMutation = useCreateExchangeRate();
  const fetchLiveRatesMutation = useFetchLiveExchangeRates();

  const handleCreateCurrency = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      const data: CurrencyCreate = {
        code: currencyForm.code.toUpperCase(),
        name: currencyForm.name,
        symbol: currencyForm.symbol,
        decimal_places: currencyForm.decimal_places,
        is_base_currency: currencyForm.is_base_currency,
        active: currencyForm.active,
      };

      await createCurrencyMutation.mutateAsync(data);
      toast.success('Currency created successfully');
      setShowCurrencyDialog(false);
      resetCurrencyForm();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to create currency');
    }
  };

  const handleUpdateCurrency = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!editingCurrency) return;

    try {
      const data: CurrencyUpdate = {
        name: currencyForm.name,
        symbol: currencyForm.symbol,
        decimal_places: currencyForm.decimal_places,
        is_base_currency: currencyForm.is_base_currency,
        active: currencyForm.active,
      };

      await updateCurrencyMutation.mutateAsync({
        currency_id: editingCurrency.id,
        data,
      });
      
      toast.success('Currency updated successfully');
      setShowCurrencyDialog(false);
      setEditingCurrency(null);
      resetCurrencyForm();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to update currency');
    }
  };

  const handleCreateExchangeRate = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      const data: ExchangeRateCreate = {
        from_currency: rateForm.from_currency,
        to_currency: rateForm.to_currency,
        rate: rateForm.rate,
        rate_date: rateForm.rate_date,
        source: rateForm.source,
      };

      await createRateMutation.mutateAsync(data);
      toast.success('Exchange rate created successfully');
      setShowRateDialog(false);
      resetRateForm();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to create exchange rate');
    }
  };

  const handleFetchLiveRates = async () => {
    try {
      const baseCurrency = summary?.base_currency?.code || 'USD';
      const result = await fetchLiveRatesMutation.mutateAsync(baseCurrency);
      
      if (result.success) {
        toast.success(`Fetched ${result.rates_count} live exchange rates`);
      } else {
        toast.error(result.error || 'Failed to fetch live rates');
      }
    } catch (error: any) {
      toast.error('Failed to fetch live exchange rates');
    }
  };

  const resetCurrencyForm = () => {
    setCurrencyForm({
      code: '',
      name: '',
      symbol: '',
      decimal_places: 2,
      is_base_currency: false,
      active: true,
    });
  };

  const resetRateForm = () => {
    setRateForm({
      from_currency: '',
      to_currency: '',
      rate: 1.0,
      rate_date: new Date().toISOString().split('T')[0],
      source: 'manual',
    });
  };

  const openEditDialog = (currency: Currency) => {
    setEditingCurrency(currency);
    setCurrencyForm({
      code: currency.code,
      name: currency.name,
      symbol: currency.symbol,
      decimal_places: currency.decimal_places,
      is_base_currency: currency.is_base_currency,
      active: currency.active,
    });
    setShowCurrencyDialog(true);
  };

  const openCreateDialog = () => {
    setEditingCurrency(null);
    resetCurrencyForm();
    setShowCurrencyDialog(true);
  };

  if (currenciesLoading) {
    return <div className="p-6">Loading currencies...</div>;
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Currency Management</h1>
          <p className="text-muted-foreground">
            Manage currencies and exchange rates for multi-currency support
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            onClick={handleFetchLiveRates}
            variant="outline"
            disabled={fetchLiveRatesMutation.isPending}
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Fetch Live Rates
          </Button>
          <Dialog open={showRateDialog} onOpenChange={setShowRateDialog}>
            <DialogTrigger asChild>
              <Button variant="outline">
                <TrendingUp className="h-4 w-4 mr-2" />
                Add Exchange Rate
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Add Exchange Rate</DialogTitle>
              </DialogHeader>
              <form onSubmit={handleCreateExchangeRate} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="from_currency">From Currency</Label>
                    <Input
                      id="from_currency"
                      value={rateForm.from_currency}
                      onChange={(e) =>
                        setRateForm({ ...rateForm, from_currency: e.target.value.toUpperCase() })
                      }
                      placeholder="USD"
                      maxLength={3}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="to_currency">To Currency</Label>
                    <Input
                      id="to_currency"
                      value={rateForm.to_currency}
                      onChange={(e) =>
                        setRateForm({ ...rateForm, to_currency: e.target.value.toUpperCase() })
                      }
                      placeholder="EUR"
                      maxLength={3}
                      required
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="rate">Exchange Rate</Label>
                    <Input
                      id="rate"
                      type="number"
                      step="0.000001"
                      value={rateForm.rate}
                      onChange={(e) =>
                        setRateForm({ ...rateForm, rate: parseFloat(e.target.value) || 0 })
                      }
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="rate_date">Rate Date</Label>
                    <Input
                      id="rate_date"
                      type="date"
                      value={rateForm.rate_date}
                      onChange={(e) =>
                        setRateForm({ ...rateForm, rate_date: e.target.value })
                      }
                      required
                    />
                  </div>
                </div>
                <div className="flex justify-end gap-2">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setShowRateDialog(false)}
                  >
                    Cancel
                  </Button>
                  <Button type="submit" disabled={createRateMutation.isPending}>
                    {createRateMutation.isPending ? 'Creating...' : 'Create Rate'}
                  </Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
          <Dialog open={showCurrencyDialog} onOpenChange={setShowCurrencyDialog}>
            <DialogTrigger asChild>
              <Button onClick={openCreateDialog}>
                <Plus className="h-4 w-4 mr-2" />
                Add Currency
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>
                  {editingCurrency ? 'Edit Currency' : 'Add Currency'}
                </DialogTitle>
              </DialogHeader>
              <form
                onSubmit={editingCurrency ? handleUpdateCurrency : handleCreateCurrency}
                className="space-y-4"
              >
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="code">Currency Code</Label>
                    <Input
                      id="code"
                      value={currencyForm.code}
                      onChange={(e) =>
                        setCurrencyForm({ ...currencyForm, code: e.target.value.toUpperCase() })
                      }
                      placeholder="USD"
                      maxLength={3}
                      disabled={!!editingCurrency}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="symbol">Symbol</Label>
                    <Input
                      id="symbol"
                      value={currencyForm.symbol}
                      onChange={(e) =>
                        setCurrencyForm({ ...currencyForm, symbol: e.target.value })
                      }
                      placeholder="$"
                      maxLength={10}
                    />
                  </div>
                </div>
                <div>
                  <Label htmlFor="name">Currency Name</Label>
                  <Input
                    id="name"
                    value={currencyForm.name}
                    onChange={(e) =>
                      setCurrencyForm({ ...currencyForm, name: e.target.value })
                    }
                    placeholder="US Dollar"
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="decimal_places">Decimal Places</Label>
                  <Input
                    id="decimal_places"
                    type="number"
                    min="0"
                    max="6"
                    value={currencyForm.decimal_places}
                    onChange={(e) =>
                      setCurrencyForm({
                        ...currencyForm,
                        decimal_places: parseInt(e.target.value) || 0,
                      })
                    }
                    required
                  />
                </div>
                <div className="flex items-center space-x-2">
                  <Switch
                    id="is_base_currency"
                    checked={currencyForm.is_base_currency}
                    onCheckedChange={(checked) =>
                      setCurrencyForm({ ...currencyForm, is_base_currency: checked })
                    }
                  />
                  <Label htmlFor="is_base_currency">Base Currency</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Switch
                    id="active"
                    checked={currencyForm.active}
                    onCheckedChange={(checked) =>
                      setCurrencyForm({ ...currencyForm, active: checked })
                    }
                  />
                  <Label htmlFor="active">Active</Label>
                </div>
                <div className="flex justify-end gap-2">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => {
                      setShowCurrencyDialog(false);
                      setEditingCurrency(null);
                    }}
                  >
                    Cancel
                  </Button>
                  <Button
                    type="submit"
                    disabled={
                      editingCurrency
                        ? updateCurrencyMutation.isPending
                        : createCurrencyMutation.isPending
                    }
                  >
                    {editingCurrency
                      ? updateCurrencyMutation.isPending
                        ? 'Updating...'
                        : 'Update Currency'
                      : createCurrencyMutation.isPending
                      ? 'Creating...'
                      : 'Create Currency'}
                  </Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Summary Cards */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Currencies</CardTitle>
              <Globe className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{summary.total_currencies}</div>
              <p className="text-xs text-muted-foreground">
                {summary.active_currencies} active
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Base Currency</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{summary.base_currency.code}</div>
              <p className="text-xs text-muted-foreground">
                {summary.base_currency.name}
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Multi-Currency</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {summary.multi_currency_enabled ? 'Enabled' : 'Disabled'}
              </div>
              <p className="text-xs text-muted-foreground">
                {summary.recent_exchange_rates.length} recent rates
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Currencies Table */}
      <Card>
        <CardHeader>
          <CardTitle>Currencies</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Code</TableHead>
                <TableHead>Name</TableHead>
                <TableHead>Symbol</TableHead>
                <TableHead>Decimal Places</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Base Currency</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {currencies.map((currency) => (
                <TableRow key={currency.id}>
                  <TableCell className="font-medium">{currency.code}</TableCell>
                  <TableCell>{currency.name}</TableCell>
                  <TableCell>{currency.symbol}</TableCell>
                  <TableCell>{currency.decimal_places}</TableCell>
                  <TableCell>
                    <Badge variant={currency.active ? 'default' : 'secondary'}>
                      {currency.active ? 'Active' : 'Inactive'}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    {currency.is_base_currency && (
                      <Badge variant="outline">Base</Badge>
                    )}
                  </TableCell>
                  <TableCell>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => openEditDialog(currency)}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Recent Exchange Rates */}
      {summary?.recent_exchange_rates && summary.recent_exchange_rates.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Recent Exchange Rates</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>From</TableHead>
                  <TableHead>To</TableHead>
                  <TableHead>Rate</TableHead>
                  <TableHead>Date</TableHead>
                  <TableHead>Source</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {summary.recent_exchange_rates.map((rate) => (
                  <TableRow key={rate.id}>
                    <TableCell>{rate.from_currency}</TableCell>
                    <TableCell>{rate.to_currency}</TableCell>
                    <TableCell>{rate.rate.toFixed(6)}</TableCell>
                    <TableCell>{rate.rate_date}</TableCell>
                    <TableCell>
                      <Badge variant="outline">{rate.source}</Badge>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default CurrencyManagementPage;