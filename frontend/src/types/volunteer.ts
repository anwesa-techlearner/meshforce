export type VolunteerStatus = 'active_idle' | 'on_mission' | 'resting' | 'offline';

export interface Volunteer {
  id: string;
  name: string;
  phone: string;
  skills: string[];
  languages: string[];
  sector_id: string | null;
  status: VolunteerStatus;
  active_mission_id: string | null;
  hours_worked: number;
  shift_start: string;
  is_mock: boolean;
  created_at: string;
}

export interface VolunteerCreate {
  name: string;
  phone: string;
  skills: string[];
  languages: string[];
  sector_id: string;
}
