import { ReactNode } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Activity, Wrench, FileCheck, Package, BarChart3 } from 'lucide-react';

interface LayoutProps {
  children: ReactNode;
  title: string;
}

export default function Layout({ children, title }: LayoutProps) {
  const location = useLocation();

  const navItems = [
    { path: '/', icon: BarChart3, label: 'Dashboard' },
    { path: '/tickets', icon: Wrench, label: 'Tickets' },
    { path: '/warranty', icon: FileCheck, label: 'Warranty' },
    { path: '/parts', icon: Package, label: 'Parts' },
    { path: '/agents', icon: Activity, label: 'Agent Activity' },
  ];

  return (
    <div className="min-h-screen flex">
      <aside className="w-64 bg-dark-surface border-r border-dark-border">
        <div className="p-6">
          <h1 className="text-xl font-bold text-white">Field Service AI</h1>
          <p className="text-sm text-dark-muted mt-1">Agent Platform</p>
        </div>

        <nav className="mt-6">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;

            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-6 py-3 transition-colors ${
                  isActive
                    ? 'bg-blue-600 text-white border-r-4 border-blue-400'
                    : 'text-dark-muted hover:bg-dark-bg hover:text-white'
                }`}
              >
                <Icon size={20} />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>
      </aside>

      <main className="flex-1 overflow-auto">
        <header className="bg-dark-surface border-b border-dark-border px-8 py-6">
          <h2 className="text-2xl font-semibold text-white">{title}</h2>
        </header>

        <div className="p-8">{children}</div>
      </main>
    </div>
  );
}
