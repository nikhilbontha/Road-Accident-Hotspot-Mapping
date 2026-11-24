import React from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { TopBar } from './TopBar';

export const Layout: React.FC = () => {
  const location = useLocation();

  // Page title and subtitle mapping based on current path
  const getPageMeta = () => {
    switch (location.pathname) {
      case '/dashboard':
        return {
          title: 'Dashboard',
          subtitle: 'Dec 2025 – Nov 2026 · Overview of road accident clusters and actions',
        };
      case '/map':
        return {
          title: 'Hotspot Map',
          subtitle: 'Geospatial clustering and risk assessment of high-density accident zones',
        };
      case '/import':
        return {
          title: 'Data Import',
          subtitle: 'Upload, validate, mask personal identifiers and ingest accident records',
        };
      case '/cases':
        return {
          title: 'Hotspot Cases',
          subtitle: 'Active blackspot investigations, assignments and intervention tracking',
        };
      case '/assistant':
        return {
          title: 'AI Insights Assistant',
          subtitle: 'Grounded geospatial analysis and decision support for road safety experts',
        };
      case '/reports':
        return {
          title: 'Reports & Export',
          subtitle: 'Official summary dossiers, trend analyses and intervention audits',
        };
      case '/users':
        return {
          title: 'User Management',
          subtitle: 'Administer authorized personnel, approvals and department role permissions',
        };
      case '/notifications':
        return {
          title: 'Notifications',
          subtitle: 'Critical blackspot alerts, assignments and safety action updates',
        };
      default:
        return {
          title: 'Road Accident Hotspot Mapping',
          subtitle: 'Team 12 · Anurag University',
        };
    }
  };

  const meta = getPageMeta();

  // Retrieve demo or stored user
  let user = {
    name: 'Asha Reddy',
    role: 'safety_analyst' as const,
    roleLabel: 'Road Safety Analyst',
  };

  try {
    const stored = localStorage.getItem('rah_user');
    if (stored) {
      const parsed = JSON.parse(stored);
      user = {
        name: parsed.fullName || parsed.n || user.name,
        role: parsed.role || user.role,
        roleLabel: parsed.roleLabel || parsed.r || user.roleLabel,
      };
    }
  } catch (e) {
    // fallback
  }

  return (
    <div className="flex min-h-screen bg-paper font-sans">
      <Sidebar
        userRole={user.role}
        userName={user.name}
        userRoleLabel={user.roleLabel}
      />
      <div className="flex-1 flex flex-col min-w-0">
        <TopBar title={meta.title} subtitle={meta.subtitle} />
        <main className="flex-1 p-6 md:p-7 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
