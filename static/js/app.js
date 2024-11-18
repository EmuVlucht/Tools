let currentEmailId = null;
let refreshInterval = null;

document.addEventListener('DOMContentLoaded', () => {
    loadDomains();
    loadEmails();
    setupEventListeners();
});

function setupEventListeners() {
    document.getElementById('createRandomBtn').addEventListener('click', createRandomEmail);
    document.getElementById('createCustomBtn').addEventListener('click', createCustomEmail);
    document.getElementById('refreshInboxBtn').addEventListener('click', () => refreshInbox(true));
    document.getElementById('deleteEmailBtn').addEventListener('click', deleteCurrentEmail);
    document.getElementById('closeModalBtn').addEventListener('click', closeModal);
    document.querySelector('.modal-overlay').addEventListener('click', closeModal);
    
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeModal();
    });
}

async function loadDomains() {
    try {
        const response = await fetch('/api/domains');
        const data = await response.json();
        
        if (data.success && data.domains) {
            const select = document.getElementById('domainSelect');
            select.innerHTML = '<option value="">Pilih domain...</option>';
            data.domains.forEach(domain => {
                const option = document.createElement('option');
                option.value = domain;
                option.textContent = '@' + domain;
                select.appendChild(option);
            });
        }
    } catch (error) {
        showToast('Gagal memuat domain', 'error');
    }
}

async function loadEmails() {
    try {
        const response = await fetch('/api/emails');
        const data = await response.json();
        
        const emailList = document.getElementById('emailList');
        
        if (data.success && data.emails && data.emails.length > 0) {
            emailList.innerHTML = '';
            data.emails.forEach(email => {
                emailList.appendChild(createEmailItem(email));
            });
        } else {
            emailList.innerHTML = `
                <div class="empty-state" style="padding: 20px;">
                    <i class="fas fa-envelope" style="font-size: 2rem; margin-bottom: 10px;"></i>
                    <p>Belum ada email</p>
                </div>
            `;
        }
    } catch (error) {
        showToast('Gagal memuat daftar email', 'error');
    }
}

function createEmailItem(email) {
    const div = document.createElement('div');
    div.className = `email-item ${email.is_active ? '' : 'expired'} ${currentEmailId === email.id ? 'active' : ''}`;
    div.dataset.id = email.id;
    
    const date = new Date(email.created_at);
    const formattedDate = date.toLocaleDateString('id-ID', { day: 'numeric', month: 'short', year: 'numeric' });
    
    div.innerHTML = `
        <div class="email-icon">
            <i class="fas fa-envelope"></i>
        </div>
        <div class="email-info">
            <div class="email-address">${email.email}</div>
            <div class="email-date">${formattedDate}</div>
        </div>
        <span class="email-status ${email.is_active ? 'active' : 'expired'}">
            ${email.is_active ? 'Aktif' : 'Expired'}
        </span>
    `;
    
    div.addEventListener('click', () => selectEmail(email));
    return div;
}

async function createRandomEmail() {
    const btn = document.getElementById('createRandomBtn');
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Membuat...';
    
    try {
        const response = await fetch('/api/email/create/random', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        const data = await response.json();
        
        if (data.success) {
            showToast('Email berhasil dibuat!', 'success');
            loadEmails();
            selectEmail(data.email);
        } else {
            showToast(data.error || 'Gagal membuat email', 'error');
        }
    } catch (error) {
        showToast('Gagal membuat email', 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-random"></i> Email Random';
    }
}

async function createCustomEmail() {
    const name = document.getElementById('emailName').value.trim();
    const domain = document.getElementById('domainSelect').value;
    
    if (!name) {
        showToast('Masukkan nama email', 'error');
        return;
    }
    
    if (!domain) {
        showToast('Pilih domain', 'error');
        return;
    }
    
    const btn = document.getElementById('createCustomBtn');
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Membuat...';
    
    try {
        const response = await fetch('/api/email/create/custom', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, domain })
        });
        const data = await response.json();
        
        if (data.success) {
            showToast('Email berhasil dibuat!', 'success');
            document.getElementById('emailName').value = '';
            loadEmails();
            selectEmail(data.email);
        } else {
            showToast(data.error || 'Gagal membuat email', 'error');
        }
    } catch (error) {
        showToast('Gagal membuat email', 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-plus"></i> Buat Custom';
    }
}

function selectEmail(email) {
    currentEmailId = email.id;
    
    document.querySelectorAll('.email-item').forEach(item => {
        item.classList.remove('active');
        if (parseInt(item.dataset.id) === email.id) {
            item.classList.add('active');
        }
    });
    
    const emailInfo = document.getElementById('currentEmailInfo');
    emailInfo.classList.add('active');
    emailInfo.innerHTML = `
        <i class="fas fa-envelope"></i>
        <span>${email.email}</span>
        <button class="copy-btn" onclick="copyEmail('${email.email}')" title="Salin email">
            <i class="fas fa-copy"></i>
        </button>
    `;
    
    document.getElementById('refreshInboxBtn').disabled = false;
    document.getElementById('deleteEmailBtn').disabled = false;
    
    refreshInbox(false);
    
    if (refreshInterval) clearInterval(refreshInterval);
    refreshInterval = setInterval(() => refreshInbox(false), 5000);
}

async function refreshInbox(showLoading = true) {
    if (!currentEmailId) return;
    
    const container = document.getElementById('inboxContainer');
    const refreshBtn = document.getElementById('refreshInboxBtn');
    
    if (showLoading) {
        refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    }
    
    try {
        const response = await fetch(`/api/email/${currentEmailId}/inbox`);
        const data = await response.json();
        
        if (data.success) {
            if (data.messages && data.messages.length > 0) {
                container.innerHTML = '<div class="message-list"></div>';
                const messageList = container.querySelector('.message-list');
                
                data.messages.forEach(msg => {
                    messageList.appendChild(createMessageItem(msg));
                });
            } else {
                container.innerHTML = `
                    <div class="empty-state">
                        <i class="fas fa-inbox"></i>
                        <h3>Inbox Kosong</h3>
                        <p>Menunggu pesan masuk...</p>
                        <p style="font-size: 0.8rem; margin-top: 10px;">Auto-refresh setiap 5 detik</p>
                    </div>
                `;
            }
        } else if (data.error === 'Email expired') {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-exclamation-triangle" style="color: var(--warning-color);"></i>
                    <h3>Email Expired</h3>
                    <p>Email ini sudah tidak aktif. Buat email baru untuk melanjutkan.</p>
                </div>
            `;
            if (refreshInterval) clearInterval(refreshInterval);
            loadEmails();
        }
    } catch (error) {
        console.error('Refresh inbox error:', error);
    } finally {
        refreshBtn.innerHTML = '<i class="fas fa-sync-alt"></i>';
    }
}

function createMessageItem(message) {
    const div = document.createElement('div');
    div.className = 'message-item';
    
    let fromDisplay = message.from_email;
    if (fromDisplay.includes('<')) {
        fromDisplay = fromDisplay.replace(/<|>/g, ' ').replace(/"/g, '');
    }
    
    const receivedAt = message.received_at ? new Date(message.received_at) : new Date(message.created_at);
    const formattedTime = receivedAt.toLocaleString('id-ID', {
        day: 'numeric',
        month: 'short',
        hour: '2-digit',
        minute: '2-digit'
    });
    
    const preview = (message.body_text || '').substring(0, 100).replace(/\n/g, ' ');
    
    div.innerHTML = `
        <div class="message-header">
            <span class="message-from">${fromDisplay}</span>
            <span class="message-time">${formattedTime}</span>
        </div>
        <div class="message-subject">${message.subject || '(Tanpa Subjek)'}</div>
        <div class="message-preview">${preview}${preview.length >= 100 ? '...' : ''}</div>
    `;
    
    div.addEventListener('click', () => openMessage(message));
    return div;
}

function openMessage(message) {
    const modal = document.getElementById('messageModal');
    
    document.getElementById('modalSubject').textContent = message.subject || '(Tanpa Subjek)';
    
    let fromDisplay = message.from_email;
    if (fromDisplay.includes('<')) {
        fromDisplay = fromDisplay.replace(/<|>/g, ' ').replace(/"/g, '');
    }
    document.getElementById('modalFrom').textContent = fromDisplay;
    document.getElementById('modalTo').textContent = message.to_email;
    
    const receivedAt = message.received_at ? new Date(message.received_at) : new Date(message.created_at);
    document.getElementById('modalTime').textContent = receivedAt.toLocaleString('id-ID');
    
    const content = document.getElementById('modalContent');
    if (message.body_html) {
        content.innerHTML = message.body_html;
    } else {
        content.textContent = message.body_text || '(Tidak ada konten)';
    }
    
    const attachmentsContainer = document.getElementById('modalAttachments');
    if (message.attachments && message.attachments.length > 0) {
        attachmentsContainer.innerHTML = '<h4 style="margin-bottom: 12px;"><i class="fas fa-paperclip"></i> Lampiran</h4>';
        message.attachments.forEach(att => {
            const div = document.createElement('div');
            div.className = 'attachment-item';
            div.innerHTML = `
                <i class="fas fa-file"></i>
                <a href="https://api.internal.temp-mail.io/api/v3/attachment/${att.id}?download=1" target="_blank">${att.name}</a>
            `;
            attachmentsContainer.appendChild(div);
        });
    } else {
        attachmentsContainer.innerHTML = '';
    }
    
    modal.classList.add('active');
}

function closeModal() {
    document.getElementById('messageModal').classList.remove('active');
}

async function deleteCurrentEmail() {
    if (!currentEmailId) return;
    
    if (!confirm('Yakin ingin menghapus email ini?')) return;
    
    try {
        const response = await fetch(`/api/email/${currentEmailId}`, {
            method: 'DELETE'
        });
        const data = await response.json();
        
        if (data.success) {
            showToast('Email berhasil dihapus', 'success');
            currentEmailId = null;
            if (refreshInterval) clearInterval(refreshInterval);
            
            document.getElementById('currentEmailInfo').innerHTML = `
                <i class="fas fa-envelope"></i>
                <span>Pilih email untuk melihat inbox</span>
            `;
            document.getElementById('currentEmailInfo').classList.remove('active');
            document.getElementById('refreshInboxBtn').disabled = true;
            document.getElementById('deleteEmailBtn').disabled = true;
            
            document.getElementById('inboxContainer').innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-envelope-open"></i>
                    <h3>Selamat Datang di M-Mail</h3>
                    <p>Buat email sementara untuk melindungi privasi Anda.</p>
                    <p>Email akan otomatis menerima pesan masuk.</p>
                </div>
            `;
            
            loadEmails();
        } else {
            showToast(data.error || 'Gagal menghapus email', 'error');
        }
    } catch (error) {
        showToast('Gagal menghapus email', 'error');
    }
}

function copyEmail(email) {
    navigator.clipboard.writeText(email).then(() => {
        showToast('Email disalin ke clipboard!', 'success');
    }).catch(() => {
        showToast('Gagal menyalin email', 'error');
    });
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        info: 'fa-info-circle'
    };
    
    toast.innerHTML = `
        <i class="fas ${icons[type] || icons.info}"></i>
        <span>${message}</span>
    `;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}
