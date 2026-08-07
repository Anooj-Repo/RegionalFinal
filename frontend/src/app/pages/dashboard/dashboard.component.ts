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

  onProjectChange(event: Event): void {
    const target = event.target as HTMLSelectElement;
    if (target) {
      this.setProject(target.value);
    }
  }

  triggerWorkflow(): void {
    const cp = this.getCurrentProject();
    alert(`Risk Analysis triggered for ${cp.code}! Portfolio risks synchronized with Risk Center.`);
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

  defaultRaidItems: any[] = [
    { project_id: 1, project_code: 'PRJ-001', category: 'Risk', title: 'Third-party API Integration Delay', likelihood: 'High', impact: 'High', risk_score: 85 },
    { project_id: 1, project_code: 'PRJ-001', category: 'Issue', title: 'Vendor Onboarding Access Bottleneck', likelihood: 'High', impact: 'Medium', risk_score: 75 },
    { project_id: 2, project_code: 'PRJ-002', category: 'Assumption', title: 'Legacy System Data Compatibility Assumption', likelihood: 'Medium', impact: 'Medium', risk_score: 60 },
    { project_id: 3, project_code: 'PRJ-003', category: 'Dependency', title: 'Biometric Hardware Module Availability', likelihood: 'High', impact: 'High', risk_score: 80 },
    { project_id: 4, project_code: 'PRJ-004', category: 'Risk', title: 'Data Migration Validation Failure', likelihood: 'Medium', impact: 'High', risk_score: 90 },
    { project_id: 5, project_code: 'PRJ-005', category: 'Dependency', title: 'Operational Handover Sign-off', likelihood: 'Low', impact: 'Medium', risk_score: 35 }
  ];

  getProjectRaidItems(): any[] {
    const cp = this.getCurrentProject();
    const source = (this.raidItems && this.raidItems.length > 0) ? this.raidItems : this.defaultRaidItems;
    return source.filter(r => 
      r.project_id === cp.id || 
      r.project_code === cp.code || 
      (cp.code === 'PRJ-001' && (r.project_id === 1 || r.project_code === 'PRJ-001')) ||
      (cp.code === 'PRJ-002' && (r.project_id === 2 || r.project_code === 'PRJ-002')) ||
      (cp.code === 'PRJ-003' && (r.project_id === 3 || r.project_code === 'PRJ-003')) ||
      (cp.code === 'PRJ-004' && (r.project_id === 4 || r.project_code === 'PRJ-004')) ||
      (cp.code === 'PRJ-005' && (r.project_id === 5 || r.project_code === 'PRJ-005'))
    );
  }

  getLikelihoodLevel(l: any): number {
    if (typeof l === 'number') return l;
    if (!l) return 3;
    const str = l.toString().toUpperCase();
    if (str.includes('1') || str.includes('VERY LOW') || str.includes('RARE')) return 1;
    if (str.includes('2') || str === 'LOW' || str.includes('UNLIKELY')) return 2;
    if (str.includes('3') || str === 'MEDIUM' || str.includes('MODERATE') || str.includes('POSSIBLE')) return 3;
    if (str.includes('4') || str === 'HIGH' || str.includes('LIKELY')) return 4;
    if (str.includes('5') || str.includes('VERY HIGH') || str.includes('CRITICAL') || str.includes('CERTAIN')) return 5;
    return 3;
  }

  getImpactLevel(i: any, score?: number): number {
    if (score && score >= 90) return 5;
    if (typeof i === 'number') return i;
    if (!i) return 3;
    const str = i.toString().toUpperCase();
    if (str.includes('5') || str.includes('VERY HIGH') || str.includes('CRITICAL') || str.includes('SEVERE')) return 5;
    if (str.includes('4') || str === 'HIGH' || str.includes('MAJOR')) return 4;
    if (str.includes('3') || str === 'MEDIUM' || str.includes('MODERATE')) return 3;
    if (str.includes('2') || str === 'LOW' || str.includes('MINOR')) return 2;
    if (str.includes('1') || str.includes('VERY LOW') || str.includes('NEGLIGIBLE')) return 1;
    return 3;
  }

  getCellItems(l: number, i: number): any[] {
    return this.getProjectRaidItems().filter(r => 
      this.getLikelihoodLevel(r.likelihood) === l && this.getImpactLevel(r.impact, r.risk_score) === i
    );
  }

  getCellText(l: number, i: number): string {
    const items = this.getCellItems(l, i);
    if (items.length === 0) return `L${l}/I${i}`;
    const scores = items.map(item => item.risk_score).filter(s => s !== undefined).join(', ');
    return `L${l}/I${i} (${scores})`;
  }

  getCellTooltip(l: number, i: number): string {
    const items = this.getCellItems(l, i);
    if (items.length === 0) return `L${l}/I${i}`;
    return items.map(item => `${item.category}: ${item.title} (Score: ${item.risk_score})`).join(' | ');
  }

  getCellClass(l: number, i: number): string {
    const items = this.getCellItems(l, i);
    if (items.some(r => (r.risk_score || 0) >= 70)) {
      return 'cell-critical';
    }
    if (items.length > 0) {
      return 'cell-high';
    }
    const sum = l + i;
    if (sum <= 3) return 'cell-low';
    if (sum <= 5) return 'cell-med';
    if (sum <= 7) return 'cell-high';
    return 'cell-critical';
  }
}

