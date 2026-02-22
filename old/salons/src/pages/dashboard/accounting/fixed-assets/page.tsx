import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
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
import { Plus, Edit, TrendingDown, Package, Calendar, DollarSign, Trash2 } from '@/components/icons';
import {
  useGetFixedAssets,
  useCreateFixedAsset,
  useUpdateFixedAsset,
  useGetFixedAssetsSummary,
  usePostDepreciation,
  useDisposeAsset,
  usePostBulkDepreciation,
  useGetDepreciationSchedule,
  type FixedAsset,
  type FixedAssetCreate,
  type FixedAssetUpdate,
  type AssetDisposalCreate,
  type DepreciationPostingRequest,
} from '@/lib/api/hooks/useAccounting';

interface AssetFormData {
  name: string;
  description: string;
  category: string;
  purchase_date: string;
  purchase_price: number;
  salvage_value: number;
  useful_life_years: number;
  useful_life_units?: number;
  depreciation_method: 'straight_line' | 'declining_balance' | 'double_declining_balance' | 'units_of_production';
  location: string;
  serial_number: string;
  vendor_id?: string;
  currency_code: string;
}

interface DisposalFormData {
  disposal_date: string;
  disposal_price: number;
  disposal_method: string;
  notes: string;
}

const FixedAssetsPage: React.FC = () => {
  const [showAssetDialog, setShowAssetDialog] = useState(false);
  const [showDisposalDialog, setShowDisposalDialog] = useState(false);
  const [showDepreciationDialog, setShowDepreciationDialog] = useState(false);
  const [editingAsset, setEditingAsset] = useState<FixedAsset | null>(null);
  const [disposingAsset, setDisposingAsset] = useState<FixedAsset | null>(null);
  const [selectedAssets, setSelectedAssets] = useState<string[]>([]);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [categoryFilter, setCategoryFilter] = useState<string>('');

  const [assetForm, setAssetForm] = useState<AssetFormData>({
    name: '',
    description: '',
    category: '',
    purchase_date: '',
    purchase_price: 0,
    salvage_value: 0,
    useful_life_years: 5,
    depreciation_method: 'straight_line',
    location: '',
    serial_number: '',
    currency_code: 'USD',
  });

  const [disposalForm, setDisposalForm] = useState<DisposalFormData>({
    disposal_date: new Date().toISOString().split('T')[0],
    disposal_price: 0,
    disposal_method: 'sale',
    notes: '',
  });

  const [depreciationDate, setDepreciationDate] = useState(
    new Date().toISOString().split('T')[0]
  );

  const { data: assets = [], isLoading: assetsLoading } = useGetFixedAssets({
    status: statusFilter || undefined,
    category: categoryFilter || undefined,
  });
  const { data: summary } = useGetFixedAssetsSummary();
  const { data: depreciationSchedule } = useGetDepreciationSchedule();
  
  const createAssetMutation = useCreateFixedAsset();
  const updateAssetMutation = useUpdateFixedAsset();
  const postDepreciationMutation = usePostDepreciation();
  const disposeAssetMutation = useDisposeAsset();
  const postBulkDepreciationMutation = usePostBulkDepreciation();

  const handleCreateAsset = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      const data: FixedAssetCreate = {
        ...assetForm,
        useful_life_units: assetForm.useful_life_units || undefined,
        vendor_id: assetForm.vendor_id || undefined,
      };

      await createAssetMutation.mutateAsync(data);
      toast.success('Fixed asset created successfully');
      setShowAssetDialog(false);
      resetAssetForm();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to create asset');
    }
  };

  const handleUpdateAsset = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!editingAsset) return;

    try {
      const data: FixedAssetUpdate = {
        name: assetForm.name,
        description: assetForm.description,
        category: assetForm.category,
        location: assetForm.location,
        serial_number: assetForm.serial_number,
      };

      await updateAssetMutation.mutateAsync({
        asset_id: editingAsset.id,
        data,
      });
      
      toast.success('Asset updated successfully');
      setShowAssetDialog(false);
      setEditingAsset(null);
      resetAssetForm();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to update asset');
    }
  };

  const handleDisposeAsset = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!disposingAsset) return;

    try {
      const data: AssetDisposalCreate = {
        disposal_date: disposalForm.disposal_date,
        disposal_price: disposalForm.disposal_price,
        disposal_method: disposalForm.disposal_method,
        notes: disposalForm.notes,
      };

      await disposeAssetMutation.mutateAsync({
        asset_id: disposingAsset.id,
        disposal_data: data,
      });
      
      toast.success('Asset disposed successfully');
      setShowDisposalDialog(false);
      setDisposingAsset(null);
      resetDisposalForm();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to dispose asset');
    }
  };

  const handlePostDepreciation = async (assetId: string) => {
    try {
      await postDepreciationMutation.mutateAsync({
        asset_id: assetId,
        depreciation_date: depreciationDate,
      });
      toast.success('Depreciation posted successfully');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to post depreciation');
    }
  };

  const handleBulkDepreciation = async () => {
    try {
      const data: DepreciationPostingRequest = {
        asset_ids: selectedAssets.length > 0 ? selectedAssets : undefined,
        depreciation_date: depreciationDate,
        period_type: 'monthly',
      };

      const result = await postBulkDepreciationMutation.mutateAsync(data);
      
      toast.success(
        `Posted depreciation for ${result.posted_count} assets. Total: $${result.total_depreciation_amount.toFixed(2)}`
      );
      
      if (result.failed_assets.length > 0) {
        toast.warning(`${result.failed_assets.length} assets failed to process`);
      }
      
      setShowDepreciationDialog(false);
      setSelectedAssets([]);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to post bulk depreciation');
    }
  };

  const resetAssetForm = () => {
    setAssetForm({
      name: '',
      description: '',
      category: '',
      purchase_date: '',
      purchase_price: 0,
      salvage_value: 0,
      useful_life_years: 5,
      depreciation_method: 'straight_line',
      location: '',
      serial_number: '',
      currency_code: 'USD',
    });
  };

  const resetDisposalForm = () => {
    setDisposalForm({
      disposal_date: new Date().toISOString().split('T')[0],
      disposal_price: 0,
      disposal_method: 'sale',
      notes: '',
    });
  };

  const openEditDialog = (asset: FixedAsset) => {
    setEditingAsset(asset);
    setAssetForm({
      name: asset.name,
      description: asset.description || '',
      category: asset.category,
      purchase_date: asset.purchase_date,
      purchase_price: asset.purchase_price,
      salvage_value: asset.salvage_value,
      useful_life_years: asset.useful_life_years,
      useful_life_units: asset.useful_life_units,
      depreciation_method: asset.depreciation_method,
      location: asset.location || '',
      serial_number: asset.serial_number || '',
      vendor_id: asset.vendor_id,
      currency_code: asset.currency_code,
    });
    setShowAssetDialog(true);
  };

  const openCreateDialog = () => {
    setEditingAsset(null);
    resetAssetForm();
    setShowAssetDialog(true);
  };

  const openDisposalDialog = (asset: FixedAsset) => {
    setDisposingAsset(asset);
    setDisposalForm({
      ...disposalForm,
      disposal_price: asset.book_value,
    });
    setShowDisposalDialog(true);
  };

  const toggleAssetSelection = (assetId: string) => {
    setSelectedAssets(prev =>
      prev.includes(assetId)
        ? prev.filter(id => id !== assetId)
        : [...prev, assetId]
    );
  };

  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case 'active':
        return 'default';
      case 'disposed':
        return 'destructive';
      case 'fully_depreciated':
        return 'secondary';
      case 'inactive':
        return 'outline';
      default:
        return 'outline';
    }
  };

  if (assetsLoading) {
    return <div className="p-6">Loading fixed assets...</div>;
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Fixed Assets Management</h1>
          <p className="text-muted-foreground">
            Manage fixed assets, depreciation, and asset disposal
          </p>
        </div>
        <div className="flex gap-2">
          <Dialog open={showDepreciationDialog} onOpenChange={setShowDepreciationDialog}>
            <DialogTrigger asChild>
              <Button variant="outline">
                <TrendingDown className="h-4 w-4 mr-2" />
                Post Depreciation
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Post Depreciation</DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="depreciation_date">Depreciation Date</Label>
                  <Input
                    id="depreciation_date"
                    type="date"
                    value={depreciationDate}
                    onChange={(e) => setDepreciationDate(e.target.value)}
                    required
                  />
                </div>
                <div className="text-sm text-muted-foreground">
                  {selectedAssets.length > 0
                    ? `Post depreciation for ${selectedAssets.length} selected assets`
                    : 'Post depreciation for all active assets'}
                </div>
                <div className="flex justify-end gap-2">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setShowDepreciationDialog(false)}
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={handleBulkDepreciation}
                    disabled={postBulkDepreciationMutation.isPending}
                  >
                    {postBulkDepreciationMutation.isPending ? 'Posting...' : 'Post Depreciation'}
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
          <Dialog open={showAssetDialog} onOpenChange={setShowAssetDialog}>
            <DialogTrigger asChild>
              <Button onClick={openCreateDialog}>
                <Plus className="h-4 w-4 mr-2" />
                Add Asset
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>
                  {editingAsset ? 'Edit Fixed Asset' : 'Add Fixed Asset'}
                </DialogTitle>
              </DialogHeader>
              <form
                onSubmit={editingAsset ? handleUpdateAsset : handleCreateAsset}
                className="space-y-4"
              >
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="name">Asset Name</Label>
                    <Input
                      id="name"
                      value={assetForm.name}
                      onChange={(e) =>
                        setAssetForm({ ...assetForm, name: e.target.value })
                      }
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="category">Category</Label>
                    <Input
                      id="category"
                      value={assetForm.category}
                      onChange={(e) =>
                        setAssetForm({ ...assetForm, category: e.target.value })
                      }
                      required
                    />
                  </div>
                </div>
                <div>
                  <Label htmlFor="description">Description</Label>
                  <Textarea
                    id="description"
                    value={assetForm.description}
                    onChange={(e) =>
                      setAssetForm({ ...assetForm, description: e.target.value })
                    }
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="purchase_date">Purchase Date</Label>
                    <Input
                      id="purchase_date"
                      type="date"
                      value={assetForm.purchase_date}
                      onChange={(e) =>
                        setAssetForm({ ...assetForm, purchase_date: e.target.value })
                      }
                      disabled={!!editingAsset}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="purchase_price">Purchase Price</Label>
                    <Input
                      id="purchase_price"
                      type="number"
                      step="0.01"
                      value={assetForm.purchase_price}
                      onChange={(e) =>
                        setAssetForm({
                          ...assetForm,
                          purchase_price: parseFloat(e.target.value) || 0,
                        })
                      }
                      disabled={!!editingAsset}
                      required
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="salvage_value">Salvage Value</Label>
                    <Input
                      id="salvage_value"
                      type="number"
                      step="0.01"
                      value={assetForm.salvage_value}
                      onChange={(e) =>
                        setAssetForm({
                          ...assetForm,
                          salvage_value: parseFloat(e.target.value) || 0,
                        })
                      }
                      disabled={!!editingAsset}
                    />
                  </div>
                  <div>
                    <Label htmlFor="useful_life_years">Useful Life (Years)</Label>
                    <Input
                      id="useful_life_years"
                      type="number"
                      min="1"
                      value={assetForm.useful_life_years}
                      onChange={(e) =>
                        setAssetForm({
                          ...assetForm,
                          useful_life_years: parseInt(e.target.value) || 1,
                        })
                      }
                      disabled={!!editingAsset}
                      required
                    />
                  </div>
                </div>
                <div>
                  <Label htmlFor="depreciation_method">Depreciation Method</Label>
                  <Select
                    value={assetForm.depreciation_method}
                    onValueChange={(value: any) =>
                      setAssetForm({ ...assetForm, depreciation_method: value })
                    }
                    disabled={!!editingAsset}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="straight_line">Straight Line</SelectItem>
                      <SelectItem value="declining_balance">Declining Balance</SelectItem>
                      <SelectItem value="double_declining_balance">Double Declining Balance</SelectItem>
                      <SelectItem value="units_of_production">Units of Production</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="location">Location</Label>
                    <Input
                      id="location"
                      value={assetForm.location}
                      onChange={(e) =>
                        setAssetForm({ ...assetForm, location: e.target.value })
                      }
                    />
                  </div>
                  <div>
                    <Label htmlFor="serial_number">Serial Number</Label>
                    <Input
                      id="serial_number"
                      value={assetForm.serial_number}
                      onChange={(e) =>
                        setAssetForm({ ...assetForm, serial_number: e.target.value })
                      }
                    />
                  </div>
                </div>
                <div className="flex justify-end gap-2">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => {
                      setShowAssetDialog(false);
                      setEditingAsset(null);
                    }}
                  >
                    Cancel
                  </Button>
                  <Button
                    type="submit"
                    disabled={
                      editingAsset
                        ? updateAssetMutation.isPending
                        : createAssetMutation.isPending
                    }
                  >
                    {editingAsset
                      ? updateAssetMutation.isPending
                        ? 'Updating...'
                        : 'Update Asset'
                      : createAssetMutation.isPending
                      ? 'Creating...'
                      : 'Create Asset'}
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
              <CardTitle className="text-sm font-medium">Total Assets</CardTitle>
              <Package className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{summary.total_assets}</div>
              <p className="text-xs text-muted-foreground">
                {summary.active_assets} active
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Cost</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                ${summary.status_breakdown
                  ?.reduce((sum, item) => sum + (item.total_cost || 0), 0)
                  ?.toFixed(0) || '0'}
              </div>
              <p className="text-xs text-muted-foreground">
                Original purchase cost
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Book Value</CardTitle>
              <TrendingDown className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                ${summary.status_breakdown
                  ?.reduce((sum, item) => sum + (item.total_book_value || 0), 0)
                  ?.toFixed(0) || '0'}
              </div>
              <p className="text-xs text-muted-foreground">
                Current book value
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Filters */}
      <div className="flex gap-4">
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-48">
            <SelectValue placeholder="Filter by status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="">All Statuses</SelectItem>
            <SelectItem value="active">Active</SelectItem>
            <SelectItem value="disposed">Disposed</SelectItem>
            <SelectItem value="fully_depreciated">Fully Depreciated</SelectItem>
            <SelectItem value="inactive">Inactive</SelectItem>
          </SelectContent>
        </Select>
        <Input
          placeholder="Filter by category"
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value)}
          className="w-48"
        />
      </div>

      {/* Assets Table */}
      <Card>
        <CardHeader>
          <CardTitle>Fixed Assets</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-12">
                  <input
                    type="checkbox"
                    checked={selectedAssets.length === assets.length && assets.length > 0}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedAssets(assets.map(asset => asset.id));
                      } else {
                        setSelectedAssets([]);
                      }
                    }}
                  />
                </TableHead>
                <TableHead>Asset #</TableHead>
                <TableHead>Name</TableHead>
                <TableHead>Category</TableHead>
                <TableHead>Purchase Price</TableHead>
                <TableHead>Book Value</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {assets.map((asset) => (
                <TableRow key={asset.id}>
                  <TableCell>
                    <input
                      type="checkbox"
                      checked={selectedAssets.includes(asset.id)}
                      onChange={() => toggleAssetSelection(asset.id)}
                    />
                  </TableCell>
                  <TableCell className="font-medium">{asset.asset_number}</TableCell>
                  <TableCell>{asset.name}</TableCell>
                  <TableCell>{asset.category}</TableCell>
                  <TableCell>${asset.purchase_price.toFixed(2)}</TableCell>
                  <TableCell>${asset.book_value.toFixed(2)}</TableCell>
                  <TableCell>
                    <Badge variant={getStatusBadgeVariant(asset.status)}>
                      {asset.status.replace('_', ' ')}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-1">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => openEditDialog(asset)}
                      >
                        <Edit className="h-4 w-4" />
                      </Button>
                      {asset.status === 'active' && (
                        <>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handlePostDepreciation(asset.id)}
                            disabled={postDepreciationMutation.isPending}
                          >
                            <TrendingDown className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => openDisposalDialog(asset)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </>
                      )}
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Asset Disposal Dialog */}
      <Dialog open={showDisposalDialog} onOpenChange={setShowDisposalDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Dispose Asset</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleDisposeAsset} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="disposal_date">Disposal Date</Label>
                <Input
                  id="disposal_date"
                  type="date"
                  value={disposalForm.disposal_date}
                  onChange={(e) =>
                    setDisposalForm({ ...disposalForm, disposal_date: e.target.value })
                  }
                  required
                />
              </div>
              <div>
                <Label htmlFor="disposal_price">Disposal Price</Label>
                <Input
                  id="disposal_price"
                  type="number"
                  step="0.01"
                  value={disposalForm.disposal_price}
                  onChange={(e) =>
                    setDisposalForm({
                      ...disposalForm,
                      disposal_price: parseFloat(e.target.value) || 0,
                    })
                  }
                  required
                />
              </div>
            </div>
            <div>
              <Label htmlFor="disposal_method">Disposal Method</Label>
              <Select
                value={disposalForm.disposal_method}
                onValueChange={(value) =>
                  setDisposalForm({ ...disposalForm, disposal_method: value })
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="sale">Sale</SelectItem>
                  <SelectItem value="scrap">Scrap</SelectItem>
                  <SelectItem value="trade">Trade-in</SelectItem>
                  <SelectItem value="donation">Donation</SelectItem>
                  <SelectItem value="other">Other</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="disposal_notes">Notes</Label>
              <Textarea
                id="disposal_notes"
                value={disposalForm.notes}
                onChange={(e) =>
                  setDisposalForm({ ...disposalForm, notes: e.target.value })
                }
              />
            </div>
            <div className="flex justify-end gap-2">
              <Button
                type="button"
                variant="outline"
                onClick={() => {
                  setShowDisposalDialog(false);
                  setDisposingAsset(null);
                }}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                variant="destructive"
                disabled={disposeAssetMutation.isPending}
              >
                {disposeAssetMutation.isPending ? 'Disposing...' : 'Dispose Asset'}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default FixedAssetsPage;