export interface WbsTask {
  id: number;
  project_id: number;
  wbs_code: string;
  title: string;
  status: 'Completed' | 'In Progress' | 'Blocked' | 'Not Started';
  priority: 'High' | 'Medium' | 'Low';
  assignee_name: string;
  due_date: string;
  progress_pct: number;
  effort_sp: number;
  depends_on?: string;
  created_at?: string;
}

export interface Project {
  id: number;
  code: string;
  name: string;
  description?: string;
  lifecycle_phase: 'Mobilization' | 'Planning' | 'Design' | 'Execution' | 'Closure';
  health_status: 'Healthy' | 'At Risk' | 'Critical';
  progress_pct: number;
  owner_name: string;
  start_date?: string;
  end_date?: string;
  budget: number;
  spent: number;
  tasks?: WbsTask[];
  raid_items?: any[];
  created_at?: string;
}

export interface PortfolioSummary {
  total_projects: number;
  healthy_count: number;
  at_risk_count: number;
  critical_count: number;
}
