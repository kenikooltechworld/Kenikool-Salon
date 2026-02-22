'use client';

import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Search, X, Save } from 'lucide-react';

interface Product {
  id: string;
  name: string;
  sku: string;
  category: string;
  quantity: number;
  price: number;
}

export function AdvancedSearch() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [selectedSuppliers, setSelectedSuppliers] = useState<string[]>([]);
  const [stockMin, setStockMin] = useState<number | ''>('');
  const [stockMax, setStockMax] = useState<number | ''>('');
  const [priceMin, setPriceMin] = useState<number | ''>('');
  const [priceMax, setPriceMax] = useState<number | ''>('');
  const [sortBy, setSortBy] = useState('name');
  const [sortOrder, setSortOrder] = useState(1);
  const [presetName, setPresetName] = useState('');
  const [showSavePreset, setShowSavePreset] = useState(false);

  const queryClient = useQueryClient();

  const { data: filters } = useQuery({
    queryKey: ['availableFilters'],
    queryFn: async () => {
      const res = await fetch('/api/inventory/search/filters');
      if (!res.ok) throw new Error('Failed to fetch filters');
      return res.json();
    },
  });

  const { data: searchResults, isLoading } = useQuery({
    queryKey: [
      'searchProducts',
      searchQuery,
      selectedCategories,
      selectedSuppliers,
      stockMin,
      stockMax,
      priceMin,
      priceMax,
      sortBy,
      sortOrder,
    ],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (searchQuery) params.append('query', searchQuery);
      selectedCategories.forEach((c) => params.append('categories', c));
      selectedSuppliers.forEach((s) => params.append('suppliers', s));
      if (stockMin !== '') params.append('stock_min', stockMin.toString());
      if (stockMax !== '') params.append('stock_max', stockMax.toString());
      if (priceMin !== '') params.append('price_min', priceMin.toString());
      if (priceMax !== '') params.append('price_max', priceMax.toString());
      params.append('sort_by', sortBy);
      params.append('sort_order', sortOrder.toString());

      const res = await fetch(`/api/inventory/search/products?${params}`);
      if (!res.ok) throw new Error('Failed to search');
      return res.json();
    },
  });

  const savePresetMutation = useMutation({
    mutationFn: async () => {
      const params = new URLSearchParams();
      params.append('preset_name', presetName);
      if (searchQuery) params.append('query', searchQuery);
      selectedCategories.forEach((c) => params.append('categories', c));
      selectedSuppliers.forEach((s) => params.append('suppliers', s));
      if (stockMin !== '') params.append('stock_min', stockMin.toString());
      if (stockMax !== '') params.append('stock_max', stockMax.toString());
      if (priceMin !== '') params.append('price_min', priceMin.toString());
      if (priceMax !== '') params.append('price_max', priceMax.toString());
      params.append('sort_by', sortBy);
      params.append('sort_order', sortOrder.toString());

      const res = await fetch('/api/inventory/search/presets', {
        method: 'POST',
        body: params,
      });
      if (!res.ok) throw new Error('Failed to save preset');
      return res.json();
    },
    onSuccess: () => {
      toast.success('Preset saved');
      setPresetName('');
      setShowSavePreset(false);
    },
    onError: () => {
      toast.error('Failed to save preset');
    },
  });

  const clearFilters = () => {
    setSearchQuery('');
    setSelectedCategories([]);
    setSelectedSuppliers([]);
    setStockMin('');
    setStockMax('');
    setPriceMin('');
    setPriceMax('');
    setSortBy('name');
    setSortOrder(1);
  };

  const activeFilterCount =
    (searchQuery ? 1 : 0) +
    selectedCategories.length +
    selectedSuppliers.length +
    (stockMin !== '' || stockMax !== '' ? 1 : 0) +
    (priceMin !== '' || priceMax !== '' ? 1 : 0);

  const products = searchResults?.data?.products || [];
  const total = searchResults?.data?.total || 0;

  return (
    <div className="space-y-6">
      {/* Search Filters */}
      <div className="bg-white p-6 rounded-lg border space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-lg">Search & Filter</h3>
          {activeFilterCount > 0 && (
            <div className="flex items-center gap-2">
              <Badge variant="secondary">{activeFilterCount} active</Badge>
              <Button
                variant="ghost"
                size="sm"
                onClick={clearFilters}
              >
                <X className="w-4 h-4 mr-1" />
                Clear All
              </Button>
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {/* Search Query */}
          <div>
            <Label htmlFor="search">Search</Label>
            <div className="relative">
              <Search className="absolute left-3 top-3 w-4 h-4 text-gray-400" />
              <Input
                id="search"
                placeholder="Name, SKU, category..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>

          {/* Stock Range */}
          <div>
            <Label>Stock Range</Label>
            <div className="flex gap-2">
              <Input
                type="number"
                placeholder="Min"
                value={stockMin}
                onChange={(e) =>
                  setStockMin(e.target.value === '' ? '' : parseInt(e.target.value))
                }
                min="0"
              />
              <Input
                type="number"
                placeholder="Max"
                value={stockMax}
                onChange={(e) =>
                  setStockMax(e.target.value === '' ? '' : parseInt(e.target.value))
                }
                min="0"
              />
            </div>
          </div>

          {/* Price Range */}
          <div>
            <Label>Price Range</Label>
            <div className="flex gap-2">
              <Input
                type="number"
                placeholder="Min"
                value={priceMin}
                onChange={(e) =>
                  setPriceMin(e.target.value === '' ? '' : parseFloat(e.target.value))
                }
                min="0"
                step="0.01"
              />
              <Input
                type="number"
                placeholder="Max"
                value={priceMax}
                onChange={(e) =>
                  setPriceMax(e.target.value === '' ? '' : parseFloat(e.target.value))
                }
                min="0"
                step="0.01"
              />
            </div>
          </div>

          {/* Sort By */}
          <div>
            <Label htmlFor="sort">Sort By</Label>
            <Select value={sortBy} onValueChange={setSortBy}>
              <SelectTrigger id="sort">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="name">Name</SelectItem>
                <SelectItem value="quantity">Quantity</SelectItem>
                <SelectItem value="value">Price</SelectItem>
                <SelectItem value="updated">Last Updated</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Sort Order */}
          <div>
            <Label htmlFor="order">Order</Label>
            <Select
              value={sortOrder.toString()}
              onValueChange={(v) => setSortOrder(parseInt(v))}
            >
              <SelectTrigger id="order">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="1">Ascending</SelectItem>
                <SelectItem value="-1">Descending</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Save Preset */}
        {!showSavePreset ? (
          <Button
            variant="outline"
            onClick={() => setShowSavePreset(true)}
            className="w-full"
          >
            <Save className="w-4 h-4 mr-2" />
            Save as Preset
          </Button>
        ) : (
          <div className="flex gap-2">
            <Input
              placeholder="Preset name"
              value={presetName}
              onChange={(e) => setPresetName(e.target.value)}
            />
            <Button
              onClick={() => savePresetMutation.mutate()}
              disabled={!presetName || savePresetMutation.isPending}
            >
              Save
            </Button>
            <Button
              variant="outline"
              onClick={() => {
                setShowSavePreset(false);
                setPresetName('');
              }}
            >
              Cancel
            </Button>
          </div>
        )}
      </div>

      {/* Results */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold">
            Results ({total} products)
          </h3>
        </div>

        {isLoading ? (
          <div className="text-center py-8">Loading...</div>
        ) : products.length > 0 ? (
          <div className="border rounded-lg overflow-hidden">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>SKU</TableHead>
                  <TableHead>Category</TableHead>
                  <TableHead>Stock</TableHead>
                  <TableHead>Price</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {products.map((product: Product) => (
                  <TableRow key={product.id}>
                    <TableCell className="font-medium">
                      {product.name}
                    </TableCell>
                    <TableCell className="text-sm text-gray-600">
                      {product.sku}
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">
                        {product.category}
                      </Badge>
                    </TableCell>
                    <TableCell>{product.quantity}</TableCell>
                    <TableCell>${product.price.toFixed(2)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            No products found
          </div>
        )}
      </div>
    </div>
  );
}
