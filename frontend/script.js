/* ============================================================
   STOCKSENSE AI — script.js
   ============================================================ */

let currentContext = "";
let currentSymbol = "";
let currentCurrency = "$";
let chartInstance = null;


// ── Layman's Terms Tooltip Dictionary ─────────────────────────
const TOOLTIP_DEFINITIONS = {
    open: {
        label: "Open",
        definition: "The stock's price when the market opened this morning. It's the starting point for today's trading session."
    },
    high: {
        label: "Today's High",
        definition: "The highest price the stock reached during today's trading. A rising high indicates strong buying interest."
    },
    low: {
        label: "Today's Low",
        definition: "The lowest price the stock dipped to today. A falling low can signal selling pressure."
    },
    mkt_cap: {
        label: "Market Capitalization",
        definition: "The total value of the company in the stock market. Calculated as: Share Price × Total Shares. Think of it as 'how big is this company?'"
    },
    avg_vol: {
        label: "Average Volume",
        definition: "The average number of shares traded daily over the past month. High volume means more investor interest and easier to buy/sell."
    },
    pe: {
        label: "Price-to-Earnings (P/E)",
        definition: "How much investors pay per ₹1 of company profit. A high P/E means investors expect strong future growth. A low P/E may mean the stock is undervalued."
    },
    eps: {
        label: "Earnings Per Share (EPS)",
        definition: "How much profit the company makes for each share you own. Higher EPS = more profitable company. This is the company's 'report card'."
    },
    div_yield: {
        label: "Dividend Yield",
        definition: "The annual cash payout you get as a percentage of the stock price. A 3% yield means you earn ₹3 for every ₹100 invested, just for holding the stock."
    },
    beta: {
        label: "Beta (Volatility)",
        definition: "Measures how much the stock moves compared to the whole market. Beta > 1 = moves more than the market (risky but potentially high reward). Beta < 1 = more stable than the market."
    },
    "52h": {
        label: "52-Week High",
        definition: "The highest price this stock has traded at in the last year. If the current price is near this, the stock is performing very well."
    },
    "52l": {
        label: "52-Week Low",
        definition: "The lowest price this stock has traded at in the last year. If the current price is near this, the stock may be a buying opportunity — or in trouble."
    }
};

// ── Custom Tooltip Logic ──────────────────────────────────────
const tooltipEl = document.getElementById('custom-tooltip');

document.addEventListener('mouseover', (e) => {
    const card = e.target.closest('[data-tip]');
    if (card) {
        const tipKey = card.getAttribute('data-tip');
        const info = TOOLTIP_DEFINITIONS[tipKey];
        if (info) {
            tooltipEl.innerHTML = `<strong>${info.label}</strong>${info.definition}`;
            tooltipEl.classList.add('visible');
        }
    }
});

document.addEventListener('mousemove', (e) => {
    if (tooltipEl.classList.contains('visible')) {
        const x = e.clientX + 14;
        const y = e.clientY + 14;
        // Keep within viewport
        const maxX = window.innerWidth - tooltipEl.offsetWidth - 10;
        const maxY = window.innerHeight - tooltipEl.offsetHeight - 10;
        tooltipEl.style.left = Math.min(x, maxX) + 'px';
        tooltipEl.style.top  = Math.min(y, maxY) + 'px';
    }
});

document.addEventListener('mouseout', (e) => {
    if (e.target.closest('[data-tip]')) {
        tooltipEl.classList.remove('visible');
    }
});

// ── Search & Formatting Helpers ──────────────────────────────────
function formatNumber(val, decimals = 2) {
    if (val === 'N/A' || val === undefined || val === null) return 'N/A';
    if (typeof val === 'string') {
        // Handle strings like "1.23B" or "500M"
        if (val.match(/[BMT]$/)) return val;
        val = parseFloat(val.replace(/[^0-9.-]+/g,""));
    }
    if (isNaN(val)) return 'N/A';
    return val.toLocaleString('en-US', { 
        minimumFractionDigits: decimals, 
        maximumFractionDigits: decimals 
    });
}

function clearSearch() {
    const input = document.getElementById('stock-input');
    input.value = "";
    input.focus();
    toggleClearBtn();
}

function toggleClearBtn() {
    const input = document.getElementById('stock-input');
    const btn = document.getElementById('clear-search');
    if (input.value.length > 0) {
        btn.classList.add('visible');
    } else {
        btn.classList.remove('visible');
    }
}

// ── Chat Popup ────────────────────────────────────────────────
function toggleChat() {
    document.getElementById('chat-popup').classList.toggle('active');
}

function toggleMinimizeChat() {
    const chatPopup = document.getElementById('chat-popup');
    chatPopup.classList.toggle('minimized');
    chatPopup.classList.remove('maximized');
}

function toggleMaximizeChat() {
    const chatPopup = document.getElementById('chat-popup');
    chatPopup.classList.toggle('maximized');
    chatPopup.classList.remove('minimized');
}

// ── Help Center Modal ─────────────────────────────────────────
function toggleHelp() {
    document.getElementById('help-modal').classList.toggle('active');
}
function closeHelpOnOverlay(e) {
    if (e.target === document.getElementById('help-modal')) toggleHelp();
}

// ── Quick Search from welcome chips ──────────────────────────
function quickSearch(ticker) {
    document.getElementById('stock-input').value = ticker;
    analyzeStock();
}

function handleSearchEnter(e) { if (e.key === "Enter") analyzeStock(); }
function handleEnter(e)       { if (e.key === "Enter") ask(); }

// ── Main Analysis Function ────────────────────────────────────
async function analyzeStock() {
    let stock = document.getElementById("stock-input").value.trim().toUpperCase();
    if (!stock) return;

    document.getElementById("welcome-state").style.display = "none";
    document.getElementById("dashboard").style.display = "none";
    document.getElementById("loader-overlay").style.display = "flex";

    try {
        let res  = await fetch(`/analyze/${stock}`);

        let data = await res.json();

        document.getElementById("loader-overlay").style.display = "none";

        if (data.error) {
            alert(`Error: ${data.error}`);
            document.getElementById("welcome-state").style.display = "flex";
            return;
        }

        document.getElementById("dashboard").style.display = "grid";

        // Store symbol for history chart
        currentSymbol = data.symbol;

        // ─ Company Header ─

        document.getElementById("company-name-display").innerText = data.company_name || data.symbol;
        document.getElementById("company-symbol-display").innerText = data.symbol;

        // Show & load history chart (default 5 years)
        document.getElementById("history-widget").style.display = "flex";
        document.getElementById("period-dropdown").value = "5y";
        loadHistory("5y", null);

        // ─ Financial Metrics ─
        if (data.metrics) {
            document.getElementById("financial-widget").style.display = "flex";
            document.getElementById("financial-price-area").style.display = "block";

            const currencyMap = { USD: "$", INR: "₹", EUR: "€", GBP: "£" };
            currentCurrency = currencyMap[data.metrics.currency] || "$";
            const curr = currentCurrency;

            // Big price in header
            document.getElementById("current-price").innerText =
                curr + formatNumber(data.metrics.price);

            const changeElem = document.getElementById("price-change");
            const changeSign = data.metrics.change >= 0 ? "+" : "";
            changeElem.innerText = `${changeSign}${formatNumber(data.metrics.change)}  (${changeSign}${data.metrics.percent_change.toFixed(2)}%)`;
            changeElem.className = "price-change " +
                (data.metrics.change > 0 ? "positive" : data.metrics.change < 0 ? "negative" : "neutral");

            // Trend arrow & label
            const arrowEl = document.getElementById("price-trend-arrow");
            const labelEl = document.getElementById("price-trend-label");
            if (data.metrics.change > 0) {
                arrowEl.innerText = "▲";
                arrowEl.style.color = "var(--positive)";
                labelEl.innerText = "Going Up";
                labelEl.className = "trend-label going-up";
            } else if (data.metrics.change < 0) {
                arrowEl.innerText = "▼";
                arrowEl.style.color = "var(--negative)";
                labelEl.innerText = "Going Down";
                labelEl.className = "trend-label going-down";
            } else {
                arrowEl.innerText = "●";
                arrowEl.style.color = "var(--neutral)";
                labelEl.innerText = "No Change";
                labelEl.className = "trend-label no-change";
            }

            // Helper to prefix currency
            const fmt = (val) => (val !== 'N/A' && val !== undefined) ? curr + formatNumber(val) : 'N/A';

            // Current Performance
            document.getElementById("metric-open").innerText  = fmt(data.metrics.open);
            document.getElementById("metric-high").innerText  = fmt(data.metrics.high);
            document.getElementById("metric-low").innerText   = fmt(data.metrics.low);
            document.getElementById("metric-mcap").innerText  = formatNumber(data.metrics.market_cap, 0);
            document.getElementById("metric-vol").innerText   = formatNumber(data.metrics.avg_vol, 0);

            // Company Health
            document.getElementById("metric-pe").innerText    = formatNumber(data.metrics.pe_ratio);
            document.getElementById("metric-eps").innerText   = fmt(data.metrics.eps);
            document.getElementById("metric-div").innerText   = data.metrics.dividend_yield;

            // Risk Assessment
            document.getElementById("metric-beta").innerText   = formatNumber(data.metrics.beta);
            document.getElementById("metric-52high").innerText = fmt(data.metrics["52_high"]);
            document.getElementById("metric-52low").innerText  = fmt(data.metrics["52_low"]);

        } else {
            document.getElementById("financial-widget").style.display = "none";
            document.getElementById("financial-price-area").style.display = "none";
        }

        // ─ Sentiment Strength Meter ─
        const score     = data.overall_score;
        const sentiment = data.overall_sentiment;

        const textElem = document.getElementById("sentiment-text");
        textElem.innerText = sentiment;
        textElem.className = "sentiment-label " + sentiment.toLowerCase();

        // Position the pin: score is -1 to 1, convert to 0–100%
        const pinPercent = ((score + 1) / 2) * 100;
        document.getElementById("strength-pin").style.left = `${Math.min(Math.max(pinPercent, 2), 98)}%`;

        // Dynamic summary sentence
        document.getElementById("sentiment-summary").innerText =
            buildSentimentSummary(score, sentiment, data.feed);

        // ─ Build Feed & Context ─
        const newsFeed = document.getElementById("news-feed");
        newsFeed.innerHTML = "";
        currentContext = `Real-time feed for ${data.symbol}:\n`;

        let posCount = 0, negCount = 0, neuCount = 0;

        data.feed.forEach(item => {
            if (item.sentiment === "Positive") posCount++;
            else if (item.sentiment === "Negative") negCount++;
            else neuCount++;

            const text  = item.title || item.text || "No title";
            const score = item.score !== undefined ? item.score : 0;
            currentContext += `- [${item.source}] (${item.sentiment}) ${text}\n`;

            const cls     = item.sentiment.toLowerCase();
            const linkHTML = item.url ? `<a href="${item.url}" target="_blank" rel="noopener">Read Full Article →</a>` : '';
            const pillIcon = cls === 'positive' ? '▲' : cls === 'negative' ? '▼' : '─';

            newsFeed.innerHTML += `
                <div class="feed-card ${cls}">
                    <div class="feed-card-header">
                        <span class="source-badge">${item.source}</span>
                        <span class="sentiment-pill ${cls}">${pillIcon} ${item.sentiment} (${score.toFixed(2)})</span>
                    </div>
                    <h4>${text}</h4>
                    ${linkHTML}
                </div>`;
        });

        updateChart(posCount, neuCount, negCount);


    } catch (err) {
        console.error(err);
        alert("Could not connect to the backend. Make sure uvicorn is running.");
        document.getElementById("loader-overlay").style.display = "none";
        document.getElementById("welcome-state").style.display = "flex";
    }
}

// ── Dynamic Sentiment Summary ─────────────────────────────────
function buildSentimentSummary(score, label, feed) {
    const total = feed.length;
    if (!total) return "No news items found to analyze.";

    const pos = feed.filter(f => f.sentiment === "Positive").length;
    const neg = feed.filter(f => f.sentiment === "Negative").length;
    const neu = feed.filter(f => f.sentiment === "Neutral").length;
    const posPct = Math.round((pos / total) * 100);

    if (label === "Positive") {
        return `${posPct}% of the ${total} articles analyzed were positive. Bullish news momentum is driving this score of ${score.toFixed(2)}.`;
    } else if (label === "Negative") {
        const negPct = Math.round((neg / total) * 100);
        return `${negPct}% of the ${total} articles were negative. Bearish headlines are weighing on sentiment, yielding a score of ${score.toFixed(2)}.`;
    } else {
        return `With ${pos} positive, ${neg} negative, and ${neu} neutral articles out of ${total}, market opinion is split — reflected in a balanced score of ${score.toFixed(2)}.`;
    }
}

// ── Price History Chart ───────────────────────────────────────
let historyChartInstance = null;

async function loadHistory(period, btn) {
    if (!currentSymbol) return;

    try {
        const res  = await fetch(`/history/${currentSymbol}?period=${period}`);

        const data = await res.json();

        if (data.error || !data.data?.length) return;
        renderHistoryChart(data.data, period);
    } catch(e) {
        console.error("History fetch failed:", e);
    }
}

function loadHistoryFromDropdown(selectEl) {
    const period = selectEl.value;
    loadHistory(period, null);
}


function renderHistoryChart(data, period) {
    const labels = data.map(d => d.date);
    const closes = data.map(d => d.close);

    const first = closes[0];
    const last  = closes[closes.length - 1];
    const isUp  = last >= first;
    const lineColor = isUp ? '#10b981' : '#ef4444';
    const fillColor = isUp ? 'rgba(16, 185, 129, 0.08)' : 'rgba(239, 68, 68, 0.08)';

    // Update subtitle
    let subtitle = "Price History";
    if (period.endsWith('y')) {
        const years = period.replace('y', '');
        subtitle = `Last ${years} Year${years > 1 ? 's' : ''} of price movement`;
    } else {
        const subtitleMap = {
            "1d": "Today's price movement",
            "1wk": "Last 1 Week of price movement",
            "1mo": "Last 1 Month of price movement",
            "3mo": "Last 3 Months of price movement",
            "max": "All-Time price history"
        };
        subtitle = subtitleMap[period] || "Price History";
    }
    const subtitleEl = document.getElementById('history-subtitle');
    if (subtitleEl) subtitleEl.innerText = subtitle;

    const hi  = Math.max(...closes);
    const lo  = Math.min(...closes);
    const chg = ((last - first) / first * 100).toFixed(2);
    const chgSign = chg >= 0 ? '+' : '';

    document.getElementById('history-stats').innerHTML = `
        <div class="hstat"><span class="hstat-label">Period High</span><span class="hstat-value positive-val">${currentCurrency}${formatNumber(hi)}</span></div>
        <div class="hstat"><span class="hstat-label">Period Low</span><span class="hstat-value negative-val">${currentCurrency}${formatNumber(lo)}</span></div>
        <div class="hstat"><span class="hstat-label">Period Change</span><span class="hstat-value ${isUp ? 'positive-val' : 'negative-val'}">${chgSign}${chg}%</span></div>
        <div class="hstat"><span class="hstat-label">Data Points</span><span class="hstat-value">${formatNumber(data.length, 0)}</span></div>
    `;

    const ctx = document.getElementById('historyChart').getContext('2d');
    if (historyChartInstance) historyChartInstance.destroy();

    historyChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels,
            datasets: [{
                label: 'Close Price',
                data: closes,
                borderColor: lineColor,
                borderWidth: 2.5,
                backgroundColor: fillColor,
                fill: true,
                tension: 0.3,
                pointRadius: data.length > 60 ? 0 : 3,
                pointHoverRadius: 5,
                pointBackgroundColor: lineColor,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { intersect: false, mode: 'index' },
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: '#ffffff',
                    titleColor: '#0f172a',
                    bodyColor: '#475569',
                    borderColor: 'rgba(37, 99, 235, 0.2)',
                    borderWidth: 1,
                    padding: 10,
                    displayColors: false,
                    callbacks: {
                        label: ctx => ` Close: ${currentCurrency}${ctx.raw.toFixed(2)}`
                    }
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(0,0,0,0.04)' },
                    ticks: {
                        color: '#64748b',
                        font: { size: 11 },
                        maxTicksLimit: 8,
                        maxRotation: 0
                    }
                },
                y: {
                    position: 'right',
                    grid: { color: 'rgba(0,0,0,0.04)' },
                    ticks: {
                        color: '#64748b',
                        font: { size: 11 },
                        callback: val => `${currentCurrency}${val.toFixed(2)}`
                    }
                }
            }
        }
    });
}

// ── Sentiment Distribution Chart ──────────────────────────────
function updateChart(pos, neu, neg) {
    const ctx = document.getElementById('sentimentChart').getContext('2d');
    if (chartInstance) chartInstance.destroy();

    Chart.defaults.color = "#475569";
    Chart.defaults.font.family = "'Inter', sans-serif";

    chartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Positive', 'Neutral', 'Negative'],
            datasets: [{
                data: [pos, neu, neg],
                backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
                borderColor: ['rgba(16,185,129,0.2)', 'rgba(245,158,11,0.2)', 'rgba(239,68,68,0.2)'],
                borderWidth: 1,
                hoverOffset: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: { boxWidth: 12, padding: 18, font: { size: 12 } }
                },
                tooltip: {
                    callbacks: {
                        label: (ctx) => ` ${ctx.label}: ${ctx.raw} articles`
                    }
                }
            },
            cutout: '72%'
        }
    });
}

// ── Chat ──────────────────────────────────────────────────────
function addMessage(text, sender, id = null) {
    const chat = document.getElementById("chat");
    const div  = document.createElement('div');
    div.className = `message ${sender}`;
    if (id) div.id = id;

    // Enhanced Markdown support for bold text, bullet points, and newlines
    let formattedText = text
        .replace(/\*\*\s*(.*?)\s*\*\*/g, '<strong>$1</strong>')
        .replace(/^\s*-\s+(.*)$/gm, '• $1')
        .replace(/\n/g, '<br>');
    
    div.innerHTML = formattedText;
    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
}

async function ask() {
    try {
        const queryInput = document.getElementById("chat-input");
        const query = queryInput.value.trim();

        if (!query) return;

        addMessage(query, "user");
        queryInput.value = "";

        // Show thinking indicator
        const thinkingId = "thinking-" + Date.now();
        addMessage(`<span class="thinking-dot"></span> Analyzing...`, "bot thinking", thinkingId);

        let metricsContext = "";
        try {
            const price = document.getElementById("current-price")?.innerText || "N/A";
            const high = document.getElementById("metric-high")?.innerText || "N/A";
            const low = document.getElementById("metric-low")?.innerText || "N/A";
            const mcap = document.getElementById("metric-mcap")?.innerText || "N/A";
            const pe = document.getElementById("metric-pe")?.innerText || "N/A";
            
            let chartData = "No chart available.";
            const hStats = document.getElementById("history-stats");
            const hPeriod = document.getElementById("history-subtitle")?.innerText || "History";
            if (hStats && hStats.innerText) {
                chartData = `Chart/Graph History (${hPeriod}): ${hStats.innerText.replace(/\n/g, ', ')}`;
            }
            
            metricsContext = `Stock: ${currentSymbol}\nCurrent Price: ${price}\nToday's High: ${high}\nToday's Low: ${low}\nMarket Cap: ${mcap}\nP/E Ratio: ${pe}\n${chartData}`;
        } catch(e) {}

        const context = `${metricsContext}\n${currentContext}\nQuery: ${query}`;

        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 60000); // Increased to 60s for detailed answers

        const response = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query, context }),
            signal: controller.signal
        });

        clearTimeout(timeoutId);
        const data = await response.json();

        const thinkingElem = document.getElementById(thinkingId);
        if (thinkingElem) thinkingElem.remove();

        addMessage(data.response, "bot");
    } catch (err) {
        console.error("Chat Error:", err);
        const thinkers = document.querySelectorAll(".bot.thinking");
        thinkers.forEach(t => t.remove());
        
        let errorMsg = "I'm sorry, I couldn't reach the analyst server. Please ensure the backend is running.";
        if (err.name === 'AbortError') {
            errorMsg = "The analysis is taking longer than expected. Please try again in a moment.";
        }
        addMessage(errorMsg, "bot");
    }
}

