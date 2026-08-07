import { Routes } from '@angular/router';

export const routes: Routes = [
  { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
  {
    path: 'login',
    loadComponent: () => import('./pages/login/login.component').then(m => m.LoginComponent)
  },
  {
    path: 'dashboard',
    loadComponent: () => import('./pages/dashboard/dashboard.component').then(m => m.DashboardComponent)
  },
  {
    path: 'analysis',
    loadComponent: () => import('./pages/analysis/analysis.component').then(m => m.AnalysisComponent)
  },
  {
    path: 'implementation',
    loadComponent: () => import('./pages/implementation/implementation.component').then(m => m.ImplementationComponent)
  },
  {
    path: 'comms',
    loadComponent: () => import('./pages/comms/comms.component').then(m => m.CommsComponent)
  },
  {
    path: 'chat-vision',
    loadComponent: () => import('./pages/chat-vision/chat-vision.component').then(m => m.ChatVisionComponent)
  },
  {
    path: 'admin-console',
    loadComponent: () => import('./pages/admin-console/admin-console.component').then(m => m.AdminConsoleComponent)
  }
];
