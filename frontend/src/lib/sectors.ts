export const SECTORS = [
  { id: 'SEC-01', name: 'Sangam Nose',   lat: 25.4244, lng: 81.8846 },
  { id: 'SEC-02', name: 'Triveni Ghat',  lat: 25.4358, lng: 81.8836 },
  { id: 'SEC-03', name: 'Parade Ground', lat: 25.4484, lng: 81.8661 },
  { id: 'SEC-04', name: 'Jhunsi',        lat: 25.4512, lng: 81.8340 },
  { id: 'SEC-05', name: 'Arail',         lat: 25.4125, lng: 81.9012 },
  { id: 'SEC-06', name: 'Medical Zone',  lat: 25.4390, lng: 81.8750 },
] as const;

export const SECTOR_BY_ID = Object.fromEntries(SECTORS.map(s => [s.id, s]));

export const SECTOR_BOUNDS: Record<string, [[number, number], [number, number]]> = {
  'SEC-01': [[25.4194, 81.8796], [25.4294, 81.8896]],
  'SEC-02': [[25.4308, 81.8786], [25.4408, 81.8886]],
  'SEC-03': [[25.4434, 81.8611], [25.4534, 81.8711]],
  'SEC-04': [[25.4462, 81.8290], [25.4562, 81.8390]],
  'SEC-05': [[25.4075, 81.8962], [25.4175, 81.9062]],
  'SEC-06': [[25.4340, 81.8700], [25.4440, 81.8800]],
};

export const SKILLS = ['first_aid','crowd_management','translation','info_desk','fire_safety'] as const;
export const LANGUAGES = ['Hindi','English','Bengali','Telugu','Tamil','Marathi','Bhojpuri'] as const;
export type Severity = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
export type Category = 'medical' | 'crowd_control' | 'lost_found' | 'infrastructure' | 'general';
export type VolunteerStatus = 'active_idle' | 'on_mission' | 'resting' | 'offline';
