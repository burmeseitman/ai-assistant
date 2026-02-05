document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const loginPage = document.getElementById('login-page');
    const mainPage = document.getElementById('main-page');
    const loginError = document.getElementById('login-error');

    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const messagesContainer = document.getElementById('messages');

    const navItems = document.querySelectorAll('.nav-item[data-page]');
    const tabContents = document.querySelectorAll('.tab-content');

    const aiModeSelect = document.getElementById('ai-mode-select');
    const apiKeyContainer = document.getElementById('api-key-container');
    const saveSettingsBtn = document.getElementById('save-settings-btn');
    const apiKeyInput = document.getElementById('api-key-input');

    const logoutBtn = document.getElementById('logout-btn');
    const botStatusAlert = document.getElementById('bot-status-alert');
    const telegramTokenInput = document.getElementById('telegram-token-input');
    const botStatusBadge = document.getElementById('bot-status-badge');

    let token = localStorage.getItem('token');

    if (token) {
        showMainPage();
    }

    // Login logic
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);

        try {
            const response = await fetch('/login', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const data = await response.json();
                token = data.access_token;
                localStorage.setItem('token', token);
                showMainPage();
            } else {
                loginError.textContent = 'Invalid username or password';
                loginError.classList.remove('hidden');
            }
        } catch (err) {
            loginError.textContent = 'Connection error';
            loginError.classList.remove('hidden');
        }
    });

    logoutBtn.addEventListener('click', () => {
        localStorage.removeItem('token');
        location.reload();
    });

    function showMainPage() {
        loginPage.classList.add('hidden');
        mainPage.classList.remove('hidden');
        loadSettings();
    }

    // Navigation
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const page = item.getAttribute('data-page');

            navItems.forEach(n => n.classList.remove('active'));
            item.classList.add('active');

            tabContents.forEach(tab => {
                if (tab.id === `${page}-tab`) {
                    tab.classList.remove('hidden');
                } else {
                    tab.classList.add('hidden');
                }
            });
        });
    });

    // Chat Logic
    async function sendMessage() {
        const text = chatInput.value.trim();
        if (!text) return;

        appendMessage('user', text);
        chatInput.value = '';

        const aiMsgDiv = appendMessage('ai', 'Thinking...');

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text })
            });

            const data = await response.json();
            aiMsgDiv.textContent = data.response;
        } catch (err) {
            aiMsgDiv.textContent = 'Error: Could not reach the assistant.';
        }
    }

    sendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    function appendMessage(role, text) {
        const div = document.createElement('div');
        div.className = `message ${role}`;
        div.textContent = text;
        messagesContainer.appendChild(div);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        return div;
    }

    // Settings Logic
    aiModeSelect.addEventListener('change', () => {
        if (aiModeSelect.value === 'api') {
            apiKeyContainer.classList.remove('hidden');
        } else {
            apiKeyContainer.classList.add('hidden');
        }
    });

    async function loadSettings() {
        try {
            const response = await fetch('/settings');
            const data = await response.json();
            aiModeSelect.value = data.ai_mode;
            apiKeyInput.value = data.api_key || '';
            telegramTokenInput.value = data.telegram_bot_token || '';

            if (data.ai_mode === 'api') {
                apiKeyContainer.classList.remove('hidden');
            }

            updateBotStatusUI(data.bot_status);
        } catch (err) {
            console.error('Failed to load settings');
        }
    }

    function updateBotStatusUI(status) {
        if (!status) return;

        if (status.ok) {
            botStatusAlert.classList.add('hidden');
            botStatusBadge.textContent = status.message;
            botStatusBadge.className = 'status-badge online';
        } else {
            botStatusAlert.classList.remove('hidden');
            botStatusBadge.textContent = status.message;
            botStatusBadge.className = 'status-badge offline';
        }
    }

    saveSettingsBtn.addEventListener('click', async () => {
        const payload = {
            ai_mode: aiModeSelect.value,
            api_key: apiKeyInput.value,
            telegram_bot_token: telegramTokenInput.value
        };

        try {
            const response = await fetch('/settings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await response.json();
            updateBotStatusUI(data.settings.bot_status);
            alert('Settings saved!');
        } catch (err) {
            alert('Failed to save settings');
        }
    });
});
