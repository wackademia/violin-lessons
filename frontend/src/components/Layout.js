import React, { useState } from 'react';
import { Outlet, NavLink, useLocation } from 'react-router-dom';
import { Home, BookOpen, Music, Activity, FileText, Wrench, Calendar, Bookmark, Menu, X } from 'lucide-react';

const navItems = [
  { path: '/', label: 'Home', icon: Home },
  { path: '/lessons', label: 'Lessons', icon: BookOpen },
  { path: '/theory', label: 'Theory', icon: Music },
  { path: '/tuner', label: 'Tuner', icon: Activity },
  { path: '/sheet-music', label: 'Sheet Music', icon: FileText },
  { path: '/care', label: 'Care', icon: Wrench },
  { path: '/practice', label: 'Practice', icon: Calendar },
  { path: '/bookmarks', label: 'Bookmarks', icon: Bookmark },
];

export default function Layout() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const location = useLocation();

  return (
    <div className="flex h-screen overflow-hidden bg-background" data-testid="app-layout">
      {/* Desktop Sidebar */}
      <aside className="hidden lg:flex flex-col w-64 bg-background-secondary border-r border-stone-800 shrink-0" data-testid="desktop-sidebar">
        <div className="p-6 border-b border-stone-800">
          <NavLink to="/" className="flex items-center gap-3" data-testid="logo-link">
            <div className="w-10 h-10 rounded-xl bg-primary flex items-center justify-center">
              <Music size={20} className="text-white" />
            </div>
            <div>
              <h1 className="font-heading text-xl font-bold tracking-tight text-stone-100">Virtuoso</h1>
              <p className="text-[11px] text-stone-500 font-body tracking-widest uppercase">Violin Learning</p>
            </div>
          </NavLink>
        </div>
        <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === '/'}
              data-testid={`nav-${item.label.toLowerCase().replace(' ', '-')}`}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-body font-medium transition-all duration-200 ${
                  isActive
                    ? 'bg-primary/10 text-primary border border-primary/20'
                    : 'text-stone-400 hover:text-stone-200 hover:bg-stone-800/50'
                }`
              }
            >
              <item.icon size={18} strokeWidth={1.5} />
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="p-4 border-t border-stone-800">
          <p className="text-[10px] text-stone-600 text-center font-body">100% Free &middot; No Ads &middot; Open Source</p>
        </div>
      </aside>

      {/* Mobile Header + Overlay */}
      <div className="flex flex-col flex-1 overflow-hidden">
        <header className="lg:hidden flex items-center justify-between px-4 py-3 bg-background-secondary border-b border-stone-800 shrink-0" data-testid="mobile-header">
          <NavLink to="/" className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
              <Music size={16} className="text-white" />
            </div>
            <span className="font-heading text-lg font-bold text-stone-100">Virtuoso</span>
          </NavLink>
          <button
            onClick={() => setMobileOpen(!mobileOpen)}
            className="p-2 text-stone-400 hover:text-stone-200 transition-colors"
            data-testid="mobile-menu-toggle"
          >
            {mobileOpen ? <X size={22} /> : <Menu size={22} />}
          </button>
        </header>

        {mobileOpen && (
          <div className="lg:hidden fixed inset-0 z-50 bg-black/60 backdrop-blur-sm" onClick={() => setMobileOpen(false)}>
            <div className="absolute right-0 top-0 h-full w-72 bg-background-secondary border-l border-stone-800 p-4 pt-16" onClick={(e) => e.stopPropagation()}>
              <button onClick={() => setMobileOpen(false)} className="absolute top-4 right-4 text-stone-400" data-testid="mobile-menu-close">
                <X size={22} />
              </button>
              <nav className="space-y-1">
                {navItems.map((item) => (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    end={item.path === '/'}
                    onClick={() => setMobileOpen(false)}
                    data-testid={`mobile-nav-${item.label.toLowerCase().replace(' ', '-')}`}
                    className={({ isActive }) =>
                      `flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-body font-medium transition-all ${
                        isActive
                          ? 'bg-primary/10 text-primary'
                          : 'text-stone-400 hover:text-stone-200 hover:bg-stone-800/50'
                      }`
                    }
                  >
                    <item.icon size={18} strokeWidth={1.5} />
                    {item.label}
                  </NavLink>
                ))}
              </nav>
            </div>
          </div>
        )}

        {/* Main Content */}
        <main className="flex-1 overflow-y-auto" data-testid="main-content">
          <div className="max-w-6xl mx-auto px-4 md:px-8 py-6 md:py-10">
            <Outlet />
          </div>
        </main>

        {/* Mobile Bottom Nav */}
        <nav className="lg:hidden flex items-center justify-around py-2 bg-background-secondary border-t border-stone-800 shrink-0" data-testid="mobile-bottom-nav">
          {navItems.slice(0, 5).map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === '/'}
              data-testid={`bottom-nav-${item.label.toLowerCase().replace(' ', '-')}`}
              className={({ isActive }) =>
                `flex flex-col items-center gap-0.5 px-2 py-1 text-[10px] font-body transition-colors ${
                  isActive ? 'text-primary' : 'text-stone-500'
                }`
              }
            >
              <item.icon size={18} strokeWidth={1.5} />
              {item.label}
            </NavLink>
          ))}
        </nav>
      </div>
    </div>
  );
}
