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
  auditLogs: any[] = [];
  telemetry: any = {};

  constructor(private apiService: ApiService) {}

  ngOnInit(): void {
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
}
