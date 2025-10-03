import { useState } from 'react';
import { Edit, Trash2, Plus, Check, ThumbsUp, ThumbsDown, DollarSign } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Table, TableHead, TableBody, TableRow, TableHeader, TableCell } from '@/components/ui/Table';
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

  const [searchTerm, setSearchTerm] = useState('');

  // Group items by section
  const itemsBySection = items_with_prices.reduce((acc, itemData) => {
    const section = itemData.pli.section || 'Uncategorized';
    if (!acc[section]) {
      acc[section] = [];
    }
    acc[section].push(itemData);
    return acc;
  }, {} as Record<string, typeof items_with_prices>);

  const handleTogglePacked = async (itemId: number) => {
    try {
      await togglePackedMutation.mutateAsync({
        listId: packing_list.id,
        itemId,
      });
    } catch (error) {
      console.error('Failed to toggle packed status:', error);
    }
  };

  const handleDeleteItem = async (itemId: number) => {
    if (confirm('Are you sure you want to delete this item?')) {
      try {
        await deleteItemMutation.mutateAsync({
          listId: packing_list.id,
          itemId,
        });
      } catch (error) {
        console.error('Failed to delete item:', error);
      }
    }
  };

  const handleVote = async (priceId: number, isUpvote: boolean) => {
    try {
      await voteMutation.mutateAsync({ priceId, isUpvote });
    } catch (error) {
      console.error('Failed to vote:', error);
    }
  };

  const filteredSections = Object.entries(itemsBySection).filter(([_, items]) =>
    items.some(({ item }) =>
      item.name.toLowerCase().includes(searchTerm.toLowerCase())
    )
  );

  return (
    <div>
      <Card className="mb-6">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold text-military-dark mb-2">{packing_list.name}</h1>
            {packing_list.description && (
              <p className="text-gray-600">{packing_list.description}</p>
            )}
          </div>
          <div className="flex gap-2">
            <Button variant="secondary">
              <Edit className="inline mr-2" size={16} />
              Edit List
            </Button>
            <Button variant="success">
              <Plus className="inline mr-2" size={16} />
              Add Item
            </Button>
          </div>
        </div>

        {packing_list.school && (
          <span className="school-tag">{packing_list.school.name}</span>
        )}
      </Card>

      <div className="mb-4">
        <input
          type="text"
          placeholder="Search items..."
          className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-military-navy"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      {filteredSections.length === 0 ? (
        <Card>
          <p className="text-gray-600 text-center py-8">
            No items found. Add items to your packing list to get started!
          </p>
        </Card>
      ) : (
        filteredSections.map(([section, items]) => (
          <Card key={section} className="mb-6">
            <h2 className="text-xl font-semibold text-military-navy mb-4">{section}</h2>

            <Table>
              <TableHead>
                <TableRow>
                  <TableHeader>Packed</TableHeader>
                  <TableHeader>Item</TableHeader>
                  <TableHeader>Qty</TableHeader>
                  <TableHeader>NSN/LIN</TableHeader>
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

                      <TableCell>
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
                              <span className="text-xs text-gray-500">
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
                            Add Price
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
                            onClick={() => handleDeleteItem(pli.id)}
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
          </Card>
        ))
      )}
    </div>
  );
}
