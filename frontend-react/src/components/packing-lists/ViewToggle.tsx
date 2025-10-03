import { LayoutGrid, Table } from 'lucide-react';

interface ViewToggleProps {
  view: 'card' | 'table';
  onChange: (view: 'card' | 'table') => void;
}

export function ViewToggle({ view, onChange }: ViewToggleProps) {
  return (
    <div className="inline-flex rounded-lg border border-gray-300 bg-white p-1">
      <button
        onClick={() => onChange('card')}
        className={`
          flex items-center gap-2 px-3 py-1.5 rounded-md text-sm font-medium transition-all
          ${view === 'card'
            ? 'bg-military-navy text-white shadow-sm'
            : 'text-gray-600 hover:text-military-navy'
          }
        `}
      >
        <LayoutGrid size={16} />
        <span className="hidden sm:inline">Cards</span>
      </button>
      <button
        onClick={() => onChange('table')}
        className={`
          flex items-center gap-2 px-3 py-1.5 rounded-md text-sm font-medium transition-all
          ${view === 'table'
            ? 'bg-military-navy text-white shadow-sm'
            : 'text-gray-600 hover:text-military-navy'
          }
        `}
      >
        <Table size={16} />
        <span className="hidden sm:inline">Table</span>
      </button>
    </div>
  );
}
