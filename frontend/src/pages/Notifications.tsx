import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getApiUrl } from '../services/api';
import {
  Bell,
  CheckCheck,
  ShieldAlert,
  UserCheck,
  TrendingUp,
  CheckCircle2,
  Info,
  Clock,
  ChevronRight
} from 'lucide-react';

interface NotificationItem {
  id: string;
  type: string;
  title: string;
  body: string;
  entity_id?: string;
  is_read: boolean;
  time_ago: string;
}

interface NotificationSettings {
  critical_detected: boolean;
  assigned: boolean;
  risk_changed: boolean;
  action_implemented: boolean;
}

export const NotificationsPage: React.FC = () => {
  const navigate = useNavigate();
  const [filter, setFilter] = useState<'all' | 'unread'>('all');
  const [unreadCount, setUnreadCount] = useState(2);
  const [todayItems, setTodayItems] = useState<NotificationItem[]>([]);
  const [earlierItems, setEarlierItems] = useState<NotificationItem[]>([]);
  const [settings, setSettings] = useState<NotificationSettings>({
    critical_detected: true,
    assigned: true,
    risk_changed: true,
    action_implemented: true
  });

  useEffect(() => {
    fetchNotifications();
    fetchSettings();
  }, [filter]);

  const fetchNotifications = async () => {
    try {
      const token = localStorage.getItem('rah_token');
      const res = await fetch(getApiUrl(`/notifications?filter=${filter}`), {
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {})
        }
      });
      if (res.ok) {
        const data = await res.json();
        setUnreadCount(data.unread_count);
        setTodayItems(data.today || []);
        setEarlierItems(data.earlier || []);
      }
    } catch (err) {
      console.error('Failed to load notifications:', err);
    }
  };

  const fetchSettings = async () => {
    try {
      const token = localStorage.getItem('rah_token');
      const res = await fetch(getApiUrl('/notifications/settings'), {
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {})
        }
      });
      if (res.ok) {
        const data = await res.json();
        setSettings({
          critical_detected: data.critical_detected,
          assigned: data.assigned,
          risk_changed: data.risk_changed,
          action_implemented: data.action_implemented
        });
      }
    } catch (err) {
      console.error('Failed to load settings:', err);
    }
  };

  const markAllRead = async () => {
    try {
      const token = localStorage.getItem('rah_token');
      await fetch(getApiUrl('/notifications/read-all'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {})
        }
      });
      fetchNotifications();
    } catch (err) {
      console.error('Failed to mark all as read:', err);
    }
  };

  const markItemRead = async (id: string, entity_id?: string) => {
    try {
      const token = localStorage.getItem('rah_token');
      await fetch(getApiUrl(`/notifications/${id}/read`), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {})
        }
      });
      fetchNotifications();
      if (entity_id) {
        navigate(`/cases/${entity_id}`);
      }
    } catch (err) {
      console.error('Failed to mark notification read:', err);
    }
  };

  const toggleSetting = async (key: keyof NotificationSettings) => {
    const updated = { ...settings, [key]: !settings[key] };
    setSettings(updated);
    try {
      const token = localStorage.getItem('rah_token');
      await fetch(getApiUrl('/notifications/settings'), {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {})
        },
        body: JSON.stringify(updated)
      });
    } catch (err) {
      console.error('Failed to save settings:', err);
    }
  };

  const getNotifIcon = (type: string) => {
    switch (type) {
      case 'critical_detected':
        return <ShieldAlert className="w-4 h-4 text-crit" />;
      case 'assigned':
        return <UserCheck className="w-4 h-4 text-[#2F6FB5]" />;
      case 'risk_changed':
        return <TrendingUp className="w-4 h-4 text-[#E2762B]" />;
      case 'action_implemented':
        return <CheckCircle2 className="w-4 h-4 text-[#3E8E62]" />;
      default:
        return <Bell className="w-4 h-4 text-muted" />;
    }
  };

  const renderNotifRow = (item: NotificationItem) => (
    <div
      key={item.id}
      onClick={() => markItemRead(item.id, item.entity_id)}
      className={`p-4 rounded-card border transition cursor-pointer flex items-start gap-3.5 ${
        !item.is_read
          ? 'bg-card border-line shadow-sm hover:border-lane'
          : 'bg-paper/50 border-line/60 hover:bg-paper'
      }`}
    >
      <div className="p-2 rounded-full bg-paper border border-line shrink-0 mt-0.5">
        {getNotifIcon(item.type)}
      </div>

      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            {!item.is_read && <span className="w-2 h-2 rounded-full bg-crit shrink-0" />}
            <h3
              className={`text-[13.5px] leading-snug ${
                !item.is_read ? 'font-bold text-ink' : 'font-medium text-ink/80'
              }`}
            >
              {item.title}
            </h3>
          </div>
          <span className="text-[11.5px] text-muted shrink-0 whitespace-nowrap">{item.time_ago}</span>
        </div>

        <p className="text-[12.5px] text-muted mt-1 leading-relaxed">{item.body}</p>

        {item.entity_id && (
          <div className="mt-2 flex items-center gap-1 text-[11.5px] font-semibold text-[#8A6A00] hover:underline">
            <span>Inspect case {item.entity_id}</span>
            <ChevronRight className="w-3.5 h-3.5" />
          </div>
        )}
      </div>
    </div>
  );

  return (
    <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-6 pb-12">
      {/* Left Column: Notification Feed (7 cols) */}
      <div className="lg:col-span-7 space-y-6">
        {/* Top Header & Tabs */}
        <div className="flex items-center justify-between bg-card border border-line rounded-card p-4 shadow-sm">
          <div className="flex items-center gap-2">
            <button
              onClick={() => setFilter('all')}
              className={`px-3 py-1.5 rounded-full text-[13px] font-semibold transition ${
                filter === 'all'
                  ? 'bg-asphalt text-white'
                  : 'bg-paper text-muted hover:text-ink'
              }`}
            >
              All
            </button>
            <button
              onClick={() => setFilter('unread')}
              className={`px-3 py-1.5 rounded-full text-[13px] font-semibold transition flex items-center gap-1.5 ${
                filter === 'unread'
                  ? 'bg-asphalt text-white'
                  : 'bg-paper text-muted hover:text-ink'
              }`}
            >
              <span>Unread</span>
              {unreadCount > 0 && (
                <span className="w-4 h-4 rounded-full bg-crit text-white text-[10px] flex items-center justify-center font-bold">
                  {unreadCount}
                </span>
              )}
            </button>
          </div>

          <button
            onClick={markAllRead}
            className="flex items-center gap-1.5 text-xs font-semibold text-muted hover:text-ink transition"
          >
            <CheckCheck className="w-4 h-4 text-muted" />
            Mark all as read
          </button>
        </div>

        {/* Group: Today */}
        {todayItems.length > 0 && (
          <div className="space-y-3">
            <h2 className="text-[12px] font-bold uppercase tracking-wider text-muted px-1">Today</h2>
            <div className="space-y-2.5">{todayItems.map(renderNotifRow)}</div>
          </div>
        )}

        {/* Group: Earlier */}
        {earlierItems.length > 0 && (
          <div className="space-y-3">
            <h2 className="text-[12px] font-bold uppercase tracking-wider text-muted px-1">
              Earlier this week
            </h2>
            <div className="space-y-2.5">{earlierItems.map(renderNotifRow)}</div>
          </div>
        )}

        {todayItems.length === 0 && earlierItems.length === 0 && (
          <div className="p-12 text-center bg-card border border-line rounded-card shadow-sm">
            <Bell className="w-8 h-8 text-muted mx-auto mb-2 opacity-50" />
            <h3 className="text-[15px] font-semibold text-ink">No notifications</h3>
            <p className="text-[12.5px] text-muted mt-1">
              {filter === 'unread' ? 'You have read all your alerts.' : 'No alerts recorded yet.'}
            </p>
          </div>
        )}
      </div>

      {/* Right Column: "Tell me when" Settings (5 cols) */}
      <div className="lg:col-span-5">
        <div className="bg-card border border-line rounded-card p-5 shadow-sm space-y-5">
          <div>
            <h2 className="text-[15px] font-semibold text-ink">Tell me when</h2>
            <p className="text-[12.5px] text-muted">
              Choose which in-app safety events notify you immediately.
            </p>
          </div>

          <div className="space-y-4 divide-y divide-line/60">
            {/* Toggle 1: Critical Hotspot */}
            <div className="pt-3 first:pt-0 flex items-center justify-between gap-4">
              <div>
                <div className="font-semibold text-ink text-[13px] flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-crit" />
                  Critical hotspot detected
                </div>
                <div className="text-[11.5px] text-muted mt-0.5">
                  When a cluster crosses risk score 85 or has 5+ fatalities
                </div>
              </div>
              <button
                type="button"
                onClick={() => toggleSetting('critical_detected')}
                className={`w-11 h-6 rounded-full transition-colors relative shrink-0 ${
                  settings.critical_detected ? 'bg-lane' : 'bg-line'
                }`}
              >
                <span
                  className={`w-4 h-4 rounded-full bg-white shadow-sm absolute top-1 transition-transform ${
                    settings.critical_detected ? 'right-1' : 'left-1'
                  }`}
                />
              </button>
            </div>

            {/* Toggle 2: Hotspot Assigned */}
            <div className="pt-3 flex items-center justify-between gap-4">
              <div>
                <div className="font-semibold text-ink text-[13px] flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-[#2F6FB5]" />
                  Hotspot assigned to me
                </div>
                <div className="text-[11.5px] text-muted mt-0.5">
                  When an administrator or supervisor assigns you a case
                </div>
              </div>
              <button
                type="button"
                onClick={() => toggleSetting('assigned')}
                className={`w-11 h-6 rounded-full transition-colors relative shrink-0 ${
                  settings.assigned ? 'bg-lane' : 'bg-line'
                }`}
              >
                <span
                  className={`w-4 h-4 rounded-full bg-white shadow-sm absolute top-1 transition-transform ${
                    settings.assigned ? 'right-1' : 'left-1'
                  }`}
                />
              </button>
            </div>

            {/* Toggle 3: Risk Level Changed */}
            <div className="pt-3 flex items-center justify-between gap-4">
              <div>
                <div className="font-semibold text-ink text-[13px] flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-[#E2762B]" />
                  Risk level changed
                </div>
                <div className="text-[11.5px] text-muted mt-0.5">
                  When manual override or data refresh changes a blackspot level
                </div>
              </div>
              <button
                type="button"
                onClick={() => toggleSetting('risk_changed')}
                className={`w-11 h-6 rounded-full transition-colors relative shrink-0 ${
                  settings.risk_changed ? 'bg-lane' : 'bg-line'
                }`}
              >
                <span
                  className={`w-4 h-4 rounded-full bg-white shadow-sm absolute top-1 transition-transform ${
                    settings.risk_changed ? 'right-1' : 'left-1'
                  }`}
                />
              </button>
            </div>

            {/* Toggle 4: Action Implemented */}
            <div className="pt-3 flex items-center justify-between gap-4">
              <div>
                <div className="font-semibold text-ink text-[13px] flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-[#3E8E62]" />
                  Action marked implemented
                </div>
                <div className="text-[11.5px] text-muted mt-0.5">
                  When road authority marks safety interventions completed
                </div>
              </div>
              <button
                type="button"
                onClick={() => toggleSetting('action_implemented')}
                className={`w-11 h-6 rounded-full transition-colors relative shrink-0 ${
                  settings.action_implemented ? 'bg-lane' : 'bg-line'
                }`}
              >
                <span
                  className={`w-4 h-4 rounded-full bg-white shadow-sm absolute top-1 transition-transform ${
                    settings.action_implemented ? 'right-1' : 'left-1'
                  }`}
                />
              </button>
            </div>
          </div>

          {/* Channel Note Box */}
          <div className="p-3 bg-paper rounded-btn border border-line text-[12px] text-muted flex items-start gap-2">
            <Info className="w-4 h-4 text-muted shrink-0 mt-0.5" />
            <span>
              Notifications appear here in the app. Email and SMS channels are not available yet.
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
