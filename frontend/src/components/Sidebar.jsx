import { NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard, CheckSquare, Calendar, MessageSquare,
  Settings, Leaf
} from 'lucide-react';

const navItems = [
  { to: '/',           label: 'Overview',     icon: LayoutDashboard },
  { to: '/tasks',      label: 'My Tasks',     icon: CheckSquare },
  { to: '/my-day',     label: 'My Day',       icon: Calendar },
  { to: '/assistant',  label: 'AI Assistant', icon: MessageSquare },
  { to: '/settings',   label: 'Settings',     icon: Settings },
];

export default function Sidebar({ onClose, aiStatus }) {
  const location = useLocation();

  return (
    <aside className="app-sidebar" id="sidebar" aria-label="Main navigation">
      {/* Brand */}
      <div className="sidebar-brand">
        <div className="sidebar-brand-icon" aria-hidden="true">
          <Leaf size={18} />
        </div>
        <div>
          <div className="sidebar-brand-name">PlanWise AI</div>
          <div className="sidebar-brand-sub">Your day, thoughtfully planned.</div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="sidebar-nav" aria-label="App navigation">
        <div className="sidebar-section-label">Navigation</div>
        {navItems.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
            onClick={onClose}
            aria-current={location.pathname === to ? 'page' : undefined}
          >
            <Icon size={18} className="nav-link-icon" aria-hidden="true" />
            <span>{label}</span>
            {to === '/assistant' && (
              <span
                style={{
                  marginLeft: 'auto',
                  width: 7, height: 7,
                  borderRadius: '50%',
                  background: aiStatus?.available ? 'var(--clr-success)' : 'var(--clr-ink-4)',
                  flexShrink: 0,
                }}
                title={aiStatus?.available ? `AI: ${aiStatus.provider}` : 'AI: Rule-based mode'}
              />
            )}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}

