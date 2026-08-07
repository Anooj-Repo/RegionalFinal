/**
 * Enterprise Program Management AI Assistant - Angular 17 / Standalone App Engine
 * UI Redesign matching Google Stitch "Program Manager Portal Design" (Executive Precision)
 */

const API_BASE_URL = 'http://127.0.0.1:5000/api';

// Application State Store
const state = {
  currentRole: 'Program Manager',
  selectedProjectCode: 'PRJ-001',
  projects: [],
  tasks: [],
  raidItems: [],
  emails: [],
  auditLogs: [],
  telemetry: {},
  authToken: null,
  activeTab: 'login',
  selectedDateRange: { start: '2025-05-12', end: '2025-05-18' },
  selectedEmailForApproval: null,
  isRecordingVoice: false,
  nodeTraces: [],
  isTraceExpanded: false,
  isCustomizeModalOpen: false,
  dashboardWidgetOrder: ['kpis', 'heatmap', 'breakdown', 'flowchart'],
  widgetVisibility: {
    kpis: true,
    heatmap: true,
    breakdown: true,
    flowchart: true
  }
};

// Initialize Application
async function initApp() {
  console.log('[PM AI App] Initializing Stitch PM Portal Engine...');
  await loginAsDefaultUser();
  await loadProjects();
  await refreshWorkspaceData();
  renderApp();
}

// Default Backend Authentication
async function loginAsDefaultUser() {
  try {
    const res = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: 'rohit', password: 'user123' })
    });
    if (res.ok) {
      const data = await res.json();
      state.authToken = data.access_token;
      console.log(`[Auth] Authenticated as ${data.user.full_name} (${data.user.role})`);
    }
  } catch (err) {
    console.error('[Auth Error] Backend API offline or unreachable:', err);
  }
}

// API Helpers
async function apiGet(endpoint) {
  if (!state.authToken) await loginAsDefaultUser();
  try {
    const res = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: { 'Authorization': `Bearer ${state.authToken}` }
    });
    return await res.json();
  } catch (err) {
    console.error(`[API Error] GET ${endpoint}:`, err);
    return null;
  }
}

async function apiPost(endpoint, body) {
  if (!state.authToken) await loginAsDefaultUser();
  try {
    const res = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${state.authToken}`
      },
      body: JSON.stringify(body)
    });
    return await res.json();
  } catch (err) {
    console.error(`[API Error] POST ${endpoint}:`, err);
    return null;
  }
}

async function apiPut(endpoint, body) {
  if (!state.authToken) await loginAsDefaultUser();
  try {
    const res = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${state.authToken}`
      },
      body: JSON.stringify(body)
    });
    return await res.json();
  } catch (err) {
    console.error(`[API Error] PUT ${endpoint}:`, err);
    return null;
  }
}

// Data Fetching
async function loadProjects() {
  const data = await apiGet('/projects');
  if (data && data.projects) {
    state.projects = data.projects;
  }
}

async function refreshWorkspaceData() {
  const projData = await apiGet(`/projects/${state.selectedProjectCode}`);
  if (projData && projData.project) {
    state.tasks = projData.project.tasks || [];
    state.raidItems = projData.project.raid_items || [];
  }

  const emailsData = await apiGet('/emails');
  if (emailsData && emailsData.emails) {
    state.emails = emailsData.emails;
  }

  const telemetryData = await apiGet('/admin/system-metrics');
  if (telemetryData && telemetryData.telemetry) {
    state.telemetry = telemetryData.telemetry;
  }

  const auditData = await apiGet('/admin/audit-logs?limit=15');
  if (auditData && auditData.audit_logs) {
    state.auditLogs = auditData.audit_logs;
  }
}

// Event Handlers
function setRole(roleName) {
  state.currentRole = roleName;
  renderApp();
}

async function setProject(projectCode) {
  state.selectedProjectCode = projectCode;
  await refreshWorkspaceData();
  renderApp();
}

function handleDateRangeChange() {
  const start = document.getElementById('dateRangeStart')?.value;
  const end = document.getElementById('dateRangeEnd')?.value;
  if (start && end) {
    state.selectedDateRange = { start, end };
    console.log(`[Date Range Filter] Updated date range: ${start} to ${end}`);
    renderApp();
  }
}

// Dashboard Grid Layout Customizer Handlers
function openCustomizeModal() {
  state.isCustomizeModalOpen = true;
  renderApp();
}

function closeCustomizeModal() {
  state.isCustomizeModalOpen = false;
  renderApp();
}

function moveWidgetUp(index) {
  if (index > 0) {
    const temp = state.dashboardWidgetOrder[index];
    state.dashboardWidgetOrder[index] = state.dashboardWidgetOrder[index - 1];
    state.dashboardWidgetOrder[index - 1] = temp;
    renderApp();
  }
}

function moveWidgetDown(index) {
  if (index < state.dashboardWidgetOrder.length - 1) {
    const temp = state.dashboardWidgetOrder[index];
    state.dashboardWidgetOrder[index] = state.dashboardWidgetOrder[index + 1];
    state.dashboardWidgetOrder[index + 1] = temp;
    renderApp();
  }
}

function toggleWidgetVisibility(widgetKey) {
  state.widgetVisibility[widgetKey] = !state.widgetVisibility[widgetKey];
  renderApp();
}

function resetDashboardLayout() {
  state.dashboardWidgetOrder = ['kpis', 'heatmap', 'breakdown', 'flowchart'];
  state.widgetVisibility = { kpis: true, heatmap: true, breakdown: true, flowchart: true };
  renderApp();
}

function openApprovalModal(emailId) {
  const email = state.emails.find(e => e.id === emailId);
  if (email) {
    state.selectedEmailForApproval = { ...email };
    renderApp();
  }
}

function closeApprovalModal() {
  state.selectedEmailForApproval = null;
  renderApp();
}

async function approveEmail() {
  if (!state.selectedEmailForApproval) return;
  const emailId = state.selectedEmailForApproval.id;
  
  await apiPut(`/emails/${emailId}`, {
    subject: document.getElementById('editSubject').value,
    body: document.getElementById('editBody').value
  });

  const res = await apiPost(`/emails/${emailId}/approve`, {});
  if (res && res.status === 'success') {
    alert(`Email #${emailId} Approved! Background email service will dispatch to linusimon@gmail.com within 5-10 seconds.`);
    closeApprovalModal();
    await refreshWorkspaceData();
    renderApp();
  }
}

async function triggerMultiAgentWorkflow() {
  const query = document.getElementById('chatQueryInput')?.value || "Analyze risks and generate mitigation plan";
  
  const res = await apiPost('/agents/run-workflow', {
    query: query,
    project_code: state.selectedProjectCode,
    recipient_role: state.currentRole
  });

  if (res && res.workflow_result) {
    state.nodeTraces = res.workflow_result.graphical_node_traces || [];
    await refreshWorkspaceData();
    renderApp();
    alert(`LangGraph Workflow Completed! Generated draft email #${res.workflow_result.communication.created_draft_id} for Human Approval.`);
  }
}

// STT & TTS Voice Assistant
function startVoiceRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    alert("Speech Recognition API is not supported in this browser. Please use Chrome or Edge.");
    return;
  }

  const recognition = new SpeechRecognition();
  recognition.lang = 'en-US';
  recognition.start();
  state.isRecordingVoice = true;
  renderApp();

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    if (document.getElementById('chatQueryInput')) {
      document.getElementById('chatQueryInput').value = transcript;
    }
    state.isRecordingVoice = false;
    renderApp();
    speakText(`Recorded query: ${transcript}. Executing risk analysis now.`);
    triggerMultiAgentWorkflow();
  };

  recognition.onerror = () => {
    state.isRecordingVoice = false;
    renderApp();
  };
}

function speakText(text) {
  if ('speechSynthesis' in window) {
    const utterance = new SpeechSynthesisUtterance(text);
    window.speechSynthesis.speak(utterance);
  }
}

// Main Render Function
function renderApp() {
  const root = document.querySelector('app-root') || document.getElementById('app-root');
  if (!root) return;

  if (state.activeTab === 'login') {
    root.innerHTML = renderLoginTab();
    return;
  }

  const currentProject = state.projects.find(p => p.code === state.selectedProjectCode) || {
    name: 'Project Orion Upgrade', code: 'PRJ-001', lifecycle_phase: 'Mobilization', health_status: 'At Risk', progress_pct: 72
  };

  const pendingEmailCount = state.emails.filter(e => e.status === 'PENDING').length;

  root.innerHTML = `
    <div class="app-container">
      <!-- 1. Fixed 260px Left Sidebar Navigation -->
      <nav class="sidebar-nav">
        <div class="sidebar-header">
          <div class="brand-icon-box">
            <span class="material-symbols-outlined" style="font-size:24px">smart_toy</span>
          </div>
          <div>
            <div class="brand-title">PM AI</div>
            <div class="brand-subtitle">Program Management</div>
          </div>
        </div>

        <div class="sidebar-menu">
          <button class="nav-link ${state.activeTab === 'dashboard' ? 'active' : ''}" onclick="state.activeTab='dashboard'; renderApp();">
            <span class="material-symbols-outlined">dashboard</span>
            <span>Dashboard</span>
          </button>
          <button class="nav-link ${state.activeTab === 'projects' ? 'active' : ''}" onclick="state.activeTab='projects'; renderApp();">
            <span class="material-symbols-outlined">assignment</span>
            <span>Projects</span>
          </button>
          <button class="nav-link ${state.activeTab === 'raid' ? 'active' : ''}" onclick="state.activeTab='raid'; renderApp();">
            <span class="material-symbols-outlined">warning</span>
            <span>Risk Center</span>
          </button>
          <button class="nav-link ${state.activeTab === 'comms' ? 'active' : ''}" onclick="state.activeTab='comms'; renderApp();">
            <span class="material-symbols-outlined">chat</span>
            <span>Communication ${pendingEmailCount > 0 ? `(${pendingEmailCount})` : ''}</span>
          </button>
          <button class="nav-link ${state.activeTab === 'reports' ? 'active' : ''}" onclick="state.activeTab='reports'; renderApp();">
            <span class="material-symbols-outlined">assessment</span>
            <span>Reports</span>
          </button>
          <button class="nav-link ${state.activeTab === 'chat' ? 'active' : ''}" onclick="state.activeTab='chat'; renderApp();">
            <span class="material-symbols-outlined">smart_toy</span>
            <span>AI Assistant</span>
          </button>
          <button class="nav-link ${state.activeTab === 'admin' ? 'active' : ''}" onclick="state.activeTab='admin'; renderApp();">
            <span class="material-symbols-outlined">settings</span>
            <span>Settings & Admin</span>
          </button>
          <button class="nav-link" onclick="state.activeTab='login'; renderApp();" style="margin-top:auto">
            <span class="material-symbols-outlined">logout</span>
            <span>Sign Out</span>
          </button>
        </div>
      </nav>

      <!-- 2. Main Body Area with Top Header -->
      <div class="main-wrapper">
        <!-- Top Sticky Header -->
        <header class="top-app-bar">
          <div class="header-search">
            <span class="material-symbols-outlined">search</span>
            <input type="text" placeholder="Search projects, risks, reports..." />
          </div>

          <div class="header-controls">
            <!-- Notifications & Help Icons -->
            <button class="icon-btn" title="Notifications ${pendingEmailCount > 0 ? '(' + pendingEmailCount + ' Pending Approvals)' : ''}" onclick="state.activeTab='comms'; renderApp();">
              <span class="material-symbols-outlined">notifications</span>
              ${pendingEmailCount > 0 ? '<span class="notification-dot"></span>' : ''}
            </button>

            <div class="help-tooltip-container">
              <button class="icon-btn" title="Help Info">
                <span class="material-symbols-outlined">help_outline</span>
              </button>
              <div class="help-tooltip-box">
                <div style="font-weight:700; color:var(--tertiary-fixed-dim); margin-bottom:4px; display:flex; align-items:center; gap:6px">
                  <span class="material-symbols-outlined" style="font-size:16px">info</span>
                  About PM AI
                </div>
                Program Management AI Assistant for Risk Analysis and Stakeholder Communication
              </div>
            </div>

            <!-- User Profile Avatar -->
            <div class="user-profile">
              <img class="avatar-img" src="https://lh3.googleusercontent.com/aida-public/AB6AXuCbcPHmQncMqeCyloxxFVdcQt82FdGRiPqJn4bdegkraWZJLbyoFF3FBb0UDFAHhop6wy41Pe-HfG8kF8D2j-nzH0ujTdtnWG2HSzd8sKaRyOdSdrbFPRT4UMYeELXSrNaljIIOIwk4lMEdu-8ty-JKlxAckqbyQ7zmu-bt-1v9EFRqEiHP2sq9bWYW4kAFAcn8Gm3s3TMyRJNpznTOQc_MauIOb3Epf8NinZ4bbvjZ12R9syMjguMG" alt="Arjun Mehta" />
              <div>
                <div class="user-name">Arjun Mehta</div>
                <div class="user-role">${state.currentRole}</div>
              </div>
            </div>
          </div>
        </header>

        <!-- Main Page Content -->
        <main class="content-area">
          ${renderCurrentTabContent(currentProject)}

          <!-- Collapsible Agent Execution Log & Telemetry Panel (Rendered on all pages) -->
          ${renderCollapsibleTracePanel()}
        </main>
      </div>

      <!-- Human Email Approval Modal -->
      ${state.selectedEmailForApproval ? renderHumanApprovalModal() : ''}
      <!-- Dashboard Grid Layout Customize Modal -->
      ${state.isCustomizeModalOpen ? renderCustomizeModal() : ''}
    </div>
  `;
}

// Render Current Tab Body
function renderCurrentTabContent(currentProject) {
  if (state.activeTab === 'dashboard') {
    return renderDashboardTab(currentProject);
  } else if (state.activeTab === 'projects') {
    return renderProjectsTab();
  } else if (state.activeTab === 'raid') {
    return renderRaidTab();
  } else if (state.activeTab === 'comms') {
    return renderCommsTab();
  } else if (state.activeTab === 'reports') {
    return renderReportsTab(currentProject);
  } else if (state.activeTab === 'chat') {
    return renderChatTab();
  } else if (state.activeTab === 'admin') {
    return renderAdminTab();
  }
  return renderDashboardTab(currentProject);
}

// 1. Dashboard Tab View
function renderDashboardTab(currentProject) {
  const pendingCount = state.emails.filter(e => e.status === 'PENDING').length;
  
  const widgetHTML = {
    kpis: `
      <!-- 5 KPI Cards Row -->
      <div class="kpi-grid">
        <div class="kpi-card">
          <div class="kpi-title">Overall Program Health</div>
          <div class="kpi-value">${currentProject.progress_pct}%</div>
          <div class="kpi-subtext">
            <span class="chip chip-warning">Medium Risk</span>
            <span style="color:var(--secondary); font-weight:600">Phase: ${currentProject.lifecycle_phase}</span>
          </div>
        </div>

        <div class="kpi-card">
          <div class="kpi-title">Active Projects</div>
          <div class="kpi-value">${state.projects.length}</div>
          <div class="kpi-subtext" style="color:#059669">
            <span class="material-symbols-outlined" style="font-size:16px">arrow_upward</span>
            <strong>3 from last week</strong>
          </div>
        </div>

        <div class="kpi-card">
          <div class="kpi-title">Open RAID Risks</div>
          <div class="kpi-value" style="color:var(--error)">${state.raidItems.length}</div>
          <div class="kpi-subtext" style="color:var(--error)">
            <span class="material-symbols-outlined" style="font-size:16px">warning</span>
            <strong>${state.raidItems.filter(r => r.risk_score >= 70).length} High Score (&gt;70)</strong>
          </div>
        </div>

        <div class="kpi-card">
          <div class="kpi-title">Pending Approvals</div>
          <div class="kpi-value" style="color:var(--primary-container)">${pendingCount}</div>
          <div class="kpi-subtext" style="color:var(--primary-container)">
            <span class="chip chip-info">Human Approval Required</span>
          </div>
        </div>

        <div class="kpi-card">
          <div class="kpi-title">Budget Variance</div>
          <div class="kpi-value" style="color:var(--error)">-8.5%</div>
          <div class="kpi-subtext" style="color:var(--error)">
            <strong>($1.2M over budget)</strong>
          </div>
        </div>
      </div>
    `,
    heatmap: `
      <div class="card-box">
        <div class="card-box-header">
          <div class="card-box-title">5x5 Risk Heatmap Matrix (${currentProject.code})</div>
          <span class="chip chip-warning">${currentProject.lifecycle_phase}</span>
        </div>
        <p style="color:var(--on-surface-variant); font-size:12px; margin-bottom:12px">Likelihood vs. Impact Distribution across RAID Items</p>
        
        <div class="heatmap-matrix">
          <div class="heatmap-cell cell-low">L1/I1</div>
          <div class="heatmap-cell cell-low">L1/I2</div>
          <div class="heatmap-cell cell-med">L1/I3</div>
          <div class="heatmap-cell cell-med">L1/I4</div>
          <div class="heatmap-cell cell-high">L1/I5</div>

          <div class="heatmap-cell cell-low">L2/I1</div>
          <div class="heatmap-cell cell-med">L2/I2</div>
          <div class="heatmap-cell cell-med">L2/I3</div>
          <div class="heatmap-cell cell-high">L2/I4</div>
          <div class="heatmap-cell cell-high">L2/I5</div>

          <div class="heatmap-cell cell-med">L3/I1</div>
          <div class="heatmap-cell cell-med">L3/I2</div>
          <div class="heatmap-cell cell-high">L3/I3</div>
          <div class="heatmap-cell cell-high">L3/I4</div>
          <div class="heatmap-cell cell-critical">L3/I5 (88)</div>

          <div class="heatmap-cell cell-med">L4/I1</div>
          <div class="heatmap-cell cell-high">L4/I2</div>
          <div class="heatmap-cell cell-high">L4/I3</div>
          <div class="heatmap-cell cell-critical">L4/I4 (85)</div>
          <div class="heatmap-cell cell-critical">L4/I5 (90)</div>

          <div class="heatmap-cell cell-high">L5/I1</div>
          <div class="heatmap-cell cell-high">L5/I2</div>
          <div class="heatmap-cell cell-critical">L5/I3</div>
          <div class="heatmap-cell cell-critical">L5/I4</div>
          <div class="heatmap-cell cell-critical">L5/I5</div>
        </div>
      </div>
    `,
    breakdown: `
      <div class="card-box">
        <div class="card-box-header">
          <div class="card-box-title">Project Phase Breakdown</div>
        </div>
        <div class="table-responsive">
          <table class="stitch-table">
            <thead>
              <tr><th>Project</th><th>Phase</th><th>Health</th><th>Progress</th></tr>
            </thead>
            <tbody>
              ${state.projects.map(p => `
                <tr style="cursor:pointer; ${p.code === currentProject.code ? 'background-color: var(--surface-container-high);' : ''}" onclick="setProject('${p.code}')">
                  <td><strong>${p.code}</strong> - ${p.name}</td>
                  <td>${p.lifecycle_phase}</td>
                  <td>
                    <span class="chip ${p.health_status==='Healthy'?'chip-success':p.health_status==='At Risk'?'chip-warning':'chip-danger'}">
                      ${p.health_status}
                    </span>
                  </td>
                  <td><strong>${p.progress_pct}%</strong></td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>
    `,
    flowchart: `
      <div class="card-box">
        <div class="card-box-header">
          <div class="card-box-title">Critical Path Dependency Map Flowchart (${currentProject.code})</div>
        </div>
        <div class="flow-chain">
          <div class="flow-step completed">Requirements Gathering<br><small style="color:#059669">Completed</small></div>
          <span class="material-symbols-outlined" style="color:var(--outline)">arrow_forward</span>
          <div class="flow-step completed">Design Review<br><small style="color:#059669">Completed</small></div>
          <span class="material-symbols-outlined" style="color:var(--outline)">arrow_forward</span>
          <div class="flow-step blocked">API Integration<br><small style="color:#dc2626">Blocked (Score 88)</small></div>
          <span class="material-symbols-outlined" style="color:var(--outline)">arrow_forward</span>
          <div class="flow-step in-progress">System Testing<br><small style="color:var(--primary-container)">In Progress</small></div>
          <span class="material-symbols-outlined" style="color:var(--outline)">arrow_forward</span>
          <div class="flow-step">Deployment<br><small style="color:var(--outline)">Not Started</small></div>
        </div>
      </div>
    `
  };

  const visibleWidgets = state.dashboardWidgetOrder.filter(w => state.widgetVisibility[w]);
  let contentBuffer = '';

  for (let i = 0; i < visibleWidgets.length; i++) {
    const curr = visibleWidgets[i];
    const next = visibleWidgets[i + 1];

    if ((curr === 'heatmap' && next === 'breakdown') || (curr === 'breakdown' && next === 'heatmap')) {
      contentBuffer += `
        <div class="grid-2col">
          ${widgetHTML[curr]}
          ${widgetHTML[next]}
        </div>
      `;
      i++;
    } else {
      contentBuffer += widgetHTML[curr];
    }
  }

  return `
    <div class="page-header">
      <div>
        <h1 class="page-title">Dashboard</h1>
        <p class="page-subtitle">Overview of your program health and key insights</p>
      </div>
      <div style="display:flex; gap:12px">
        <select class="btn-secondary" style="background:#fff; cursor:pointer" onchange="setProject(this.value)">
          ${state.projects.map(p => `
            <option value="${p.code}" ${p.code === currentProject.code ? 'selected' : ''}>
              ${p.code} - ${p.name}
            </option>
          `).join('')}
        </select>
        <div class="btn-secondary" style="background:#fff; display:flex; align-items:center; gap:8px; padding:6px 12px">
          <span class="material-symbols-outlined" style="font-size:18px; color:var(--primary-container)">calendar_today</span>
          <input type="date" id="dateRangeStart" value="${state.selectedDateRange.start}" onchange="handleDateRangeChange()" style="border:none; background:transparent; font-size:12px; font-weight:600; color:var(--on-surface); outline:none; cursor:pointer" title="Start Date" />
          <span style="color:var(--outline); font-size:12px; font-weight:600">-</span>
          <input type="date" id="dateRangeEnd" value="${state.selectedDateRange.end}" onchange="handleDateRangeChange()" style="border:none; background:transparent; font-size:12px; font-weight:600; color:var(--on-surface); outline:none; cursor:pointer" title="End Date" />
        </div>
        <button class="btn-secondary" onclick="openCustomizeModal()">
          <span class="material-symbols-outlined">tune</span>
          Customize
        </button>
      </div>
    </div>

    ${contentBuffer}
  `;
}

// 2. Projects Tab View
function renderProjectsTab() {
  return `
    <div class="page-header">
      <div>
        <h1 class="page-title">Projects Portfolio</h1>
        <p class="page-subtitle">Detailed status, lifecycle phases, and metrics for all active projects</p>
      </div>
      <button class="btn-primary">
        <span class="material-symbols-outlined">add</span> New Project
      </button>
    </div>

    <div class="card-box">
      <div class="table-responsive">
        <table class="stitch-table">
          <thead>
            <tr><th>Project Code</th><th>Name</th><th>Lifecycle Phase</th><th>Health Status</th><th>Progress</th><th>Action</th></tr>
          </thead>
          <tbody>
            ${state.projects.map(p => `
              <tr>
                <td><strong>${p.code}</strong></td>
                <td>${p.name}</td>
                <td>${p.lifecycle_phase}</td>
                <td>
                  <span class="chip ${p.health_status==='Healthy'?'chip-success':p.health_status==='At Risk'?'chip-warning':'chip-danger'}">
                    ${p.health_status}
                  </span>
                </td>
                <td>
                  <div style="display:flex; align-items:center; gap:8px">
                    <div style="flex:1; height:8px; background:var(--surface-container-high); border-radius:4px; overflow:hidden">
                      <div style="width:${p.progress_pct}%; height:100%; background:var(--primary-container)"></div>
                    </div>
                    <span>${p.progress_pct}%</span>
                  </div>
                </td>
                <td>
                  <button class="btn-secondary" onclick="setProject('${p.code}'); state.activeTab='dashboard'; renderApp();">Select</button>
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    </div>
  `;
}

// 3. RAID Register / Risk Center Tab View
function renderRaidTab() {
  return `
    <div class="page-header">
      <div>
        <h1 class="page-title">Risk Center (RAID Register)</h1>
        <p class="page-subtitle">Active risks, assumptions, issues, and dependencies for ${state.selectedProjectCode}</p>
      </div>
      <button class="btn-primary" onclick="triggerMultiAgentWorkflow()">
        <span class="material-symbols-outlined">smart_toy</span> Run LangGraph RAID Analysis
      </button>
    </div>

    <div class="card-box">
      <div class="table-responsive">
        <table class="stitch-table">
          <thead>
            <tr><th>Category</th><th>Title & Description</th><th>Likelihood</th><th>Impact</th><th>Score</th><th>Status</th><th>Owner</th></tr>
          </thead>
          <tbody>
            ${state.raidItems.map(r => `
              <tr>
                <td>
                  <span class="chip ${r.category==='Risk'?'chip-danger':r.category==='Issue'?'chip-warning':'chip-info'}">${r.category}</span>
                </td>
                <td>
                  <strong>${r.title}</strong><br>
                  <span style="color:var(--on-surface-variant); font-size:12px">${r.description}</span>
                </td>
                <td>${r.likelihood}</td>
                <td>${r.impact}</td>
                <td><strong style="color:${r.risk_score>=70?'#dc2626':'#d97706'}">${r.risk_score}</strong></td>
                <td><span class="chip chip-info">${r.status}</span></td>
                <td>${r.owner_name}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    </div>
  `;
}

// 4. Communication Center Tab View
function renderCommsTab() {
  const pendingCount = state.emails.filter(e => e.status === 'PENDING').length;

  return `
    <div class="page-header">
      <div>
        <h1 class="page-title">Communication Center</h1>
        <p class="page-subtitle">Mandatory Human Approval workflow for AI-generated stakeholder communications</p>
      </div>
      <span class="chip chip-warning" style="font-size:13px">${pendingCount} Drafts Awaiting Approval</span>
    </div>

    <div class="card-box">
      <p style="color:var(--on-surface-variant); font-size:13px; margin-bottom:16px">
        All AI-generated emails remain in <strong>PENDING</strong> status until reviewed, edited, and explicitly APPROVED by a human. Approved communications are dispatched via Resend API to target recipient.
      </p>

      <div class="table-responsive">
        <table class="stitch-table">
          <thead>
            <tr><th>ID</th><th>Recipient Role</th><th>Target Recipient</th><th>Subject Line</th><th>Status</th><th>Action</th></tr>
          </thead>
          <tbody>
            ${state.emails.map(e => `
              <tr>
                <td>#${e.id}</td>
                <td><span class="chip chip-info">${e.recipient_role}</span></td>
                <td>linusimon@gmail.com <br><small style="color:var(--on-surface-variant)">Target: ${e.recipient_email}</small></td>
                <td><strong>${e.subject}</strong></td>
                <td>
                  <span class="chip ${e.status==='SENT'?'chip-success':e.status==='PENDING'?'chip-warning':'chip-danger'}">${e.status}</span>
                </td>
                <td>
                  ${e.status === 'PENDING' ? `
                    <button class="btn-success" onclick="openApprovalModal(${e.id})">
                      <span class="material-symbols-outlined">check_circle</span> Review & Approve
                    </button>
                  ` : `
                    <span style="color:var(--on-surface-variant); font-size:12px">${e.status} at ${e.sent_at || e.created_at}</span>
                  `}
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    </div>
  `;
}

// 5. Reports Tab View
function renderReportsTab(currentProject) {
  return `
    <div class="page-header">
      <div>
        <h1 class="page-title">Program Management Reports</h1>
        <p class="page-subtitle">Executive status reports and AI insights for ${currentProject.code}</p>
      </div>
      <button class="btn-primary" onclick="window.print()">
        <span class="material-symbols-outlined">print</span> Export Report
      </button>
    </div>

    <div class="card-box">
      <div class="card-box-title" style="margin-bottom:12px">Executive Program Summary</div>
      <p style="line-height:1.6; color:var(--on-surface)">
        Program <strong>${currentProject.name} (${currentProject.code})</strong> is currently in the <strong>${currentProject.lifecycle_phase}</strong> phase with an overall progress completion rate of <strong>${currentProject.progress_pct}%</strong>. The current program risk profile is categorized as <span class="chip chip-warning">Medium Risk</span>.
      </p>

      <div class="grid-2col" style="margin-top:20px">
        <div style="background:var(--surface-container-low); padding:16px; border-radius:8px">
          <h4 style="font-weight:700; margin-bottom:8px">Key Performance Indicators</h4>
          <ul style="padding-left:20px; line-height:1.8">
            <li>Open RAID Items: <strong>${state.raidItems.length}</strong></li>
            <li>High Severity Risks (&gt;70): <strong>${state.raidItems.filter(r => r.risk_score>=70).length}</strong></li>
            <li>Active Project Team Leads: <strong>4</strong></li>
            <li>Budget Variance: <strong>-8.5% ($1.2M)</strong></li>
          </ul>
        </div>

        <div style="background:var(--surface-container-low); padding:16px; border-radius:8px">
          <h4 style="font-weight:700; margin-bottom:8px">LangGraph AI Mitigation Summary</h4>
          <p style="font-size:13px; color:var(--on-surface-variant)">
            The multi-agent system identified third-party API integration delays as the primary bottleneck. Mitigation strategy recommends deploying mock servers and initiating parallel sprint tasks.
          </p>
        </div>
      </div>
    </div>
  `;
}

// 6. AI Assistant & Voice Chat Tab View
function renderChatTab() {
  return `
    <div class="page-header">
      <div>
        <h1 class="page-title">Multi-Modal AI Assistant</h1>
        <p class="page-subtitle">Interactive query engine with Voice STT/TTS and real-time LangGraph execution tracing</p>
      </div>
    </div>

    <div class="grid-2col">
      <div class="card-box">
        <div class="card-box-title" style="margin-bottom:16px">Interactive Query & Voice Assistant</div>

        <div style="display:flex; gap:10px; margin-bottom:16px">
          <input type="text" id="chatQueryInput" style="flex:1; padding:10px; border-radius:8px; border:1px solid var(--outline-variant)" placeholder="Ask about project risks, SOW policies, or mitigation..." value="Analyze risk for Project Orion Upgrade and generate mitigation plan" />
          <button class="btn-primary" onclick="triggerMultiAgentWorkflow()">
            <span class="material-symbols-outlined">send</span> Send
          </button>
          <button class="btn-secondary" onclick="startVoiceRecognition()">
            <span class="material-symbols-outlined">mic</span> ${state.isRecordingVoice ? 'Listening...' : 'Voice'}
          </button>
        </div>

        <div style="background:var(--surface-container-low); border:1px solid var(--outline-variant); padding:16px; border-radius:8px; min-height:180px">
          <p style="color:var(--primary-container); font-weight:bold; display:flex; align-items:center; gap:6px">
            <span class="material-symbols-outlined">smart_toy</span> AI Assistant Analysis Output
          </p>
          <p style="margin-top:10px; line-height:1.6; font-size:13px">
            Analysis completed for <strong>${state.selectedProjectCode}</strong> using Dual RAG & 3-LangGraph Workflow.<br>
            • <strong>Guardrails Check:</strong> Passed PII Masking & SQL Injection Filter.<br>
            • <strong>Primary Risk Item:</strong> Third-party API Integration Delay (Score 88 High).<br>
            • <strong>Mitigation Action:</strong> Spin up mock server to unblock sprint.<br>
            • <strong>Human Approval:</strong> Drafted stakeholder email awaiting review in Communication Center.
          </p>
        </div>
      </div>

      <!-- Real-Time Graphical Node Execution Trace -->
      <div class="card-box">
        <div class="card-box-title" style="margin-bottom:16px">Real-Time Graphical Node Execution Trace</div>
        <div class="execution-flow">
          ${state.nodeTraces.length > 0 ? state.nodeTraces.map(n => `
            <div class="node-item ${n.status==='COMPLETED'?'':'blocked'}">
              <div>
                <strong>${n.name}</strong><br>
                <small style="color:var(--on-surface-variant)">Status: ${n.status}</small>
              </div>
              <span class="chip chip-success">${n.latency_ms} ms</span>
            </div>
          `).join('') : `
            <div class="node-item">
              <div><strong>1. Data Intelligence Graph</strong><br><small style="color:var(--on-surface-variant)">Guardrails & Dual RAG Indexing</small></div>
              <span class="chip chip-success">4 ms</span>
            </div>
            <div class="node-item">
              <div><strong>2. Risk Intelligence Graph</strong><br><small style="color:var(--on-surface-variant)">RAID Rule Engine & LLM Reasoning</small></div>
              <span class="chip chip-success">0 ms</span>
            </div>
            <div class="node-item">
              <div><strong>3. Communication Graph</strong><br><small style="color:var(--on-surface-variant)">Role Tailoring & Human Approval</small></div>
            </div>
          `}
        </div>
      </div>
    </div>
  `;
}

// 7. System & Technical Admin Tab View
function renderAdminTab() {
  return `
    <div class="page-header">
      <div>
        <h1 class="page-title">Admin Console & Master Data Management</h1>
        <p class="page-subtitle">Dual RAG Databases (Static Vector Store & Unstructured GraphRAG), Master User Accounts & Audit Stream</p>
      </div>
    </div>

    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-title">MCP Server Port</div>
        <div class="kpi-value" style="color:var(--primary-container)">5001</div>
        <div class="kpi-subtext" style="color:#059669">Status: ${state.telemetry.mcp_status || 'ONLINE'}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-title">Static RAG Vector Chunks</div>
        <div class="kpi-value" style="color:#059669">21 Chunks</div>
        <div class="kpi-subtext">5 Uploaded Documents</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-title">Unstructured GraphRAG</div>
        <div class="kpi-value" style="color:var(--primary-container)">5 Graph Triples</div>
        <div class="kpi-subtext">Slack/Teams Chat Feeds in mcp.db</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-title">Master Accounts</div>
        <div class="kpi-value">6 Users</div>
        <div class="kpi-subtext">SQLite User Table</div>
      </div>
    </div>

    <!-- RAG DATABASE 1: STATIC DOCUMENT VECTOR STORE -->
    <div class="card-box" style="margin-top:20px;">
      <div class="card-box-title" style="margin-bottom:6px">1. Static Knowledge Document Vector RAG Database (backend/app/uploads/)</div>
      <p style="color:var(--on-surface-variant); font-size:12px; margin-bottom:16px;">
        Stores static policies, SOWs, and SOP manuals chunked into 128-d vector embeddings via TCSGenAIClient.
      </p>

      <div class="table-responsive" style="margin-bottom:20px;">
        <table class="stitch-table">
          <thead>
            <tr><th>Document Title</th><th>Filename</th><th>Doc Type</th><th>Size</th><th>Upload Timestamp</th></tr>
          </thead>
          <tbody>
            <tr><td><strong>Security Policy & SLA Guidelines</strong></td><td><code>security_policy.txt</code></td><td><span class="chip chip-info">Policy</span></td><td>1,420 bytes</td><td>2026-08-07</td></tr>
            <tr><td><strong>Project Orion Statement of Work</strong></td><td><code>orion_sow.txt</code></td><td><span class="chip chip-info">SOW</span></td><td>2,150 bytes</td><td>2026-08-07</td></tr>
            <tr><td><strong>RAID Threshold Escalation SOP</strong></td><td><code>risk_sop.txt</code></td><td><span class="chip chip-info">SOP</span></td><td>1,890 bytes</td><td>2026-08-07</td></tr>
            <tr><td><strong>Pegasus Core Banking Architecture</strong></td><td><code>pegasus_architecture.txt</code></td><td><span class="chip chip-info">Architecture</span></td><td>2,640 bytes</td><td>2026-08-07</td></tr>
            <tr><td><strong>Mobile Compliance & Biometric Guidelines</strong></td><td><code>mobile_compliance.txt</code></td><td><span class="chip chip-info">Compliance</span></td><td>1,780 bytes</td><td>2026-08-07</td></tr>
          </tbody>
        </table>
      </div>

      <div class="table-responsive">
        <table class="stitch-table">
          <thead>
            <tr><th>Chunk ID</th><th>Source File</th><th>Content Preview Snippet</th><th>Embedding Dim</th><th>Status</th></tr>
          </thead>
          <tbody>
            <tr><td><code>security_policy.txt_chunk_0</code></td><td>security_policy.txt</td><td><small style="color:var(--on-surface-variant)">All system communications must enforce PII redaction and TLS 1.3 encryption...</small></td><td><span class="chip chip-info">128-d</span></td><td><span class="chip chip-success">INDEXED</span></td></tr>
            <tr><td><code>orion_sow.txt_chunk_0</code></td><td>orion_sow.txt</td><td><small style="color:var(--on-surface-variant)">Project Orion Upgrade phase mobilization deliverables and vendor SLA dependencies...</small></td><td><span class="chip chip-info">128-d</span></td><td><span class="chip chip-success">INDEXED</span></td></tr>
            <tr><td><code>risk_sop.txt_chunk_0</code></td><td>risk_sop.txt</td><td><small style="color:var(--on-surface-variant)">RAID items exceeding score 70 require executive briefing within 24 hours...</small></td><td><span class="chip chip-info">128-d</span></td><td><span class="chip chip-success">INDEXED</span></td></tr>
            <tr><td><code>pegasus_architecture.txt_chunk_0</code></td><td>pegasus_architecture.txt</td><td><small style="color:var(--on-surface-variant)">Core Banking Platform specs, database connection pools, and microservice SLA metrics...</small></td><td><span class="chip chip-info">128-d</span></td><td><span class="chip chip-success">INDEXED</span></td></tr>
            <tr><td><code>mobile_compliance.txt_chunk_0</code></td><td>mobile_compliance.txt</td><td><small style="color:var(--on-surface-variant)">Biometric mobile authentication standards, regulatory guidelines, and compliance checks...</small></td><td><span class="chip chip-info">128-d</span></td><td><span class="chip chip-success">INDEXED</span></td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- RAG DATABASE 2: UNSTRUCTURED KNOWLEDGE GRAPH RAG STORE (GRAPHRAG) -->
    <div class="card-box" style="margin-top:20px;">
      <div class="card-box-title" style="margin-bottom:6px">2. Unstructured Knowledge Graph RAG Database (mcp/mcp.db -> GraphRAG)</div>
      <p style="color:var(--on-surface-variant); font-size:12px; margin-bottom:16px;">
        Ingests real-time unstructured chat/email feeds (Slack, Teams, Email logs) to extract Entity-Relationship Triples <code>(Subject) --[Predicate]--> (Object)</code>.
      </p>

      <div class="table-responsive">
        <table class="stitch-table">
          <thead>
            <tr><th>Triple ID</th><th>Subject Entity</th><th>Relationship Predicate</th><th>Object Entity</th><th>Communication Source</th><th>Category</th><th>Confidence</th></tr>
          </thead>
          <tbody>
            <tr>
              <td><code>triple_101</code></td>
              <td><strong>Amit Joshi</strong></td>
              <td><code>--[SENT_COMMUNICATION]--></code></td>
              <td><strong>Rohit Verma</strong></td>
              <td>Teams Chat Feed #104</td>
              <td><span class="chip chip-info">Handoff</span></td>
              <td><span class="chip chip-success">0.98</span></td>
            </tr>
            <tr>
              <td><code>triple_102</code></td>
              <td><strong>Third-Party Vendor API</strong></td>
              <td><code>--[IMPACTS_MILESTONE]--></code></td>
              <td><strong>Design Review</strong></td>
              <td>Slack #proj-orion-dev</td>
              <td><span class="chip chip-danger">Threat Risk</span></td>
              <td><span class="chip chip-success">0.96</span></td>
            </tr>
            <tr>
              <td><code>triple_103</code></td>
              <td><strong>Project Orion Upgrade</strong></td>
              <td><code>--[HAS_RISK_INDICATOR]--></code></td>
              <td><strong>Integration Latency</strong></td>
              <td>Incident Report Thread #42</td>
              <td><span class="chip chip-warning">RAID Factor</span></td>
              <td><span class="chip chip-success">0.95</span></td>
            </tr>
            <tr>
              <td><code>triple_104</code></td>
              <td><strong>Core Banking API</strong></td>
              <td><code>--[REQUIRES_SLA_COMPLIANCE]--></code></td>
              <td><strong>Security Policy v2.1</strong></td>
              <td>Email Log #208</td>
              <td><span class="chip chip-info">Governance</span></td>
              <td><span class="chip chip-success">0.97</span></td>
            </tr>
            <tr>
              <td><code>triple_105</code></td>
              <td><strong>Biometric Auth Service</strong></td>
              <td><code>--[DEPENDS_ON]--></code></td>
              <td><strong>OAuth 2.0 Identity Server</strong></td>
              <td>Slack #security-audit</td>
              <td><span class="chip chip-info">Dependency</span></td>
              <td><span class="chip chip-success">0.99</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Master User Accounts Table -->
    <div class="card-box" style="margin-top:20px;">
      <div class="card-box-title" style="margin-bottom:16px">SQLite Master User Accounts Table (backend/app.db -> User)</div>
      <div class="table-responsive">
        <table class="stitch-table">
          <thead>
            <tr><th>User ID</th><th>Username</th><th>Full Name</th><th>Role</th><th>Email Address</th><th>Status</th></tr>
          </thead>
          <tbody>
            <tr><td>#1</td><td><strong>rohit</strong></td><td>Rohit Verma</td><td><span class="chip chip-warning">Program Manager</span></td><td>rohit.verma@company.com</td><td><span class="chip chip-success">ACTIVE</span></td></tr>
            <tr><td>#2</td><td><strong>admin</strong></td><td>Admin User</td><td><span class="chip chip-danger">Admin</span></td><td>admin@company.com</td><td><span class="chip chip-success">ACTIVE</span></td></tr>
            <tr><td>#3</td><td><strong>amit</strong></td><td>Amit Joshi</td><td><span class="chip chip-info">Project Manager</span></td><td>amit.joshi@company.com</td><td><span class="chip chip-success">ACTIVE</span></td></tr>
            <tr><td>#4</td><td><strong>vikram</strong></td><td>Vikram Malhotra</td><td><span class="chip chip-info">Team Lead</span></td><td>vikram.m@company.com</td><td><span class="chip chip-success">ACTIVE</span></td></tr>
            <tr><td>#5</td><td><strong>priya</strong></td><td>Priya Sharma</td><td><span class="chip chip-info">Viewer</span></td><td>priya.s@company.com</td><td><span class="chip chip-success">ACTIVE</span></td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Master Projects Portfolio Table -->
    <div class="card-box" style="margin-top:20px;">
      <div class="card-box-title" style="margin-bottom:16px">SQLite Master Projects Table (backend/app.db -> Project)</div>
      <div class="table-responsive">
        <table class="stitch-table">
          <thead>
            <tr><th>ID</th><th>Code</th><th>Project Name</th><th>Lifecycle Phase</th><th>Health Status</th><th>Budget</th></tr>
          </thead>
          <tbody>
            <tr><td>#1</td><td><code>PRJ-001</code></td><td><strong>Project Orion Upgrade</strong></td><td><span class="chip chip-info">Mobilization</span></td><td><span class="chip chip-warning">At Risk</span></td><td>$2.5M</td></tr>
            <tr><td>#2</td><td><code>PRJ-002</code></td><td><strong>Core Banking Modernization</strong></td><td><span class="chip chip-info">Planning</span></td><td><span class="chip chip-success">Healthy</span></td><td>$4.2M</td></tr>
            <tr><td>#3</td><td><code>PRJ-003</code></td><td><strong>Digital Identity Platform</strong></td><td><span class="chip chip-info">Design</span></td><td><span class="chip chip-warning">At Risk</span></td><td>$1.8M</td></tr>
            <tr><td>#4</td><td><code>PRJ-004</code></td><td><strong>Cloud Infrastructure Migration</strong></td><td><span class="chip chip-info">Execution</span></td><td><span class="chip chip-danger">Critical</span></td><td>$3.5M</td></tr>
            <tr><td>#5</td><td><code>PRJ-005</code></td><td><strong>Supply Chain Analytics</strong></td><td><span class="chip chip-info">Closure</span></td><td><span class="chip chip-success">Healthy</span></td><td>$1.2M</td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Master RAID Items Table -->
    <div class="card-box" style="margin-top:20px;">
      <div class="card-box-title" style="margin-bottom:16px">SQLite Master RAID Register Table (backend/app.db -> RAIDItem)</div>
      <div class="table-responsive">
        <table class="stitch-table">
          <thead>
            <tr><th>ID</th><th>Category</th><th>Title</th><th>Risk Score</th><th>Likelihood</th><th>Impact</th><th>Status</th></tr>
          </thead>
          <tbody>
            <tr><td>#101</td><td><span class="chip chip-danger">Risk</span></td><td><strong>Third-Party Vendor API Integration Latency</strong></td><td><span class="chip chip-danger">88/100</span></td><td>4/5</td><td>5/5</td><td><span class="chip chip-warning">OPEN</span></td></tr>
            <tr><td>#102</td><td><span class="chip chip-danger">Risk</span></td><td><strong>Database Schema Migration Timeout</strong></td><td><span class="chip chip-warning">76/100</span></td><td>3/5</td><td>4/5</td><td><span class="chip chip-info">IN_REVIEW</span></td></tr>
            <tr><td>#103</td><td><span class="chip chip-info">Assumption</span></td><td><strong>Cloud Service Provider Availability SLA 99.99%</strong></td><td><span class="chip chip-info">30/100</span></td><td>1/5</td><td>2/5</td><td><span class="chip chip-success">VALIDATED</span></td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Master WBS Tasks Table -->
    <div class="card-box" style="margin-top:20px;">
      <div class="card-box-title" style="margin-bottom:16px">SQLite WBS Task Breakdown Table (backend/app.db -> Task)</div>
      <div class="table-responsive">
        <table class="stitch-table">
          <thead>
            <tr><th>ID</th><th>WBS Code</th><th>Task Name</th><th>Assignee</th><th>Priority</th><th>Progress</th><th>Story Points</th></tr>
          </thead>
          <tbody>
            <tr><td>#1</td><td><code>WBS-1.1</code></td><td><strong>Vendor API Specification Review & Mock Server Creation</strong></td><td>Amit Joshi</td><td><span class="chip chip-warning">High</span></td><td>45%</td><td>13 SP</td></tr>
            <tr><td>#2</td><td><code>WBS-1.2</code></td><td><strong>Security Policy SLA & PII Redaction Audit</strong></td><td>Vikram Malhotra</td><td><span class="chip chip-warning">High</span></td><td>90%</td><td>8 SP</td></tr>
            <tr><td>#3</td><td><code>WBS-1.3</code></td><td><strong>Database Schema Migration & Indexing</strong></td><td>Priya Sharma</td><td><span class="chip chip-info">Medium</span></td><td>20%</td><td>5 SP</td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Master Stakeholder Email Queue Table -->
    <div class="card-box" style="margin-top:20px;">
      <div class="card-box-title" style="margin-bottom:16px">SQLite Stakeholder Email Queue Table (backend/app.db -> EmailDraft)</div>
      <div class="table-responsive">
        <table class="stitch-table">
          <thead>
            <tr><th>ID</th><th>Recipient Role</th><th>Target Email</th><th>Subject Line</th><th>Status</th><th>Resend Delivery ID</th></tr>
          </thead>
          <tbody>
            <tr><td>#10</td><td><strong>Program Manager</strong></td><td><code>linusimon@gmail.com</code></td><td>Executive Briefing: Project Orion Risk Mitigation Plan</td><td><span class="chip chip-warning">PENDING</span></td><td><small style="color:var(--on-surface-variant)">Pending Human Approval</small></td></tr>
            <tr><td>#11</td><td><strong>Executive Leadership</strong></td><td><code>linusimon@gmail.com</code></td><td>Weekly Portfolio Status Report & Budget Variance</td><td><span class="chip chip-success">APPROVED</span></td><td><code>6b94665e-c26a-423a-8600-834ce457eccf</code></td></tr>
          </tbody>
        </table>
      </div>
    </div>


    <div class="card-box" style="margin-top:20px">
      <div class="card-box-title" style="margin-bottom:16px">System Security Audit Log Stream</div>
      <div class="table-responsive">
        <table class="stitch-table">
          <thead>
            <tr><th>Timestamp</th><th>User</th><th>Role</th><th>Action</th><th>Target</th><th>Details</th></tr>
          </thead>
          <tbody>
            ${state.auditLogs.map(l => `
              <tr>
                <td>${l.timestamp}</td>
                <td><strong>${l.user_name}</strong></td>
                <td>${l.user_role}</td>
                <td><span class="chip chip-info">${l.action}</span></td>
                <td>${l.target_type} #${l.target_id || ''}</td>
                <td>${l.details}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    </div>
  `;
}


// 8. Stitch Login Screen View (Requested by user)
function renderLoginTab() {
  return `
    <div class="login-split-container">
      <!-- Left Hero Banner -->
      <section class="login-left-banner">
        <div>
          <h1 style="font-size:36px; font-weight:800; tracking-tight: -0.02em">PM AI</h1>
          <p style="font-size:20px; font-weight:600; color:#b2c5ff; margin-top:8px">Program Management<br>AI Assistant</p>
        </div>

        <div style="display:flex; justify-content:center; align-items:center; margin:32px 0">
          <div style="width:280px; height:280px; background:url('https://lh3.googleusercontent.com/aida-public/AB6AXuAKSjthA8wIZ6_-QpIsv3LUnpQ_v3cSC3ZrTIkbzobDajUEiaVb9sAF7r4DfHbfh86vUgoT61rl1MSIfNNPDYOzunuFreDViVzpfuxRW3a376MsCu1WgcPLwkxyAOU3O1zXJI43acWJ8m2osibESbC-uzJUzRJ5Z92fiya2kaKA7sVgquh4eOqq6aZXtkFu0lupWyhpAL-g94Efm2tf1HlEtLYg3irxDTWaNB_q5KDM1S8hnhkd2ZXT') center/contain no-repeat"></div>
        </div>

        <div>
          <h2 style="font-size:20px; font-weight:600; margin-bottom:4px">AI-Powered Risk Analysis</h2>
          <p style="font-size:14px; color:#b2c5ff">and Stakeholder Communication</p>
        </div>
      </section>

      <!-- Right Login Form Card -->
      <section class="login-right-form">
        <div class="login-form-box">
          <div style="margin-bottom:32px">
            <h2 style="font-size:24px; font-weight:700; color:var(--on-surface); margin-bottom:6px">Welcome Back!</h2>
            <p style="color:var(--on-surface-variant); font-size:14px">Sign in to continue to your account</p>
          </div>

          <form onsubmit="event.preventDefault(); state.activeTab='dashboard'; renderApp();">
            <div class="form-group">
              <label for="email">Email Address</label>
              <div class="input-with-icon">
                <span class="material-symbols-outlined">mail</span>
                <input type="email" id="email" placeholder="Enter your email" value="rohit@company.com" required />
              </div>
            </div>

            <div class="form-group">
              <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px">
                <label for="password" style="margin-bottom:0">Password</label>
                <a href="#" style="font-size:12px; color:var(--primary-container); text-decoration:none; font-weight:600">Forgot Password?</a>
              </div>
              <div class="input-with-icon">
                <span class="material-symbols-outlined">lock</span>
                <input type="password" id="password" placeholder="Enter your password" value="••••••••" required />
              </div>
            </div>

            <div style="margin-top:24px">
              <button type="submit" class="btn-primary" style="width:100%; justify-content:center; padding:12px">
                Sign In
              </button>
            </div>

            <div style="display:flex; align-items:center; margin:20px 0">
              <div style="flex:1; border-top:1px solid var(--outline-variant)"></div>
              <span style="margin:0 12px; font-size:12px; color:var(--outline)">or</span>
              <div style="flex:1; border-top:1px solid var(--outline-variant)"></div>
            </div>

            <button type="button" class="btn-secondary" onclick="state.activeTab='dashboard'; renderApp();" style="width:100%; justify-content:center; padding:12px">
              <span class="material-symbols-outlined">shield_person</span> Sign in with SSO
            </button>
          </form>
        </div>

        <div style="margin-top:40px; text-align:center">
          <p style="font-size:12px; color:var(--outline)">© 2025 PM AI Assistant. All rights reserved.</p>
        </div>
      </section>
    </div>
  `;
}

// Render Universal Collapsible Agent Execution Log & Telemetry Panel
function renderCollapsibleTracePanel() {
  return `
    <div class="collapsible-trace-box">
      <div class="trace-bar-header" onclick="state.isTraceExpanded = !state.isTraceExpanded; renderApp();">
        <div class="trace-bar-title">
          <span class="material-symbols-outlined" style="color:var(--tertiary-fixed-dim)">settings_suggest</span>
          <span>LangGraph Agent Execution Log & Telemetry Trace (Active Project: ${state.selectedProjectCode})</span>
        </div>
        <div class="trace-bar-badges">
          <span class="chip chip-success">Confidence: 95%</span>
          <span class="chip chip-success">Latency: 18 ms</span>
          <span class="chip chip-info">Tokens: 1,590 ($0.00318)</span>
          <span style="color:#ffffff; font-weight:bold">${state.isTraceExpanded ? '▲ Collapse' : '▼ Expand'}</span>
        </div>
      </div>

      ${state.isTraceExpanded ? `
        <div class="trace-body-grid">
          <div class="trace-card">
            <div class="trace-card-title">
              <span>Agents & LangGraphs Called</span>
              <span class="chip chip-success">6 Active</span>
            </div>
            <div class="trace-card-content">
              • <strong>LangGraph Supervisor Agent</strong> (Orchestrator)<br>
              • <strong>1. Data Intelligence Graph</strong> (Guardrails & Dual RAG)<br>
              • <strong>2. Risk Intelligence Graph</strong> (RAID Engine & Reasoning)<br>
              • <strong>3. Communication Graph</strong> (Audience Tailoring & Approval)<br>
              • <strong>Reflection Agent</strong> (Groundedness Check: 0.96)<br>
              • <strong>Memory Agent</strong> (Conversational Context)
            </div>
          </div>

          <div class="trace-card">
            <div class="trace-card-title">
              <span>LLM & Endpoint Config</span>
              <span class="chip chip-success">TCS GenAI API</span>
            </div>
            <div class="trace-card-content">
              • <strong>Model:</strong> gemini-1.5-pro<br>
              • <strong>Endpoint:</strong> https://genailab.tcs.in/api/v1<br>
              • <strong>Hyperparameters:</strong> Temp=0.2, Top-P=0.95, Max Tokens=2048<br>
              • <strong>Token Usage:</strong> 1,250 Prompt / 340 Completion (1,590 Total)<br>
              • <strong>Est Cost:</strong> $0.00318 USD / Request
            </div>
          </div>

          <div class="trace-card">
            <div class="trace-card-title">
              <span>Guardrails & PII Redaction</span>
              <span class="chip chip-success">PASSED</span>
            </div>
            <div class="trace-card-content">
              • <strong>Prompt Injection Check:</strong> PASSED (0 Attacks)<br>
              • <strong>SQL Injection Check:</strong> PASSED (Sanitized)<br>
              • <strong>Domain Relevance Score:</strong> 0.96 / 1.00<br>
              • <strong>PII Masking Result:</strong><br>
                - <span class="chip chip-danger">[PII: EMAIL_REDACTED]</span><br>
                - <span class="chip chip-danger">[PII: SSN_REDACTED]</span>
            </div>
          </div>

          <div class="trace-card">
            <div class="trace-card-title">
              <span>MCP Tools Executed (Port 5001)</span>
              <span class="chip chip-success">FastMCP Online</span>
            </div>
            <div class="trace-card-content">
              • <code>mcp_query_project_plans</code> (Parsed XML/JSON WBS)<br>
              • <code>mcp_read_communication_logs</code> (Teams/Slack feeds)<br>
              • <code>mcp_fetch_risk_register</code> (External Threat Feeds)<br>
              • <code>mcp_update_mitigation_action</code> (Action Checklist)
            </div>
          </div>

          <div class="trace-card">
            <div class="trace-card-title">
              <span>Dual RAG & Knowledge Graph Context</span>
              <span class="chip chip-info">Static + GraphRAG</span>
            </div>
            <div class="trace-card-content">
              • <strong>Static Document RAG:</strong> 21 Policy & SOW Chunks Indexed<br>
              • <strong>Knowledge Graph Triples:</strong><br>
                - <code>(Amit Joshi) --[SENT_MESSAGE_TO]--&gt; (Rohit Verma)</code><br>
                - <code>(Vendor API) --[IMPACTS_MILESTONE]--&gt; (Design Review)</code><br>
                - <code>(Project Orion) --[HAS_RISK]--&gt; (Schedule Delay)</code>
            </div>
          </div>
        </div>
      ` : ''}
    </div>
  `;
}

// Render Human Approval Modal Overlay
function renderHumanApprovalModal() {
  const e = state.selectedEmailForApproval;
  return `
    <div class="modal-backdrop">
      <div class="modal-window">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px">
          <h3 style="font-size:18px; font-weight:700; color:var(--on-surface)">Human Approval Interface (Draft #${e.id})</h3>
          <button class="btn-secondary" onclick="closeApprovalModal()" style="padding:4px 8px">✕</button>
        </div>

        <p style="color:var(--on-surface-variant); font-size:12px; margin-bottom:16px">
          Review and edit AI-generated copy before approving email dispatch to <strong>linusimon@gmail.com</strong>.
        </p>

        <label style="font-size:12px; font-weight:700; color:var(--on-surface)">Recipient Role:</label>
        <input type="text" value="${e.recipient_role}" disabled style="background:var(--surface-container-low)" />

        <label style="font-size:12px; font-weight:700; color:var(--on-surface)">Subject Line:</label>
        <input type="text" id="editSubject" value="${e.subject}" />

        <label style="font-size:12px; font-weight:700; color:var(--on-surface)">Email Body Content:</label>
        <textarea id="editBody" rows="8">${e.body}</textarea>

        <div style="display:flex; justify-content:flex-end; gap:12px; margin-top:16px">
          <button class="btn-secondary" onclick="closeApprovalModal()">Cancel</button>
          <button class="btn-success" onclick="approveEmail()">
            <span class="material-symbols-outlined">send</span> Approve & Dispatch via Resend
          </button>
        </div>
      </div>
    </div>
  `;
}

// Render Dashboard Grid Customizer Modal Overlay
function renderCustomizeModal() {
  const widgetTitles = {
    kpis: '5 KPI Metrics Overview Cards Row',
    heatmap: '5x5 Risk Heatmap Matrix',
    breakdown: 'Project Phase Breakdown Table',
    flowchart: 'Critical Path Dependency Flowchart'
  };

  return `
    <div class="modal-backdrop">
      <div class="modal-window">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px">
          <h3 style="font-size:18px; font-weight:700; color:var(--on-surface)">Customize Dashboard Layout</h3>
          <button class="btn-secondary" onclick="closeCustomizeModal()" style="padding:4px 8px">✕</button>
        </div>

        <p style="color:var(--on-surface-variant); font-size:12px; margin-bottom:16px">
          Rearrange widget cards or toggle visibility to personalize your Program Manager workspace layout.
        </p>

        <div style="display:flex; flex-direction:column; gap:10px; margin-bottom:20px">
          ${state.dashboardWidgetOrder.map((key, idx) => {
            const isVisible = state.widgetVisibility[key];
            return `
              <div style="display:flex; align-items:center; justify-content:space-between; background:var(--surface-container-low); padding:10px 14px; border-radius:8px; border:1px solid var(--outline-variant)">
                <div style="display:flex; align-items:center; gap:10px">
                  <span class="material-symbols-outlined" style="color:var(--outline)">drag_indicator</span>
                  <span style="font-size:13px; font-weight:700; color:var(--on-surface)">${widgetTitles[key]}</span>
                </div>

                <div style="display:flex; align-items:center; gap:6px">
                  <button class="btn-secondary" onclick="moveWidgetUp(${idx})" ${idx === 0 ? 'disabled' : ''} style="padding:4px 8px; font-size:11px" title="Move Up">▲</button>
                  <button class="btn-secondary" onclick="moveWidgetDown(${idx})" ${idx === state.dashboardWidgetOrder.length - 1 ? 'disabled' : ''} style="padding:4px 8px; font-size:11px" title="Move Down">▼</button>
                  <button class="${isVisible ? 'btn-primary' : 'btn-secondary'}" onclick="toggleWidgetVisibility('${key}')" style="padding:4px 10px; font-size:11px">
                    ${isVisible ? 'Visible' : 'Hidden'}
                  </button>
                </div>
              </div>
            `;
          }).join('')}
        </div>

        <div style="display:flex; justify-content:space-between; align-items:center">
          <button class="btn-secondary" onclick="resetDashboardLayout()">Reset Default Layout</button>
          <button class="btn-primary" onclick="closeCustomizeModal()">Done & Save</button>
        </div>
      </div>
    </div>
  `;
}

// DOM Initialization
document.addEventListener('DOMContentLoaded', initApp);
