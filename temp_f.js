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

// DOM Initialization
document.addEventListener('DOMContentLoaded', initApp);
