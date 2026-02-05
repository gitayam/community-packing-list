import { Check, Edit, Trash2, DollarSign, ThumbsUp, ThumbsDown, ChevronDown, ChevronUp } from 'lucide-react';
import { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { SwipeableCard } from '@/components/ui/SwipeableCard';
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
    <SwipeableCard
      onSwipeRight={onTogglePacked}
      onSwipeLeft={onDelete}
      rightLabel={pli.packed ? 'Unpack' : 'Pack'}
      disabled={isPending}
    >
      <div
        className={`
          relative rounded-xl border transition-all duration-200 p-5
          ${pli.packed
            ? 'bg-dark-elevated/50 border-dark-border'
            : 'bg-dark-surface border-dark-border hover:border-accent-blue/50'
          }
          ${pli.required && !pli.packed ? 'border-l-4 border-l-status-danger' : ''}
          ${!pli.required && !pli.packed ? 'border-l-4 border-l-accent-blue' : ''}
        `}
      >
        {/* Header Row */}
        <div className="flex items-start gap-4 mb-4">
          {/* Checkbox */}
          <button
            onClick={onTogglePacked}
            disabled={isPending}
            className={`
              flex-shrink-0 w-12 h-12 rounded-xl border-2 flex items-center justify-center
              transition-all duration-200 tap-active
              ${pli.packed
                ? 'bg-status-success border-status-success glow-success'
                : 'bg-dark-elevated border-dark-border hover:border-accent-blue'
              }
              ${isPending ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
            `}
          >
            {pli.packed && <Check size={24} strokeWidth={3} className="text-white animate-checkmark" />}
          </button>

          {/* Item Info */}
          <div className="flex-1 min-w-0">
            <h3
              className={`
                text-lg font-bold mb-2 transition-opacity
                ${pli.packed ? 'text-text-muted line-through' : 'text-text-primary'}
              `}
            >
              {item.name}
            </h3>

            {/* Badges */}
            <div className="flex flex-wrap gap-2">
              {pli.required ? (
                <Badge variant="danger" size="sm">REQUIRED</Badge>
              ) : (
                <Badge variant="info" size="sm">Optional</Badge>
              )}
              {pli.quantity > 1 && (
                <Badge variant="default" size="sm">Qty: {pli.quantity}</Badge>
              )}
              {pli.nsn_lin && (
                <Badge variant="default" size="sm" className="font-mono text-xs">
                  {pli.nsn_lin}
                </Badge>
              )}
            </div>
          </div>

          {/* Actions - Desktop only */}
          <div className="hidden md:flex flex-shrink-0 gap-2">
            {onEdit && (
              <Button
                size="sm"
                variant="secondary"
                onClick={onEdit}
                disabled={isPending}
                className="px-3"
              >
                <Edit size={16} />
              </Button>
            )}
            <Button
              size="sm"
              variant="danger"
              onClick={onDelete}
              disabled={isPending}
              className="px-3"
            >
              <Trash2 size={16} />
            </Button>
          </div>
        </div>

        {/* Quick Notes */}
        {pli.notes && pli.notes.length < 60 && (
          <p className="text-sm text-text-secondary mb-4">{pli.notes}</p>
        )}

        {/* Price Info */}
        {bestPrice ? (
          <div className="glass rounded-xl p-4 mb-4">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-xl font-bold text-status-success">
                  ${parseFloat(bestPrice.price.price).toFixed(2)}
                </span>
                <span className="text-sm text-text-secondary ml-2">
                  @ {bestPrice.price.store.name}
                </span>
              </div>
              <div className="flex items-center gap-3">
                <button
                  onClick={() => onVote(bestPrice.price.id, true)}
                  disabled={isPending}
                  className="flex items-center gap-1 text-status-success hover:glow-success rounded-lg px-2 py-1 transition-all tap-active disabled:opacity-50"
                >
                  <ThumbsUp size={18} />
                  <span className="text-sm font-medium">{bestPrice.upvotes}</span>
                </button>
                <button
                  onClick={() => onVote(bestPrice.price.id, false)}
                  disabled={isPending}
                  className="flex items-center gap-1 text-status-danger hover:glow-danger rounded-lg px-2 py-1 transition-all tap-active disabled:opacity-50"
                >
                  <ThumbsDown size={18} />
                  <span className="text-sm font-medium">{bestPrice.downvotes}</span>
                </button>
              </div>
            </div>
          </div>
        ) : (
          <Button size="sm" variant="secondary" className="w-full mb-4 glass">
            <DollarSign size={16} className="mr-2" />
            Add Price
          </Button>
        )}

        {/* Expandable Details */}
        {hasDetails && (
          <>
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="flex items-center gap-2 text-sm text-accent-blue hover:text-accent-glow transition-colors w-full tap-active"
            >
              {isExpanded ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
              <span className="font-medium">
                {isExpanded ? 'Hide Details' : 'Show Details'}
              </span>
            </button>

            {isExpanded && (
              <div className="mt-4 pt-4 border-t border-dark-border space-y-3 animate-slideDown">
                {pli.notes && pli.notes.length >= 60 && (
                  <div>
                    <p className="text-xs font-semibold text-text-secondary mb-1">Notes:</p>
                    <p className="text-sm text-text-primary">{pli.notes}</p>
                  </div>
                )}
                {pli.instructions && (
                  <div>
                    <p className="text-xs font-semibold text-text-secondary mb-1">Instructions:</p>
                    <p className="text-sm text-text-primary italic">{pli.instructions}</p>
                  </div>
                )}

                {/* Mobile Actions */}
                <div className="flex gap-2 pt-2 md:hidden">
                  {onEdit && (
                    <Button size="sm" variant="secondary" onClick={onEdit} disabled={isPending} className="flex-1">
                      <Edit size={16} className="mr-2" />
                      Edit
                    </Button>
                  )}
                  <Button size="sm" variant="danger" onClick={onDelete} disabled={isPending} className="flex-1">
                    <Trash2 size={16} className="mr-2" />
                    Delete
                  </Button>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </SwipeableCard>
  );
}
