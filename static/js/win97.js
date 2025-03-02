// Global Variables
let activeWindow = null;
let windows = {};
let isDragging = false;
let dragOffsetX = 0;
let dragOffsetY = 0;
let isStartMenuOpen = false;
let isMaximized = {};
let windowPositions = {};
let windowSizes = {};
let soundEnabled = true;

// API Configuration
const API_BASE_URL = window.location.origin;
let API_KEY = localStorage.getItem('api_key') || '';

// Initialize when DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Load window elements
    document.querySelectorAll('.window').forEach(function(windowElement) {
        windows[windowElement.id] = windowElement;
        isMaximized[windowElement.id] = false;
    });

    // Initialize window drag functionality
    initWindowDrag();

    // Initialize taskbar
    updateTaskbar();
    
    // Initialize the digital clock
    updateClock();
    setInterval(updateClock, 60000); // Update every minute
    
    // Initialize start menu
    const startButton = document.getElementById('start-button');
    const startMenu = document.getElementById('start-menu');
    
    startButton.addEventListener('click', function() {
        toggleStartMenu();
    });

    // Close start menu when clicking elsewhere
    document.addEventListener('click', function(event) {
        if (!event.target.closest('#start-menu') && !event.target.closest('#start-button') && isStartMenuOpen) {
            toggleStartMenu();
        }
    });

    // Handle Enter key in chat input
    document.getElementById('chat-input').addEventListener('keydown', function(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            sendMessage();
        }
    });

    // Handle window focus on click
    document.querySelectorAll('.window').forEach(function(windowEl) {
        windowEl.addEventListener('mousedown', function() {
            activateWindow(windowEl.id);
        });
    });

    // Handle tab switching
    document.querySelectorAll('.tab-button').forEach(function(button) {
        button.addEventListener('click', function() {
            const tabId = this.getAttribute('onclick').match(/'([^']+)'/)[1];
            showTab(tabId);
        });
    });

    // Handle help tab switching
    document.querySelectorAll('.help-sidebar-item').forEach(function(item) {
        item.addEventListener('click', function() {
            const tabId = this.getAttribute('onclick').match(/'([^']+)'/)[1];
            showHelpTab(tabId);
        });
    });

    // Attach event listeners to analysis buttons
    document.getElementById('quick-token').addEventListener('change', function() {
        const resultsContainer = document.getElementById('quick-analysis-results');
        resultsContainer.innerHTML = '<div class="placeholder-message"><p>Select a cryptocurrency and click "Run Analysis" to see results.</p></div>';
    });

    document.getElementById('technical-token').addEventListener('change', function() {
        const resultsContainer = document.getElementById('technical-analysis-results');
        resultsContainer.innerHTML = '<div class="placeholder-message"><p>Configure your technical analysis parameters and click "Calculate Indicators".</p></div>';
    });

    document.getElementById('whale-token').addEventListener('change', function() {
        const resultsContainer = document.getElementById('whale-analysis-results');
        resultsContainer.innerHTML = '<div class="placeholder-message"><p>Select a cryptocurrency and click "Analyze Whale Activity" to see whale dominance metrics.</p></div>';
    });

    // Load settings
    loadSettings();

    // Play startup sound
    playSound('startup-sound');
});

// Window Management Functions

function openWindow(windowId) {
    playSound('click-sound');
    
    if (windows[windowId]) {
        windows[windowId].style.display = 'block';
        
        // Remove minimized class if present
        windows[windowId].classList.remove('minimized');
        
        // Activate the window
        activateWindow(windowId);
        
        // Add to taskbar if not there already
        updateTaskbar();
    }
}

function closeWindow(windowId) {
    playSound('click-sound');
    
    if (windows[windowId]) {
        windows[windowId].style.display = 'none';
        
        // If this was the active window, remove the active class
        windows[windowId].classList.remove('active');
        
        // Update the taskbar
        updateTaskbar();
        
        // If there are other visible windows, activate the last one
        let visibleWindows = Array.from(document.querySelectorAll('.window'))
            .filter(w => w.style.display !== 'none' && !w.classList.contains('minimized'));
        
        if (visibleWindows.length > 0) {
            activateWindow(visibleWindows[visibleWindows.length - 1].id);
        }
    }
}

function minimizeWindow(windowId) {
    playSound('click-sound');
    
    if (windows[windowId]) {
        // Add minimized class
        windows[windowId].classList.add('minimized');
        
        // Remove active class
        windows[windowId].classList.remove('active');
        
        // Update the active window variable if needed
        if (activeWindow === windowId) {
            activeWindow = null;
        }
        
        // Update the taskbar
        updateTaskbar();
    }
}

function toggleMaximize(windowId) {
    playSound('click-sound');
    
    if (windows[windowId]) {
        if (!isMaximized[windowId]) {
            // Save current position and size before maximizing
            windowPositions[windowId] = {
                top: windows[windowId].style.top,
                left: windows[windowId].style.left
            };
            
            windowSizes[windowId] = {
                width: windows[windowId].style.width,
                height: windows[windowId].style.height
            };
            
            // Apply maximized class
            windows[windowId].classList.add('maximized');
            isMaximized[windowId] = true;
        } else {
            // Restore previous position and size
            if (windowPositions[windowId]) {
                windows[windowId].style.top = windowPositions[windowId].top;
                windows[windowId].style.left = windowPositions[windowId].left;
            }
            
            if (windowSizes[windowId]) {
                windows[windowId].style.width = windowSizes[windowId].width;
                windows[windowId].style.height = windowSizes[windowId].height;
            }
            
            // Remove maximized class
            windows[windowId].classList.remove('maximized');
            isMaximized[windowId] = false;
        }
        
        // Activate the window
        activateWindow(windowId);
    }
}

function activateWindow(windowId) {
    // Remove active class from all windows
    document.querySelectorAll('.window').forEach(function(win) {
        win.classList.remove('active');
    });
    
    // Add active class to the selected window
    if (windows[windowId]) {
        windows[windowId].classList.add('active');
        
        // Bring to front by setting a higher z-index
        windows[windowId].style.zIndex = getHighestZIndex() + 1;
        
        // Update active window variable
        activeWindow = windowId;
        
        // Update taskbar to show active window
        updateTaskbar();
    }
}

function getHighestZIndex() {
    let highest = 10; // Start from base z-index for windows
    
    document.querySelectorAll('.window').forEach(function(win) {
        const zIndex = parseInt(window.getComputedStyle(win).zIndex, 10);
        if (zIndex > highest) {
            highest = zIndex;
        }
    });
    
    return highest;
}

function initWindowDrag() {
    // Enable dragging for all window title bars
    document.querySelectorAll('.title-bar').forEach(function(titleBar) {
        titleBar.addEventListener('mousedown', function(e) {
            // Don't start drag if clicking on a title bar button
            if (e.target.closest('.title-bar-button')) {
                return;
            }
            
            const windowElement = titleBar.closest('.window');
            const windowId = windowElement.id;
            
            // Activate the window on drag start
            activateWindow(windowId);
            
            // Don't drag maximized windows
            if (isMaximized[windowId]) {
                return;
            }
            
            isDragging = true;
            
            // Calculate offset of click relative to window position
            const windowRect = windowElement.getBoundingClientRect();
            dragOffsetX = e.clientX - windowRect.left;
            dragOffsetY = e.clientY - windowRect.top;
            
            // Add dragging class
            windowElement.classList.add('dragging');
            
            // Prevent text selection while dragging
            e.preventDefault();
        });
    });
    
    // Handle drag movement
    document.addEventListener('mousemove', function(e) {
        if (isDragging && activeWindow) {
            const windowElement = windows[activeWindow];
            
            // Calculate new position
            let newLeft = e.clientX - dragOffsetX;
            let newTop = e.clientY - dragOffsetY;
            
            // Constrain to window boundaries
            newLeft = Math.max(0, Math.min(newLeft, window.innerWidth - 100));
            newTop = Math.max(0, Math.min(newTop, window.innerHeight - 30));
            
            // Update position
            windowElement.style.left = newLeft + 'px';
            windowElement.style.top = newTop + 'px';
        }
    });
    
    // Handle drag end
    document.addEventListener('mouseup', function() {
        if (isDragging && activeWindow) {
            // Remove dragging class
            windows[activeWindow].classList.remove('dragging');
            isDragging = false;
        }
    });
}

// Taskbar Functions

function updateTaskbar() {
    const taskbarEntries = document.getElementById('taskbar-entries');
    taskbarEntries.innerHTML = '';
    
    // Add taskbar entries for open windows
    document.querySelectorAll('.window').forEach(function(windowEl) {
        if (windowEl.style.display !== 'none' || windowEl.classList.contains('minimized')) {
            const taskbarEntry = document.createElement('div');
            taskbarEntry.className = 'taskbar-entry';
            if (windowEl.classList.contains('active') && !windowEl.classList.contains('minimized')) {
                taskbarEntry.classList.add('active');
            }
            
            // Get title text
            const titleText = windowEl.querySelector('.title-bar-text').textContent.trim();
            
            // Get icon based on window id
            let iconPath = '';
            switch(windowEl.id) {
                case 'chat-window':
                    iconPath = 'static/img/w95_27.png';
                    break;
                case 'analysis-window':
                    iconPath = 'static/img/w95_52.png';
                    break;
                case 'settings-window':
                    iconPath = 'static/img/w2k_control_panel.png';
                    break;
                case 'help-window':
                    iconPath = 'static/img/w95_46.png';
                    break;
                default:
                    iconPath = 'static/img/w95_9.png';
            }
            
            // Add icon and text
            const icon = document.createElement('img');
            icon.className = 'taskbar-entry-icon';
            icon.src = iconPath;
            icon.alt = '';
            
            const text = document.createElement('span');
            text.className = 'taskbar-entry-text';
            text.textContent = titleText;
            
            taskbarEntry.appendChild(icon);
            taskbarEntry.appendChild(text);
            
            // Add click handler
            taskbarEntry.addEventListener('click', function() {
                playSound('click-sound');
                
                if (windowEl.classList.contains('minimized')) {
                    // Restore window from minimized state
                    windowEl.classList.remove('minimized');
                    activateWindow(windowEl.id);
                } else if (windowEl.classList.contains('active')) {
                    // Minimize if already active
                    minimizeWindow(windowEl.id);
                } else {
                    // Activate if not active
                    activateWindow(windowEl.id);
                }
            });
            
            taskbarEntries.appendChild(taskbarEntry);
        }
    });
}

// Start Menu Functions

function toggleStartMenu() {
    playSound('click-sound');
    
    const startMenu = document.getElementById('start-menu');
    const startButton = document.getElementById('start-button');
    
    if (isStartMenuOpen) {
        startMenu.classList.remove('active');
        startButton.classList.remove('active');
    } else {
        startMenu.classList.add('active');
        startButton.classList.add('active');
    }
    
    isStartMenuOpen = !isStartMenuOpen;
}

// Tab Functions

function showTab(tabId) {
    playSound('click-sound');
    
    // Hide all tab panes
    document.querySelectorAll('.tab-pane').forEach(function(tab) {
        tab.classList.remove('active');
    });
    
    // Show the selected tab pane
    const selectedTab = document.getElementById(tabId);
    if (selectedTab) {
        selectedTab.classList.add('active');
    }
    
    // Update tab buttons
    document.querySelectorAll('.tab-button').forEach(function(button) {
        button.classList.remove('active');
        
        // Check if this button's onclick references the current tab
        if (button.getAttribute('onclick').includes(`'${tabId}'`)) {
            button.classList.add('active');
        }
    });
}

function showHelpTab(tabId) {
    playSound('click-sound');
    
    // Hide all help tab content
    document.querySelectorAll('.help-tab-content').forEach(function(tab) {
        tab.classList.remove('active');
    });
    
    // Show the selected help tab content
    const selectedTab = document.getElementById(tabId);
    if (selectedTab) {
        selectedTab.classList.add('active');
    }
    
    // Update help sidebar items
    document.querySelectorAll('.help-sidebar-item').forEach(function(item) {
        item.classList.remove('active');
        
        // Check if this item's onclick references the current tab
        if (item.getAttribute('onclick').includes(`'${tabId}'`)) {
            item.classList.add('active');
        }
    });
}

// Clock Function

function updateClock() {
    const now = new Date();
    let hours = now.getHours();
    const minutes = now.getMinutes();
    const ampm = hours >= 12 ? 'PM' : 'AM';
    
    hours = hours % 12;
    hours = hours ? hours : 12; // the hour '0' should be '12'
    
    const timeString = hours + ':' + (minutes < 10 ? '0' + minutes : minutes) + ' ' + ampm;
    document.getElementById('taskbar-time').textContent = timeString;
}

// Sound Functions

function playSound(soundId) {
    if (soundEnabled) {
        const sound = document.getElementById(soundId);
        if (sound) {
            // Check if the sound file actually exists/loaded properly
            if (sound.readyState > 0) {
                sound.currentTime = 0;
                sound.play().catch(e => {
                    console.log('Error playing sound:', e);
                });
            } else {
                console.log('Sound file not loaded:', soundId);
            }
        }
    }
}

// Chat Functions

async function sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Clear input
    input.value = '';
    
    // Add user message to chat
    addChatMessage(message, 'user');
    
    // Add thinking message
    addThinkingMessage();
    
    try {
        const response = await fetch(`${API_BASE_URL}/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': API_KEY ? `Bearer ${API_KEY}` : undefined
            },
            body: JSON.stringify({ message })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Remove thinking message
        removeThinkingMessage();
        
        // Add bot response to chat
        addChatMessage(data.response, 'bot');
        
        // Update status bar
        document.getElementById('status-text').textContent = 'Ready';
        
    } catch (error) {
        console.error('Error:', error);
        removeThinkingMessage();
        addChatMessage("I'm having trouble connecting right now. Please try again later.", 'error');
        document.getElementById('status-text').textContent = 'Error: Connection failed';
    }
}

function addChatMessage(text, sender) {
    const chatMessages = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    
    messageDiv.className = sender === 'user' ? 'chat-message user' : 'chat-message bot';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    const avatar = document.createElement('img');
    avatar.className = 'bot-avatar';
    avatar.src = sender === 'user' ? 'static/img/w2k_user.png' : 'static/img/w95_27.png';
    avatar.alt = sender === 'user' ? 'User' : 'Dexy';
    
    const messageText = document.createElement('div');
    messageText.className = 'message-text';
    
    // Process text for markdown-like formatting
    let formattedText = text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') // Bold
        .replace(/\*(.*?)\*/g, '<em>$1</em>') // Italic
        .replace(/`(.*?)`/g, '<code>$1</code>') // Code
        .replace(/\n\n/g, '</p><p>') // Paragraphs
        .replace(/\n/g, '<br>'); // Line breaks
    
    messageText.innerHTML = `<p>${formattedText}</p>`;
    
    contentDiv.appendChild(avatar);
    contentDiv.appendChild(messageText);
    messageDiv.appendChild(contentDiv);
    
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom of chat
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addThinkingMessage() {
    const chatMessages = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'chat-message bot thinking';
    messageDiv.id = 'thinking-message';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    const avatar = document.createElement('img');
    avatar.className = 'bot-avatar';
    avatar.src = 'static/img/w95_27.png';
    avatar.alt = 'Dexy';
    
    const messageText = document.createElement('div');
    messageText.className = 'message-text';
    messageText.innerHTML = '<p>Dexy is thinking<span class="ellipsis">...</span></p>';
    
    contentDiv.appendChild(avatar);
    contentDiv.appendChild(messageText);
    messageDiv.appendChild(contentDiv);
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    // Animate ellipsis
    let dots = 0;
    const ellipsis = messageText.querySelector('.ellipsis');
    const ellipsisInterval = setInterval(() => {
        dots = (dots + 1) % 4;
        ellipsis.textContent = '.'.repeat(dots);
    }, 500);
    
    // Store the interval in a data attribute
    messageDiv.dataset.interval = ellipsisInterval;
}

function removeThinkingMessage() {
    const thinkingMessage = document.getElementById('thinking-message');
    if (thinkingMessage) {
        // Clear the interval
        clearInterval(thinkingMessage.dataset.interval);
        
        // Remove the message
        thinkingMessage.remove();
    }
}

// Analysis Functions

function runQuickAnalysis() {
    playSound('click-sound');
    
    const token = document.getElementById('quick-token').value;
    const resultsContainer = document.getElementById('quick-analysis-results');
    const loadingContainer = document.getElementById('quick-analysis-loading');
    
    // Clear previous results
    resultsContainer.innerHTML = '';
    
    // Show loading
    loadingContainer.style.display = 'flex';
    resultsContainer.appendChild(loadingContainer);
    
    // Make the API call to the analyze endpoint
    fetch('/analyze', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token_id: token }),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // Hide loading
        loadingContainer.style.display = 'none';
        
        // Process result - extract sections from the formatted text
        const analysisText = data.result || "No analysis data available";
        
        // Parse the analysis result into sections
        const sections = parseAnalysisText(analysisText);
        
        // Create results HTML
        let resultsHTML = `
            <div class="analysis-header">
                <span>${token.toUpperCase()} Analysis</span>
                <span class="price-info">
                    ${sections.price || 'Price data unavailable'}
                </span>
            </div>
        `;
        
        // Add metrics section
        resultsHTML += `<div class="metric-container">`;
        
        // Add technical indicators
        if (sections.indicators && sections.indicators.length > 0) {
            sections.indicators.forEach(indicator => {
                const [label, value] = indicator.split(':').map(s => s.trim());
                if (label && value) {
                    // Determine signal class
                    const signalClass = getSignalClassFromValue(value);
                    
                    resultsHTML += `
                        <div class="metric-row">
                            <div class="metric-label">${label}:</div>
                            <div class="metric-value ${signalClass}">${value}</div>
                        </div>
                    `;
                }
            });
        }
        
        // Close metrics container
        resultsHTML += `</div>`;
        
        // Add mean reversion signal
        if (sections.signal) {
            const signalClass = getSignalClassFromValue(sections.signal);
            resultsHTML += `
                <div class="analysis-summary">
                    <div class="summary-title">Mean Reversion Signal:</div>
                    <div class="${signalClass}">${sections.signal}</div>
                </div>
            `;
        }
        
        // Add recommendation if available
        if (sections.recommendation) {
            resultsHTML += `
                <div class="analysis-summary" style="margin-top: 10px;">
                    <div class="summary-title">Recommendation:</div>
                    <div>${sections.recommendation}</div>
                </div>
            `;
        }
        
        // Add whale activity if available
        if (sections.whale) {
            const whaleClass = getSignalClassFromValue(sections.whale);
            resultsHTML += `
                <div class="analysis-summary" style="margin-top: 10px;">
                    <div class="summary-title">Whale Activity:</div>
                    <div class="${whaleClass}">${sections.whale}</div>
                </div>
            `;
        }
        
        // Add results to container
        resultsContainer.innerHTML = resultsHTML;
        
        // Play notification sound
        playSound('notify-sound');
    })
    .catch(error => {
        console.error('Error:', error);
        
        // Hide loading
        loadingContainer.style.display = 'none';
        
        // Show error message
        resultsContainer.innerHTML = `
            <div class="win95-error">
                <div class="error-title">
                    <img src="static/img/w98_msg_error.png" alt="Error" style="width: 24px; height: 24px; margin-right: 8px;">
                    Analysis Error
                </div>
                <div class="error-message">
                    Could not analyze ${token}. Please try again later.
                    <p>Error details: ${error.message}</p>
                </div>
            </div>
        `;
        
        // Play error sound
        playSound('error-sound');
    });
}

function parseAnalysisText(text) {
    // Parse the analysis text into sections
    const sections = {
        price: null,
        indicators: [],
        signal: null,
        recommendation: null,
        whale: null
    };
    
    // Split by lines
    const lines = text.split('\n');
    let currentSection = '';
    
    // Process each line
    for (const line of lines) {
        const trimmedLine = line.trim();
        
        // Skip empty lines
        if (!trimmedLine) continue;
        
        // Check for section headers
        if (trimmedLine.includes('===')) {
            // Extract section name
            const match = trimmedLine.match(/===\s*(.*?)\s*===/) || [];
            if (match[1]) {
                currentSection = match[1].trim();
            }
            continue;
        }
        
        // Process content based on current section
        if (currentSection.includes('PRICE & TECHNICAL')) {
            if (trimmedLine.startsWith('Current Price:')) {
                sections.price = trimmedLine;
            } else if (trimmedLine.includes(':')) {
                sections.indicators.push(trimmedLine);
            }
        } else if (currentSection.includes('MEAN REVERSION')) {
            if (trimmedLine.includes('Direction:')) {
                sections.signal = trimmedLine.replace('Direction:', '').trim();
            }
        } else if (currentSection.includes('RECOMMENDATION')) {
            if (!sections.recommendation) {
                sections.recommendation = trimmedLine;
            } else {
                sections.recommendation += ' ' + trimmedLine;
            }
        } else if (currentSection.includes('WHALE')) {
            if (trimmedLine.includes('Risk Score:')) {
                sections.whale = trimmedLine;
            }
        }
    }
    
    return sections;
}

function runTechnicalAnalysis() {
    playSound('click-sound');
    
    const token = document.getElementById('technical-token').value;
    const timePeriod = document.getElementById('time-period').value;
    const showZScore = document.getElementById('show-zscore').checked;
    const showRSI = document.getElementById('show-rsi').checked;
    const showBB = document.getElementById('show-bb').checked;
    
    const resultsContainer = document.getElementById('technical-analysis-results');
    const loadingContainer = document.getElementById('technical-analysis-loading');
    
    // Clear previous results
    resultsContainer.innerHTML = '';
    
    // Show loading
    loadingContainer.style.display = 'flex';
    resultsContainer.appendChild(loadingContainer);
    
    // Check if at least one indicator is selected
    if (!showZScore && !showRSI && !showBB) {
        loadingContainer.style.display = 'none';
        showErrorDialog('Please select at least one technical indicator to display.');
        return;
    }
    
    // Make the API call to the technical endpoint
    fetch('/technical', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
            token_id: token,
            days: parseInt(timePeriod)
        }),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // Hide loading
        loadingContainer.style.display = 'none';
        
        // Extract indicators from API response
        const indicators = data.indicators || {};
        const metrics = indicators.metrics || {};
        const currentPrice = indicators.current_price || 0;
        
        // Create results HTML
        let resultsHTML = `
            <div class="analysis-header">
                <span>${token.toUpperCase()} Technical Analysis (${timePeriod} days)</span>
                <span class="price-info">$${currentPrice.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</span>
            </div>
            
            <div class="chart-container">
                <div class="chart-placeholder">
                    [Technical indicators chart would appear here in production version]
                </div>
            </div>
            
            <div class="metric-container">
        `;
        
        // Add selected indicators
        let hasValidMetrics = false;
        
        if (showZScore && metrics.z_score) {
            hasValidMetrics = true;
            const zScoreValue = metrics.z_score.value;
            const zScoreInterpretation = metrics.z_score.interpretation || getZScoreSignal(zScoreValue);
            
            resultsHTML += `
                <div class="metric-row">
                    <div class="metric-label">Z-Score:</div>
                    <div class="metric-value ${getSignalClass(zScoreInterpretation)}">
                        ${zScoreValue.toFixed(2)} (${zScoreInterpretation})
                    </div>
                </div>
            `;
        }
        
        if (showRSI && metrics.rsi) {
            hasValidMetrics = true;
            const rsiValue = metrics.rsi.value;
            const rsiInterpretation = metrics.rsi.interpretation || getRSISignal(rsiValue);
            
            resultsHTML += `
                <div class="metric-row">
                    <div class="metric-label">RSI:</div>
                    <div class="metric-value ${getSignalClass(rsiInterpretation)}">
                        ${rsiValue.toFixed(2)} (${rsiInterpretation})
                    </div>
                </div>
            `;
        }
        
        if (showBB && metrics.bollinger_bands) {
            hasValidMetrics = true;
            const bbValue = metrics.bollinger_bands.percent_b;
            const bbInterpretation = metrics.bollinger_bands.interpretation || getBBSignal(bbValue);
            
            resultsHTML += `
                <div class="metric-row">
                    <div class="metric-label">Bollinger %B:</div>
                    <div class="metric-value ${getSignalClass(bbInterpretation)}">
                        ${bbValue.toFixed(2)} (${bbInterpretation})
                    </div>
                </div>
            `;
        }
        
        // If no valid metrics were found, show fallback content
        if (!hasValidMetrics) {
            resultsHTML += `
                <div class="metric-row">
                    <div class="metric-label">No indicators available</div>
                    <div class="metric-value">Unable to retrieve the selected indicators for ${token}.</div>
                </div>
            `;
        }
        
        // Close metrics container
        resultsHTML += `</div>`;
        
        // Add summary
        let summaryText = "";
        if (indicators.summary) {
            summaryText = indicators.summary;
        } else {
            summaryText = getTechnicalSummary(token, metrics);
        }
        
        resultsHTML += `
            <div class="analysis-summary">
                <div class="summary-title">Analysis Summary:</div>
                <div>This technical analysis is based on ${timePeriod} days of historical data. ${summaryText}</div>
            </div>
        `;
        
        // Add results to container
        resultsContainer.innerHTML = resultsHTML;
        
        // Play notification sound
        playSound('notify-sound');
    })
    .catch(error => {
        console.error('Error:', error);
        
        // Hide loading
        loadingContainer.style.display = 'none';
        
        // Show error message
        resultsContainer.innerHTML = `
            <div class="win95-error">
                <div class="error-title">
                    <img src="static/img/w98_msg_error.png" alt="Error" style="width: 24px; height: 24px; margin-right: 8px;">
                    Analysis Error
                </div>
                <div class="error-message">
                    Could not retrieve technical indicators for ${token}. Please try again later.
                    <p>Error details: ${error.message}</p>
                </div>
            </div>
        `;
        
        // Play error sound
        playSound('error-sound');
    });
}

function runWhaleAnalysis() {
    playSound('click-sound');
    
    const token = document.getElementById('whale-token').value;
    const resultsContainer = document.getElementById('whale-analysis-results');
    const loadingContainer = document.getElementById('whale-analysis-loading');
    
    // Clear previous results
    resultsContainer.innerHTML = '';
    
    // Show loading
    loadingContainer.style.display = 'flex';
    resultsContainer.appendChild(loadingContainer);
    
    // Make the API call to the whale endpoint
    fetch('/whale', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token_id: token }),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // Hide loading
        loadingContainer.style.display = 'none';
        
        // Get price data in a separate API call
        fetch('/technical', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ token_id: token }),
        })
        .then(priceResponse => priceResponse.json())
        .then(priceData => {
            // Extract the price if available, otherwise use a placeholder
            const price = priceData.indicators?.current_price || 0;
            
            // Create results HTML with current price
            displayWhaleResults(token, data, price, resultsContainer);
        })
        .catch(priceError => {
            console.error('Price fetch error:', priceError);
            // Display results without price
            displayWhaleResults(token, data, 0, resultsContainer);
        });
    })
    .catch(error => {
        console.error('Error:', error);
        
        // Hide loading
        loadingContainer.style.display = 'none';
        
        // Show error message
        resultsContainer.innerHTML = `
            <div class="win95-error">
                <div class="error-title">
                    <img src="static/img/w98_msg_error.png" alt="Error" style="width: 24px; height: 24px; margin-right: 8px;">
                    Analysis Error
                </div>
                <div class="error-message">
                    Could not retrieve whale activity data for ${token}. Please try again later.
                    <p>Error details: ${error.message}</p>
                </div>
            </div>
        `;
        
        // Play error sound
        playSound('error-sound');
    });
}

function displayWhaleResults(token, data, price, container) {
    const priceDisplay = price > 0 ? 
        `$${price.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}` : 
        'Price data unavailable';
    
    // Create results HTML
    const resultsHTML = `
        <div class="analysis-header">
            <span>${token.toUpperCase()} Whale Activity Analysis</span>
            <span class="price-info">${priceDisplay}</span>
        </div>
        
        <div class="chart-container">
            <div class="chart-placeholder">
                [Whale activity chart would appear here in production version]
            </div>
        </div>
        
        <div class="metric-container">
            <div class="metric-row">
                <div class="metric-label">Risk Score:</div>
                <div class="metric-value ${getRiskClass(data.risk_score)}">
                    ${data.risk_score} / 100 (${data.level})
                </div>
            </div>
            
            <div class="metric-row">
                <div class="metric-label">Detected Signals:</div>
                <div class="metric-value">
                    ${data.signals && data.signals.length > 0 ? 
                        `<ul>${data.signals.map(signal => `<li>${signal}</li>`).join('')}</ul>` : 
                        'No specific risk signals detected'}
                </div>
            </div>
        </div>
        
        <div class="analysis-summary">
            <div class="summary-title">Whale Analysis Summary:</div>
            <div>The current whale activity for ${token.toUpperCase()} shows ${getWhaleAnalysisSummary(data)}.</div>
        </div>
    `;
    
    // Add results to container
    container.innerHTML = resultsHTML;
    
    // Play notification sound
    playSound('notify-sound');
}

// Helper Functions

function getSignalClassFromValue(value) {
    if (!value) return 'neutral';
    
    value = value.toString().toUpperCase();
    
    if (value.includes('BULLISH') || 
        value.includes('UPWARD') || 
        value.includes('OVERSOLD') || 
        value.includes('BUY') ||
        value.includes('LOW')) {
        return 'bullish';
    } else if (value.includes('BEARISH') || 
               value.includes('DOWNWARD') || 
               value.includes('OVERBOUGHT') || 
               value.includes('SELL') ||
               value.includes('HIGH')) {
        return 'bearish';
    } else {
        return 'neutral';
    }
}

function getSignalClass(signal) {
    return getSignalClassFromValue(signal);
}

function getRiskClass(score) {
    if (score < 40) return 'bullish';
    if (score > 60) return 'bearish';
    return 'neutral';
}

function getZScoreSignal(value) {
    if (value > 2) return 'STRONGLY OVERBOUGHT';
    if (value > 1) return 'OVERBOUGHT';
    if (value < -2) return 'STRONGLY OVERSOLD';
    if (value < -1) return 'OVERSOLD';
    return 'NEUTRAL';
}

function getRSISignal(value) {
    if (value > 70) return 'OVERBOUGHT';
    if (value > 60) return 'APPROACHING OVERBOUGHT';
    if (value < 30) return 'OVERSOLD';
    if (value < 40) return 'APPROACHING OVERSOLD';
    return 'NEUTRAL';
}

function getBBSignal(value) {
    if (value > 1) return 'ABOVE UPPER BAND';
    if (value > 0.8) return 'UPPER BAND TOUCH';
    if (value < 0) return 'BELOW LOWER BAND';
    if (value < 0.2) return 'LOWER BAND TOUCH';
    return 'MIDDLE BAND';
}

function getTechnicalSummary(token, metrics) {
    // Generate a meaningful summary based on the technical indicators
    let summary = '';
    
    if (metrics.z_score && metrics.rsi && metrics.bollinger_bands) {
        const z_score = metrics.z_score.value;
        const rsi = metrics.rsi.value;
        const bb = metrics.bollinger_bands.percent_b;
        
        // Overextended to the upside?
        if (z_score > 1 && rsi > 65 && bb > 0.8) {
            summary = `${token.toUpperCase()} is showing signs of being overextended to the upside, with multiple indicators in overbought territory. This often precedes a reversion to the mean (downward movement).`;
        } 
        // Overextended to the downside?
        else if (z_score < -1 && rsi < 35 && bb < 0.2) {
            summary = `${token.toUpperCase()} is showing signs of being overextended to the downside, with multiple indicators in oversold territory. This may present a buying opportunity as prices often revert to the mean.`;
        }
        // Mixed signals but leaning bullish
        else if ((z_score < 0 || rsi < 45 || bb < 0.4) && !(z_score > 1 || rsi > 65 || bb > 0.8)) {
            summary = `${token.toUpperCase()} is showing some signs of weakness, but not yet in extreme oversold territory. Watch for potential buying opportunities if indicators move further into oversold zones.`;
        }
        // Mixed signals but leaning bearish
        else if ((z_score > 0 || rsi > 55 || bb > 0.6) && !(z_score < -1 || rsi < 35 || bb < 0.2)) {
            summary = `${token.toUpperCase()} is showing some strength, but not yet in extreme overbought territory. Caution is advised if indicators continue to move higher into overbought zones.`;
        }
        // Neutral
        else {
            summary = `${token.toUpperCase()} is currently in neutral territory with no extreme readings on technical indicators. The asset may be in a ranging or consolidation phase.`;
        }
    } else {
        summary = `Technical indicators suggest monitoring ${token.toUpperCase()} for more decisive signals before making trading decisions.`;
    }
    
    return summary;
}

function getWhaleAnalysisSummary(data) {
    if (data.risk_score > 70) {
        return 'significant distribution from large holders, which often precedes downward price movements';
    } else if (data.risk_score > 50) {
        return 'moderate activity from larger players with some concerning transfer patterns';
    } else if (data.risk_score > 30) {
        return 'typical movement patterns with no significant anomalies in wallet transfers';
    } else {
        return 'accumulation patterns from large holders, which is typically a positive long-term signal';
    }
}

// Settings Functions

function saveSettings() {
    playSound('click-sound');
    
    const apiKey = document.getElementById('api-key').value;
    const apiProvider = document.getElementById('api-provider').value;
    const enableSounds = document.getElementById('enable-sounds').checked;
    const autostartChat = document.getElementById('autostart-chat').checked;
    
    // Apply sound setting immediately
    soundEnabled = enableSounds;
    
    // Save settings to localStorage
    localStorage.setItem('dexy_apiKey', apiKey);
    localStorage.setItem('dexy_apiProvider', apiProvider);
    localStorage.setItem('dexy_enableSounds', enableSounds);
    localStorage.setItem('dexy_autostartChat', autostartChat);
    
    // Show notification
    showNotification('Settings saved successfully!');
    
    // Close settings window
    closeWindow('settings-window');
}

function loadSettings() {
    // Load settings from localStorage
    const apiKey = localStorage.getItem('dexy_apiKey') || '';
    const apiProvider = localStorage.getItem('dexy_apiProvider') || 'defillama';
    const enableSounds = localStorage.getItem('dexy_enableSounds') !== 'false'; // Default to true
    const autostartChat = localStorage.getItem('dexy_autostartChat') === 'true'; // Default to false
    
    // Apply settings
    document.getElementById('api-key').value = apiKey;
    document.getElementById('api-provider').value = apiProvider;
    document.getElementById('enable-sounds').checked = enableSounds;
    document.getElementById('autostart-chat').checked = autostartChat;
    
    // Apply sound setting
    soundEnabled = enableSounds;
    
    // Auto-start chat if enabled
    if (autostartChat) {
        setTimeout(() => {
            openWindow('chat-window');
        }, 1000);
    }
}

function connectWallet() {
    playSound('click-sound');
    
    const walletAddress = document.getElementById('wallet-address');
    
    // Show connecting state
    walletAddress.textContent = 'Connecting...';
    
    // Get wallet data from API
    fetch('/wallet')
    .then(response => {
        if (!response.ok) {
            throw new Error(response.status === 404 ? 'No wallet data found' : 'Error connecting to wallet');
        }
        return response.json();
    })
    .then(data => {
        if (data.wallet && data.wallet.address) {
            walletAddress.textContent = data.wallet.address;
        } else {
            walletAddress.textContent = 'CDP wallet created (address hidden)';
        }
        
        // Play notification sound
        playSound('notify-sound');
    })
    .catch(error => {
        console.error('Wallet error:', error);
        walletAddress.textContent = 'Error: ' + error.message;
        
        // Play error sound
        playSound('error-sound');
    });
}

// Error and Notification Functions

function showErrorDialog(message) {
    playSound('error-sound');
    
    document.getElementById('error-message').textContent = message;
    document.getElementById('error-dialog-overlay').style.display = 'flex';
}

function closeErrorDialog() {
    playSound('click-sound');
    
    document.getElementById('error-dialog-overlay').style.display = 'none';
}

function showNotification(message) {
    playSound('notify-sound');
    
    // Create and show toast notification
    const notification = document.createElement('div');
    notification.className = 'win97-notification';
    notification.textContent = message;
    notification.style.position = 'fixed';
    notification.style.bottom = '40px';
    notification.style.right = '20px';
    notification.style.background = 'var(--win97-blue)';
    notification.style.color = 'white';
    notification.style.padding = '10px 15px';
    notification.style.border = '2px solid';
    notification.style.borderColor = 'var(--win97-light) var(--win97-dark) var(--win97-dark) var(--win97-light)';
    notification.style.zIndex = '2000';
    notification.style.transition = 'opacity 0.3s, transform 0.3s';
    notification.style.opacity = '0';
    notification.style.transform = 'translateY(20px)';
    notification.style.boxShadow = '3px 3px 5px rgba(0,0,0,0.3)';
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.opacity = '1';
        notification.style.transform = 'translateY(0)';
    }, 10);
    
    // Remove after delay
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateY(20px)';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

// Update CDP connection status
function updateCDPStatus() {
    const statusElement = document.getElementById('cdp-status');
    if (!statusElement) return;
    
    fetch(`${API_BASE_URL}/status`)
        .then(response => response.json())
        .then(data => {
            if (data.status === "AgentKit is running") {
                statusElement.textContent = 'Connected to CDP';
                document.getElementById('status-text').textContent = 'Connected to CDP';
            } else {
                throw new Error('CDP not connected');
            }
        })
        .catch(error => {
            statusElement.textContent = 'CDP Connection Failed';
            document.getElementById('status-text').textContent = 'Not connected to CDP';
        });
}

// Call updateCDPStatus every 30 seconds
setInterval(updateCDPStatus, 30000);
// Initial CDP status check
updateCDPStatus();