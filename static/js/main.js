// ================================
// MOBILE MENU TOGGLE
// ================================
document.addEventListener('DOMContentLoaded', function() {
    const menuBtn = document.getElementById('mobileMenuBtn');
    const mobileMenu = document.getElementById('mobileMenu');
    
    if (menuBtn && mobileMenu) {
        menuBtn.addEventListener('click', function() {
            mobileMenu.classList.toggle('active');
        });
    }
    
    // ================================
    // ALERT CLOSE BUTTONS
    // ================================
    const alertCloseBtns = document.querySelectorAll('.alert-close');
    alertCloseBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            this.parentElement.style.display = 'none';
        });
    });
    
    // ================================
    // AUTO-HIDE ALERTS
    // ================================
    setTimeout(() => {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => {
            alert.style.opacity = '0';
            alert.style.transition = 'opacity 0.5s';
            setTimeout(() => alert.remove(), 500);
        });
    }, 5000);
    
    // ================================
    // SEARCH FORM VALIDATION
    // ================================
    const searchForms = document.querySelectorAll('.search-form');
    searchForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const input = this.querySelector('input[name="q"]');
            if (input && input.value.trim() === '') {
                e.preventDefault();
            }
        });
    });
    
    // ================================
    // IMAGE ERROR HANDLING
    // ================================
    const images = document.querySelectorAll('img');
    images.forEach(img => {
        img.addEventListener('error', function() {
            this.style.display = 'none';
        });
    });
    
    // ================================
    // QUILL EDITOR INITIALIZATION (if present)
    // ================================
    if (typeof Quill !== 'undefined') {
        const editorContainer = document.getElementById('editor');
        if (editorContainer) {
            const quill = new Quill('#editor', {
                theme: 'snow',
                placeholder: 'Write your content here...',
                modules: {
                    toolbar: [
                        [{ 'header': [1, 2, 3, false] }],
                        ['bold', 'italic', 'underline', 'strike'],
                        ['blockquote', 'code-block'],
                        [{ 'list': 'ordered'}, { 'list': 'bullet' }],
                        [{ 'color': [] }, { 'background': [] }],
                        ['link', 'image'],
                        ['clean']
                    ]
                }
            });
            
            // Store editor instance for form submission
            window.quillEditor = quill;
            
            // Update hidden input on form submit
            const forms = document.querySelectorAll('form');
            forms.forEach(form => {
                form.addEventListener('submit', function() {
                    const contentInput = document.getElementById('content');
                    if (contentInput && window.quillEditor) {
                        contentInput.value = window.quillEditor.root.innerHTML;
                    }
                });
            });
        }
    }
    
    // ================================
    // ADMIN SIDEBAR TOGGLE
    // ================================
    const adminMenuToggle = document.getElementById('menuToggle');
    const adminSidebar = document.getElementById('sidebar');
    
    if (adminMenuToggle && adminSidebar) {
        adminMenuToggle.addEventListener('click', function() {
            adminSidebar.classList.toggle('open');
        });
    }
    
    // ================================
    // CONFIRM DELETE
    // ================================
    const deleteBtns = document.querySelectorAll('.delete-btn');
    deleteBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item?')) {
                e.preventDefault();
            }
        });
    });
    
    // ================================
    // CURRENT YEAR
    // ================================
    const yearElements = document.querySelectorAll('.current-year');
    const currentYear = new Date().getFullYear();
    yearElements.forEach(el => {
        el.textContent = currentYear;
    });
    
    console.log('Blog JavaScript loaded successfully');
});