export type UserRole =
  | 'admin'
  | 'police_officer'
  | 'safety_analyst'
  | 'authority_official'
  | 'public_viewer';

export type UserStatus = 'pending' | 'active' | 'deactivated';

export interface User {
  id: string;
  fullName: string;
  email: string;
  organisation: string;
  role: UserRole;
  status: UserStatus;
  lastActiveAt?: string;
}

export type RiskLevel = 'critical' | 'high' | 'medium' | 'low';

export type HotspotStatus =
  | 'Identified'
  | 'Under review'
  | 'Assigned'
  | 'Action in progress'
  | 'Implemented'
  | 'Closed';

export interface Hotspot {
  id: string;
  code: string;
  name: string;
  roadName: string;
  area: string;
  accidentsCount: number;
  fatalities: number;
  injured: number;
  riskScore: number;
  riskLevel: RiskLevel;
  riskOverridden: boolean;
  status: HotspotStatus;
  assigneeName?: string;
  assigneeRole?: string;
  peakTimeText: string;
  lat: number;
  lon: number;
  updatedAt: string;
  scoreBreakdown?: {
    deaths: number;
    frequency: number;
    injuries: number;
  };
}
