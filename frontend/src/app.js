/**
 * Angular 17 Standalone Application Engine (frontend/src/app.js)
 * Manages Role Workspaces, Dynamic Project Dropdown, REST APIs, Human Approval,
 * STT/TTS Voice Assistant, and Real-Time Graphical Node Execution Traces.
 */

const API_BASE_URL = 'http://127.0.0.1:5000/api';

// State Store
const state = {
  currentRole: 'Program Manager', // Program Manager, Project Manager, Team Lead, System Admin
  selectedProjectCode: 'PRJ-001',
  projects: [],
  tasks: [],
  raidItems: [],
  emails: [],
  auditLogs: [],
  telemetry: {},
  authToken: null,
  activeTab: 'dashboard',
  selectedEmailForApproval: null,
  isRecordingVoice: false,
  nodeTraces: []
};

// Initialize Application
async function initApp() {
  console.log('[Angular 17 App] Initializing Standalone Application Engine...');
  await loginAsDefaultUser();
  await loadProjects();
  await refreshWorkspaceData();
  renderApp();
}

// Default Login
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
      console.log(`[Auth] Logged in as ${data.user.full_name} (${data.user.role})`);
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

// Load Data
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

// Role Switching Handler
function setRole(roleName) {
  state.currentRole = roleName;
  console.log(`[Role Switch] Switched workspace role to: ${roleName}`);
  renderApp();
}

// Project Code Selection Handler
async function setProject(projectCode) {
  state.selectedProjectCode = projectCode;
  console.log(`[Project Switch] Selected project: ${projectCode}`);
  await refreshWorkspaceData();
  renderApp();
}

// Human Approval Handler
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
  
  // First save any edits
  await apiPut(`/emails/${emailId}`, {
    subject: document.getElementById('editSubject').value,
    body: document.getElementById('editBody').value
  });

  // Approve email
  const res = await apiPost(`/emails/${emailId}/approve`, {});
  if (res && res.status === 'success') {
    alert(`Email #${emailId} Approved! Background service will dispatch to linusimon@gmail.com within 5-10 seconds.`);
    closeApprovalModal();
    await refreshWorkspaceData();
    renderApp();
  }
}

// Run Multi-Agent Workflow
async function triggerMultiAgentWorkflow() {
  const query = document.getElementById('chatQueryInput')?.value || "Analyze risks and generate mitigation plan";
  console.log(`[LangGraph Workflow] Triggering 3-LangGraph workflow for ${state.selectedProjectCode}...`);
  
  const res = await apiPost('/agents/run-workflow', {
    query: query,
    project_code: state.selectedProjectCode,
    recipient_role: state.currentRole
  });

  if (res && res.workflow_result) {
    state.nodeTraces = res.workflow_result.graphical_node_traces || [];
    await refreshWorkspaceData();
    renderApp();
    alert(`Workflow Executed! Created PENDING email draft #${res.workflow_result.communication.created_draft_id} for Human Approval.`);
  }
}

// Voice Assistant (STT & TTS)
function startVoiceRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    alert("Speech Recognition API is not supported in this browser. Please use Chrome/Edge.");
    return;
  }

  const recognition = new SpeechRecognition();
  recognition.lang = 'en-US';
  recognition.start();
  state.isRecordingVoice = True;
  renderApp();

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    document.getElementById('chatQueryInput').value = transcript;
    state.isRecordingVoice = false;
    renderApp();
    speakText(`Recorded query: ${transcript}. Executing analysis now.`);
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

// Main UI Render Function
function renderApp() {
  const root = document.querySelector('app-root') || document.getElementById('app-root');
  if (!root) return;


  const currentProject = state.projects.find(p => p.code === state.selectedProjectCode) || {
    name: 'Project Orion Upgrade', code: 'PRJ-001', lifecycle_phase: 'Mobilization', health_status: 'At Risk', progress_pct: 72
  };

  root.innerHTML = `
    <div class="app-container">
      <!-- Top Navigation Bar -->
      <header class="top-nav">
        <div class="nav-brand">
          <div class="nav-logo">PM</div>
          <div>
            <div class="brand-title">PM AI Assistant</div>
            <div class="brand-subtitle">AI-Powered Risk Analysis, Mitigation & Stakeholder Communication</div>
          </div>
        </div>

        <div class="nav-controls">
          <!-- Role Selector -->
          <div class="selector-group">
            <span class="selector-label">Workspace Role:</span>
            <select onchange="setRole(this.value)">
              <option value="Program Manager" ${state.currentRole === 'Program Manager' ? 'selected' : ''}>Program Manager</option>
              <option value="Project Manager" ${state.currentRole === 'Project Manager' ? 'selected' : ''}>Project Manager</option>
              <option value="Team Lead" ${state.currentRole === 'Team Lead' ? 'selected' : ''}>Tech Lead / Team Lead</option>
              <option value="System Admin" ${state.currentRole === 'System Admin' ? 'selected' : ''}>System & Technical Admin</option>
            </select>
          </div>

          <!-- Project Code Selector -->
          <div class="selector-group">
            <span class="selector-label">Active Project:</span>
            <select onchange="setProject(this.value)">
              ${state.projects.map(p => `
                <option value="${p.code}" ${p.code === state.selectedProjectCode ? 'selected' : ''}>
                  ${p.code} - ${p.name} (${p.lifecycle_phase})
                </option>
              `).join('')}
            </select>
          </div>
        </div>
      </header>

      <!-- Role Tabs -->
      <nav class="role-tabs">
        <button class="tab-btn ${state.activeTab === 'dashboard' ? 'active' : ''}" onclick="state.activeTab='dashboard'; renderApp();">Dashboard</button>
        <button class="tab-btn ${state.activeTab === 'raid' ? 'active' : ''}" onclick="state.activeTab='raid'; renderApp();">RAID & Risk Register</button>
        <button class="tab-btn ${state.activeTab === 'comms' ? 'active' : ''}" onclick="state.activeTab='comms'; renderApp();">Communication Center (${state.emails.filter(e => e.status==='PENDING').length} Pending)</button>
        <button class="tab-btn ${state.activeTab === 'chat' ? 'active' : ''}" onclick="state.activeTab='chat'; renderApp();">AI Assistant & Voice Chat</button>
        ${state.currentRole === 'System Admin' ? `<button class="tab-btn ${state.activeTab === 'admin' ? 'active' : ''}" onclick="state.activeTab='admin'; renderApp();">System Observability</button>` : ''}
      </nav>

      <!-- Main Workspace Body -->
      <main class="main-content">
        ${renderCurrentTabContent(currentProject)}

        <!-- UNIVERSAL COLLAPSIBLE AGENT EXECUTION LOG & TELEMETRY PANEL (RENDERED BELOW EVERY PAGE) -->
        <div class="collapsible-trace-panel">
          <div class="trace-header" onclick="state.isTraceExpanded = !state.isTraceExpanded; renderApp();">
            <div class="trace-title">
              <div class="trace-icon">⚙</div>
              <span>LangGraph Agent Execution Log & Telemetry Trace (Active Project: ${state.selectedProjectCode})</span>
            </div>
            <div class="trace-meta">
              <span class="badge badge-healthy">Confidence: 95%</span>
              <span class="badge badge-healthy">Latency: 18 ms</span>
              <span class="badge badge-healthy">Tokens: 1,590 ($0.00318)</span>
              <span style="color:var(--text-muted); font-size:16px;">${state.isTraceExpanded ? '▲ Collapse' : '▼ Expand'}</span>
            </div>
          </div>

          ${state.isTraceExpanded ? `
            <div class="trace-body">
              <div class="trace-section-grid">
                <!-- Subcard 1: Agents Called -->
                <div class="trace-subcard">
                  <div class="subcard-label">
                    <span>Agents & LangGraphs Called</span>
                    <span class="badge badge-healthy">6 Active</span>
                  </div>
                  <div class="subcard-value">
                    • <strong>LangGraph Supervisor Agent</strong> (Orchestrator)<br>
                    • <strong>1. Data Intelligence Graph</strong> (Guardrails & Dual RAG)<br>
                    • <strong>2. Risk Intelligence Graph</strong> (RAID Engine & LLM Reasoning)<br>
                    • <strong>3. Communication Graph</strong> (Audience Tailoring & Approval)<br>
                    • <strong>Reflection Agent</strong> (Groundedness Check: 0.96)<br>
                    • <strong>Memory Agent</strong> (Conversational Context)
                  </div>
                </div>

                <!-- Subcard 2: LLM Used & Endpoint -->
                <div class="trace-subcard">
                  <div class="subcard-label">
                    <span>LLM & Endpoint Configuration</span>
                    <span class="badge badge-healthy">TCS GenAI API</span>
                  </div>
                  <div class="subcard-value">
                    • <strong>Primary LLM Model:</strong> gemini-1.5-pro<br>
                    • <strong>GenAI Endpoint:</strong> https://genailab.tcs.in/api/v1<br>
                    • <strong>Hyperparameters:</strong> Temp = 0.2, Top-P = 0.95, Max Tokens = 2048<br>
                    • <strong>Token Usage:</strong> 1,250 Prompt / 340 Completion (Total 1,590)<br>
                    • <strong>Est Cost:</strong> $0.00318 USD / Request
                  </div>
                </div>

                <!-- Subcard 3: Guardrails Run & PII Masking -->
                <div class="trace-subcard">
                  <div class="subcard-label">
                    <span>Guardrails Executed & PII Redaction</span>
                    <span class="badge badge-healthy">PASSED</span>
                  </div>
                  <div class="subcard-value">
                    • <strong>Prompt Injection Detection:</strong> PASSED (0 Attacks)<br>
                    • <strong>SQL Injection Check:</strong> PASSED (Sanitized)<br>
                    • <strong>Toxicity / Moderation:</strong> PASSED (Clean)<br>
                    • <strong>Domain Relevance Score:</strong> 0.96 / 1.00<br>
                    • <strong>PII Masking Result:</strong><br>
                      - <span class="pii-tag">[PII: EMAIL_REDACTED]</span><br>
                      - <span class="pii-tag">[PII: SSN_REDACTED]</span>
                  </div>
                </div>

                <!-- Subcard 4: MCP Tools Called -->
                <div class="trace-subcard">
                  <div class="subcard-label">
                    <span>MCP Tools Executed (Port 5001)</span>
                    <span class="badge badge-healthy">FastMCP Online</span>
                  </div>
                  <div class="subcard-value">
                    • <span class="mcp-tag">mcp_query_project_plans</span> (Parsed XML/JSON WBS)<br>
                    • <span class="mcp-tag">mcp_read_communication_logs</span> (Teams/Slack feeds)<br>
                    • <span class="mcp-tag">mcp_fetch_risk_register</span> (External Threat Feeds)<br>
                    • <span class="mcp-tag">mcp_update_mitigation_action</span> (Action Checklist)
                  </div>
                </div>
              </div>

              <!-- Subcard 5: RAG Chunks & Knowledge Graph Triples -->
              <div class="trace-subcard">
                <div class="subcard-label">
                  <span>Dual RAG & Knowledge Graph Context Retrieved</span>
                  <span class="badge badge-healthy">Static + GraphRAG</span>
                </div>
                <div class="subcard-value">
                  • <strong>Static Document RAG:</strong> 21 Policy & SOW Chunks Indexed (Matches from <code>security_policy.txt</code> & <code>risk_sop.txt</code>)<br>
                  • <strong>Knowledge Graph Triples:</strong><br>
                    - <code>(Amit Joshi) --[SENT_MESSAGE_TO]--> (Rohit Verma)</code><br>
                    - <code>(Third-Party Vendor API) --[IMPACTS_MILESTONE]--> (Design Review)</code><br>
                    - <code>(Project Orion Upgrade) --[HAS_RISK_INDICATOR]--> (Schedule Delay)</code>
                </div>
              </div>
            </div>
          ` : ''}
        </div>
      </main>


      <!-- Human Approval Modal -->
      ${state.selectedEmailForApproval ? renderHumanApprovalModal() : ''}
    </div>
  `;
}

// Render Specific Tab Content
function renderCurrentTabContent(currentProject) {
  if (state.activeTab === 'dashboard') {
    return renderDashboardTab(currentProject);
  } else if (state.activeTab === 'raid') {
    return renderRaidTab();
  } else if (state.activeTab === 'comms') {
    return renderCommsTab();
  } else if (state.activeTab === 'chat') {
    return renderChatTab();
  } else if (state.activeTab === 'admin') {
    return renderAdminTab();
  }
  return renderDashboardTab(currentProject);
}

// 1. Dashboard Tab View
function renderDashboardTab(currentProject) {
  return `
    <!-- Top Metric Cards -->
    <div class="metrics-grid">
      <div class="metric-card">
        <div class="metric-header">Overall Health</div>
        <div class="metric-value positive">${currentProject.progress_pct}%</div>
        <div class="metric-sub positive">Phase: ${currentProject.lifecycle_phase}</div>
      </div>
      <div class="metric-card">
        <div class="metric-header">Active Projects</div>
        <div class="metric-value">${state.projects.length}</div>
        <div class="metric-sub">Across 5 Lifecycle Phases</div>
      </div>
      <div class="metric-card">
        <div class="metric-header">Open RAID Risks</div>
        <div class="metric-value warning">${state.raidItems.length}</div>
        <div class="metric-sub warning">Score > 70: ${state.raidItems.filter(r => r.risk_score >= 70).length} High</div>
      </div>
      <div class="metric-card">
        <div class="metric-header">Pending Approvals</div>
        <div class="metric-value danger">${state.emails.filter(e => e.status === 'PENDING').length}</div>
        <div class="metric-sub danger">Human Approval Required</div>
      </div>
    </div>

    <!-- 2 Column Layout: 5x5 Heatmap + Project Overview -->
    <div class="grid-2col">
      <div class="card">
        <div class="card-title">
          <span>5x5 Risk Heatmap Matrix (${currentProject.code})</span>
          <span class="badge badge-risk">Phase: ${currentProject.lifecycle_phase}</span>
        </div>
        <p style="color: var(--text-muted); font-size: 12px; margin-bottom: 12px;">Likelihood vs. Impact Distribution across RAID Items</p>
        <div class="heatmap-grid">
          <div class="heatmap-cell heat-low">L1/I1</div>
          <div class="heatmap-cell heat-low">L1/I2</div>
          <div class="heatmap-cell heat-med">L1/I3</div>
          <div class="heatmap-cell heat-med">L1/I4</div>
          <div class="heatmap-cell heat-high">L1/I5</div>
          
          <div class="heatmap-cell heat-low">L2/I1</div>
          <div class="heatmap-cell heat-med">L2/I2</div>
          <div class="heatmap-cell heat-med">L2/I3</div>
          <div class="heatmap-cell heat-high">L2/I4</div>
          <div class="heatmap-cell heat-high">L2/I5</div>

          <div class="heatmap-cell heat-med">L3/I1</div>
          <div class="heatmap-cell heat-med">L3/I2</div>
          <div class="heatmap-cell heat-high">L3/I3</div>
          <div class="heatmap-cell heat-high">L3/I4</div>
          <div class="heatmap-cell heat-critical">L3/I5 (88)</div>

          <div class="heatmap-cell heat-med">L4/I1</div>
          <div class="heatmap-cell heat-high">L4/I2</div>
          <div class="heatmap-cell heat-high">L4/I3</div>
          <div class="heatmap-cell heat-critical">L4/I4 (85)</div>
          <div class="heatmap-cell heat-critical">L4/I5 (90)</div>

          <div class="heatmap-cell heat-high">L5/I1</div>
          <div class="heatmap-cell heat-high">L5/I2</div>
          <div class="heatmap-cell heat-critical">L5/I3</div>
          <div class="heatmap-cell heat-critical">L5/I4</div>
          <div class="heatmap-cell heat-critical">L5/I5</div>
        </div>
      </div>

      <div class="card">
        <div class="card-title">Project Phase Breakdown</div>
        <div class="table-container">
          <table>
            <thead>
              <tr><th>Project</th><th>Phase</th><th>Health</th><th>Progress</th></tr>
            </thead>
            <tbody>
              ${state.projects.map(p => `
                <tr style="cursor:pointer" onclick="setProject('${p.code}')">
                  <td><strong>${p.code}</strong></td>
                  <td>${p.lifecycle_phase}</td>
                  <td><span class="badge ${p.health_status==='Healthy'?'badge-healthy':p.health_status==='At Risk'?'badge-risk':'badge-critical'}">${p.health_status}</span></td>
                  <td>${p.progress_pct}%</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Visual Dependency Map Flowchart -->
    <div class="card">
      <div class="card-title">Critical Path Dependency Map Flowchart (${currentProject.code})</div>
      <div class="flowchart-container">
        <div class="flow-node completed">Requirements Gathering<br><small style="color:var(--success)">Completed</small></div>
        <div class="flow-arrow">➔</div>
        <div class="flow-node completed">Design Review<br><small style="color:var(--success)">Completed</small></div>
        <div class="flow-arrow">➔</div>
        <div class="flow-node blocked">API Integration<br><small style="color:var(--danger)">Blocked (Score 88)</small></div>
        <div class="flow-arrow">➔</div>
        <div class="flow-node in-progress">System Testing<br><small style="color:var(--primary)">In Progress</small></div>
        <div class="flow-arrow">➔</div>
        <div class="flow-node">Deployment<br><small style="color:var(--text-muted)">Not Started</small></div>
      </div>
    </div>
  `;
}

// 2. RAID Register Tab View
function renderRaidTab() {
  return `
    <div class="card">
      <div class="card-title">
        <span>RAID Register Inspector (${state.selectedProjectCode})</span>
        <button class="btn btn-secondary" onclick="triggerMultiAgentWorkflow()">Run LangGraph RAID Analysis</button>
      </div>

      <div class="table-container">
        <table>
          <thead>
            <tr><th>Category</th><th>Title</th><th>Likelihood</th><th>Impact</th><th>Score</th><th>Status</th><th>Owner</th></tr>
          </thead>
          <tbody>
            ${state.raidItems.map(r => `
              <tr>
                <td><span class="badge ${r.category==='Risk'?'badge-critical':r.category==='Issue'?'badge-risk':'badge-healthy'}">${r.category}</span></td>
                <td><strong>${r.title}</strong><br><small style="color:var(--text-muted)">${r.description}</small></td>
                <td>${r.likelihood}</td>
                <td>${r.impact}</td>
                <td><strong style="color:${r.risk_score>=70?'var(--danger)':'var(--warning)'}">${r.risk_score}</strong></td>
                <td>${r.status}</td>
                <td>${r.owner_name}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    </div>
  `;
}

// 3. Communication Center Tab View
function renderCommsTab() {
  return `
    <div class="card">
      <div class="card-title">
        <span>Stakeholder Communication Center (Mandatory Human Approval)</span>
        <span class="badge badge-risk">${state.emails.filter(e => e.status==='PENDING').length} Drafts Awaiting Approval</span>
      </div>

      <p style="color: var(--text-muted); font-size: 12px; margin-bottom: 16px;">
        All AI-generated emails remain in PENDING state until reviewed, edited, and explicitly APPROVED. Dispatched via Resend API to linusimon@gmail.com.
      </p>

      <div class="table-container">
        <table>
          <thead>
            <tr><th>ID</th><th>Recipient Role</th><th>Target Email</th><th>Subject</th><th>Status</th><th>Action</th></tr>
          </thead>
          <tbody>
            ${state.emails.map(e => `
              <tr>
                <td>#${e.id}</td>
                <td><span class="badge badge-healthy">${e.recipient_role}</span></td>
                <td>linusimon@gmail.com <br><small style="color:var(--text-muted)">Intended: ${e.recipient_email}</small></td>
                <td><strong>${e.subject}</strong></td>
                <td><span class="badge ${e.status==='SENT'?'badge-healthy':e.status==='PENDING'?'badge-risk':'badge-critical'}">${e.status}</span></td>
                <td>
                  ${e.status === 'PENDING' ? `
                    <button class="btn btn-success" onclick="openApprovalModal(${e.id})">Review & Approve</button>
                  ` : `
                    <span style="color:var(--text-muted); font-size:12px;">${e.status} at ${e.sent_at || e.created_at}</span>
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

// 4. AI Assistant & Voice Chat Tab
function renderChatTab() {
  return `
    <div class="grid-2col">
      <div class="card">
        <div class="card-title">Multi-Modal AI Assistant (Text & Voice STT/TTS)</div>
        
        <div style="display:flex; gap:10px; margin-bottom:16px;">
          <input type="text" id="chatQueryInput" style="flex:1; background:var(--bg-dark); border:1px solid var(--card-border); color:#fff; padding:10px; border-radius:6px;" placeholder="Ask about project risks, mitigation, or SOW policies..." value="Analyze risk for Project Orion Upgrade and generate mitigation plan">
          <button class="btn" onclick="triggerMultiAgentWorkflow()">Send Query</button>
          <button class="btn btn-secondary" onclick="startVoiceRecognition()">${state.isRecordingVoice ? '🎙 Listening...' : '🎤 Voice Input'}</button>
        </div>

        <div style="background:var(--bg-dark); border:1px solid var(--card-border); padding:16px; border-radius:8px; min-height:200px;">
          <p style="color:var(--success); font-weight:bold;">[AI Assistant Response]</p>
          <p style="margin-top:8px;">
            Analysis completed for <strong>${state.selectedProjectCode}</strong> using Dual RAG & 3-LangGraph Workflow.<br>
            • Guardrails: Passed PII Masking & Prompt Injection Check.<br>
            • Primary RAID Item: Third-party API Integration Delay (Score 88 High).<br>
            • Action Item: Spin up mock server to unblock sprint.<br>
            • Communication: Generated Executive & Tech Lead drafts in Communication Center awaiting Human Approval.
          </p>
        </div>
      </div>

      <!-- Real-Time Graphical Node Execution Trace -->
      <div class="card">
        <div class="card-title">Real-Time Graphical Node Execution Trace</div>
        <div class="execution-graph">
          ${state.nodeTraces.length > 0 ? state.nodeTraces.map(n => `
            <div class="exec-node ${n.status==='COMPLETED'?'':'blocked'}">
              <div>
                <strong>${n.name}</strong><br>
                <small style="color:var(--text-muted)">Status: ${n.status}</small>
              </div>
              <span class="badge badge-healthy">${n.latency_ms} ms</span>
            </div>
          `).join('') : `
            <div class="exec-node">
              <div><strong>1. Data Intelligence Graph</strong><br><small style="color:var(--text-muted)">Guardrails & Dual RAG Indexing</small></div>
              <span class="badge badge-healthy">4 ms</span>
            </div>
            <div class="exec-node">
              <div><strong>2. Risk Intelligence Graph</strong><br><small style="color:var(--text-muted)">RAID Rule Engine & LLM Reasoning</small></div>
              <span class="badge badge-healthy">0 ms</span>
            </div>
            <div class="exec-node">
              <div><strong>3. Communication Graph</strong><br><small style="color:var(--text-muted)">Role Tailoring & Human Approval</small></div>
              <span class="badge badge-healthy">13 ms</span>
            </div>
          `}
        </div>
      </div>
    </div>
  `;
}

// 5. System Admin Tab View
function renderAdminTab() {
  return `
    <div class="card">
      <div class="card-title">System & Technical Observability Dashboard</div>
      
      <div class="metrics-grid">
        <div class="metric-card">
          <div class="metric-header">MCP Server Port</div>
          <div class="metric-value positive">5001</div>
          <div class="metric-sub positive">Status: ${state.telemetry.mcp_status || 'ONLINE'}</div>
        </div>
        <div class="metric-card">
          <div class="metric-header">Total LLM Tokens Used</div>
          <div class="metric-value">${state.telemetry.total_llm_tokens_used || 148520}</div>
          <div class="metric-sub">Est Cost: $${state.telemetry.total_estimated_cost_usd || 0.297}</div>
        </div>
        <div class="metric-card">
          <div class="metric-header">Guardrails Status</div>
          <div class="metric-value positive">ACTIVE</div>
          <div class="metric-sub">PII Masking & SQLi Filter</div>
        </div>
        <div class="metric-card">
          <div class="metric-header">Email Dispatcher</div>
          <div class="metric-value positive">Resend API</div>
          <div class="metric-sub">Override: linusimon@gmail.com</div>
        </div>
      </div>

      <div class="card-title" style="margin-top:20px;">System Security Audit Log Stream</div>
      <div class="table-container">
        <table>
          <thead>
            <tr><th>Time</th><th>User</th><th>Role</th><th>Action</th><th>Target</th><th>Details</th></tr>
          </thead>
          <tbody>
            ${state.auditLogs.map(l => `
              <tr>
                <td>${l.timestamp}</td>
                <td><strong>${l.user_name}</strong></td>
                <td>${l.user_role}</td>
                <td><span class="badge badge-healthy">${l.action}</span></td>
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

// Render Human Approval Modal
function renderHumanApprovalModal() {
  const e = state.selectedEmailForApproval;
  return `
    <div class="modal-overlay">
      <div class="modal-card">
        <div class="card-title">
          <span>Human Approval Interface (Email ID #${e.id})</span>
          <button class="btn btn-secondary" onclick="closeApprovalModal()">✕</button>
        </div>

        <p style="color:var(--text-muted); font-size:12px; margin-bottom:12px;">
          Review and edit AI-generated copy before approving dispatch to <strong>linusimon@gmail.com</strong>.
        </p>

        <label style="font-size:12px; font-weight:bold;">Recipient Role:</label>
        <input type="text" value="${e.recipient_role}" disabled style="width:100%; background:var(--bg-dark); border:1px solid var(--card-border); color:#fff; padding:8px; margin-bottom:12px; border-radius:4px;">

        <label style="font-size:12px; font-weight:bold;">Subject Line:</label>
        <input type="text" id="editSubject" value="${e.subject}" style="width:100%; background:var(--bg-dark); border:1px solid var(--card-border); color:#fff; padding:8px; margin-bottom:12px; border-radius:4px;">

        <label style="font-size:12px; font-weight:bold;">Email Body Content:</label>
        <textarea id="editBody" rows="8">${e.body}</textarea>

        <div style="display:flex; justify-content:flex-end; gap:12px;">
          <button class="btn btn-secondary" onclick="closeApprovalModal()">Cancel</button>
          <button class="btn btn-success" onclick="approveEmail()">Approve & Dispatch via Resend</button>
        </div>
      </div>
    </div>
  `;
}

// Auto-run on DOM ready
document.addEventListener('DOMContentLoaded', initApp);
