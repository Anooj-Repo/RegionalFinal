export interface EmailDraft {
  id: number;
  project_id?: number;
  project_code?: string;
  raid_id?: number;
  recipient_role: 'Executive' | 'Program Manager' | 'Project Manager' | 'Tech Lead' | 'Client';
  recipient_email: string;
  subject: string;
  body: string;
  status: 'PENDING' | 'APPROVED' | 'REJECTED' | 'SENT' | 'FAILED';
  created_by: string;
  approved_by?: string;
  sent_at?: string;
  updated_at?: string;
  error_message?: string;
  created_at?: string;
}
