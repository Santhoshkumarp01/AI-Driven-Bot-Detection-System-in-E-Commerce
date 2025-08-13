class TouchGuardTracker {
    constructor() {
        this.sessionId = this.generateSessionId();
        this.movements = [];
        this.clicks = 0;
        this.isTracking = true;
        this.detectionInterval = null;
        this.lastDetection = null;
        
        this.initializeTracking();
        this.startRealTimeDetection();
        
        console.log(`TouchGuard initialized with session: ${this.sessionId}`);
    }
    
    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    
    initializeTracking() {
        // Track mouse movements
        document.addEventListener('mousemove', (e) => {
            if (this.isTracking) {
                this.movements.push({
                    x: e.clientX,
                    y: e.clientY,
                    timestamp: Date.now()
                });
                
                // Limit movements array for performance
                if (this.movements.length > 100) {
                    this.movements = this.movements.slice(-50);
                }
                
                this.updateMovementCount();
            }
        });
        
        // Track clicks
        document.addEventListener('click', (e) => {
            if (this.isTracking) {
                this.clicks++;
                this.movements.push({
                    x: e.clientX,
                    y: e.clientY,
                    timestamp: Date.now(),
                    type: 'click'
                });
            }
        });
        
        // Track page visibility
        document.addEventListener('visibilitychange', () => {
            this.isTracking = !document.hidden;
        });
    }
    
    updateMovementCount() {
        const countElement = document.getElementById('movement-count');
        if (countElement) {
            countElement.textContent = this.movements.length;
        }
    }
    
    startRealTimeDetection() {
        // Perform detection every 5 seconds when sufficient data available
        this.detectionInterval = setInterval(() => {
            if (this.movements.length >= 10) {
                this.performDetection();
            }
        }, 5000);
    }
    
    async performDetection() {
        try {
            const response = await fetch('/api/detect', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    movements: this.movements,
                    clicks: this.clicks,
                    timestamp: new Date().toISOString()
                })
            });
            
            const result = await response.json();
            
            if (result.error) {
                console.warn('Detection error:', result.error);
                return;
            }
            
            this.lastDetection = result;
            this.updateUI(result);
            this.logDetection(result);
            
        } catch (error) {
            console.error('Detection request failed:', error);
        }
    }
    
    updateUI(result) {
        // Update desktop indicator
        const statusElement = document.getElementById('detection-status');
        const confidenceElement = document.getElementById('confidence-display');
        const statusText = statusElement?.querySelector('.status-text');
        
        if (statusElement) {
            statusElement.className = `detection-indicator ${result.is_bot ? 'bot' : 'human'}`;
        }
        
        if (statusText) {
            statusText.textContent = result.classification;
        }
        
        if (confidenceElement) {
            confidenceElement.textContent = `${result.confidence}%`;
        }
        
        // Update mobile panel
        const mobileStatus = document.getElementById('mobile-status');
        const mobileConfidence = document.getElementById('mobile-confidence');
        const mobileSession = document.getElementById('mobile-session');
        
        if (mobileStatus) mobileStatus.textContent = result.classification;
        if (mobileConfidence) mobileConfidence.textContent = `${result.confidence}%`;
        if (mobileSession) mobileSession.textContent = 'Active';
        
        // Update page title with detection status
        document.title = `${result.classification} Detected (${result.confidence}%) - TouchGuard Store`;
    }
    
    logDetection(result) {
        const historyList = document.getElementById('history-list');
        if (!historyList) return;
        
        const listItem = document.createElement('li');
        listItem.innerHTML = `
            <span class="${result.is_bot ? 'bot' : 'human'}">
                ${result.is_bot ? '🤖' : '👤'} ${result.classification} (${result.confidence}%)
            </span>
            <small>${new Date(result.timestamp).toLocaleTimeString()}</small>
        `;
        
        historyList.insertBefore(listItem, historyList.firstChild);
        
        // Keep only last 10 entries
        while (historyList.children.length > 10) {
            historyList.removeChild(historyList.lastChild);
        }
    }
    
    async finalVerification() {
        // Perform final detection before checkout
        if (this.movements.length < 5) {
            return { 
                allowed: true, 
                message: "Insufficient data for verification" 
            };
        }
        
        try {
            await this.performDetection();
            
            if (!this.lastDetection) {
                return { 
                    allowed: true, 
                    message: "Detection unavailable" 
                };
            }
            
            const { is_bot, confidence, classification } = this.lastDetection;
            
            if (is_bot && confidence > 85) {
                return {
                    allowed: false,
                    message: `Automated behavior detected (${confidence}% confidence). Please verify you are human.`,
                    requiresVerification: true
                };
            } else if (is_bot && confidence > 70) {
                return {
                    allowed: true,
                    message: `Additional verification recommended (${confidence}% bot probability).`,
                    requiresAdditionalVerification: true
                };
            } else {
                return {
                    allowed: true,
                    message: `Human behavior verified (${confidence}% confidence).`,
                    classification: classification
                };
            }
            
        } catch (error) {
            console.error('Final verification failed:', error);
            return { 
                allowed: true, 
                message: "Verification error - proceeding with caution" 
            };
        }
    }
    
    getSessionInfo() {
        return {
            sessionId: this.sessionId,
            movementCount: this.movements.length,
            clickCount: this.clicks,
            lastDetection: this.lastDetection,
            isTracking: this.isTracking
        };
    }
    
    stopTracking() {
        this.isTracking = false;
        if (this.detectionInterval) {
            clearInterval(this.detectionInterval);
            this.detectionInterval = null;
        }
        console.log('TouchGuard tracking stopped');
    }
    
    resumeTracking() {
        this.isTracking = true;
        this.startRealTimeDetection();
        console.log('TouchGuard tracking resumed');
    }
}

// Initialize TouchGuard when DOM is loaded
let touchguardTracker = null;

document.addEventListener('DOMContentLoaded', () => {
    touchguardTracker = new TouchGuardTracker();
    
    // Make it globally accessible
    window.touchguardTracker = touchguardTracker;
    
    // Handle page unload
    window.addEventListener('beforeunload', () => {
        if (touchguardTracker) {
            touchguardTracker.stopTracking();
        }
    });
});
