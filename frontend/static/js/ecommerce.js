class EcommerceManager {
    constructor() {
        this.cart = JSON.parse(localStorage.getItem('touchguard_cart') || '[]');
        this.total = 0;
        this.products = {
            laptop: {
                id: 'laptop',
                name: 'Gaming Laptop Pro',
                price: 1299.99,
                originalPrice: 1499.99,
                image: '/static/images/laptop.jpg',
                description: 'High-performance laptop for gaming and productivity'
            },
            smartphone: {
                id: 'smartphone',
                name: 'Smartphone Pro Max',
                price: 899.99,
                image: '/static/images/smartphone.jpg',
                description: 'Latest flagship smartphone with AI camera'
            },
            headphones: {
                id: 'headphones',
                name: 'Wireless Headphones',
                price: 249.99,
                originalPrice: 299.99,
                image: '/static/images/headphones.jpg',
                description: 'Premium sound quality with noise cancellation'
            },
            smartwatch: {
                id: 'smartwatch',
                name: 'Smart Watch Series X',
                price: 399.99,
                image: '/static/images/smartwatch.jpg',
                description: 'Advanced health tracking and connectivity'
            }
        };
        
        this.initializeEventListeners();
        this.updateCartUI();
        this.calculateTotal();
    }
    
    initializeEventListeners() {
        // Add to cart buttons
        document.querySelectorAll('.add-to-cart-btn').forEach(button => {
            button.addEventListener('click', (e) => {
                const productId = button.dataset.productId;
                this.addToCart(productId);
                this.showAddToCartAnimation(button);
            });
        });
        
        // Cart toggle
        const cartToggle = document.getElementById('cart-toggle');
        if (cartToggle) {
            cartToggle.addEventListener('click', () => {
                this.toggleCart();
            });
        }
        
        // Cart close
        const cartClose = document.getElementById('cart-close');
        if (cartClose) {
            cartClose.addEventListener('click', () => {
                this.closeCart();
            });
        }
        
        // Checkout button
        const checkoutBtn = document.getElementById('checkout-btn');
        if (checkoutBtn) {
            checkoutBtn.addEventListener('click', () => {
                this.initiateCheckout();
            });
        }
        
        // Checkout form
        const checkoutForm = document.getElementById('checkout-form');
        if (checkoutForm) {
            checkoutForm.addEventListener('submit', (e) => {
                this.handleCheckout(e);
            });
        }
        
        // Modal close
        const modalClose = document.getElementById('modal-close');
        if (modalClose) {
            modalClose.addEventListener('click', () => {
                this.closeCheckoutModal();
            });
        }
        
        // Overlay click
        const overlay = document.getElementById('overlay');
        if (overlay) {
            overlay.addEventListener('click', () => {
                this.closeCart();
                this.closeCheckoutModal();
            });
        }
        
        // Mobile detection panel
        const panelHeader = document.querySelector('.panel-header');
        if (panelHeader) {
            panelHeader.addEventListener('click', () => {
                this.toggleDetectionPanel();
            });
        }
    }
    
    addToCart(productId) {
        const product = this.products[productId];
        if (!product) return;
        
        const existingItem = this.cart.find(item => item.id === productId);
        if (existingItem) {
            existingItem.quantity += 1;
        } else {
            this.cart.push({
                ...product,
                quantity: 1,
                addedAt: new Date().toISOString()
            });
        }
        
        this.saveCart();
        this.updateCartUI();
        this.calculateTotal();
        
        // Show success notification
        this.showNotification(`${product.name} added to cart!`, 'success');
    }
    
    removeFromCart(productId) {
        this.cart = this.cart.filter(item => item.id !== productId);
        this.saveCart();
        this.updateCartUI();
        this.calculateTotal();
        
        this.showNotification('Item removed from cart', 'info');
    }
    
    updateQuantity(productId, quantity) {
        const item = this.cart.find(item => item.id === productId);
        if (item) {
            if (quantity <= 0) {
                this.removeFromCart(productId);
            } else {
                item.quantity = quantity;
                this.saveCart();
                this.updateCartUI();
                this.calculateTotal();
            }
        }
    }
    
    updateCartUI() {
        const cartCount = document.getElementById('cart-count');
        const cartItems = document.getElementById('cart-items');
        const checkoutBtn = document.getElementById('checkout-btn');
        
        const totalItems = this.cart.reduce((sum, item) => sum + item.quantity, 0);
        
        if (cartCount) {
            cartCount.textContent = totalItems;
            cartCount.style.display = totalItems > 0 ? 'flex' : 'none';
        }
        
        if (cartItems) {
            if (this.cart.length === 0) {
                cartItems.innerHTML = `
                    <div class="empty-cart">
                        <i class="fas fa-shopping-cart"></i>
                        <p>Your cart is empty</p>
                        <small>Add some products to get started!</small>
                    </div>
                `;
            } else {
                cartItems.innerHTML = this.cart.map(item => `
                    <div class="cart-item" data-product-id="${item.id}">
                        <div class="cart-item-image">
                            <img src="${item.image}" alt="${item.name}" loading="lazy">
                        </div>
                        <div class="cart-item-info">
                            <div class="cart-item-name">${item.name}</div>
                            <div class="cart-item-price">$${item.price.toFixed(2)}</div>
                            <div class="quantity-controls">
                                <button class="quantity-btn minus" onclick="ecommerce.updateQuantity('${item.id}', ${item.quantity - 1})">
                                    <i class="fas fa-minus"></i>
                                </button>
                                <span class="quantity">${item.quantity}</span>
                                <button class="quantity-btn plus" onclick="ecommerce.updateQuantity('${item.id}', ${item.quantity + 1})">
                                    <i class="fas fa-plus"></i>
                                </button>
                            </div>
                        </div>
                        <button class="cart-item-remove" onclick="ecommerce.removeFromCart('${item.id}')">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                `).join('');
            }
        }
        
        if (checkoutBtn) {
            checkoutBtn.disabled = this.cart.length === 0;
        }
    }
    
    calculateTotal() {
        this.total = this.cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
        
        // Update all total displays
        const totalElements = [
            document.getElementById('cart-total'),
            document.getElementById('sidebar-total')
        ];
        
        totalElements.forEach(element => {
            if (element) {
                element.textContent = `$${this.total.toFixed(2)}`;
            }
        });
    }
    
    toggleCart() {
        const cartSidebar = document.getElementById('cart-sidebar');
        const overlay = document.getElementById('overlay');
        
        if (cartSidebar && overlay) {
            const isActive = cartSidebar.classList.contains('active');
            
            if (isActive) {
                this.closeCart();
            } else {
                cartSidebar.classList.add('active');
                overlay.classList.add('active');
                document.body.style.overflow = 'hidden';
            }
        }
    }
    
    closeCart() {
        const cartSidebar = document.getElementById('cart-sidebar');
        const overlay = document.getElementById('overlay');
        
        if (cartSidebar) cartSidebar.classList.remove('active');
        if (overlay) overlay.classList.remove('active');
        document.body.style.overflow = '';
    }
    
    async initiateCheckout() {
        if (this.cart.length === 0) {
            this.showNotification('Your cart is empty!', 'warning');
            return;
        }
        
        // Perform pre-checkout bot detection
        if (window.touchguardTracker) {
            const verification = await window.touchguardTracker.finalVerification();
            
            if (!verification.allowed) {
                this.showBotDetectionWarning(verification.message);
                return;
            }
            
            if (verification.requiresAdditionalVerification) {
                this.showAdditionalVerificationPrompt(verification.message);
                // Continue with checkout but with additional monitoring
            }
        }
        
        // Close cart and open checkout modal
        this.closeCart();
        this.openCheckoutModal();
    }
    
    openCheckoutModal() {
        const modal = document.getElementById('checkout-modal');
        if (modal) {
            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
            
            // Focus on first input
            const firstInput = modal.querySelector('input');
            if (firstInput) {
                setTimeout(() => firstInput.focus(), 300);
            }
        }
    }
    
    closeCheckoutModal() {
        const modal = document.getElementById('checkout-modal');
        if (modal) {
            modal.classList.remove('active');
            document.body.style.overflow = '';
        }
    }
    
    async handleCheckout(event) {
        event.preventDefault();
        
        const submitBtn = event.target.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        
        // Show loading state
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
        submitBtn.disabled = true;
        
        try {
            // Simulate payment processing
            await this.simulatePayment();
            
            // Final bot detection check
            if (window.touchguardTracker) {
                const finalVerification = await window.touchguardTracker.finalVerification();
                
                if (!finalVerification.allowed) {
                    throw new Error(finalVerification.message);
                }
            }
            
            // Success
            this.showSuccessMessage();
            this.clearCart();
            this.closeCheckoutModal();
            
        } catch (error) {
            console.error('Checkout failed:', error);
            this.showNotification(error.message || 'Payment failed. Please try again.', 'error');
        } finally {
            // Restore button
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    }
    
    async simulatePayment() {
        // Simulate payment processing delay
        return new Promise((resolve, reject) => {
            setTimeout(() => {
                // Simulate 95% success rate
                if (Math.random() > 0.05) {
                    resolve();
                } else {
                    reject(new Error('Payment processing failed'));
                }
            }, 2000);
        });
    }
    
    showBotDetectionWarning(message) {
        const modal = this.createModal('Bot Detection Warning', `
            <div class="bot-warning">
                <i class="fas fa-robot" style="font-size: 3rem; color: var(--danger-color); margin-bottom: 1rem;"></i>
                <p>${message}</p>
                <p>If you believe this is an error, please contact our customer support.</p>
            </div>
        `, [
            {
                text: 'Contact Support',
                class: 'btn btn-primary',
                action: () => this.contactSupport()
            },
            {
                text: 'Try Again',
                class: 'btn btn-secondary',
                action: () => this.closeModal()
            }
        ]);
        
        this.showModal(modal);
    }
    
    showAdditionalVerificationPrompt(message) {
        const modal = this.createModal('Additional Verification', `
            <div class="verification-prompt">
                <i class="fas fa-shield-alt" style="font-size: 2rem; color: var(--warning-color); margin-bottom: 1rem;"></i>
                <p>${message}</p>
                <p>We may require additional verification steps during checkout.</p>
            </div>
        `, [
            {
                text: 'Continue',
                class: 'btn btn-primary',
                action: () => {
                    this.closeModal();
                    this.openCheckoutModal();
                }
            },
            {
                text: 'Cancel',
                class: 'btn btn-secondary',
                action: () => this.closeModal()
            }
        ]);
        
        this.showModal(modal);
    }
    
    showSuccessMessage() {
        const sessionInfo = window.touchguardTracker?.getSessionInfo();
        
        const modal = this.createModal('Purchase Successful! 🎉', `
            <div class="success-message">
                <i class="fas fa-check-circle" style="font-size: 3rem; color: var(--success-color); margin-bottom: 1rem;"></i>
                <p>Your order has been placed successfully!</p>
                <p>Total: <strong>$${this.total.toFixed(2)}</strong></p>
                
                ${sessionInfo ? `
                    <div class="security-info">
                        <h4>🔐 Security Verification</h4>
                        <p>Classification: <strong>${sessionInfo.lastDetection?.classification || 'Human'}</strong></p>
                        <p>Confidence: <strong>${sessionInfo.lastDetection?.confidence || 'N/A'}%</strong></p>
                        <p>Session: <strong>${sessionInfo.sessionId.substr(0, 12)}...</strong></p>
                    </div>
                ` : ''}
                
                <p><small>You will receive an email confirmation shortly.</small></p>
            </div>
        `, [
            {
                text: 'Continue Shopping',
                class: 'btn btn-primary',
                action: () => {
                    this.closeModal();
                    window.location.reload();
                }
            }
        ]);
        
        this.showModal(modal);
    }
    
    createModal(title, content, buttons = []) {
        return { title, content, buttons };
    }
    
    showModal(modalData) {
        // Remove existing modal if any
        const existingModal = document.getElementById('dynamic-modal');
        if (existingModal) {
            existingModal.remove();
        }
        
        const modal = document.createElement('div');
        modal.id = 'dynamic-modal';
        modal.className = 'checkout-modal active';
        
        const buttonsHtml = modalData.buttons.map(btn => 
            `<button class="${btn.class}" onclick="this.closest('.checkout-modal').remove(); (${btn.action.toString()})()">${btn.text}</button>`
        ).join('');
        
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>${modalData.title}</h3>
                    <button class="modal-close" onclick="this.closest('.checkout-modal').remove()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="modal-body">
                    ${modalData.content}
                    <div class="modal-buttons" style="margin-top: 1.5rem; display: flex; gap: 1rem;">
                        ${buttonsHtml}
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        document.body.style.overflow = 'hidden';
    }
    
    closeModal() {
        const modal = document.getElementById('dynamic-modal');
        if (modal) {
            modal.remove();
            document.body.style.overflow = '';
        }
    }
    
    contactSupport() {
        window.open('mailto:support@touchguard.com?subject=Bot Detection Issue', '_blank');
        this.closeModal();
    }
    
    toggleDetectionPanel() {
        const panel = document.getElementById('detection-panel');
        if (panel) {
            panel.classList.toggle('expanded');
        }
    }
    
    showAddToCartAnimation(button) {
        button.classList.add('loading');
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Adding...';
        
        setTimeout(() => {
            button.classList.remove('loading');
            button.innerHTML = '<i class="fas fa-check"></i> Added!';
            
            setTimeout(() => {
                button.innerHTML = '<i class="fas fa-cart-plus"></i> Add to Cart';
            }, 1500);
        }, 800);
    }
    
    showNotification(message, type = 'info') {
        // Remove existing notification
        const existing = document.querySelector('.notification');
        if (existing) existing.remove();
        
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${this.getNotificationIcon(type)}"></i>
                <span>${message}</span>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Auto remove after 3 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 3000);
    }
    
    getNotificationIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }
    
    saveCart() {
        localStorage.setItem('touchguard_cart', JSON.stringify(this.cart));
    }
    
    clearCart() {
        this.cart = [];
        this.total = 0;
        this.saveCart();
        this.updateCartUI();
        this.calculateTotal();
    }
}

// Initialize ecommerce when DOM is loaded
let ecommerce = null;

document.addEventListener('DOMContentLoaded', () => {
    ecommerce = new EcommerceManager();
    window.ecommerce = ecommerce;
});
