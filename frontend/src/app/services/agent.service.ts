import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface WorkflowResult {
  status: string;
  workflow: string;
  total_latency_ms: number;
  confidence_score: number;
  token_usage: { prompt_tokens: number; completion_tokens: number; total_tokens: number };
  estimated_cost_usd: number;
  data_intelligence: any;
  risk_intelligence: any;
  communication: any;
  graphical_node_traces: any[];
}

@Injectable({
  providedIn: 'root'
})
export class AgentService {
  private readonly baseUrl = 'http://127.0.0.1:5000/api/agents';

  constructor(private http: HttpClient) {}

  private getHeaders(): HttpHeaders {
    const token = localStorage.getItem('access_token') || '';
    return new HttpHeaders({
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    });
  }

  runMultiAgentWorkflow(query: string, projectCode: string, recipientRole: string): Observable<{ status: string; workflow_result: WorkflowResult }> {
    return this.http.post<{ status: string; workflow_result: WorkflowResult }>(
      `${this.baseUrl}/run-workflow`,
      { query, project_code: projectCode, recipient_role: recipientRole, recipient_email: 'linusimon@gmail.com' },
      { headers: this.getHeaders() }
    );
  }

  sendAgentChat(message: string, projectCode: string): Observable<any> {
    return this.http.post(
      `${this.baseUrl}/chat`,
      { message, project_code: projectCode },
      { headers: this.getHeaders() }
    );
  }
}
