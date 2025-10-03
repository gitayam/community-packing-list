import { Search, X, Filter, SortAsc } from 'lucide-react';
import { Badge } from '@/components/ui/Badge';
import { useState } from 'react';

export interface Filters {
  search: string;
  sections: string[];
  status: 'all' | 'packed' | 'unpacked';
  required: 'all' | 'required' | 'optional';
  sortBy: 'name' | 'section' | 'required';
}

interface FilterBarProps {
  sections: string[];
  filters: Filters;
  onFilterChange: (filters: Filters) => void;
}

export function FilterBar({ sections, filters, onFilterChange }: FilterBarProps) {
  const [showFilters, setShowFilters] = useState(false);

  const updateFilter = (updates: Partial<Filters>) => {
    onFilterChange({ ...filters, ...updates });
  };

  const clearFilters = () => {
    onFilterChange({
      search: '',
      sections: [],
      status: 'all',
      required: 'all',
      sortBy: 'section',
    });
  };

  const hasActiveFilters =
    filters.search !== '' ||
    filters.sections.length > 0 ||
    filters.status !== 'all' ||
    filters.required !== 'all' ||
    filters.sortBy !== 'section';

  const activeFilterCount =
    (filters.search ? 1 : 0) +
    (filters.sections.length > 0 ? 1 : 0) +
    (filters.status !== 'all' ? 1 : 0) +
    (filters.required !== 'all' ? 1 : 0) +
    (filters.sortBy !== 'section' ? 1 : 0);

  return (
    <div className="space-y-3">
      {/* Search and Filter Toggle */}
      <div className="flex gap-2">
        {/* Search Input */}
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
          <input
            type="text"
            placeholder="Search items..."
            value={filters.search}
            onChange={(e) => updateFilter({ search: e.target.value })}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-military-navy transition-all"
          />
          {filters.search && (
            <button
              onClick={() => updateFilter({ search: '' })}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
            >
              <X size={18} />
            </button>
          )}
        </div>

        {/* Filter Toggle Button */}
        <button
          onClick={() => setShowFilters(!showFilters)}
          className={`
            flex items-center gap-2 px-4 py-2 rounded-lg border transition-all font-medium
            ${showFilters
              ? 'bg-military-navy text-white border-military-navy'
              : 'bg-white text-gray-700 border-gray-300 hover:border-military-navy'
            }
          `}
        >
          <Filter size={18} />
          <span className="hidden sm:inline">Filters</span>
          {activeFilterCount > 0 && (
            <Badge variant="danger" size="sm" className="ml-1">
              {activeFilterCount}
            </Badge>
          )}
        </button>
      </div>

      {/* Expanded Filters */}
      {showFilters && (
        <div className="bg-gray-50 rounded-lg p-4 space-y-4 border border-gray-200">
          {/* Status Filter */}
          <div>
            <label className="block text-sm font-semibold text-military-dark mb-2">
              Status
            </label>
            <div className="flex flex-wrap gap-2">
              {(['all', 'packed', 'unpacked'] as const).map((status) => (
                <button
                  key={status}
                  onClick={() => updateFilter({ status })}
                  className={`
                    px-3 py-1.5 rounded-md text-sm font-medium transition-all border
                    ${filters.status === status
                      ? 'bg-military-navy text-white border-military-navy'
                      : 'bg-white text-gray-700 border-gray-300 hover:border-military-navy'
                    }
                  `}
                >
                  {status === 'all' ? 'All Items' : status === 'packed' ? 'Packed' : 'Unpacked'}
                </button>
              ))}
            </div>
          </div>

          {/* Required Filter */}
          <div>
            <label className="block text-sm font-semibold text-military-dark mb-2">
              Priority
            </label>
            <div className="flex flex-wrap gap-2">
              {(['all', 'required', 'optional'] as const).map((req) => (
                <button
                  key={req}
                  onClick={() => updateFilter({ required: req })}
                  className={`
                    px-3 py-1.5 rounded-md text-sm font-medium transition-all border
                    ${filters.required === req
                      ? 'bg-military-navy text-white border-military-navy'
                      : 'bg-white text-gray-700 border-gray-300 hover:border-military-navy'
                    }
                  `}
                >
                  {req === 'all' ? 'All Items' : req === 'required' ? 'Required Only' : 'Optional Only'}
                </button>
              ))}
            </div>
          </div>

          {/* Section Filter */}
          {sections.length > 0 && (
            <div>
              <label className="block text-sm font-semibold text-military-dark mb-2">
                Sections ({filters.sections.length} selected)
              </label>
              <div className="flex flex-wrap gap-2 max-h-40 overflow-y-auto">
                {sections.map((section) => {
                  const isSelected = filters.sections.includes(section);
                  return (
                    <button
                      key={section}
                      onClick={() => {
                        const newSections = isSelected
                          ? filters.sections.filter(s => s !== section)
                          : [...filters.sections, section];
                        updateFilter({ sections: newSections });
                      }}
                      className={`
                        px-3 py-1.5 rounded-md text-sm font-medium transition-all border
                        ${isSelected
                          ? 'bg-military-olive text-white border-military-olive'
                          : 'bg-white text-gray-700 border-gray-300 hover:border-military-olive'
                        }
                      `}
                    >
                      {section}
                    </button>
                  );
                })}
              </div>
              {filters.sections.length > 0 && (
                <button
                  onClick={() => updateFilter({ sections: [] })}
                  className="text-sm text-military-navy hover:underline mt-2"
                >
                  Clear section filter
                </button>
              )}
            </div>
          )}

          {/* Sort By */}
          <div>
            <label className="block text-sm font-semibold text-military-dark mb-2">
              <SortAsc size={16} className="inline mr-1" />
              Sort By
            </label>
            <select
              value={filters.sortBy}
              onChange={(e) => updateFilter({ sortBy: e.target.value as Filters['sortBy'] })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-military-navy"
            >
              <option value="section">Section</option>
              <option value="name">Name (A-Z)</option>
              <option value="required">Priority (Required First)</option>
            </select>
          </div>

          {/* Clear Filters Button */}
          {hasActiveFilters && (
            <div className="pt-2 border-t border-gray-200">
              <button
                onClick={clearFilters}
                className="w-full px-4 py-2 bg-white border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 font-medium transition-all"
              >
                <X size={16} className="inline mr-2" />
                Clear All Filters
              </button>
            </div>
          )}
        </div>
      )}

      {/* Active Filter Pills */}
      {hasActiveFilters && !showFilters && (
        <div className="flex flex-wrap gap-2 items-center">
          <span className="text-xs font-semibold text-gray-600">Active:</span>
          {filters.search && (
            <Badge variant="default" size="sm">
              Search: "{filters.search}"
              <button
                onClick={() => updateFilter({ search: '' })}
                className="ml-1 hover:text-gray-700"
              >
                <X size={12} />
              </button>
            </Badge>
          )}
          {filters.status !== 'all' && (
            <Badge variant="info" size="sm">
              {filters.status === 'packed' ? 'Packed' : 'Unpacked'}
              <button
                onClick={() => updateFilter({ status: 'all' })}
                className="ml-1 hover:text-gray-700"
              >
                <X size={12} />
              </button>
            </Badge>
          )}
          {filters.required !== 'all' && (
            <Badge variant="danger" size="sm">
              {filters.required === 'required' ? 'Required' : 'Optional'}
              <button
                onClick={() => updateFilter({ required: 'all' })}
                className="ml-1 hover:text-gray-700"
              >
                <X size={12} />
              </button>
            </Badge>
          )}
          {filters.sections.length > 0 && (
            <Badge variant="military" size="sm">
              {filters.sections.length} section{filters.sections.length > 1 ? 's' : ''}
              <button
                onClick={() => updateFilter({ sections: [] })}
                className="ml-1 hover:text-gray-700"
              >
                <X size={12} />
              </button>
            </Badge>
          )}
          <button
            onClick={clearFilters}
            className="text-xs text-military-navy hover:underline font-medium"
          >
            Clear all
          </button>
        </div>
      )}
    </div>
  );
}
