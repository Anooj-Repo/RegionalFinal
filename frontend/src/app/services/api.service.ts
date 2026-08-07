import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';
import { Project, PortfolioSummary } from '../models/project.model';
import { RAIDItem } from '../models/raid.model';
import { EmailDraft } from '../models/email.model';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private readonly baseUrl = 'http://127.0.0.1:5000/api';

  constructor(private http: HttpClient) {}

  private getHeaders(): HttpHeaders {
    const token = localStorage.getItem('access_token') || '';
    return new HttpHeaders({
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    });
  }

  getProjects(phase?: string, health?: string): Observable<{ status: string; portfolio_summary: PortfolioSummary; projects: Project[] }> {
    let url = `${this.baseUrl}/projects`;
    const params: string[] = [];
    if (phase) params.push(`phase=${phase}`);
    if (health) params.push(`health=${health}`);
    if (params.length > 0) url += `?${params.join('&')}`;

    return this.http.get<{ status: string; portfolio_summary: PortfolioSummary; projects: Project[] }>(url, { headers: this.getHeaders() });
  }

  getProjectByCode(code: string): Observable<{ status: string; project: Project }> {
    return this.http.get<{ status: string; project: Project }>(`${this.baseUrl}/projects/${code}`, { headers: this.getHeaders() });
  }

  getRaidItems(projectId?: number, category?: string): Observable<{ status: string; raid_summary: any; raid_items: RAIDItem[] }> {
    let url = `${this.baseUrl}/raid`;
    const params: string[] = [];
    if (projectId) params.push(`project_id=${projectId}`);
    if (category) params.push(`category=${category}`);
    if (params.length > 0) url += `?${params.join('&')}`;

    return this.http.get<{ status: string; raid_summary: any; raid_items: RAIDItem[] }>(url, { headers: this.getHeaders() });
  }

  getEmails(status?: string): Observable<{ status: string; email_summary: any; emails: EmailDraft[] }> {
    let url = `${this.baseUrl}/emails`;
    if (status) url += `?status=${status}`;
    return this.http.get<{ status: string; email_summary: any; emails: EmailDraft[] }>(url, { headers: this.getHeaders() });
  }

  updateEmailDraft(id: number, subject: string, body: string): Observable<any> {
    return this.http.put(`${this.baseUrl}/emails/${id}`, { subject, body }, { headers: this.getHeaders() });
  }

  approveEmail(id: number): Observable<any> {
    return this.http.post(`${this.baseUrl}/emails/${id}/approve`, {}, { headers: this.getHeaders() });
  }

  getAuditLogs(): Observable<any> {
    return this.http.get(`${this.baseUrl}/admin/audit-logs?limit=20`, { headers: this.getHeaders() });
  }

  getSystemMetrics(): Observable<any> {
    return this.http.get(`${this.baseUrl}/admin/system-metrics`, { headers: this.getHeaders() });
  }
}
