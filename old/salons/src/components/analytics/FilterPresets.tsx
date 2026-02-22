import React, { useState, useEffect } from 'react';

interface Filter {
  id: string;
  field: string;
  operator: string;
  value: string | number | boolean | string[];
  logicalOperator?: 'AND' | 'OR';
}

interface Preset {
  id: string;
  name: string;
  description?: string;
  filters: Filter[];
  category?: string;
  createdAt: string;
  isPublic?: boolean;
}

interface FilterPresetsProps {
  currentFilters: Filter[];
  onLoadPreset?: (filters: Filter[]) => void;
}

export const FilterPresets: React.FC<FilterPresetsProps> = ({ currentFilters, onLoadPreset }) => {
  const [presets, setPresets] = useState<Preset[]>([]);
  const [presetName, setPresetName] = useState('');
  const [presetDescription, setPresetDescription] = useState('');
  const [presetCategory, setPresetCategory] = useState('');
  const [showSaveForm, setShowSaveForm] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [isPublic, setIsPublic] = useState(false);

  useEffect(() => {
    loadPresetsFromStorage();
  }, []);

  const loadPresetsFromStorage = () => {
    try {
      const stored = localStorage.getItem('filter_presets');
      if (stored) {
        setPresets(JSON.parse(stored));
      }
    } catch (error) {
      console.error('Error loading presets:', error);
    }
  };

  const savePreset = () => {
    if (!presetName.trim()) {
      alert('Please enter a preset name');
      return;
    }

    const newPreset: Preset = {
      id: `preset_${Date.now()}`,
      name: presetName,
      description: presetDescription,
      filters: currentFilters,
      category: presetCategory || 'General',
      createdAt: new Date().toISOString(),
      isPublic,
    };

    const updatedPresets = [...presets, newPreset];
    setPresets(updatedPresets);
    localStorage.setItem('filter_presets', JSON.stringify(updatedPresets));
    setPresetName('');
    setPresetDescription('');
    setPresetCategory('');
    setIsPublic(false);
    setShowSaveForm(false);
  };

  const loadPreset = (preset: Preset) => {
    onLoadPreset?.(preset.filters);
  };

  const deletePreset = (presetId: string) => {
    const updatedPresets = presets.filter((p) => p.id !== presetId);
    setPresets(updatedPresets);
    localStorage.setItem('filter_presets', JSON.stringify(updatedPresets));
  };

  const duplicatePreset = (preset: Preset) => {
    const newPreset: Preset = {
      ...preset,
      id: `preset_${Date.now()}`,
      name: `${preset.name} (Copy)`,
      createdAt: new Date().toISOString(),
    };
    const updatedPresets = [...presets, newPreset];
    setPresets(updatedPresets);
    localStorage.setItem('filter_presets', JSON.stringify(updatedPresets));
  };

  const categories = Array.from(new Set(presets.map((p) => p.category || 'General')));

  const filteredPresets = presets.filter((preset) => {
    const matchesSearch =
      preset.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      preset.description?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = !selectedCategory || preset.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <div className="flex items-center justify-between mb-4">
        <h4 className="text-sm font-bold text-gray-900">Filter Presets</h4>
        <button
          onClick={() => setShowSaveForm(!showSaveForm)}
          className="text-xs px-2 py-1 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          {showSaveForm ? 'Cancel' : 'Save Current'}
        </button>
      </div>

      {showSaveForm && (
        <div className="mb-4 p-3 bg-gray-50 rounded border border-gray-200 space-y-2">
          <input
            type="text"
            value={presetName}
            onChange={(e) => setPresetName(e.target.value)}
            placeholder="Preset name"
            className="w-full px-2 py-1 text-sm border border-gray-300 rounded mb-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <textarea
            value={presetDescription}
            onChange={(e) => setPresetDescription(e.target.value)}
            placeholder="Description (optional)"
            rows={2}
            className="w-full px-2 py-1 text-sm border border-gray-300 rounded mb-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <input
            type="text"
            value={presetCategory}
            onChange={(e) => setPresetCategory(e.target.value)}
            placeholder="Category (e.g., Sales, Finance)"
            className="w-full px-2 py-1 text-sm border border-gray-300 rounded mb-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <label className="flex items-center text-sm">
            <input
              type="checkbox"
              checked={isPublic}
              onChange={(e) => setIsPublic(e.target.checked)}
              className="rounded border-gray-300"
            />
            <span className="ml-2 text-gray-700">Make Public</span>
          </label>
          <button
            onClick={savePreset}
            className="w-full px-2 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700"
          >
            Save Preset
          </button>
        </div>
      )}

      {/* Search and Filter */}
      <div className="mb-3 space-y-2">
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="Search presets..."
          className="w-full px-2 py-1 text-xs border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        {categories.length > 0 && (
          <div className="flex gap-1 flex-wrap">
            <button
              onClick={() => setSelectedCategory(null)}
              className={`text-xs px-2 py-1 rounded ${
                selectedCategory === null
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              All
            </button>
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`text-xs px-2 py-1 rounded ${
                  selectedCategory === cat
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Presets List */}
      {filteredPresets.length > 0 ? (
        <div className="space-y-2 max-h-96 overflow-y-auto">
          {filteredPresets.map((preset) => (
            <div
              key={preset.id}
              className="flex items-start justify-between p-2 bg-gray-50 rounded border border-gray-200 hover:bg-gray-100"
            >
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <p className="text-xs font-medium text-gray-900 truncate">{preset.name}</p>
                  {preset.isPublic && (
                    <span className="text-xs bg-green-100 text-green-800 px-1 rounded">Public</span>
                  )}
                </div>
                {preset.description && (
                  <p className="text-xs text-gray-600 truncate">{preset.description}</p>
                )}
                <p className="text-xs text-gray-500">{preset.filters.length} filters</p>
              </div>
              <div className="flex gap-0.5 ml-2 flex-shrink-0">
                <button
                  onClick={() => loadPreset(preset)}
                  className="text-xs px-1.5 py-0.5 bg-blue-600 text-white rounded hover:bg-blue-700"
                  title="Load this preset"
                >
                  Load
                </button>
                <button
                  onClick={() => duplicatePreset(preset)}
                  className="text-xs px-1.5 py-0.5 bg-gray-600 text-white rounded hover:bg-gray-700"
                  title="Duplicate this preset"
                >
                  Copy
                </button>
                <button
                  onClick={() => deletePreset(preset.id)}
                  className="text-xs px-1.5 py-0.5 bg-red-600 text-white rounded hover:bg-red-700"
                  title="Delete this preset"
                >
                  Del
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-xs text-gray-500 text-center py-3">
          {presets.length === 0 ? 'No presets saved yet' : 'No presets match your search'}
        </p>
      )}
    </div>
  );
};
