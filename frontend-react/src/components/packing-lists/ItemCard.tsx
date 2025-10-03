import { Check, Edit, Trash2, DollarSign, ThumbsUp, ThumbsDown, ChevronDown, ChevronUp } from 'lucide-react';
import { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import type { PackingListItem, Item, PriceWithVotes } from '@/types';

interface ItemCardProps {
  pli: PackingListItem;
  item: Item;
  prices: PriceWithVotes[];
  onTogglePacked: () => void;
  onDelete: () => void;
  onEdit?: () => void;
  onVote: (priceId: number, isUpvote: boolean) => void;
  isPending?: boolean;
}

export function ItemCard({
  pli,
  item,
  prices,
  onTogglePacked,
  onDelete,
  onEdit,
  onVote,
  isPending = false,
}: ItemCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const bestPrice = prices[0];

  const hasDetails = pli.notes || pli.instructions || pli.nsn_lin;

  return (
    <div
      className={`
        relative rounded-lg border-2 transition-all duration-200
        ${pli.packed ? 'bg-gray-50 border-gray-200' : 'bg-white border-gray-200'}
        ${pli.required ? 'border-l-4 border-l-status-required' : 'border-l-4 border-l-blue-400'}
        hover:shadow-md
      `}
    >
      <div className="p-4">
        {/* Header Row */}
        <div className="flex items-start gap-3 mb-3">
          {/* Checkbox - Touch-friendly */}
          <button
            onClick={onTogglePacked}
            disabled={isPending}
            className={`
              flex-shrink-0 w-12 h-12 rounded-lg border-2 flex items-center justify-center transition-all duration-200
              ${pli.packed
                ? 'bg-status-complete border-status-complete text-white scale-105'
                : 'bg-white border-gray-300 hover:border-status-complete hover:scale-105'
              }
              ${isPending ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
            `}
          >
            {pli.packed && <Check size={24} strokeWidth={3} className="animate-checkmark" />}
          </button>

          {/* Item Info */}
          <div className="flex-1 min-w-0">
            <h3
              className={`
                text-lg font-bold mb-1 transition-opacity
                ${pli.packed ? 'text-gray-500 line-through' : 'text-military-navy'}
              `}
            >
              {item.name}
            </h3>

            {/* Badges */}
            <div className="flex flex-wrap gap-1.5 mb-2">
              {pli.required ? (
                <Badge variant="danger" size="sm">REQUIRED</Badge>
              ) : (
                <Badge variant="info" size="sm">Optional</Badge>
              )}
              {pli.quantity > 1 && (
                <Badge variant="default" size="sm">Qty: {pli.quantity}</Badge>
              )}
              {pli.nsn_lin && (
                <Badge variant="military" size="sm" className="font-mono text-xs">
                  {pli.nsn_lin}
                </Badge>
              )}
            </div>

            {/* Quick Notes (always visible if short) */}
            {pli.notes && pli.notes.length < 60 && (
              <p className="text-sm text-gray-600 mb-2">{pli.notes}</p>
            )}
          </div>

          {/* Actions */}
          <div className="flex-shrink-0 flex gap-1">
            {onEdit && (
              <Button
                size="sm"
                variant="secondary"
                onClick={onEdit}
                disabled={isPending}
                className="px-2"
              >
                <Edit size={16} />
              </Button>
            )}
            <Button
              size="sm"
              variant="danger"
              onClick={onDelete}
              disabled={isPending}
              className="px-2"
            >
              <Trash2 size={16} />
            </Button>
          </div>
        </div>

        {/* Price Info */}
        {bestPrice ? (
          <div className="bg-gray-50 rounded-lg p-3 mb-3">
            <div className="flex items-center justify-between mb-2">
              <div>
                <span className="text-lg font-bold text-status-complete">
                  ${parseFloat(bestPrice.price.price).toFixed(2)}
                </span>
                <span className="text-sm text-gray-600 ml-2">
                  @ {bestPrice.price.store.name}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => onVote(bestPrice.price.id, true)}
                  disabled={isPending}
                  className="flex items-center gap-1 text-status-complete hover:opacity-70 disabled:opacity-50"
                >
                  <ThumbsUp size={16} />
                  <span className="text-sm">{bestPrice.upvotes}</span>
                </button>
                <button
                  onClick={() => onVote(bestPrice.price.id, false)}
                  disabled={isPending}
                  className="flex items-center gap-1 text-status-required hover:opacity-70 disabled:opacity-50"
                >
                  <ThumbsDown size={16} />
                  <span className="text-sm">{bestPrice.downvotes}</span>
                </button>
              </div>
            </div>
          </div>
        ) : (
          <div className="mb-3">
            <Button size="sm" variant="secondary" className="w-full">
              <DollarSign size={14} className="mr-1" />
              Add Price
            </Button>
          </div>
        )}

        {/* Expandable Details */}
        {hasDetails && (
          <>
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="flex items-center gap-2 text-sm text-military-navy hover:text-military-olive transition-colors w-full"
            >
              {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
              <span className="font-medium">
                {isExpanded ? 'Hide Details' : 'Show Details'}
              </span>
            </button>

            {isExpanded && (
              <div className="mt-3 pt-3 border-t border-gray-200 space-y-2">
                {pli.notes && pli.notes.length >= 60 && (
                  <div>
                    <p className="text-xs font-semibold text-gray-700 mb-1">Notes:</p>
                    <p className="text-sm text-gray-600">{pli.notes}</p>
                  </div>
                )}
                {pli.instructions && (
                  <div>
                    <p className="text-xs font-semibold text-gray-700 mb-1">Instructions:</p>
                    <p className="text-sm text-gray-600 italic">{pli.instructions}</p>
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
