import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from './components/Layout';
import { LandingPage } from './pages/Landing';
import { SignupPage } from './pages/Signup';
import { LoginPage } from './pages/Login';
import { DashboardPage } from './pages/Dashboard';
import { HotspotMapPage } from './pages/HotspotMap';
import { DataImportPage } from './pages/DataImport';
import { HotspotCasesPage } from './pages/HotspotCases';
import { HotspotDetailPage } from './pages/HotspotDetail';
import { AIAssistantPage } from './pages/AIAssistant';
import { ReportsPage } from './pages/Reports';
import { UserManagementPage } from './pages/UserManagement';
import { NotificationsPage } from './pages/Notifications';
import { PublicMapPage } from './pages/PublicMap';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/signup" element={<SignupPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/public" element={<PublicMapPage />} />
        <Route path="/public-map" element={<Navigate to="/public" replace />} />

        {/* Authenticated Application Shell */}
        <Route element={<Layout />}>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/map" element={<HotspotMapPage />} />
          <Route path="/import" element={<DataImportPage />} />
          <Route path="/cases" element={<HotspotCasesPage />} />
          <Route path="/cases/:code" element={<HotspotDetailPage />} />
          <Route path="/assistant" element={<AIAssistantPage />} />
          <Route path="/reports" element={<ReportsPage />} />
          <Route path="/users" element={<UserManagementPage />} />
          <Route path="/notifications" element={<NotificationsPage />} />
        </Route>

        {/* Catch-all redirect */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;
