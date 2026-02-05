import { useState, useEffect, useMemo } from 'react';
import { Edit, Trash2, Plus, Check, ThumbsUp, ThumbsDown, DollarSign } from 'lucide-react';
import toast from 'react-hot-toast';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Table, TableHead, TableBody, TableRow, TableHeader, TableCell } from '@/components/ui/Table';
import { ItemCard } from '@/components/packing-lists/ItemCard';
import { ViewToggle } from '@/components/packing-lists/ViewToggle';
import { ProgressStats } from '@/components/packing-lists/ProgressStats';
import { FilterBar, type Filters } from '@/components/packing-lists/FilterBar';
import { useTogglePacked, useDeleteItem } from '@/hooks/usePackingListMutations';
import { useVotePrice } from '@/hooks/usePrices';
import type { PackingListDetailResponse } from '@/types';

interface PackingListDetailProps {
  data: PackingListDetailResponse;
}

export function PackingListDetail({ data }: PackingListDetailProps) {
  const { packing_list, items_with_prices } = data;
  const togglePackedMutation = useTogglePacked();
  const deleteItemMutation = useDeleteItem();
  const voteMutation = useVotePrice();

  const [view, setView] = useState<'card' | 'table'>(() => {
    // Restore view preference from localStorage
    const saved = localStorage.getItem('packinglist-view');
    return (saved as 'card' | 'table') || 'card';
  });

  const [filters, setFilters] = useState<Filters>(() => {
    // Restore filters from localStorage
    const saved = localStorage.getItem('packinglist-filters');
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch {
        return {
          search: '',
          sections: [],
          status: 'all' as const,
          required: 'all' as const,
          sortBy: 'section' as const,
        };
      }
    }
    return {
      search: '',
      sections: [],
      status: 'all' as const,
      required: 'all' as const,
      sortBy: 'section' as const,
    };
  });

  // Save view preference
  useEffect(() => {
    localStorage.setItem('packinglist-view', view);
  }, [view]);

  // Save filters
  useEffect(() => {
    localStorage.setItem('packinglist-filters', JSON.stringify(filters));
  }, [filters]);

  // Get all unique sections
  const allSections = useMemo(() => {
    const sections = new Set<string>();
    items_with_prices.forEach(({ pli }) => {
      sections.add(pli.section || 'Uncategorized');
    });
    return Array.from(sections).sort();
  }, [items_with_prices]);

  // Apply filters and sorting
  const filteredAndSortedItems = useMemo(() => {
    let filtered = [...items_with_prices];

    // Apply search filter
    if (filters.search) {
      const searchLower = filters.search.toLowerCase();
      filtered = filtered.filter(({ item, pli }) =>
        item.name.toLowerCase().includes(searchLower) ||
        pli.notes?.toLowerCase().includes(searchLower) ||
        pli.instructions?.toLowerCase().includes(searchLower) ||
        pli.nsn_lin?.toLowerCase().includes(searchLower)
      );
    }

    // Apply status filter
    if (filters.status !== 'all') {
      filtered = filtered.filter(({ pli }) =>
        filters.status === 'packed' ? pli.packed : !pli.packed
      );
    }

    // Apply required filter
    if (filters.required !== 'all') {
      filtered = filtered.filter(({ pli }) =>
        filters.required === 'required' ? pli.required : !pli.required
      );
    }

    // Apply section filter
    if (filters.sections.length > 0) {
      filtered = filtered.filter(({ pli }) =>
        filters.sections.includes(pli.section || 'Uncategorized')
      );
    }

    // Apply sorting
    filtered.sort((a, b) => {
      if (filters.sortBy === 'name') {
        return a.item.name.localeCompare(b.item.name);
      } else if (filters.sortBy === 'required') {
        // Required first
        if (a.pli.required && !b.pli.required) return -1;
        if (!a.pli.required && b.pli.required) return 1;
        return a.item.name.localeCompare(b.item.name);
      } else {
        // Sort by section (default)
        const sectionCompare = (a.pli.section || 'Uncategorized').localeCompare(
          b.pli.section || 'Uncategorized'
        );
        if (sectionCompare !== 0) return sectionCompare;
        return a.item.name.localeCompare(b.item.name);
      }
    });

    return filtered;
  }, [items_with_prices, filters]);

  // Group filtered items by section
  const itemsBySection = useMemo(() => {
    return filteredAndSortedItems.reduce((acc, itemData) => {
      const section = itemData.pli.section || 'Uncategorized';
      if (!acc[section]) {
        acc[section] = [];
      }
      acc[section].push(itemData);
      return acc;
    }, {} as Record<string, typeof items_with_prices>);
  }, [filteredAndSortedItems]);

  const handleTogglePacked = async (itemId: number) => {
    try {
      await togglePackedMutation.mutateAsync({
        listId: packing_list.id,
        itemId,
      });
    } catch (error) {
      toast.error('Failed to update item status');
      console.error('Failed to toggle packed status:', error);
    }
  };

  const handleDeleteItem = async (itemId: number, itemName: string) => {
    if (confirm(`Are you sure you want to delete "${itemName}"?`)) {
      try {
        await deleteItemMutation.mutateAsync({
          listId: packing_list.id,
          itemId,
        });
        toast.success(`${itemName} deleted successfully`);
      } catch (error) {
        toast.error('Failed to delete item');
        console.error('Failed to delete item:', error);
      }
    }
  };

  const handleVote = async (priceId: number, isUpvote: boolean) => {
    try {
      await voteMutation.mutateAsync({ priceId, isUpvote });
    } catch (error) {
      toast.error('Failed to vote on price');
      console.error('Failed to vote:', error);
    }
  };

  // Calculate progress
  const totalItems = items_with_prices.length;
  const packedItems = items_with_prices.filter(i => i.pli.packed).length;
  const requiredItems = items_with_prices.filter(i => i.pli.required).length;
  const packedRequired = items_with_prices.filter(i => i.pli.required && i.pli.packed).length;

  const filteredSections = Object.entries(itemsBySection);

  return (
    <div>
      {/* Header Card */}
      <Card className="mb-6">
        <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4 mb-4">
          <div className="flex-1">
            <h1 className="text-2xl sm:text-3xl font-bold text-military-dark mb-2">{packing_list.name}</h1>
            {packing_list.description && (
              <p className="text-gray-600 text-sm sm:text-base">{packing_list.description}</p>
            )}
          </div>
          <div className="flex gap-2 flex-wrap sm:flex-nowrap">
            <Button variant="secondary" className="flex-1 sm:flex-none">
              <Edit className="inline mr-2" size={16} />
              <span className="hidden sm:inline">Edit List</span>
              <span className="sm:hidden">Edit</span>
            </Button>
            <Button variant="success" className="flex-1 sm:flex-none">
              <Plus className="inline mr-2" size={16} />
              <span className="hidden sm:inline">Add Item</span>
              <span className="sm:hidden">Add</span>
            </Button>
          </div>
        </div>

        {/* Badges */}
        <div className="flex flex-wrap gap-2">
          {packing_list.school && (
            <Badge variant="info">{packing_list.school.name}</Badge>
          )}
          {packing_list.base && (
            <Badge variant="info">{packing_list.base.name}</Badge>
          )}
          {packing_list.type && (
            <Badge variant="default">{packing_list.type}</Badge>
          )}
        </div>
      </Card>

      {/* Progress Stats */}
      <div className="mb-6">
        <ProgressStats
          totalItems={totalItems}
          packedItems={packedItems}
          requiredItems={requiredItems}
          packedRequired={packedRequired}
        />
      </div>

      {/* FilterBar and View Toggle */}
      <div className="space-y-3 mb-6">
        <div className="flex items-start gap-3">
          <div className="flex-1">
            <FilterBar
              sections={allSections}
              filters={filters}
              onFilterChange={setFilters}
            />
          </div>
          <ViewToggle view={view} onChange={setView} />
        </div>
      </div>

      {filteredSections.length === 0 ? (
        <Card>
          <p className="text-gray-600 text-center py-8">
            No items found. Add items to your packing list to get started!
          </p>
        </Card>
      ) : (
        filteredSections.map(([section, items]) => {
          const sectionPacked = items.filter(i => i.pli.packed).length;
          const sectionTotal = items.length;
          const sectionProgress = Math.round((sectionPacked / sectionTotal) * 100);

          return (
            <Card key={section} className="mb-6">
              {/* Section Header with Progress */}
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-military-navy">{section}</h2>
                <div className="flex items-center gap-2">
                  <span className="text-sm text-gray-600">
                    {sectionPacked} / {sectionTotal}
                  </span>
                  <Badge
                    variant={sectionProgress === 100 ? 'success' : sectionProgress >= 50 ? 'warning' : 'default'}
                    size="sm"
                  >
                    {sectionProgress}%
                  </Badge>
                </div>
              </div>

              {/* Card View */}
              {view === 'card' ? (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                  {items.map(({ pli, item, prices_with_votes }) => (
                    <ItemCard
                      key={pli.id}
                      pli={pli}
                      item={item}
                      prices={prices_with_votes}
                      onTogglePacked={() => handleTogglePacked(pli.id)}
                      onDelete={() => handleDeleteItem(pli.id, item.name)}
                      onVote={handleVote}
                      isPending={togglePackedMutation.isPending || deleteItemMutation.isPending || voteMutation.isPending}
                    />
                  ))}
                </div>
              ) : (
                /* Table View */
                <div className="overflow-x-auto">
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableHeader>Packed</TableHeader>
                        <TableHeader>Item</TableHeader>
                        <TableHeader>Qty</TableHeader>
                        <TableHeader className="hidden md:table-cell">NSN/LIN</TableHeader>
                        <TableHeader>Best Price</TableHeader>
                        <TableHeader>Actions</TableHeader>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {items.map(({ pli, item, prices_with_votes }) => {
                        const bestPrice = prices_with_votes[0];

                        return (
                          <TableRow key={pli.id}>
                            <TableCell>
                              <button
                                onClick={() => handleTogglePacked(pli.id)}
                                className={`w-8 h-8 rounded flex items-center justify-center ${
                                  pli.packed
                                    ? 'bg-status-complete text-white'
                                    : 'bg-gray-200 text-gray-400'
                                }`}
                                disabled={togglePackedMutation.isPending}
                              >
                                {pli.packed && <Check size={16} />}
                              </button>
                            </TableCell>

                            <TableCell>
                              <div>
                                <div className="font-medium">
                                  {item.name}
                                  {pli.required && (
                                    <span className="ml-2 text-xs text-status-required">Required</span>
                                  )}
                                </div>
                                {pli.notes && (
                                  <div className="text-xs text-gray-500 mt-1">{pli.notes}</div>
                                )}
                                {pli.instructions && (
                                  <div className="text-xs text-gray-600 mt-1 italic">{pli.instructions}</div>
                                )}
                              </div>
                            </TableCell>

                            <TableCell>{pli.quantity}</TableCell>

                            <TableCell className="hidden md:table-cell">
                              {pli.nsn_lin && (
                                <span className="text-xs font-mono bg-gray-100 px-2 py-1 rounded">
                                  {pli.nsn_lin}
                                </span>
                              )}
                            </TableCell>

                            <TableCell>
                              {bestPrice ? (
                                <div>
                                  <div className="flex items-center gap-2">
                                    <span className="font-medium text-status-complete">
                                      ${parseFloat(bestPrice.price.price).toFixed(2)}
                                    </span>
                                    <span className="text-xs text-gray-500 hidden sm:inline">
                                      @ {bestPrice.price.store.name}
                                    </span>
                                  </div>
                                  <div className="flex items-center gap-1 mt-1">
                                    <button
                                      onClick={() => handleVote(bestPrice.price.id, true)}
                                      className="text-status-complete hover:opacity-70"
                                      disabled={voteMutation.isPending}
                                    >
                                      <ThumbsUp size={14} />
                                    </button>
                                    <span className="text-xs">{bestPrice.upvotes}</span>
                                    <button
                                      onClick={() => handleVote(bestPrice.price.id, false)}
                                      className="text-status-required hover:opacity-70 ml-2"
                                      disabled={voteMutation.isPending}
                                    >
                                      <ThumbsDown size={14} />
                                    </button>
                                    <span className="text-xs">{bestPrice.downvotes}</span>
                                  </div>
                                </div>
                              ) : (
                                <Button size="sm" variant="secondary">
                                  <DollarSign size={14} className="inline mr-1" />
                                  <span className="hidden sm:inline">Add Price</span>
                                </Button>
                              )}
                            </TableCell>

                            <TableCell>
                              <div className="flex gap-2">
                                <Button size="sm" variant="secondary">
                                  <Edit size={14} />
                                </Button>
                                <Button
                                  size="sm"
                                  variant="danger"
                                  onClick={() => handleDeleteItem(pli.id, item.name)}
                                  disabled={deleteItemMutation.isPending}
                                >
                                  <Trash2 size={14} />
                                </Button>
                              </div>
                            </TableCell>
                          </TableRow>
                        );
                      })}
                    </TableBody>
                  </Table>
                </div>
              )}
            </Card>
          );
        })
      )}
    </div>
  );
}
