import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-admin-console',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './admin-console.component.html'
})
export class AdminConsoleComponent implements OnInit {
  documents: any[] = [];
  ragChunks: any[] = [];
  masterUsers: any[] = [];
  masterProjects: any[] = [];
  masterRaid: any[] = [];
  masterTasks: any[] = [];
  masterMitigations: any[] = [];
  masterEmails: any[] = [];
  auditLogs: any[] = [];
  telemetry: any = {};
  activeSubTab: 'rag_docs' | 'db_tables' | 'metrics' | 'audit_logs' = 'rag_docs';
  selectedDbTable: 'users' | 'projects' | 'raid' | 'tasks' | 'mitigations' | 'emails' | 'docs' = 'users';

  constructor(private apiService: ApiService) {}

  ngOnInit(): void {
    this.loadAdminData();
  }

  loadAdminData(): void {
    this.apiService.getKnowledgeDocs().subscribe(res => {
      if (res) {
        this.documents = res.documents || [];
        this.ragChunks = res.rag_chunks || [];
      }
    });

    this.apiService.getAllDbTables().subscribe(res => {
      if (res && res.tables) {
        this.masterUsers = res.tables.users || [];
        this.masterProjects = res.tables.projects || [];
        this.masterRaid = res.tables.raid_items || [];
        this.masterTasks = res.tables.tasks || [];
        this.masterMitigations = res.tables.mitigations || [];
        this.masterEmails = res.tables.emails || [];
      }
    });

    this.apiService.getSystemMetrics().subscribe(res => {
      if (res && res.telemetry) {
        this.telemetry = res.telemetry;
      }
    });

    this.apiService.getAuditLogs().subscribe(res => {
      if (res && res.audit_logs) {
        this.auditLogs = res.audit_logs;
      }
    });
  }

  setSubTab(tab: 'rag_docs' | 'db_tables' | 'metrics' | 'audit_logs'): void {
    this.activeSubTab = tab;
  }

  selectDbTable(table: 'users' | 'projects' | 'raid' | 'tasks' | 'mitigations' | 'emails' | 'docs'): void {
    this.selectedDbTable = table;
  }
}
