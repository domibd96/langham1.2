// Modal Management Functions
function openModal() {
    const modal = document.getElementById('reservation-modal');
    modal.classList.remove('hidden');
    modal.setAttribute('aria-hidden', 'false');
    document.getElementById('date').focus();
}

function closeModal() {
    const modal = document.getElementById('reservation-modal');
    modal.classList.add('hidden');
    modal.setAttribute('aria-hidden', 'true');
    document.querySelector('.reserve-button').focus();
}

function openAuthModal(modalId) {
    const modal = document.getElementById(modalId);
    modal.classList.remove('hidden');
    modal.setAttribute('aria-hidden', 'false');
    
    // Focus on first input field
    const firstInput = modal.querySelector('input');
    if (firstInput) {
        setTimeout(() => firstInput.focus(), 100);
    }
}

function closeAuthModal(modalId) {
    const modal = document.getElementById(modalId);
    modal.classList.add('hidden');
    modal.setAttribute('aria-hidden', 'true');
    
    // Clear form fields
    const form = modal.querySelector('form');
    if (form) {
        form.reset();
    }
}

// Status Message Functions
function showStatusMessage(message, isError = false) {
    const statusDiv = document.getElementById('status-message');
    if (!statusDiv) return;
    
    statusDiv.textContent = message;
    statusDiv.className = 'status'; // Reset classes
    
    if (isError) {
        statusDiv.classList.add('error');
    }
    
    statusDiv.classList.add('show');
    
    // Auto-hide after 3 seconds
    setTimeout(() => {
        statusDiv.classList.remove('show');
    }, 3000);
}

// Keyboard Navigation
document.addEventListener('keydown', (event) => {
    // Escape key closes any open modal
    if (event.key === 'Escape') {
        const reservationModal = document.getElementById('reservation-modal');
        const loginModal = document.getElementById('login-auth-modal');
        const signupModal = document.getElementById('signup-auth-modal');
        
        if (reservationModal && !reservationModal.classList.contains('hidden')) {
            closeModal();
        } else if (loginModal && !loginModal.classList.contains('hidden')) {
            closeAuthModal('login-auth-modal');
        } else if (signupModal && !signupModal.classList.contains('hidden')) {
            closeAuthModal('signup-auth-modal');
        }
    }
    
    // Space key on homepage triggers reserve button (only when no modal is open)
    if (event.key === ' ' && 
        document.activeElement.tagName !== 'INPUT' && 
        document.activeElement.tagName !== 'TEXTAREA' &&
        document.activeElement.tagName !== 'SELECT') {
        
        const reservationModal = document.getElementById('reservation-modal');
        const loginModal = document.getElementById('login-auth-modal');
        const signupModal = document.getElementById('signup-auth-modal');
        
        // Check if any modal is open
        const isAnyModalOpen = (reservationModal && !reservationModal.classList.contains('hidden')) ||
                              (loginModal && !loginModal.classList.contains('hidden')) ||
                              (signupModal && !signupModal.classList.contains('hidden'));
        
        if (!isAnyModalOpen) {
            event.preventDefault();
            const reserveButton = document.querySelector('.reserve-button');
            if (reserveButton) {
                reserveButton.click();
            }
        }
    }
});

// Click outside modal to close
document.addEventListener('click', (event) => {
    const reservationModal = document.getElementById('reservation-modal');
    const loginModal = document.getElementById('login-auth-modal');
    const signupModal = document.getElementById('signup-auth-modal');
    
    // Close reservation modal if clicking outside
    if (reservationModal && !reservationModal.classList.contains('hidden') && 
        !reservationModal.contains(event.target) && 
        !event.target.classList.contains('reserve-button')) {
        closeModal();
    }
    
    // Close auth modals if clicking outside
    if (loginModal && !loginModal.classList.contains('hidden') && 
        !loginModal.contains(event.target) && 
        !event.target.classList.contains('auth-link')) {
        closeAuthModal('login-auth-modal');
    }
    
    if (signupModal && !signupModal.classList.contains('hidden') && 
        !signupModal.contains(event.target) && 
        !event.target.classList.contains('auth-link')) {
        closeAuthModal('signup-auth-modal');
    }
});

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    // Check authentication status on page load
    checkAuthStatus();
    
    // Set minimum date to today for reservation form
    const dateInput = document.getElementById('date');
    if (dateInput) {
        const today = new Date().toISOString().split('T')[0];
        dateInput.setAttribute('min', today);
    }
    
    // Add loading states to forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.textContent = 'Processing...';
                submitButton.disabled = true;
                
                // Re-enable button after 5 seconds as fallback
                setTimeout(() => {
                    submitButton.textContent = submitButton.textContent === 'Processing...' ? 'Confirm Reservation' : 'Submit';
                    submitButton.disabled = false;
                }, 5000);
            }
        });
    });
});

// Check authentication status
function checkAuthStatus() {
    fetch('/check-auth')
        .then(response => response.json())
        .then(data => {
            if (data.authenticated) {
                updateAuthUI(true, data.user.email, data.user.name);
            }
        })
        .catch(error => {
            console.log('User not authenticated');
        });
}

// Update auth UI with user info
function updateAuthUI(isLoggedIn, userEmail, userName = null) {
    const authNav = document.querySelector('.auth-nav');
    if (isLoggedIn && userEmail) {
        const displayName = userName || userEmail.split('@')[0];
        authNav.innerHTML = `
            <span class="user-welcome">Welcome, ${displayName}</span>
            <button class="auth-link" onclick="logout()">Logout</button>
        `;
    }
}

  
  