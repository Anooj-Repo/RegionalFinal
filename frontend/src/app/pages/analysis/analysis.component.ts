import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../services/api.service';
import { AgentService } from '../../services/agent.service';
import { RAIDItem } from '../../models/raid.model';

@Component({
  selector: 'app-analysis',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './analysis.component.html'
})
export class AnalysisComponent implements OnInit {
  raidItems: RAIDItem[] = [];
  selectedProjectCode: string = 'PRJ-001';

  constructor(
    private apiService: ApiService,
    private agentService: AgentService
  ) {}

  ngOnInit(): void {
    this.apiService.getRaidItems().subscribe(res => {
      if (res && res.raid_items) {
        this.raidItems = res.raid_items;
      }
    });
  }

  runAnalysis(): void {
    this.agentService.runMultiAgentWorkflow('Analyze RAID risks', this.selectedProjectCode, 'Executive').subscribe(res => {
      alert('Risk Intelligence Agent executed successfully! Created PENDING draft email.');
    });
  }
}
