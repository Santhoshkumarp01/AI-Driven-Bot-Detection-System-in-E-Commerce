class AdminDashboard {
    constructor() {
        this.sessions = [];
        this.stats = {};
        this.autoRefreshEnabled = true;
        this.refreshInterval = null;
        this.init();
    }

    async init() {
        console.log('TouchGuard Admin Dashboard initializing...');
        this.loadInitialData();
        this.setupAutoRefresh();
        this.initializeEventListeners();
        console.log('✅ TouchGuard Admin Dashboard initialized successfully');
    }

    loadInitialData() {
        // Load data from server-rendered template
        this.updateStatsDisplay();
        this.updateTimeAgo();
        console.log('📊 Initial data loaded');
    }

    setupAutoRefresh() {
        // Auto-refresh every 10 seconds
        this.refreshInterval = setInterval(() => {
            if (this.autoRefreshEnabled) {
                this.refreshPage();
            }
        }, 10000);

        // Update time indicators every 30 seconds
        setInterval(() => {
            this.updateTimeAgo();
        }, 30000);

        console.log('🔄 Auto-refresh setup complete (10s interval)');
    }

    initializeEventListeners() {
        // Auto-refresh toggle
        const autoRefreshCheckbox = document.getElementById('auto-refresh');
        if (autoRefreshCheckbox) {
            autoRefreshCheckbox.addEventListener('change', (e) => {
                this.autoRefreshEnabled = e.target.checked;
                if (this.autoRefreshEnabled) {
                    this.showNotification('Auto-refresh enabled', 'success');
                } else {
                    this.showNotification('Auto-refresh disabled', 'info');
                }
            });
        }

        // Manual refresh button
        const refreshBtn = document.querySelector('.refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.refreshPage();
            });
        }

        // Session row interactions
        document.addEventListener('click', (e) => {
            // Copy session ID
            if (e.target.classList.contains('copy-btn')) {
                const sessionId = e.target.dataset.sessionId || e.target.parentElement.dataset.sessionId;
                this.copyToClipboard(sessionId);
            }

            // View session details
            if (e.target.closest('.view-session-btn')) {
                const sessionId = e.target.closest('tr').dataset.sessionId;
                this.viewSession(sessionId);
            }

            // Block session
            if (e.target.closest('.block-session-btn')) {
                const sessionId = e.target.closest('tr').dataset.sessionId;
                this.blockSession(sessionId);
            }

            // Delete session
            if (e.target.closest('.delete-session-btn')) {
                const sessionId = e.target.closest('tr').dataset.sessionId;
                this.deleteSession(sessionId);
            }
        });

        console.log('🎯 Event listeners initialized');
    }

    refreshPage() {
        console.log('🔄 Refreshing admin dashboard...');
        this.showLoadingState();
        
        // Add a small delay to show loading state
        setTimeout(() => {
            window.location.reload();
        }, 500);
    }

    showLoadingState() {
        const refreshBtn = document.querySelector('.refresh-btn');
        if (refreshBtn) {
            refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Refreshing...';
            refreshBtn.disabled = true;
        }

        // Show loading overlay
        const loadingOverlay = document.createElement('div');
        loadingOverlay.className = 'loading-overlay';
        loadingOverlay.innerHTML = `
            <div class="loading-spinner">
                <i class="fas fa-spinner fa-spin"></i>
                <p>Refreshing dashboard...</p>
            </div>
        `;
        document.body.appendChild(loadingOverlay);
    }

    updateStatsDisplay() {
        // Stats are already rendered by server template
        const statCards = document.querySelectorAll('.stat-card');
        statCards.forEach(card => {
            card.classList.add('fade-in');
        });
        console.log('📈 Stats display updated');
    }

    updateTimeAgo() {
        document.querySelectorAll('.time-ago').forEach(element => {
            const timeStr = element.dataset.time;
            if (timeStr) {
                try {
                    const time = new Date(timeStr);
                    const now = new Date();
                    const diff = now - time;
                    const minutes = Math.floor(diff / 60000);
                    
                    if (minutes < 1) {
                        element.textContent = 'Just now';
                        element.style.color = 'var(--success-color)';
                    } else if (minutes < 5) {
                        element.textContent = `${minutes}m ago`;
                        element.style.color = 'var(--success-color)';
                    } else if (minutes < 60) {
                        element.textContent = `${minutes}m ago`;
                        element.style.color = 'var(--warning-color)';
                    } else {
                        const hours = Math.floor(minutes / 60);
                        if (hours < 24) {
                            element.textContent = `${hours}h ago`;
                            element.style.color = 'var(--danger-color)';
                        } else {
                            const days = Math.floor(hours / 24);
                            element.textContent = `${days}d ago`;
                            element.style.color = 'var(--text-light)';
                        }
                    }
                } catch (error) {
                    element.textContent = 'Unknown';
                    console.warn('Failed to parse time:', timeStr, error);
                }
            }
        });
    }

    async viewSession(sessionId) {
        console.log(`👀 Viewing session: ${sessionId}`);
        try {
            const response = await fetch(`/api/session/${sessionId}`);
            const data = await response.json();
            
            if (data.error) {
                this.showNotification(data.error, 'error');
                return;
            }

            this.showSessionModal(data);
        } catch (error) {
            console.error('Failed to load session details:', error);
            this.showNotification('Failed to load session details', 'error');
        }
    }

    showSessionModal(data) {
        const modal = document.createElement('div');
        modal.className = 'modal active';
        modal.innerHTML = `
            <div class="modal-content large">
                <div class="modal-header">
                    <h3>Session Details</h3>
                    <button class="modal-close" onclick="this.closest('.modal').remove()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="modal-body">
                    <div class="session-details-grid">
                        <div class="detail-section">
                            <h4>Session Information</h4>
                            <div class="detail-item">
                                <span class="detail-label">Session ID:</span>
                                <span class="detail-value">${data.session[0]}</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">Created At:</span>
                                <span class="detail-value">${new Date(data.session[1]).toLocaleString()}</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">Classification:</span>
                                <span class="detail-value user-type ${data.session[2].toLowerCase()}">
                                    ${data.session[2] === 'Human' ? '👤' : '🤖'} ${data.session[2]}
                                </span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">Confidence:</span>
                                <span class="detail-value">${data.session[3] || 0}%</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">Movement Count:</span>
                                <span class="detail-value">${data.session[5] || 0}</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">IP Address:</span>
                                <span class="detail-value">${data.session[7] || 'N/A'}</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">User Agent:</span>
                                <span class="detail-value">${data.session[8] || 'N/A'}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Close modal on overlay click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    }

    async blockSession(sessionId) {
        if (!confirm('Are you sure you want to block this session?')) {
            return;
        }

        console.log(`🚫 Blocking session: ${sessionId}`);
        try {
            const response = await fetch(`/api/admin/block/${sessionId}`, {
                method: 'POST'
            });
            
            const result = await response.json();
            
            if (result.message) {
                this.showNotification(result.message, 'success');
                this.updateSessionStatus(sessionId, 'blocked');
            } else {
                this.showNotification('Failed to block session', 'error');
            }
        } catch (error) {
            console.error('Failed to block session:', error);
            this.showNotification('Failed to block session', 'error');
        }
    }

    async deleteSession(sessionId) {
        if (!confirm('Are you sure you want to delete this session? This action cannot be undone.')) {
            return;
        }

        console.log(`🗑️ Deleting session: ${sessionId}`);
        try {
            const response = await fetch(`/api/admin/delete/${sessionId}`, {
                method: 'DELETE'
            });
            
            const result = await response.json();
            
            if (result.message) {
                this.showNotification(result.message, 'success');
                this.removeSessionFromTable(sessionId);
            } else {
                this.showNotification('Failed to delete session', 'error');
            }
        } catch (error) {
            console.error('Failed to delete session:', error);
            this.showNotification('Failed to delete session', 'error');
        }
    }

    updateSessionStatus(sessionId, status) {
        const sessionRow = document.querySelector(`tr[data-session-id="${sessionId}"]`);
        if (sessionRow) {
            const statusBadge = sessionRow.querySelector('.status-badge');
            if (statusBadge) {
                statusBadge.className = `status-badge ${status}`;
                statusBadge.innerHTML = `<i class="fas fa-ban"></i> Blocked`;
            }
        }
    }

    removeSessionFromTable(sessionId) {
        const sessionRow = document.querySelector(`tr[data-session-id="${sessionId}"]`);
        if (sessionRow) {
            sessionRow.style.opacity = '0';
            sessionRow.style.transform = 'translateX(-100px)';
            setTimeout(() => {
                sessionRow.remove();
            }, 300);
        }
    }

    copyToClipboard(text) {
        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(text).then(() => {
                this.showNotification('Session ID copied to clipboard', 'success');
            }).catch(() => {
                this.fallbackCopyToClipboard(text);
            });
        } else {
            this.fallbackCopyToClipboard(text);
        }
    }

    fallbackCopyToClipboard(text) {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            document.execCommand('copy');
            this.showNotification('Session ID copied to clipboard', 'success');
        } catch (err) {
            this.showNotification('Failed to copy to clipboard', 'error');
        }
        
        document.body.removeChild(textArea);
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        
        const icon = type === 'success' ? 'check' : 
                    type === 'error' ? 'times' : 
                    type === 'warning' ? 'exclamation-triangle' : 'info';
        
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${icon}"></i>
                <span>${message}</span>
            </div>
        `;
        
        // Add to notification container
        let container = document.getElementById('notification-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'notification-container';
            container.className = 'notification-container';
            document.body.appendChild(container);
        }
        
        container.appendChild(notification);
        
        // Animate in
        setTimeout(() => notification.classList.add('show'), 100);
        
        // Remove after 4 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 4000);
        
        console.log(`📢 Notification: ${message} (${type})`);
    }

    exportData() {
        console.log('📊 Exporting session data...');
        
        try {
            const sessions = Array.from(document.querySelectorAll('.session-row')).map(row => {
                const cells = row.querySelectorAll('td');
                return {
                    sessionId: cells[0]?.textContent?.trim(),
                    classification: cells[1]?.textContent?.trim(),
                    confidence: cells[2]?.textContent?.trim(),
                    movements: cells[3]?.textContent?.trim(),
                    status: cells[4]?.textContent?.trim(),
                    lastActivity: cells[5]?.textContent?.trim(),
                    ipAddress: cells[6]?.textContent?.trim()
                };
            });

            const csvContent = [
                ['Session ID', 'Classification', 'Confidence', 'Movements', 'Status', 'Last Activity', 'IP Address'],
                ...sessions.map(session => Object.values(session))
            ].map(row => row.map(field => `"${field}"`).join(',')).join('\n');

            const blob = new Blob([csvContent], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `touchguard-sessions-${new Date().toISOString().split('T')[0]}.csv`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);

            this.showNotification('Session data exported successfully', 'success');
        } catch (error) {
            console.error('Export failed:', error);
            this.showNotification('Failed to export data', 'error');
        }
    }

    destroy() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
        console.log('🔄 Admin dashboard destroyed');
    }
}

// Global functions for backwards compatibility
window.refreshSessions = () => {
    if (window.adminDashboard) {
        window.adminDashboard.refreshPage();
    }
};

window.exportData = () => {
    if (window.adminDashboard) {
        window.adminDashboard.exportData();
    }
};

window.copyToClipboard = (text) => {
    if (window.adminDashboard) {
        window.adminDashboard.copyToClipboard(text);
    }
};

window.viewSession = (sessionId) => {
    if (window.adminDashboard) {
        window.adminDashboard.viewSession(sessionId);
    }
};

window.blockSession = (sessionId) => {
    if (window.adminDashboard) {
        window.adminDashboard.blockSession(sessionId);
    }
};

window.deleteSession = (sessionId) => {
    if (window.adminDashboard) {
        window.adminDashboard.deleteSession(sessionId);
    }
};

window.closeModal = () => {
    const modal = document.querySelector('.modal');
    if (modal) {
        modal.remove();
    }
};

// Initialize when DOM loads
document.addEventListener('DOMContentLoaded', () => {
    window.adminDashboard = new AdminDashboard();
    
    // Handle page unload
    window.addEventListener('beforeunload', () => {
        if (window.adminDashboard) {
            window.adminDashboard.destroy();
        }
    });
    
    console.log('🚀 TouchGuard Admin Dashboard fully loaded');
});

// Handle visibility change
document.addEventListener('visibilitychange', () => {
    if (window.adminDashboard) {
        if (document.hidden) {
            window.adminDashboard.autoRefreshEnabled = false;
            console.log('⏸️ Auto-refresh paused (tab hidden)');
        } else {
            window.adminDashboard.autoRefreshEnabled = true;
            console.log('▶️ Auto-refresh resumed (tab visible)');
        }
    }
});
