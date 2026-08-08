import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';
import { EmailDraft } from '../../models/email.model';
import { Project } from '../../models/project.model';

@Component({
  selector: 'app-comms',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './comms.component.html'
})
export class CommsComponent implements OnInit {
  emails: EmailDraft[] = [];
  projects: Project[] = [];
  selectedProjectCode: string = 'PRJ-001';
  selectedEmail: EmailDraft | null = null;
  selectedTone: string = 'Executive';
  isRefiningTone: boolean = false;

  constructor(private apiService: ApiService) {}

  ngOnInit(): void {
    this.refreshData();
  }

  refreshData(): void {
    this.apiService.getProjects().subscribe(res => {
      if (res && res.projects) {
        this.projects = res.projects;
      }
    });

    this.apiService.getEmails().subscribe(res => {
      if (res && res.emails) {
        this.emails = res.emails;
      }
    });
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

  getRecipientName(role?: string, email?: string): string {
    return 'Linus Simon';
  }

  getFilteredEmails(): EmailDraft[] {
    if (this.selectedProjectCode === 'ALL') {
      return this.emails;
    }
    const currentProject = this.projects.find(p => p.code === this.selectedProjectCode);
    const projId = currentProject ? currentProject.id : 1;

    return this.emails.filter(e => e.project_id === projId || e.project_code === this.selectedProjectCode);
  }

  getPendingCount(): number {
    return this.getFilteredEmails().filter(e => e.status === 'PENDING').length;
  }

  getSentCount(): number {
    return this.getFilteredEmails().filter(e => e.status === 'SENT').length;
  }

  openApprovalModal(email: EmailDraft): void {
    this.selectedEmail = { ...email };
  }

  closeModal(): void {
    this.selectedEmail = null;
  }

  refineToneWithAI(): void {
    if (!this.selectedEmail || !this.selectedEmail.body) return;
    const e = this.selectedEmail;
    this.isRefiningTone = true;

    this.apiService.refineEmailTone(e.subject, e.body, this.selectedTone, '', e.recipient_role || '', e.recipient_email || '').subscribe(res => {
      this.isRefiningTone = false;
      if (res && res.status === 'success') {
        if (res.refined_subject) e.subject = res.refined_subject;
        if (res.refined_body) e.body = res.refined_body;
        alert(`AI Tone Transformation Applied! Converted email content to '${res.tone_applied}' sentiment.`);
      }
    }, () => {
      this.isRefiningTone = false;
    });
  }

  approveEmail(): void {
    if (!this.selectedEmail) return;
    const e = this.selectedEmail;

    this.apiService.updateEmailDraft(e.id, e.subject, e.body).subscribe(() => {
      this.apiService.approveEmail(e.id).subscribe(() => {
        alert(`Email #${e.id} approved! Background service will dispatch to linusimon@gmail.com within 5-10s.`);
        this.closeModal();
        this.refreshData();
      });
    });
  }
}
