import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  MapPin,
  Upload,
  FolderKanban,
  Bot,
  FileBarChart,
  Users,
  LogOut,
} from 'lucide-react';
import { UserRole } from '../types';

interface SidebarProps {
  userRole?: UserRole;
  userName?: string;
  userRoleLabel?: string;
}

export const Sidebar: React.FC<SidebarProps> = ({
  userRole = 'safety_analyst',
  userName = 'Asha Reddy',
  userRoleLabel = 'Road Safety Analyst',
}) => {
  const navigate = useNavigate();

  const handleSignOut = () => {
    localStorage.removeItem('rah_token');
    localStorage.removeItem('rah_user');
    navigate('/login');
  };

  const navItems = [
    { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/map', label: 'Hotspot Map', icon: MapPin },
    { to: '/import', label: 'Data Import', icon: Upload },
    { to: '/cases', label: 'Hotspot Cases', icon: FolderKanban },
    { to: '/assistant', label: 'AI Assistant', icon: Bot },
    { to: '/reports', label: 'Reports', icon: FileBarChart },
  ];

  const adminNav = [
    { to: '/users', label: 'User Management', icon: Users },
  ];

  return (
    <aside className="w-[224px] bg-asphalt text-[#BFC4C9] flex flex-col h-screen sticky top-0 shrink-0 z-30 lane-divider select-none">
      {/* Brand Header */}
      <div
        onClick={() => navigate('/')}
        className="px-4 py-5 flex items-center gap-3 text-white font-semibold cursor-pointer border-b border-[#2C3136]"
      >
        <div className="w-8 h-8 rounded-lg bg-lane flex items-center justify-center text-asphalt shadow-sm">
          <MapPin className="w-4 h-4 text-asphalt fill-asphalt" />
        </div>
        <span className="text-[15px] font-semibold tracking-tight text-white">
          Hotspot Mapping
        </span>
      </div>

      {/* Primary Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-btn text-[13.5px] font-medium transition-colors ${
                isActive
                  ? 'bg-lane/15 text-white border-l-4 border-lane shadow-inner font-semibold'
                  : 'text-[#BFC4C9] hover:bg-[#2C3136] hover:text-white'
              }`
            }
          >
            <item.icon className="w-4 h-4 shrink-0" />
            <span>{item.label}</span>
          </NavLink>
        ))}

        {/* Admin Divider & Item */}
        {userRole === 'admin' && (
          <div className="pt-4 mt-4 border-t border-[#2C3136]">
            <div className="px-3 pb-2 text-[11px] font-semibold tracking-wider text-muted uppercase">
              Administration
            </div>
            {adminNav.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 rounded-btn text-[13.5px] font-medium transition-colors ${
                    isActive
                      ? 'bg-lane/15 text-white border-l-4 border-lane font-semibold'
                      : 'text-[#BFC4C9] hover:bg-[#2C3136] hover:text-white'
                  }`
                }
              >
                <item.icon className="w-4 h-4 shrink-0" />
                <span>{item.label}</span>
              </NavLink>
            ))}
          </div>
        )}
      </nav>

      {/* User Footer Profile */}
      <div className="p-3 border-t border-[#2C3136] bg-[#191D21]">
        <div className="flex items-center justify-between gap-2 px-1">
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="w-8 h-8 rounded-full bg-[#2E353D] text-lane font-semibold text-xs flex items-center justify-center shrink-0 border border-[#404852]">
              {userName
                .split(' ')
                .map((n) => n[0])
                .join('')
                .toUpperCase()
                .slice(0, 2)}
            </div>
            <div className="min-w-0">
              <div className="text-[13px] font-medium text-white truncate">
                {userName}
              </div>
              <div className="text-[11.5px] text-[#8E959C] truncate">
                {userRoleLabel}
              </div>
            </div>
          </div>
          <button
            onClick={handleSignOut}
            title="Sign out"
            className="p-1.5 rounded-md text-muted hover:text-white hover:bg-[#2C3136] transition-colors"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>
  );
};
