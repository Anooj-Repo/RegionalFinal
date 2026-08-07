import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <nav class="role-tabs">
      <button class="tab-btn" routerLink="/dashboard" routerLinkActive="active">Summary Dashboard</button>
      <button class="tab-btn" routerLink="/analysis" routerLinkActive="active">RAID Risk Analysis</button>
      <button class="tab-btn" routerLink="/implementation" routerLinkActive="active">WBS Implementation</button>
      <button class="tab-btn" routerLink="/comms" routerLinkActive="active">Communication Center</button>
      <button class="tab-btn" routerLink="/chat-vision" routerLinkActive="active">AI Chat & Vision</button>
      <button class="tab-btn" routerLink="/admin-console" routerLinkActive="active">Admin Console</button>
    </nav>
  `
})
export class NavbarComponent {}
