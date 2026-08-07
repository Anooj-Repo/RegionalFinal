import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';
import { EmailDraft } from '../../models/email.model';

@Component({
  selector: 'app-comms',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './comms.component.html'
})
export class CommsComponent implements OnInit {
  emails: EmailDraft[] = [];
  selectedEmail: EmailDraft | null = null;

  constructor(private apiService: ApiService) {}

  ngOnInit(): void {
    this.refreshEmails();
  }

  refreshEmails(): void {
    this.apiService.getEmails().subscribe(res => {
      if (res && res.emails) {
        this.emails = res.emails;
      }
    });
  }

  openApprovalModal(email: EmailDraft): void {
    this.selectedEmail = { ...email };
  }

  closeModal(): void {
    this.selectedEmail = null;
  }

  approveEmail(): void {
    if (!this.selectedEmail) return;
    const e = this.selectedEmail;

    this.apiService.updateEmailDraft(e.id, e.subject, e.body).subscribe(() => {
      this.apiService.approveEmail(e.id).subscribe(() => {
        alert(`Email #${e.id} approved! Background service will dispatch to linusimon@gmail.com within 5-10s.`);
        this.closeModal();
        this.refreshEmails();
      });
    });
  }
}
