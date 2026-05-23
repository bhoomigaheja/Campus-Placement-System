/**
 * Reusable Premium UI Components for CampusPlacement Cell
 * Implements Tag-Based Inputs, Searchable Multi-Selects, Toast systems, and Form loaders.
 */

document.addEventListener("DOMContentLoaded", function () {
    // 1. Initialize core premium components
    initTagsInputs();
    initSearchableMultiSelects();
    initDatePickerConstraints();
    
    // 2. Setup Centralized Toast Validation Error Scanners and Message managers
    NotificationManager.init();
    
    // 3. Register robust duplicate submission guards
    initDuplicateSubmissionGuard();
});

/* ==========================================================================
   GLOBAL NOTIFICATION MANAGER (SaaS Toast Architecture)
   ========================================================================== */
const NotificationManager = {
    // Unique key to track the last processed server render ID
    RENDER_ID_KEY: 'campus_placement_last_render_id',
    
    // In-memory guard to prevent multiple parsing runs in the exact same script execution cycle
    hasProcessedThisCycle: false,

    init() {
        // Handle pageshow event to capture bfcache restores
        window.addEventListener('pageshow', (e) => {
            if (e.persisted) {
                // Page was loaded from Back-Forward Cache. Force clear messages to prevent replay!
                this.clearMessagesDOM();
            }
        });

        // Run primary toast display
        this.processDjangoMessages();
        this.scanValidationErrors();
    },

    clearMessagesDOM() {
        const messageContainer = document.getElementById('django-messages');
        if (messageContainer) {
            messageContainer.innerHTML = '';
        }
    },

    show(message, type = 'info') {
        let bgColor = "#4f46e5"; // default (indigo)
        let icon = '<i class="bi bi-info-circle-fill me-2 fs-5"></i>';
        
        const cleanType = type.toLowerCase();
        if (cleanType.includes('error') || cleanType.includes('danger')) {
            bgColor = "#ef4444"; // red
            icon = '<i class="bi bi-exclamation-triangle-fill me-2 fs-5"></i>';
        } else if (cleanType.includes('success')) {
            bgColor = "#10b981"; // green
            icon = '<i class="bi bi-check-circle-fill me-2 fs-5"></i>';
        } else if (cleanType.includes('warning')) {
            bgColor = "#f59e0b"; // amber
            icon = '<i class="bi bi-exclamation-octagon-fill me-2 fs-5"></i>';
        }

        Toastify({
            duration: 4500,
            close: true,
            gravity: "top", 
            position: "right",
            escapeMarkup: false, // allow bootstrap icons in toasts
            text: `<div class="d-flex align-items-center">${icon}<span>${message}</span></div>`,
            style: {
                background: bgColor,
                borderRadius: "10px",
                boxShadow: "0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.05)",
                padding: "12px 24px",
                fontWeight: "550",
                fontSize: "0.95rem"
            }
        }).showToast();
    },

    processDjangoMessages() {
        const messageContainer = document.getElementById('django-messages');
        if (!messageContainer) return;

        // Prevent duplicate execution within the exact same page execution cycle
        if (this.hasProcessedThisCycle) return;

        // Detect if page load is a bfcache reload to prevent replaying stale server messages
        const navigationEntries = performance.getEntriesByType("navigation");
        const isBackForward = navigationEntries.length > 0 && navigationEntries[0].type === "back_forward";
        
        if (isBackForward) {
            this.clearMessagesDOM();
            return;
        }

        // Get server-side rendered request timestamp / Render ID
        const currentRenderId = messageContainer.dataset.renderId;
        const lastRenderId = sessionStorage.getItem(this.RENDER_ID_KEY);

        // If the render ID matches the last processed one, it is a cached reload or back-forward navigation replay!
        if (currentRenderId && currentRenderId === lastRenderId) {
            this.clearMessagesDOM();
            return;
        }

        // Mark as processed in this execution cycle and set session last render ID
        this.hasProcessedThisCycle = true;
        if (currentRenderId) {
            sessionStorage.setItem(this.RENDER_ID_KEY, currentRenderId);
        }

        const messages = messageContainer.querySelectorAll('span');
        messages.forEach(msg => {
            const text = msg.textContent.trim();
            const tag = msg.dataset.tag || 'info';

            if (text) {
                this.show(text, tag);
            }
        });

        // Physically clear DOM elements immediately to prevent any potential duplicate scripts from parsing them
        this.clearMessagesDOM();
    },

    scanValidationErrors() {
        // Scan standard Django field validation nodes, form errors, or non-field errors
        // Scoped inside forms or general alerts to avoid parsing general layout links (like 'Logout')
        const errors = document.querySelectorAll('form .text-danger, form .invalid-feedback, form .errorlist li, .alert-danger');
        const toastedMessages = new Set();
        
        errors.forEach(err => {
            // Exclude interactive buttons, links, or specific ignored tags
            if (err.tagName === 'A' || err.tagName === 'BUTTON' || err.closest('a') || err.closest('button')) {
                return;
            }
            const text = err.innerText.trim();
            // Ignore date validation error because it already calls showNotification natively
            if (text && !toastedMessages.has(text) && !err.classList.contains('date-validation-error')) {
                toastedMessages.add(text);
                this.show(text, 'error');
            }
        });
    }
};

// Expose showNotification globally so manual scripts can still call window.showNotification
window.showNotification = function(message, type = 'info') {
    NotificationManager.show(message, type);
};

/* ==========================================================================
   1. TAGS INPUT SYSTEM (SaaS Tags / Skills Input)
   ========================================================================== */
function initTagsInputs() {
    const inputs = document.querySelectorAll('input[data-tags-input="true"]');
    
    const predefinedSuggestions = [
        'Python', 'Django', 'React', 'JavaScript', 'TypeScript', 'SQL', 
        'Java', 'C++', 'C', 'Git', 'AWS', 'Docker', 'Kubernetes',
        'Machine Learning', 'Data Science', 'HTML/CSS', 'PostgreSQL', 
        'Node.js', 'MongoDB', 'Go', 'Rust', 'Swift', 'Kotlin', 'Flutter'
    ];

    inputs.forEach(hiddenInput => {
        if (hiddenInput.classList.contains('initialized-tags')) return;
        hiddenInput.classList.add('initialized-tags');

        hiddenInput.style.display = 'none';

        const wrapper = document.createElement('div');
        wrapper.className = 'tags-input-wrapper';
        hiddenInput.parentNode.insertBefore(wrapper, hiddenInput.nextSibling);

        const chipContainer = document.createElement('div');
        chipContainer.style.display = 'flex';
        chipContainer.style.flexWrap = 'wrap';
        chipContainer.style.gap = '6px';
        chipContainer.style.alignItems = 'center';
        wrapper.appendChild(chipContainer);

        const textInput = document.createElement('input');
        textInput.type = 'text';
        textInput.className = 'tags-input-field';
        textInput.placeholder = hiddenInput.placeholder || 'Type skill and press Enter...';
        wrapper.appendChild(textInput);

        const suggestionsBox = document.createElement('div');
        suggestionsBox.className = 'tags-input-suggestions';
        wrapper.appendChild(suggestionsBox);

        let tags = [];
        if (hiddenInput.value.trim()) {
            tags = hiddenInput.value.split(',').map(s => s.trim()).filter(s => s.length > 0);
        }

        function renderTags() {
            chipContainer.innerHTML = '';
            tags.forEach((tag, idx) => {
                const chip = document.createElement('span');
                chip.className = 'tags-input-chip';
                chip.innerHTML = `
                    <span>${tag}</span>
                    <button type="button" class="tags-input-remove" data-index="${idx}">&times;</button>
                `;
                
                chip.querySelector('.tags-input-remove').addEventListener('click', (e) => {
                    e.stopPropagation();
                    removeTag(idx);
                });
                
                chipContainer.appendChild(chip);
            });
            
            hiddenInput.value = tags.join(', ');
        }

        function addTag(value) {
            const trimmed = value.trim();
            if (trimmed && !tags.includes(trimmed)) {
                tags.push(trimmed);
                renderTags();
            }
            textInput.value = '';
            hideSuggestions();
        }

        function removeTag(index) {
            tags.splice(index, 1);
            renderTags();
            textInput.focus();
        }

        function filterSuggestions(query) {
            suggestionsBox.innerHTML = '';
            if (!query.trim()) {
                hideSuggestions();
                return;
            }

            const cleanQuery = query.toLowerCase().trim();
            const matches = predefinedSuggestions.filter(s => 
                s.toLowerCase().includes(cleanQuery) && !tags.includes(s)
            );

            if (matches.length === 0) {
                hideSuggestions();
                return;
            }

            matches.forEach(match => {
                const item = document.createElement('div');
                item.className = 'tags-input-suggestion-item';
                item.innerText = match;
                item.addEventListener('click', () => {
                    addTag(match);
                    textInput.focus();
                });
                suggestionsBox.appendChild(item);
            });

            suggestionsBox.style.display = 'block';
        }

        function hideSuggestions() {
            setTimeout(() => {
                suggestionsBox.style.display = 'none';
            }, 200);
        }
        
        textInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ',') {
                e.preventDefault();
                if (textInput.value.trim()) {
                    addTag(textInput.value);
                }
            } else if (e.key === 'Backspace' && !textInput.value) {
                if (tags.length > 0) {
                    removeTag(tags.length - 1);
                }
            }
        });

        textInput.addEventListener('input', (e) => {
            filterSuggestions(e.target.value);
        });

        textInput.addEventListener('focus', () => {
            if (textInput.value) filterSuggestions(textInput.value);
        });

        textInput.addEventListener('blur', () => {
            hideSuggestions();
        });

        wrapper.addEventListener('click', () => {
            textInput.focus();
        });

        renderTags();
    });
}

/* ==========================================================================
   2. SEARCHABLE MULTI-SELECT DROPDOWN (SaaS Select2-Alternative)
   ========================================================================== */
function initSearchableMultiSelects() {
    const selectElements = document.querySelectorAll('select[multiple]');

    selectElements.forEach(selectEl => {
        if (selectEl.classList.contains('initialized-multiselect')) return;
        selectEl.classList.add('initialized-multiselect');

        selectEl.style.display = 'none';

        const wrapper = document.createElement('div');
        wrapper.className = 'multi-select-wrapper';
        selectEl.parentNode.insertBefore(wrapper, selectEl.nextSibling);

        const trigger = document.createElement('div');
        trigger.className = 'multi-select-trigger';
        wrapper.appendChild(trigger);

        const dropdown = document.createElement('div');
        dropdown.className = 'multi-select-dropdown';
        wrapper.appendChild(dropdown);

        const searchContainer = document.createElement('div');
        searchContainer.className = 'multi-select-search-container';
        searchContainer.innerHTML = `
            <i class="bi bi-search"></i>
            <input type="text" class="multi-select-search-input" placeholder="Search branches...">
        `;
        dropdown.appendChild(searchContainer);
        const searchInput = searchContainer.querySelector('.multi-select-search-input');

        const optionsList = document.createElement('div');
        optionsList.className = 'multi-select-options-list';
        dropdown.appendChild(optionsList);

        let options = [];
        
        function syncOptionsFromOriginal() {
            options = Array.from(selectEl.options).map(opt => ({
                value: opt.value,
                text: opt.text,
                selected: opt.selected
            }));
        }

        function renderTrigger() {
            trigger.innerHTML = '';
            const selectedCount = options.filter(o => o.selected).length;

            if (selectedCount === 0) {
                trigger.innerHTML = `<span class="multi-select-trigger-placeholder">Select eligible branches...</span>`;
                return;
            }

            options.forEach(opt => {
                if (opt.selected) {
                    const chip = document.createElement('span');
                    chip.className = 'multi-select-trigger-chip';
                    chip.innerHTML = `
                        <span>${opt.text}</span>
                        <span class="multi-select-remove-chip" data-value="${opt.value}">&times;</span>
                    `;
                    
                    chip.querySelector('.multi-select-remove-chip').addEventListener('click', (e) => {
                        e.stopPropagation();
                        toggleOption(opt.value, false);
                    });

                    trigger.appendChild(chip);
                }
            });
        }

        function renderDropdownList(filterText = '') {
            optionsList.innerHTML = '';
            const cleanFilter = filterText.toLowerCase().trim();

            options.forEach(opt => {
                if (cleanFilter && !opt.text.toLowerCase().includes(cleanFilter)) {
                    return;
                }

                const item = document.createElement('div');
                item.className = `multi-select-option-item ${opt.selected ? 'selected' : ''}`;
                item.innerHTML = `
                    <input type="checkbox" ${opt.selected ? 'checked' : ''}>
                    <span>${opt.text}</span>
                `;

                // Handle both label click and physical checkbox toggling safely
                item.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const checkbox = item.querySelector('input[type="checkbox"]');
                    const isNowChecked = (e.target === checkbox) ? checkbox.checked : !checkbox.checked;
                    toggleOption(opt.value, isNowChecked);
                });

                optionsList.appendChild(item);
            });
        }

        function toggleOption(value, isSelected) {
            options.forEach(o => {
                if (o.value === value) o.selected = isSelected;
            });

            // Set both the in-memory property and physical DOM attributes to guarantee browser serialization
            Array.from(selectEl.options).forEach(opt => {
                if (opt.value === value) {
                    opt.selected = isSelected;
                    if (isSelected) {
                        opt.setAttribute('selected', 'selected');
                    } else {
                        opt.removeAttribute('selected');
                    }
                }
            });

            selectEl.dispatchEvent(new Event('change'));

            renderTrigger();
            renderDropdownList(searchInput.value);
        }

        trigger.addEventListener('click', (e) => {
            e.stopPropagation();
            const isOpen = wrapper.classList.contains('open');
            
            document.querySelectorAll('.multi-select-wrapper').forEach(w => w.classList.remove('open'));
            
            if (!isOpen) {
                wrapper.classList.add('open');
                searchInput.focus();
                renderDropdownList();
            } else {
                wrapper.classList.remove('open');
            }
        });

        searchInput.addEventListener('input', (e) => {
            renderDropdownList(e.target.value);
        });

        document.addEventListener('click', (e) => {
            if (!wrapper.contains(e.target)) {
                wrapper.classList.remove('open');
                searchInput.value = '';
            }
        });

        syncOptionsFromOriginal();
        renderTrigger();
    });
}

/* ==========================================================================
   3. DATETIME PICKER FUTURE CONSTRAINTS
   ========================================================================== */
function initDatePickerConstraints() {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const currentDateTime = `${year}-${month}-${day}T${hours}:${minutes}`;
    
    document.querySelectorAll('input[type="datetime-local"]').forEach(input => {
        input.min = currentDateTime;
        
        input.addEventListener('change', function () {
            const selectedDate = new Date(this.value);
            const parent = this.parentElement;
            
            const existingError = parent.querySelector('.date-validation-error');
            if (existingError) existingError.remove();

            if (selectedDate < new Date()) {
                const errorDiv = document.createElement('div');
                errorDiv.className = 'text-danger small fw-medium mt-1 date-validation-error';
                errorDiv.innerHTML = '<i class="bi bi-exclamation-triangle-fill me-1"></i>Please select a future date/time.';
                parent.appendChild(errorDiv);
                
                this.classList.add('is-invalid');
                window.showNotification("Application deadline must be in the future.", "error");
            } else {
                this.classList.remove('is-invalid');
            }
        });
    });
}

/* ==========================================================================
   6. DUPLICATE SUBMISSION AND SCREEN-LOCK GUARD
   ========================================================================== */
function initDuplicateSubmissionGuard() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function (e) {
            // Verify HTML5 validation state before triggering screens locks
            if (form.checkValidity && !form.checkValidity()) {
                return; // Let browser trigger native tooltips
            }
            
            // Lock form button to prevent double-clicks
            const submits = form.querySelectorAll('button[type="submit"], input[type="submit"]');
            submits.forEach(btn => {
                btn.disabled = true;
                if (btn.tagName === 'BUTTON') {
                    btn.innerHTML = `<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Processing...`;
                }
            });
            
            const loader = document.getElementById('globalLoader');
            if (loader) {
                loader.classList.add('active');
            }
        });
    });
}