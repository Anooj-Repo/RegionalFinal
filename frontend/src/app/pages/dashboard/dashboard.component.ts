import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../services/api.service';
import { Project } from '../../models/project.model';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard.component.html'
})
export class DashboardComponent implements OnInit {
  projects: Project[] = [];
  raidItems: any[] = [];
  emails: any[] = [];
  selectedProjectCode: string = 'PRJ-001';

  constructor(private apiService: ApiService) {}

  ngOnInit(): void {
    this.loadData();
  }

  loadData(): void {
    this.apiService.getProjects().subscribe(res => {
      if (res && res.projects) {
        this.projects = res.projects;
      }
    });

    this.apiService.getRaidItems().subscribe(res => {
      if (res && res.raid_items) {
        this.raidItems = res.raid_items;
      }
    });

    this.apiService.getEmails().subscribe(res => {
      if (res && res.emails) {
        this.emails = res.emails;
      }
    });
  }

  getCurrentProject(): Project {
    return this.projects.find(p => p.code === this.selectedProjectCode) || {
      id: 1, code: 'PRJ-001', name: 'Project Orion Upgrade', lifecycle_phase: 'Mobilization', health_status: 'At Risk', progress_pct: 72, owner_name: 'Rohit Verma', budget: 2500000, spent: 1450000
    };
  }

  setProject(code: string): void {
    this.selectedProjectCode = code;
  }

  getProjectRaidItems(): any[] {
    const cp = this.getCurrentProject();
    return this.raidItems.filter(r => r.project_id === cp.id || r.project_code === cp.code);
  }

  getProjectHighRiskCount(): number {
    return this.getProjectRaidItems().filter(r => (r.risk_score || 0) >= 70).length;
  }

  getProjectPendingEmailCount(): number {
    const cp = this.getCurrentProject();
    return this.emails.filter(e => (e.project_id === cp.id || e.project_code === cp.code) && e.status === 'PENDING').length;
  }

  getBudgetVarianceValue(): string {
    const cp = this.getCurrentProject();
    const budget = cp.budget || 2500000;
    const spent = cp.spent || 1450000;
    const variance = budget - spent;
    const variancePct = ((variance / budget) * 100).toFixed(1);
    const isOverBudget = variance < 0;
    return isOverBudget ? `-${Math.abs(Number(variancePct))}%` : `+${variancePct}%`;
  }

  getBudgetVarianceSubtext(): string {
    const cp = this.getCurrentProject();
    const budget = cp.budget || 2500000;
    const spent = cp.spent || 1450000;
    const variance = budget - spent;
    const formattedDiff = (Math.abs(variance) / 1000000).toFixed(1);
    const isOverBudget = variance < 0;
    return isOverBudget ? `($${formattedDiff}M over budget)` : `($${formattedDiff}M under budget)`;
  }

  getBudgetVarianceColor(): string {
    const cp = this.getCurrentProject();
    const budget = cp.budget || 2500000;
    const spent = cp.spent || 1450000;
    return (budget - spent) < 0 ? 'var(--error)' : '#059669';
  }

  triggerWorkflow(): void {
    const cp = this.getCurrentProject();
    this.apiService.runWorkflow("Analyze portfolio risks and generate mitigation plan", cp.code, "Program Manager").subscribe(res => {
      if (res && res.workflow_result) {
        alert(`LangGraph Workflow Completed for ${cp.code}! Generated draft email #${res.workflow_result.communication.created_draft_id} for Human Approval.`);
        this.loadData();
      }
    });
  }
}

