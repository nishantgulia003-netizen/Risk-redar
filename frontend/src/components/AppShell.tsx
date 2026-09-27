import React, { useState } from "react";
import {
  Bot,
  Building2,
  LayoutDashboard,
  MapPinned,
  Menu,
  Radar,
  Route,
  Siren,
  X,
} from "lucide-react";
import { NavLink, Outlet } from "react-router-dom";

export interface NavItem {
  to: string;
  label: string;
  icon: React.ComponentType<{ size?: number; className?: string }>;
  description?: string;
}

const navItems: NavItem[] = [
  { to: "/dashboard", label: "Overview", icon: LayoutDashboard },
  { to: "/risk-zones", label: "Risk Zones", icon: MapPinned },
  { to: "/safe-evacuation-route", label: "Evacuation", icon: Route },
  { to: "/shelters", label: "Shelters", icon: Building2 },
  { to: "/field-incident-report", label: "Reports", icon: Siren },
  { to: "/ai-decision-assistant", label: "AI Assistant", icon: Bot },
];

export function AppShell() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="min-h-screen bg-background text-white selection:bg-primary-red selection:text-white">
      {/* Top Liquid Glass Command Bar */}
      <header className="fixed inset-x-0 top-0 z-40 border-b border-white/10 bg-[#0E0E0E]/80 backdrop-blur-glass shadow-glass">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6">
          {/* Brand Identity */}
          <div className="flex items-center gap-3">
            <div className="relative flex h-10 w-10 items-center justify-center rounded-xl bg-primary-red/15 border border-primary-red/40 text-bright-red shadow-radar">
              <Radar size={22} className="text-bright-red" />
              <span className="absolute -top-0.5 -right-0.5 flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-bright-red opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-primary-red"></span>
              </span>
            </div>

            <div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold tracking-tight text-white text-base">
                  RiskRadar
                </span>
                <span className="rounded bg-white/5 px-1.5 py-0.5 text-[9px] font-mono font-bold uppercase tracking-wider text-muted-text border border-white/15">
                  Command
                </span>
              </div>
              <div className="text-[10px] uppercase tracking-wider font-semibold text-muted-text">
                Emergency Intelligence Command
              </div>
            </div>
          </div>

          {/* Desktop Navigation Links */}
          <nav
            className="hidden lg:flex items-center gap-1.5 rounded-full border border-white/10 bg-white/[0.035] p-1 backdrop-blur-md"
            aria-label="Main Navigation"
          >
            {navItems.map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) =>
                  `flex items-center gap-2 rounded-full px-3.5 py-1.5 text-xs font-semibold transition-all duration-200 ${
                    isActive
                      ? "glass-active-red text-white shadow-radar font-bold"
                      : "text-muted-text hover:bg-white/5 hover:text-white"
                  }`
                }
              >
                <Icon size={15} />
                <span>{label}</span>
              </NavLink>
            ))}
          </nav>

          {/* Right Header Badges & Actions */}
          <div className="flex items-center gap-3">
            <div className="hidden sm:flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.04] px-3 py-1.5 text-xs text-muted-text">
              <span className="font-mono text-[11px] font-semibold text-white">Command Center</span>
            </div>

            {/* Mobile menu trigger */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="lg:hidden focus-ring rounded-lg p-2 text-muted-text hover:bg-white/10 hover:text-white"
              aria-label="Toggle navigation menu"
              aria-expanded={mobileMenuOpen}
            >
              {mobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
            </button>
          </div>
        </div>

        {/* Mobile Dropdown Menu */}
        {mobileMenuOpen && (
          <div className="lg:hidden border-t border-white/10 bg-[#0E0E0E]/95 backdrop-blur-2xl px-4 py-3 space-y-1">
            {navItems.map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                onClick={() => setMobileMenuOpen(false)}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-4 py-2.5 text-sm font-semibold transition ${
                    isActive
                      ? "glass-active-red text-white font-bold"
                      : "text-muted-text hover:bg-white/5 hover:text-white"
                  }`
                }
              >
                <Icon size={18} />
                <span>{label}</span>
              </NavLink>
            ))}
          </div>
        )}
      </header>

      {/* Main Command Viewport */}
      <main className="mx-auto min-h-screen max-w-7xl px-4 pb-28 pt-24 sm:px-6">
        <Outlet />
      </main>

      {/* Floating Bottom Dock for Tablet / Mobile */}
      <nav
        className="fixed inset-x-4 bottom-3 z-40 mx-auto flex max-w-lg items-center justify-around rounded-full border border-white/15 bg-[#141416]/90 p-1.5 shadow-[0_16px_40px_rgba(0,0,0,0.7)] backdrop-blur-glass lg:hidden"
        aria-label="Mobile Navigation"
      >
        {navItems.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex min-w-[50px] flex-col items-center gap-1 rounded-full px-2.5 py-1.5 text-[10px] font-semibold transition ${
                isActive
                  ? "bg-primary-red/20 text-white font-bold border border-primary-red/40"
                  : "text-muted-text hover:text-white"
              }`
            }
          >
            <Icon size={17} />
            <span className="truncate max-w-[54px]">{label}</span>
          </NavLink>
        ))}
      </nav>
    </div>
  );
}
