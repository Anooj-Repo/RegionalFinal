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
  selectedProjectCode: string = 'PRJ-001';

  constructor(private apiService: ApiService) {}

  ngOnInit(): void {
    this.apiService.getProjects().subscribe(res => {
      if (res && res.projects) {
        this.projects = res.projects;
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
}
