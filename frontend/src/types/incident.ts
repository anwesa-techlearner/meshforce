export type Severity = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
export type IncidentCategory = 'medical' | 'crowd_control' | 'lost_found' | 'infrastructure' | 'general';
export type IncidentStatus = 'reported' | 'dispatched' | 'resolved';

export interface Incident {
  id: string;
  reported_by: string | null;
  raw_text: string;
  severity: Severity;
  category: IncidentCategory;
  required_skills: string[];
  summary: string;
  sector_id: string | null;
  location_lat: number;
  location_lng: number;
  status: IncidentStatus;
  assigned_volunteer_ids: string[];
  source: 'app' | 'sms';
  is_mock: boolean;
  created_at: string;
  resolved_at: string | null;
}

export interface IncidentReport {
  raw_text: string;
  sector_id?: string;
  reported_by?: string;
}
