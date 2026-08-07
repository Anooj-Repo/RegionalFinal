import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from './services/api.service';
import { AgentService } from './services/agent.service';
import { SpeechService } from './services/speech.service';
import { Project } from './models/project.model';
import { RAIDItem } from './models/raid.model';
import { EmailDraft } from './models/email.model';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './app.component.html',
  styleUrls: ['../styles.css']
})
export class AppComponent implements OnInit {
  currentRole: 'Program Manager' | 'Project Manager' | 'Team Lead' | 'System Admin' = 'Program Manager';
  selectedProjectCode: string = 'PRJ-001';
  activeTab: 'dashboard' | 'raid' | 'comms' | 'chat' | 'admin' = 'dashboard';

  projects: Project[] = [];
  tasks: any[] = [];
  raidItems: RAIDItem[] = [];
  emails: EmailDraft[] = [];
  auditLogs: any[] = [];
  telemetry: any = {};
  nodeTraces: any[] = [];

  userQuery: string = 'Analyze risk for Project Orion Upgrade and generate mitigation plan';
  chatResponse: string = '';
  selectedEmailForApproval: EmailDraft | null = null;
  isRecordingVoice: boolean = false;

  constructor(
    private apiService: ApiService,
    private agentService: AgentService,
    private speechService: SpeechService
  ) {}

  ngOnInit(): void {
    this.loadProjects();
    this.refreshWorkspace();
  }

  loadProjects(): void {
    this.apiService.getProjects().subscribe(res => {
      if (res && res.projects) {
        this.projects = res.projects;
      }
    });
  }

  refreshWorkspace(): void {
    this.apiService.getProjectByCode(this.selectedProjectCode).subscribe(res => {
      if (res && res.project) {
        this.tasks = res.project.tasks || [];
        this.raidItems = res.project.raid_items || [];
      }
    });

    this.apiService.getEmails().subscribe(res => {
      if (res && res.emails) {
        this.emails = res.emails;
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

  onRoleChange(newRole: any): void {
    this.currentRole = newRole;
  }

  onProjectChange(newCode: string): void {
    this.selectedProjectCode = newCode;
    this.refreshWorkspace();
  }

  setTab(tab: 'dashboard' | 'raid' | 'comms' | 'chat' | 'admin'): void {
    this.activeTab = tab;
  }

  getCurrentProject(): Project {
    return this.projects.find(p => p.code === this.selectedProjectCode) || {
      id: 1, code: 'PRJ-001', name: 'Project Orion Upgrade', lifecycle_phase: 'Mobilization', health_status: 'At Risk', progress_pct: 72, owner_name: 'Rohit Verma', budget: 2500000, spent: 1450000
    };
  }

  getPendingEmailsCount(): number {
    return this.emails.filter(e => e.status === 'PENDING').length;
  }

  runMultiAgentWorkflow(): void {
    this.agentService.runMultiAgentWorkflow(this.userQuery, this.selectedProjectCode, this.currentRole).subscribe(res => {
      if (res && res.workflow_result) {
        this.nodeTraces = res.workflow_result.graphical_node_traces || [];
        this.chatResponse = `Workflow Executed! Risk Score: ${res.workflow_result.risk_intelligence?.top_risk_score || 85}. Created PENDING email draft #${res.workflow_result.communication?.created_draft_id} for Human Approval.`;
        this.refreshWorkspace();
      }
    });
  }

  startVoiceAssistant(): void {
    this.isRecordingVoice = true;
    this.speechService.startSpeechToText(
      (transcript) => {
        this.userQuery = transcript;
        this.isRecordingVoice = false;
        this.speechService.textToSpeech(`Received query: ${transcript}. Running analysis now.`);
        this.runMultiAgentWorkflow();
      },
      (err) => {
        this.isRecordingVoice = false;
        alert(`Voice Error: ${err}`);
      }
    );
  }

  openApprovalModal(email: EmailDraft): void {
    this.selectedEmailForApproval = { ...email };
  }

  closeApprovalModal(): void {
    this.selectedEmailForApproval = null;
  }

  approveEmail(): void {
    if (!this.selectedEmailForApproval) return;
    const email = this.selectedEmailForApproval;

    this.apiService.updateEmailDraft(email.id, email.subject, email.body).subscribe(() => {
      this.apiService.approveEmail(email.id).subscribe(res => {
        alert(`Email #${email.id} Approved! Background service will dispatch to linusimon@gmail.com within 5-10 seconds.`);
        this.closeApprovalModal();
        this.refreshWorkspace();
      });
    });
  }
}
