import { Outlet } from 'react-router-dom';
import { Header } from './Header';
import { Footer } from './Footer';
import { BottomNav } from './BottomNav';

export function Layout() {
  return (
    <div className="flex flex-col min-h-screen bg-tactical-bg">
      <Header />
      <main className="flex-1 container mx-auto px-4 py-6 pb-24 md:pb-6">
        <Outlet />
      </main>
      <Footer />
      <BottomNav />
    </div>
  );
}
