/* ═══════════════════════════════════════════════════════════════════
   Research Cloud Portal — JavaScript
   Multi-step wizard, file upload, real-time polling, animations
   ═══════════════════════════════════════════════════════════════════ */

// ── Wizard Navigation ──────────────────────────────────────────────
let currentStep = 1;
const totalSteps = 5;

function wizardNext() {
    if (currentStep < totalSteps) {
        setWizardStep(currentStep + 1);
    }
}

function wizardPrev() {
    if (currentStep > 1) {
        setWizardStep(currentStep - 1);
    }
}

function setWizardStep(step) {
    // Hide current step
    const currentEl = document.getElementById(`step-${currentStep}`);
    if (currentEl) currentEl.classList.remove('active');

    // Show new step
    const newEl = document.getElementById(`step-${step}`);
    if (newEl) newEl.classList.add('active');

    // Update progress indicators
    document.querySelectorAll('.progress-step').forEach((el, index) => {
        const stepNum = index + 1;
        el.classList.remove('active', 'completed');
        if (stepNum === step) {
            el.classList.add('active');
        } else if (stepNum < step) {
            el.classList.add('completed');
        }
    });

    // Update progress lines
    document.querySelectorAll('.progress-line').forEach((el, index) => {
        if (index < step - 1) {
            el.classList.add('active');
        } else {
            el.classList.remove('active');
        }
    });

    currentStep = step;

    // If on review step, populate the review values
    if (step === 5) {
        populateReview();
    }

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function populateReview() {
    // OS
    const osRadio = document.querySelector('input[name="os_image"]:checked');
    if (osRadio) {
        const osLabel = osRadio.closest('.option-card').querySelector('h3');
        const reviewOs = document.getElementById('review-os');
        if (reviewOs && osLabel) reviewOs.textContent = osLabel.textContent;
    }

    // CPU
    const cpuRadio = document.querySelector('input[name="cpu"]:checked');
    if (cpuRadio) {
        const reviewCpu = document.getElementById('review-cpu');
        if (reviewCpu) reviewCpu.textContent = cpuRadio.value + (cpuRadio.value === '1' ? ' Core' : ' Cores');
    }

    // RAM
    const ramRadio = document.querySelector('input[name="ram"]:checked');
    if (ramRadio) {
        const ramMB = parseInt(ramRadio.value);
        const reviewRam = document.getElementById('review-ram');
        if (reviewRam) reviewRam.textContent = ramMB >= 1024 ? (ramMB / 1024) + ' GB' : ramMB + ' MB';
    }

    // GPU
    const gpuCheck = document.getElementById('gpu-toggle');
    const reviewGpu = document.getElementById('review-gpu');
    if (reviewGpu) reviewGpu.textContent = gpuCheck && gpuCheck.checked ? '✅ Enabled' : '❌ Disabled';

    // Software Stack
    const stackRadio = document.querySelector('input[name="software_stack"]:checked');
    if (stackRadio) {
        const stackLabel = stackRadio.closest('.option-card').querySelector('h3');
        const reviewStack = document.getElementById('review-stack');
        if (reviewStack && stackLabel) reviewStack.textContent = stackLabel.textContent;
    }

    // Dataset
    const fileInput = document.getElementById('dataset-input');
    const reviewDataset = document.getElementById('review-dataset');
    if (reviewDataset) {
        if (fileInput && fileInput.files.length > 0) {
            reviewDataset.textContent = fileInput.files[0].name;
        } else {
            reviewDataset.textContent = 'No dataset uploaded';
        }
    }
}


// ── File Upload ────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    const uploadArea = document.getElementById('upload-area');
    const fileInput = document.getElementById('dataset-input');
    const preview = document.getElementById('upload-preview');
    const uploadContent = uploadArea ? uploadArea.querySelector('.upload-content') : null;

    if (uploadArea && fileInput) {
        // Drag & Drop
        ['dragenter', 'dragover'].forEach(evt => {
            uploadArea.addEventListener(evt, (e) => {
                e.preventDefault();
                uploadArea.classList.add('dragover');
            });
        });

        ['dragleave', 'drop'].forEach(evt => {
            uploadArea.addEventListener(evt, (e) => {
                e.preventDefault();
                uploadArea.classList.remove('dragover');
            });
        });

        uploadArea.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            if (files.length) {
                fileInput.files = files;
                showFilePreview(files[0]);
            }
        });

        fileInput.addEventListener('change', () => {
            if (fileInput.files.length) {
                showFilePreview(fileInput.files[0]);
            }
        });
    }

    function showFilePreview(file) {
        if (preview && uploadContent) {
            document.getElementById('preview-filename').textContent = file.name;
            document.getElementById('preview-filesize').textContent = formatFileSize(file.size);
            preview.style.display = 'flex';
            uploadContent.style.display = 'none';
        }
    }

    // Auto-dismiss flash messages
    document.querySelectorAll('.flash').forEach((flash) => {
        setTimeout(() => {
            flash.style.animation = 'slideOutRight 0.4s ease forwards';
            setTimeout(() => flash.remove(), 400);
        }, 5000);
    });

    // Animate stat counters
    document.querySelectorAll('.stat-value[data-count]').forEach((el) => {
        const target = parseInt(el.dataset.count);
        if (target > 0) {
            animateCounter(el, target);
        }
    });
});


function removeFile() {
    const fileInput = document.getElementById('dataset-input');
    const preview = document.getElementById('upload-preview');
    const uploadContent = document.querySelector('.upload-content');

    if (fileInput) fileInput.value = '';
    if (preview) preview.style.display = 'none';
    if (uploadContent) uploadContent.style.display = 'block';
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}


// ── Counter Animation ──────────────────────────────────────────────
function animateCounter(el, target) {
    let current = 0;
    const duration = 1000;
    const step = target / (duration / 16);

    function update() {
        current += step;
        if (current >= target) {
            el.textContent = target;
            return;
        }
        el.textContent = Math.floor(current);
        requestAnimationFrame(update);
    }

    requestAnimationFrame(update);
}


// ── Job Status Polling ─────────────────────────────────────────────
function pollJobStatus(jobId) {
    const interval = setInterval(async () => {
        try {
            const response = await fetch(`/job/${jobId}/status`);
            if (!response.ok) return;

            const data = await response.json();

            // Update status text
            const statusText = document.getElementById('job-status-text');
            if (statusText) statusText.textContent = capitalize(data.status);

            // Update status sub
            const statusSub = document.getElementById('job-status-sub');
            if (statusSub) {
                const messages = {
                    'pending': 'Waiting in queue for provisioning...',
                    'provisioning': 'Setting up your virtual machine...',
                    'running': 'Executing your workload on the cloud...',
                    'completed': 'Your results are ready for download!',
                    'failed': data.error_message || 'An error occurred during execution.',
                };
                statusSub.textContent = messages[data.status] || '';
            }

            // Update VM info
            if (data.vm_id) {
                const vmIdEl = document.getElementById('vm-id-value');
                if (vmIdEl) vmIdEl.textContent = data.vm_id;
            }
            if (data.vm_ip) {
                const vmIpEl = document.getElementById('vm-ip-value');
                if (vmIpEl) vmIpEl.textContent = data.vm_ip;
            }

            // If job finished, reload the page for full UI update
            if (['completed', 'failed'].includes(data.status)) {
                clearInterval(interval);
                setTimeout(() => location.reload(), 1000);
            }
        } catch (e) {
            console.error('Status poll error:', e);
        }
    }, 3000);
}

function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}


// ── Slide Out Animation (for flash dismiss) ────────────────────────
const styleSheet = document.createElement('style');
styleSheet.textContent = `
    @keyframes slideOutRight {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(styleSheet);
