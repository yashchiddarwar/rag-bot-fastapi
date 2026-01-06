// Check if running from file system
if (window.location.protocol === 'file:') {
    alert('Error: You are opening this file directly. Please run the Python server (python main.py) and access http://localhost:8000');
}

const chatContainer = document.getElementById('chatContainer');
const questionInput = document.getElementById('questionInput');
const sendButton = document.getElementById('sendButton');

// Format text with basic markdown-like syntax
function formatText(text) {
    if (!text) return '';
    
    // Escape HTML to prevent XSS
    let formatted = text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");

    // Bold: **text**
    formatted = formatted.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    
    // Code blocks: `text`
    formatted = formatted.replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>');
    
    // Bullet points: - text or * text
    formatted = formatted.replace(/^[\-\*]\s+(.+)$/gm, '• $1');
    
    // Line breaks
    formatted = formatted.replace(/\n/g, '<br>');
    
    return formatted;
}

function addMessage(content, isUser, sources = null) {
    // Remove empty state if it exists
    const emptyState = chatContainer.querySelector('.empty-state');
    if (emptyState) {
        emptyState.remove();
    }

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user' : 'bot'}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = isUser ? '👤' : '🤖';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    if (isUser) {
        contentDiv.textContent = content;
    } else {
        contentDiv.innerHTML = formatText(content);
    }

    if (sources && sources.length > 0) {
        const sourcesDiv = document.createElement('div');
        sourcesDiv.className = 'sources';
        sourcesDiv.innerHTML = '<strong>📚 Sources:</strong>';
        
        sources.forEach(source => {
            const tag = document.createElement('span');
            tag.className = 'source-tag';
            tag.textContent = source;
            tag.onclick = () => viewDocument(source);
            sourcesDiv.appendChild(tag);
        });
        
        contentDiv.appendChild(sourcesDiv);
    }

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);
    chatContainer.appendChild(messageDiv);
    
    // Scroll to bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function addLoading() {
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message bot';
    loadingDiv.id = 'loading';

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = '🤖';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content loading';
    contentDiv.innerHTML = '<span></span><span></span><span></span>';

    loadingDiv.appendChild(avatar);
    loadingDiv.appendChild(contentDiv);
    chatContainer.appendChild(loadingDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function removeLoading() {
    const loading = document.getElementById('loading');
    if (loading) {
        loading.remove();
    }
}

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = `❌ ${message}`;
    chatContainer.appendChild(errorDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

async function sendQuestion() {
    const question = questionInput.value.trim();
    if (!question) return;

    addMessage(question, true);
    questionInput.value = '';
    sendButton.disabled = true;
    addLoading();

    try {
        const response = await fetch('/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ question: question })
        });

        removeLoading();

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to get response');
        }

        const data = await response.json();
        addMessage(data.answer, false, data.sources);
    } catch (error) {
        removeLoading();
        showError(error.message || 'Something went wrong. Please try again.');
    } finally {
        sendButton.disabled = false;
        questionInput.focus();
    }
}

function askQuestion(question) {
    questionInput.value = question;
    sendQuestion();
}

function handleKeyPress(event) {
    if (event.key === 'Enter') {
        sendQuestion();
    }
}

// Document Viewing Logic
async function viewDocument(filename) {
    const modal = document.getElementById('documentModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalBody = document.getElementById('modalBody');

    modalTitle.textContent = filename.replace('.md', '').replace(/_/g, ' ');
    modalBody.innerHTML = '<p style="text-align: center; color: #999;">Loading...</p>';
    modal.classList.add('active');

    try {
        const response = await fetch(`/documents/${filename}`);
        if (!response.ok) throw new Error('Failed to load document');

        const data = await response.json();
        // Simple markdown rendering for the modal
        const content = data.content
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/\n/g, '<br>');
            
        modalBody.innerHTML = `<div style="font-family: monospace; white-space: pre-wrap;">${content}</div>`;
    } catch (error) {
        modalBody.innerHTML = `<p style="color: #dc2626;">Error loading document: ${error.message}</p>`;
    }
}

async function showKnowledgeBase(event) {
    if (event) event.preventDefault();
    
    const modal = document.getElementById('documentModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalBody = document.getElementById('modalBody');

    modalTitle.textContent = '📚 Knowledge Base';
    modalBody.innerHTML = '<p style="text-align: center; color: #999;">Loading...</p>';
    modal.classList.add('active');

    try {
        const response = await fetch('/documents');
        if (!response.ok) throw new Error(`Server returned ${response.status}: ${response.statusText}`);

        const data = await response.json();
        
        let html = '<div class="doc-list">';
        if (data.documents && data.documents.length > 0) {
            data.documents.forEach(doc => {
                html += `
                    <div class="doc-item" onclick="viewDocument('${doc.filename}')">
                        <h3>${doc.filename}</h3>
                        <p>Click to view content</p>
                    </div>
                `;
            });
        } else {
            html += '<p>No documents found.</p>';
        }
        html += '</div>';
        
        modalBody.innerHTML = html;
    } catch (error) {
        console.error('Error fetching documents:', error);
        let errorMsg = error.message;
        if (error.message === 'Failed to fetch') {
            errorMsg = 'Cannot connect to server. Is it running?';
        }
        modalBody.innerHTML = `<div style="text-align: center; padding: 20px;">
            <p style="color: #dc2626; margin-bottom: 10px;">❌ Error loading knowledge base</p>
            <p style="color: #666; font-size: 13px;">${errorMsg}</p>
        </div>`;
    }
}

function closeModal() {
    const modal = document.getElementById('documentModal');
    modal.classList.remove('active');
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    // Close modal when clicking outside
    const modal = document.getElementById('documentModal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                closeModal();
            }
        });
    }

    // Focus input on load
    if (questionInput) {
        questionInput.focus();
    }
});
