import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Bell } from 'lucide-react';

interface TopBarProps {
  title: string;
  subtitle?: string;
  actions?: React.ReactNode;
  unreadNotificationsCount?: number;
}

export const TopBar: React.FC<TopBarProps> = ({
  title,
  subtitle,
  actions,
  unreadNotificationsCount = 2,
}) => {
  const navigate = useNavigate();

  return (
    <header className="h-16 bg-card border-b border-line px-6 flex items-center justify-between shrink-0 sticky top-0 z-20">
      <div>
        <h1 className="text-[20px] font-semibold text-ink leading-tight">
          {title}
        </h1>
        {subtitle && (
          <p className="text-[12.5px] text-muted leading-none mt-0.5">
            {subtitle}
          </p>
        )}
      </div>

      <div className="flex items-center gap-3">
        {actions && <div className="flex items-center gap-2">{actions}</div>}

        {/* Notifications Icon with unread badge */}
        <button
          onClick={() => navigate('/notifications')}
          className="relative p-2 rounded-btn border border-line text-ink hover:bg-paper transition-colors"
          title="Notifications"
        >
          <Bell className="w-4 h-4 text-ink" />
          {unreadNotificationsCount > 0 && (
            <span className="absolute top-1 right-1 w-2 h-2 rounded-full bg-crit ring-2 ring-white" />
          )}
        </button>
      </div>
    </header>
  );
};
