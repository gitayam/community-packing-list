import { Shield } from 'lucide-react';

export function Footer() {
  return (
    <footer className="hidden md:block border-t border-tactical-border py-5 mt-auto bg-tactical-surface/50">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-center gap-3 text-text-muted">
          <Shield size={14} className="text-accent-cyan/40" />
          <span className="font-tactical text-[10px] uppercase tracking-[0.2em]">
            Community Packing List
          </span>
          <span className="text-accent-cyan/30">•</span>
          <span className="font-tactical text-[10px] uppercase tracking-[0.2em]">
            Tactical Mission Control
          </span>
          <span className="text-accent-cyan/30">•</span>
          <span className="font-tactical text-[10px] uppercase tracking-[0.2em]">
            {new Date().getFullYear()}
          </span>
        </div>
      </div>
    </footer>
  );
}
