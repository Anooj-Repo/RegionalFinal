export interface MitigationAction {
  id: number;
  raid_id: number;
  title: string;
  description?: string;
  owner_name: string;
  due_date: string;
  status: 'In Progress' | 'Planned' | 'Completed' | 'Overdue';
  progress_pct: number;
  created_at?: string;
}

export interface RAIDItem {
  id: number;
  project_id: number;
  category: 'Risk' | 'Assumption' | 'Issue' | 'Dependency';
  title: string;
  description: string;
  likelihood: 'High' | 'Medium' | 'Low';
  impact: 'High' | 'Medium' | 'Low';
  risk_score: number;
  status: 'Open' | 'Monitoring' | 'Closed' | 'Resolved';
  owner_name: string;
  root_cause: string;
  created_at?: string;
  mitigation_actions?: MitigationAction[];
}
