// Cloudflare Worker for FinPress
const HTML = `<!DOCTYPE html>
<html lang="en" class="h-full antialiased" data-theme="light">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>FinBrief Institutional Workspace — Trader Terminal</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          fontFamily: {
            sans: ['"Plus Jakarta Sans"', 'system-ui', 'sans-serif'],
            mono: ['"JetBrains Mono"', 'monospace'],
          },
          colors: {
            brand: { 50: '#EEF2FF', 100: '#E0E7FF', 500: '#6366F1', 600: '#4F46E5', 700: '#4338CA' }
          }
        }
      }
    }
  </script>
  <style>
    body { font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif; font-size: 14px; }
    .font-mono { font-family: 'JetBrains Mono', monospace; }
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #CBD5E1; border-radius: 4px; }
    .dark ::-webkit-scrollbar-thumb { background: #334155; }
    .table-row-hover:hover { background-color: rgba(99, 102, 241, 0.05); }
    .dark .table-row-hover:hover { background-color: rgba(99, 102, 241, 0.10); }
    mark { background-color: #FEF08A; color: #854D0E; padding: 0 2px; border-radius: 2px; font-weight: 700; }
    .dark mark { background-color: #854D0E; color: #FEF08A; }
  </style>
</head>
<body class="min-h-full bg-[#F3F5F8] text-slate-900 dark:bg-[#090D16] dark:text-slate-100 transition-colors duration-150">
  <div class="min-h-screen flex flex-col">

    <!-- ================= SINGLE COMPACT TOP BAR ================= -->
    <header class="sticky top-0 z-40 bg-white dark:bg-[#0E1322] border-b border-slate-200 dark:border-slate-800 shadow-xs px-3.5 py-1.5 flex items-center justify-between gap-3 flex-wrap">
      
      <!-- Left: Logo & Primary Navigation Tabs -->
      <div class="flex items-center gap-3.5 shrink-0">
        <div class="flex items-center gap-2 shrink-0 cursor-pointer" onclick="switchView('feed')">
          <div class="w-7 h-7 rounded-lg bg-brand-600 flex items-center justify-center shadow-xs">
            <span class="text-white text-xs font-black tracking-tighter">FB</span>
          </div>
          <span class="text-[16px] font-black tracking-tight text-slate-900 dark:text-white mr-1">
            Fin<span class="text-brand-600 dark:text-brand-500">Brief</span>
          </span>
        </div>

        <nav class="flex items-center bg-slate-100 dark:bg-[#141A2E] p-0.5 rounded-lg border border-slate-200/80 dark:border-slate-800 text-[12.5px]">
          <button id="tab-btn-feed" onclick="switchView('feed')" class="px-3 py-1 font-bold rounded-md transition-all bg-white dark:bg-brand-600 text-slate-900 dark:text-white shadow-xs flex items-center gap-1.5">
            <span>⚡ News Stream</span>
            <span id="tab-feed-count" class="px-1.5 py-0.2 rounded text-[10.5px] font-mono bg-slate-100 dark:bg-black/30 font-bold">218</span>
          </button>
          <button id="tab-btn-ipo" onclick="switchView('ipo')" class="px-3 py-1 font-semibold rounded-md transition-all text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white flex items-center gap-1.5">
            <span>🚀 IPO Central</span>
            <span id="tab-ipo-count" class="px-1.5 py-0.2 rounded text-[10.5px] font-mono bg-amber-100 text-amber-800 dark:bg-amber-950/60 dark:text-amber-300 font-bold">17</span>
          </button>
          <button id="tab-btn-corporate" onclick="switchView('corporate')" class="px-2.5 py-1 font-semibold rounded-md transition-all text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white">
            🏢 Corporate
          </button>
          <button id="tab-btn-macro" onclick="switchView('macro')" class="px-2.5 py-1 font-semibold rounded-md transition-all text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white">
            🌐 Macro
          </button>
        </nav>
      </div>

      <!-- Center Controls (Category Dropdown + Sentiment Filters / IPO Subfilters) -->
      <div class="flex items-center gap-2.5 flex-wrap flex-1 max-w-2xl">
        
        <!-- Feed Controls -->
        <div id="feed-controls" class="flex items-center gap-2 flex-wrap">
          <select id="category-select" onchange="onCategorySelect(this.value)" class="text-[12.5px] font-bold px-2.5 py-1 rounded-md border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-[#141A2E] text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-1 focus:ring-brand-500">
            <option value="ALL">✨ All Sections (218)</option>
            <option value="Sector">Sector (43)</option>
            <option value="Corporate Events">Corporate Events (33)</option>
            <option value="Economy">Economy (25)</option>
            <option value="Policy">Policy (23)</option>
            <option value="Market">Market (18)</option>
            <option value="IPO">IPO (17)</option>
            <option value="International News">International (8)</option>
            <option value="Corporate Appointments">Appointments (5)</option>
            <option value="Trade">Trade (4)</option>
            <option value="Others">Others (42)</option>
          </select>

          <div class="flex items-center bg-slate-100 dark:bg-[#141A2E] p-0.5 rounded-md border border-slate-200 dark:border-slate-800 text-[12px] font-bold">
            <button id="sent-all" onclick="setFeedSentiment('ALL')" class="px-2.5 py-0.5 rounded bg-white dark:bg-slate-800 text-slate-900 dark:text-white shadow-xs">
              All (<span id="feed-count-all">218</span>)
            </button>
            <button id="sent-bullish" onclick="setFeedSentiment('BULLISH')" class="px-2.5 py-0.5 rounded text-emerald-700 dark:text-emerald-400 hover:bg-emerald-50 dark:hover:bg-emerald-950/30 flex items-center gap-1">
              <span>🟢</span> Bullish (<span id="feed-count-bullish">0</span>)
            </button>
            <button id="sent-bearish" onclick="setFeedSentiment('BEARISH')" class="px-2.5 py-0.5 rounded text-rose-700 dark:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-950/30 flex items-center gap-1">
              <span>🔴</span> Bearish (<span id="feed-count-bearish">0</span>)
            </button>
          </div>
        </div>

        <!-- IPO Controls -->
        <div id="ipo-controls" class="hidden items-center gap-2 flex-wrap">
          <div class="flex items-center bg-slate-100 dark:bg-[#141A2E] p-0.5 rounded-md border border-slate-200 dark:border-slate-800 text-[12px] font-bold">
            <button id="ipo-stage-all" onclick="filterIpoTable('ALL')" class="px-2.5 py-0.5 rounded bg-brand-600 text-white shadow-xs">All (17)</button>
            <button id="ipo-stage-drhp" onclick="filterIpoTable('DRHP')" class="px-2.5 py-0.5 rounded text-slate-600 dark:text-slate-400">📋 DRHP (9)</button>
            <button id="ipo-stage-bidding" onclick="filterIpoTable('BIDDING')" class="px-2.5 py-0.5 rounded text-slate-600 dark:text-slate-400">📈 Subscriptions (5)</button>
            <button id="ipo-stage-notices" onclick="filterIpoTable('NOTICES')" class="px-2.5 py-0.5 rounded text-slate-600 dark:text-slate-400">🏛️ Allotments (3)</button>
          </div>
          <button onclick="exportIpoCsv()" class="px-2.5 py-0.5 text-[11.5px] font-mono font-bold rounded border border-slate-200 dark:border-slate-700 bg-white dark:bg-[#141A2E] text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 flex items-center gap-1 shadow-xs">
            📥 CSV Export
          </button>
        </div>

      </div>

      <!-- Right: Search + Pulse + Theme Switcher -->
      <div class="flex items-center gap-2.5 shrink-0">
        <div class="relative w-52 sm:w-64">
          <input type="text" id="global-search" oninput="onSearchInput()" placeholder="Search stock (e.g. Coal India, SAIL)..." class="w-full text-[12.5px] pl-7 pr-7 py-1 rounded-md border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-[#141A2E] text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:border-brand-500 focus:bg-white dark:focus:bg-[#0E1322] font-medium"/>
          <span class="absolute left-2 top-1.5 text-slate-400 text-[11px]">🔍</span>
          <button id="clear-search-btn" onclick="clearSearch()" class="hidden absolute right-2 top-1 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 text-xs font-bold p-0.5">✕</button>
        </div>

        <button onclick="toggleTheme()" class="w-7 h-7 rounded-md border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-[#141A2E] text-slate-700 dark:text-slate-300 flex items-center justify-center text-xs shadow-xs hover:bg-slate-100 dark:hover:bg-slate-800" title="Toggle Light/Dark Theme">
          <span id="theme-icon">🌙</span>
        </button>
      </div>

    </header>

    <!-- Slim Market Pulse Bar -->
    <div class="bg-slate-900 text-slate-300 text-[11px] font-mono px-3.5 py-1 flex items-center justify-between overflow-x-auto whitespace-nowrap gap-4 border-b border-slate-800">
      <div class="flex items-center gap-3.5">
        <span class="text-amber-400 font-bold">PULSE:</span>
        <span>NIFTY <b class="text-emerald-400 font-bold">24,835 (+0.64%)</b></span>
        <span>BANK NIFTY <b class="text-emerald-400 font-bold">54,120 (+0.82%)</b></span>
        <span>INDIA VIX <b class="text-rose-400 font-bold">12.85 (-3.2%)</b></span>
        <span>BRENT <b class="text-amber-300 font-bold">\$74.2/bbl</b></span>
        <span>USD/INR <b class="text-slate-200 font-bold">₹83.65</b></span>
      </div>
      <div class="flex items-center gap-3 text-slate-400">
        <div class="flex items-center gap-1.5 bg-slate-800 px-2 py-0.5 rounded border border-slate-700">
          <span class="text-slate-400 text-[10.5px]">📅 Edition:</span>
          <select id="edition-date-select" onchange="onDateChange(this.value)" class="bg-transparent text-slate-100 font-bold font-mono text-[11px] focus:outline-none cursor-pointer">
            <option value="latest">Latest Edition</option>
          </select>
        </div>
        <span id="scan-count-badge" class="text-emerald-400 font-bold">● 218 Stories Scanned (FE + BS)</span>
      </div>
    </div>

    <!-- ================= MAIN THREE-COLUMN WORKSPACE ================= -->
    <main class="mx-auto max-w-[1920px] w-full px-3 py-2 flex-1 flex flex-col gap-2">
      
      <!-- ================= VIEW 1: NEWS STREAM (NO GRID · SPLIT WITH STOCKS IN FOCUS ON RIGHT) ================= -->
      <section id="view-feed" class="grid grid-cols-1 lg:grid-cols-[400px_minmax(0,1fr)_300px] xl:grid-cols-[440px_minmax(0,1fr)_330px] gap-2.5 items-start">
        
        <!-- COLUMN 1: COMPACT NEWS FEED LIST -->
        <div class="rounded-xl bg-white dark:bg-[#0E1322] border border-slate-200 dark:border-slate-800 overflow-hidden shadow-xs flex flex-col">
          <div class="px-3.5 py-2 border-b border-slate-100 dark:border-slate-800 bg-slate-50/80 dark:bg-slate-900/50 flex items-center justify-between text-[12px] font-mono">
            <span id="feed-list-count" class="font-bold text-slate-800 dark:text-slate-200">218 Stories</span>
            <span class="text-slate-400">Keys: <kbd class="px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-[10px] font-bold">J</kbd> / <kbd class="px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-[10px] font-bold">K</kbd></span>
          </div>

          <div id="feed-list-container" class="divide-y divide-slate-100 dark:divide-slate-800/80 max-h-[calc(100vh-6.5rem)] overflow-y-auto">
            <!-- Dynamically populated story items -->
          </div>
        </div>

        <!-- COLUMN 2: ACTIVE STORY DEEP DIVE & CATALYST INTELLIGENCE -->
        <div class="rounded-xl bg-white dark:bg-[#0E1322] border border-slate-200 dark:border-slate-800 p-5 shadow-xs sticky top-14 flex flex-col gap-3.5 min-h-[calc(100vh-6.5rem)] max-h-[calc(100vh-6.5rem)] overflow-y-auto">
          <div id="feed-detail-container">
            <!-- Dynamically populated active story intelligence -->
          </div>
        </div>

        <!-- COLUMN 3: RIGHT HAND SIDE PANEL (STOCKS IN FOCUS & TRADING CATALYSTS) -->
        <aside class="flex flex-col gap-2.5 sticky top-14 max-h-[calc(100vh-6.5rem)] overflow-y-auto">
          
          <!-- Stocks in Focus Card -->
          <div class="rounded-xl bg-white dark:bg-[#0E1322] border border-slate-200 dark:border-slate-800 p-3.5 shadow-xs flex flex-col gap-2.5">
            <div class="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-2">
              <span class="text-[12.5px] font-bold uppercase tracking-wider text-slate-800 dark:text-slate-200 flex items-center gap-1.5 font-mono">
                <span>🏷️</span> <span>Stocks in Focus</span>
              </span>
              <button id="clear-ticker-filter" onclick="clearTickerFilter()" class="hidden text-[11px] font-mono text-brand-600 dark:text-brand-400 font-bold hover:underline">
                Clear (✕)
              </button>
            </div>

            <p class="text-[11.5px] text-slate-500 dark:text-slate-400 leading-snug">Click any stock to filter stories immediately:</p>

            <!-- Stock Ticker Pill Matrix -->
            <div id="stocks-focus-list" class="flex flex-wrap gap-1.5 max-h-[240px] overflow-y-auto pt-0.5">
              <!-- Dynamically populated ticker chips -->
            </div>
          </div>

          <!-- Top Bullish Triggers Card -->
          <div class="rounded-xl bg-white dark:bg-[#0E1322] border border-emerald-200/80 dark:border-slate-800 p-3.5 shadow-xs flex flex-col gap-2">
            <div class="flex items-center justify-between border-b border-emerald-100 dark:border-slate-800 pb-1.5">
              <span class="text-[12px] font-mono font-bold uppercase tracking-wider text-emerald-700 dark:text-emerald-400 flex items-center gap-1.5">
                <span>🟢</span> <span>Top Bullish Triggers</span>
              </span>
            </div>
            <div id="top-bullish-list" class="divide-y divide-slate-100 dark:divide-slate-800 text-[12.5px] space-y-1.5">
              <!-- Dynamically populated top bullish triggers -->
            </div>
          </div>

          <!-- Top Bearish Risks Card -->
          <div class="rounded-xl bg-white dark:bg-[#0E1322] border border-rose-200/80 dark:border-slate-800 p-3.5 shadow-xs flex flex-col gap-2">
            <div class="flex items-center justify-between border-b border-rose-100 dark:border-slate-800 pb-1.5">
              <span class="text-[12px] font-mono font-bold uppercase tracking-wider text-rose-700 dark:text-rose-400 flex items-center gap-1.5">
                <span>🔴</span> <span>Key Risks & Downside</span>
              </span>
            </div>
            <div id="top-bearish-list" class="divide-y divide-slate-100 dark:divide-slate-800 text-[12.5px] space-y-1.5">
              <!-- Dynamically populated top bearish risks -->
            </div>
          </div>

        </aside>

      </section>

      <!-- ================= VIEW 2: TABULAR IPO CENTRAL ================= -->
      <section id="view-ipo" class="hidden flex-col gap-2">
        <div class="rounded-xl bg-white dark:bg-[#0E1322] border border-slate-200 dark:border-slate-800 shadow-xs overflow-hidden flex flex-col">
          
          <div class="px-4 py-2 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between bg-slate-50/70 dark:bg-[#11172A]/70 text-[12.5px] font-mono">
            <span class="font-bold text-slate-800 dark:text-slate-200 flex items-center gap-2">
              <span>🚀</span> <span>PRIMARY MARKET TRACKER (17 IPOs · ₹5,600+ Cr Capital Tracked)</span>
            </span>
            <span class="text-slate-400">Showing: <b id="ipo-table-visible-count" class="text-brand-600 font-bold">17</b> Records</span>
          </div>

          <div class="overflow-x-auto max-h-[calc(100vh-6.5rem)] overflow-y-auto">
            <table class="w-full text-left border-collapse text-[13.5px]">
              <thead class="sticky top-0 z-10 bg-slate-100 dark:bg-[#141A2E] shadow-xs">
                <tr class="border-b border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 text-[11.5px] font-mono uppercase tracking-wider font-bold">
                  <th class="py-2.5 px-3.5">#</th>
                  <th class="py-2.5 px-3.5 min-w-[220px]">Company / Issuer</th>
                  <th class="py-2.5 px-3.5 min-w-[110px]">Issue Size</th>
                  <th class="py-2.5 px-3.5 min-w-[130px]">Stage / Status</th>
                  <th class="py-2.5 px-3.5 min-w-[130px]">Subscription Demand</th>
                  <th class="py-2.5 px-3.5 min-w-[340px]">Key Analyst Insight & Details</th>
                  <th class="py-2.5 px-3.5 min-w-[130px]">Source</th>
                  <th class="py-2.5 px-3.5 text-center">Action</th>
                </tr>
              </thead>
              <tbody id="ipo-table-body" class="divide-y divide-slate-100 dark:divide-slate-800/70">
                <!-- Dynamically populated IPO rows -->
              </tbody>
            </table>
          </div>

        </div>
      </section>

    </main>

  </div>

  <!-- ================= CLIENT JAVASCRIPT ================= -->
  <script>
    let rawReport = null;
    let stories = [];
    let ipoList = [];
    let currentView = "feed";
    let selectedFeedCategory = "ALL";
    let selectedFeedSentiment = "ALL";
    let activeTickerFilter = null;
    let selectedStoryIndex = 0;
    let currentIpoFilter = "ALL";
    let currentSearchQuery = "";

    const allowedSections = [
      "ALL", "Economy", "Policy", "Sector", "IPO", "Market", "Trade",
      "Corporate Events", "Corporate Appointments", "International News", "Others"
    ];

    const tickerDictionary = [
      "RELIANCE", "TCS", "INFOSYS", "INFY", "HDFC BANK", "HDFCBANK", "ICICI BANK", "ICICIBANK", "SBI", "SBIN",
      "BHARTI AIRTEL", "AIRTEL", "ITC", "KOTAK BANK", "L&T", "LT", "TATA MOTORS", "TATA STEEL", "MARUTI",
      "SUN PHARMA", "TITAN", "BAJAJ FINANCE", "ADANI", "NTPC", "ONGC", "POWERGRID", "JSW STEEL", "COAL INDIA",
      "COALINDIA", "SAIL", "BCCL", "NCL", "HINDALCO", "WIPRO", "TECH MAHINDRA", "ZOMATO", "PAYTM", "SWIGGY",
      "HAL", "BEL", "BHEL", "BDL", "IRFC", "RVNL", "IREDA", "VEDANTA", "DLF", "GODREJ", "AXIS BANK", "ASIAN PAINTS",
      "ULTRATECH", "HERO MOTOCORP", "BAJAJ AUTO", "EICHER", "DR REDDY", "CIPLA", "TRENT", "DMART", "POLYCAB",
      "DIXON", "BSE", "MCX", "CDSL", "AUTO", "BANKING", "DEFENCE", "REALTY", "PHARMA", "IT", "METALS", "ENERGY",
      "TELECOM", "FMCG", "INFRA", "POWER"
    ];

    function initTheme() {
      const t = localStorage.getItem('finbrief_theme') || 'light';
      applyTheme(t);
    }
    function toggleTheme() {
      const isDark = document.documentElement.classList.contains('dark');
      const next = isDark ? 'light' : 'dark';
      applyTheme(next);
      localStorage.setItem('finbrief_theme', next);
    }
    function applyTheme(t) {
      const icon = document.getElementById('theme-icon');
      if (t === 'dark') {
        document.documentElement.classList.add('dark');
        if (icon) icon.textContent = '☀️';
      } else {
        document.documentElement.classList.remove('dark');
        if (icon) icon.textContent = '🌙';
      }
    }

    function switchView(viewName) {
      currentView = viewName;
      const tabFeed = document.getElementById("tab-btn-feed");
      const tabIpo = document.getElementById("tab-btn-ipo");
      const tabCorp = document.getElementById("tab-btn-corporate");
      const tabMacro = document.getElementById("tab-btn-macro");
      const viewFeed = document.getElementById("view-feed");
      const viewIpo = document.getElementById("view-ipo");
      const feedControls = document.getElementById("feed-controls");
      const ipoControls = document.getElementById("ipo-controls");

      [tabFeed, tabIpo, tabCorp, tabMacro].forEach(b => {
        b.className = "px-3 py-1 font-semibold rounded-md transition-all text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white flex items-center gap-1.5";
      });

      if (viewName === "feed") {
        tabFeed.className = "px-3 py-1 font-bold rounded-md transition-all bg-white dark:bg-brand-600 text-slate-900 dark:text-white shadow-xs flex items-center gap-1.5";
        viewFeed.classList.remove("hidden");
        viewFeed.classList.add("grid");
        viewIpo.classList.add("hidden");
        feedControls.classList.remove("hidden");
        ipoControls.classList.add("hidden");
        ipoControls.classList.remove("flex");
        selectedFeedCategory = "ALL";
        document.getElementById("category-select").value = "ALL";
        renderFeedList();
      } else if (viewName === "ipo") {
        tabIpo.className = "px-3 py-1 font-bold rounded-md transition-all bg-white dark:bg-brand-600 text-slate-900 dark:text-white shadow-xs flex items-center gap-1.5";
        viewFeed.classList.add("hidden");
        viewFeed.classList.remove("grid");
        viewIpo.classList.remove("hidden");
        viewIpo.classList.add("flex");
        feedControls.classList.add("hidden");
        ipoControls.classList.remove("hidden");
        ipoControls.classList.add("flex");
        renderIpoTable();
      } else if (viewName === "corporate") {
        tabCorp.className = "px-3 py-1 font-bold rounded-md transition-all bg-white dark:bg-brand-600 text-slate-900 dark:text-white shadow-xs flex items-center gap-1.5";
        viewFeed.classList.remove("hidden");
        viewFeed.classList.add("grid");
        viewIpo.classList.add("hidden");
        feedControls.classList.remove("hidden");
        ipoControls.classList.add("hidden");
        selectedFeedCategory = "Corporate Events";
        document.getElementById("category-select").value = "Corporate Events";
        renderFeedList();
      } else if (viewName === "macro") {
        tabMacro.className = "px-3 py-1 font-bold rounded-md transition-all bg-white dark:bg-brand-600 text-slate-900 dark:text-white shadow-xs flex items-center gap-1.5";
        viewFeed.classList.remove("hidden");
        viewFeed.classList.add("grid");
        viewIpo.classList.add("hidden");
        feedControls.classList.remove("hidden");
        ipoControls.classList.add("hidden");
        selectedFeedCategory = "Economy";
        document.getElementById("category-select").value = "Economy";
        renderFeedList();
      }
    }

    function onCategorySelect(val) {
      selectedFeedCategory = val;
      renderFeedList();
    }

    function parseStory(story, idx) {
      const text = (story.headline + " " + story.brief_details + " " + (story.bullet_points || []).join(" ")).toLowerCase();
      const bullishWords = ["surge", "growth", "profit up", "revenue up", "expansion", "order win", "contract", "approval", "bonus", "dividend", "outperform", "bullish", "record high", "upgrade", "stake buy", "acquisition", "rate cut", "duty cut", "exemption", "inflow", "raises guidance"];
      const bearishWords = ["drop", "slump", "falls", "loss", "losses", "profit down", "revenue falls", "probe", "penalty", "fine", "fraud", "curb", "default", "downgrade", "weak", "warning", "tax hike", "tariff", "outflow", "selloff", "strike", "dispute", "cancellation"];

      let b = 0, r = 0;
      bullishWords.forEach(w => { if (text.includes(w)) b++; });
      bearishWords.forEach(w => { if (text.includes(w)) r++; });

      let sentiment = "NEUTRAL";
      if (b > r) sentiment = "BULLISH";
      else if (r > b) sentiment = "BEARISH";

      const detectedTickers = [];
      const upperText = (story.headline + " " + story.brief_details + " " + (story.bullet_points || []).join(" ")).toUpperCase();
      tickerDictionary.forEach(t => {
        if (new RegExp(\`\\\\b\${t}\\\\b\`, 'i').test(upperText)) detectedTickers.push(t);
      });

      let catalyst = (story.bullet_points && story.bullet_points.length > 0) ? story.bullet_points[0] : story.brief_details.slice(0, 160) + "...";

      return {
        ...story,
        id: idx + 1,
        sentiment,
        tickers: [...new Set(detectedTickers)].slice(0, 3),
        catalyst,
        category: allowedSections.includes(story.category) ? story.category : "Others"
      };
    }

    function parseIpoItem(s, idx) {
      const h = s.headline;
      const d = s.brief_details;
      const combined = (h + " " + d).toLowerCase();

      let company = h.replace(/public announcement|basis of allotment|files ipo papers|files draft ipo papers|ipo subscribed|files for|shelves|amid market uncertainty/gi, '').trim();
      company = company.replace(/^(biscuit maker|nine firms filing ipo papers with sebi:|after reverse flip to india: cfo)/gi, '').trim();
      if (company.length > 32) company = company.slice(0, 32) + '...';

      let size = "Not Disclosed";
      const sizeMatch = (h + " " + d).match(/(?:₹|ₐ|rs\\.?)\\s?([\\d,]+(?:\\.\\d+)?)\\s?(?:cr|crore|lakh)/i);
      if (sizeMatch) size = \`₹\${sizeMatch[1]} Cr\`;
      else if (combined.includes("fresh issue")) size = "Fresh Issue";
      else if (combined.includes("sme")) size = "SME Issue";

      let stage = "📋 DRHP Filed";
      let stageBadge = "bg-amber-50 text-amber-800 border-amber-200 dark:bg-amber-950/40 dark:text-amber-300";
      let filterTag = "DRHP";

      if (combined.includes("subscribed")) {
        stage = "📈 Active Bidding";
        stageBadge = "bg-emerald-50 text-emerald-800 border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300";
        filterTag = "BIDDING";
      } else if (combined.includes("allotment") || combined.includes("basis")) {
        stage = "🏛️ Allotment Out";
        stageBadge = "bg-blue-50 text-blue-800 border-blue-200 dark:bg-blue-950/40 dark:text-blue-300";
        filterTag = "NOTICES";
      } else if (combined.includes("shelve") || combined.includes("delay")) {
        stage = "⏸️ Deferred";
        stageBadge = "bg-rose-50 text-rose-800 border-rose-200 dark:bg-rose-950/40 dark:text-rose-300";
        filterTag = "DRHP";
      } else if (combined.includes("announcement") || combined.includes("notice")) {
        stage = "📢 Public Issue Notice";
        stageBadge = "bg-purple-50 text-purple-800 border-purple-200 dark:bg-purple-950/40 dark:text-purple-300";
        filterTag = "NOTICES";
      }

      let demand = "Filing Stage";
      const subMatch = (h + " " + d).match(/subscribed\\s+([\\d\\.]+)\\s+(?:times|x)/i);
      const subPctMatch = (h + " " + d).match(/subscribed\\s+([\\d\\.]+%)/i);
      if (subMatch) demand = \`\${subMatch[1]}x Subscribed\`;
      else if (subPctMatch) demand = \`\${subPctMatch[1]} Subscribed\`;
      else if (stage.includes("Allotment")) demand = "Completed";

      return {
        id: idx + 1,
        headline: h,
        company: company || h.slice(0, 25),
        size,
        stage,
        stageBadge,
        filterTag,
        demand,
        details: d,
        source: s.page_numbers || "FE / BS"
      };
    }

    async function fetchDates() {
      try {
        const res = await fetch('/api/dates');
        if (res.ok) {
          const dates = await res.json();
          const select = document.getElementById("edition-date-select");
          if (dates && dates.length > 0) {
            select.innerHTML = "";
            dates.forEach((d, idx) => {
              const opt = document.createElement("option");
              opt.value = d;
              opt.textContent = idx === 0 ? \`\${d} (Latest)\` : d;
              opt.className = "bg-slate-900 text-white font-mono";
              select.appendChild(opt);
            });
          }
        }
      } catch (e) {}
    }

    async function onDateChange(selectedDate) {
      await loadData(selectedDate);
    }

    async function loadData(targetDate = null) {
      try {
        const endpoint = targetDate ? \`/api/report?date=\${targetDate}\` : '/api/report';
        const res = await fetch(endpoint);
        if (!res.ok) throw new Error("Failed");
        rawReport = await res.json();
      } catch (e) {
        try {
          const fallbackUrl = targetDate 
            ? \`https://pub-c81167dd545d49d0a2cd964a8bd6a1cd.r2.dev/reports/news_report_unified_\${targetDate}.json\`
            : 'https://pub-c81167dd545d49d0a2cd964a8bd6a1cd.r2.dev/reports/news_report_unified_latest.json';
          const res = await fetch(fallbackUrl);
          rawReport = await res.json();
        } catch (err) {}
      }

      if (rawReport && rawReport.major_stories) {
        const dateSelect = document.getElementById("edition-date-select");
        if (dateSelect && rawReport.edition_date && !targetDate) {
          // If option exists, select it
          for (let opt of dateSelect.options) {
            if (opt.value === rawReport.edition_date) {
              opt.selected = true;
              break;
            }
          }
        }
        stories = rawReport.major_stories.map((s, idx) => parseStory(s, idx));
        const rawIpos = stories.filter(s => s.category === "IPO");
        ipoList = rawIpos.map((s, idx) => parseIpoItem(s, idx));
        initMetrics();
      }
    }

    function initMetrics() {
      document.getElementById("tab-feed-count").textContent = stories.length;
      document.getElementById("tab-ipo-count").textContent = ipoList.length;

      let bCount = 0, rCount = 0;
      stories.forEach(s => {
        if (s.sentiment === "BULLISH") bCount++;
        else if (s.sentiment === "BEARISH") rCount++;
      });
      document.getElementById("feed-count-all").textContent = stories.length;
      document.getElementById("feed-count-bullish").textContent = bCount;
      document.getElementById("feed-count-bearish").textContent = rCount;

      renderStocksFocusSidebar();
      renderFeedList();
      renderIpoTable();
    }

    // ================= SEARCH HANDLING =================
    function onSearchInput() {
      const val = document.getElementById("global-search").value.trim();
      currentSearchQuery = val;
      document.getElementById("clear-search-btn").classList.toggle("hidden", val.length === 0);
      
      if (currentView === "ipo") {
        renderIpoTable();
      } else {
        renderFeedList();
      }
    }

    function clearSearch() {
      document.getElementById("global-search").value = "";
      currentSearchQuery = "";
      document.getElementById("clear-search-btn").classList.add("hidden");
      if (currentView === "ipo") renderIpoTable();
      else renderFeedList();
    }

    // ================= RIGHT HAND SIDEBAR: STOCKS IN FOCUS =================
    function renderStocksFocusSidebar() {
      const list = document.getElementById("stocks-focus-list");
      list.innerHTML = "";

      const counts = {};
      stories.forEach(s => {
        s.tickers.forEach(t => counts[t] = (counts[t] || 0) + 1);
      });

      const sorted = Object.keys(counts).sort((a,b) => counts[b] - counts[a]);

      sorted.forEach(t => {
        const isSelected = activeTickerFilter === t;
        const btn = document.createElement("button");
        btn.className = \`px-2.5 py-1 rounded-md text-[11.5px] font-mono font-bold transition-all shadow-2xs \${isSelected ? 'bg-brand-600 text-white shadow-xs' : 'bg-slate-100 dark:bg-[#141A2E] border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300 hover:border-brand-500 hover:text-brand-600 dark:hover:text-brand-400'}\`;
        btn.textContent = \`\${t} (\${counts[t]})\`;
        btn.onclick = () => {
          activeTickerFilter = activeTickerFilter === t ? null : t;
          document.getElementById("clear-ticker-filter").classList.toggle("hidden", !activeTickerFilter);
          renderStocksFocusSidebar();
          renderFeedList();
        };
        list.appendChild(btn);
      });

      // Render Top Bullish & Bearish Widgets
      const bullishList = document.getElementById("top-bullish-list");
      bullishList.innerHTML = "";
      stories.filter(s => s.sentiment === "BULLISH").slice(0, 3).forEach(s => {
        const d = document.createElement("div");
        d.className = "py-1.5 cursor-pointer hover:text-brand-600 transition-colors";
        d.onclick = () => {
          const idx = stories.findIndex(item => item.headline === s.headline);
          if (idx !== -1) { selectedStoryIndex = idx; renderFeedList(); }
        };
        d.innerHTML = \`
          <p class="font-bold text-[13px] leading-snug line-clamp-2">\${s.headline}</p>
          <p class="text-[11px] font-mono text-emerald-600 dark:text-emerald-400 mt-0.5 font-medium">\${s.category} · \${s.page_numbers}</p>
        \`;
        bullishList.appendChild(d);
      });

      const bearishList = document.getElementById("top-bearish-list");
      bearishList.innerHTML = "";
      stories.filter(s => s.sentiment === "BEARISH").slice(0, 3).forEach(s => {
        const d = document.createElement("div");
        d.className = "py-1.5 cursor-pointer hover:text-rose-600 transition-colors";
        d.onclick = () => {
          const idx = stories.findIndex(item => item.headline === s.headline);
          if (idx !== -1) { selectedStoryIndex = idx; renderFeedList(); }
        };
        d.innerHTML = \`
          <p class="font-bold text-[13px] leading-snug line-clamp-2">\${s.headline}</p>
          <p class="text-[11px] font-mono text-rose-600 dark:text-rose-400 mt-0.5 font-medium">\${s.category} · \${s.page_numbers}</p>
        \`;
        bearishList.appendChild(d);
      });
    }

    function clearTickerFilter() {
      activeTickerFilter = null;
      document.getElementById("clear-ticker-filter").classList.add("hidden");
      renderStocksFocusSidebar();
      renderFeedList();
    }

    function setFeedSentiment(sent) {
      selectedFeedSentiment = sent;
      document.querySelectorAll("[id^='sent-']").forEach(b => {
        b.className = "px-2.5 py-0.5 rounded text-slate-600 dark:text-slate-400 hover:bg-white/60 dark:hover:bg-slate-800/60";
      });
      const el = document.getElementById(\`sent-\${sent.toLowerCase()}\`);
      if (el) {
        el.className = sent === "BULLISH" 
          ? "px-2.5 py-0.5 rounded bg-emerald-600 text-white shadow-xs" 
          : sent === "BEARISH" 
          ? "px-2.5 py-0.5 rounded bg-rose-600 text-white shadow-xs" 
          : "px-2.5 py-0.5 rounded bg-white dark:bg-slate-800 text-slate-900 dark:text-white shadow-xs";
      }
      renderFeedList();
    }

    // ================= FEED LIST & ACTIVE STORY DETAIL =================
    function renderFeedList() {
      const rawQuery = document.getElementById("global-search").value.trim().toLowerCase();
      const queryTokens = rawQuery ? rawQuery.split(/\\s+/).filter(Boolean) : [];
      
      const displayed = stories.filter(s => {
        // Build full searchable text blob for comprehensive search
        const searchableText = (
          s.headline + " " + 
          s.brief_details + " " + 
          (s.bullet_points || []).join(" ") + " " + 
          s.category + " " + 
          s.page_numbers + " " + 
          s.tickers.join(" ")
        ).toLowerCase();

        // Tokenized multi-word search: all query tokens must be found
        const matchQuery = queryTokens.length === 0 || queryTokens.every(tok => searchableText.includes(tok));
        
        // If a specific search query is actively typed, prioritize matching across all categories
        const matchSec = (queryTokens.length > 0 && selectedFeedCategory === "ALL") || selectedFeedCategory === "ALL" || s.category === selectedFeedCategory;
        const matchSent = selectedFeedSentiment === "ALL" || s.sentiment === selectedFeedSentiment;
        const matchTicker = !activeTickerFilter || s.tickers.includes(activeTickerFilter);

        return matchSec && matchSent && matchTicker && matchQuery;
      });

      document.getElementById("feed-list-count").textContent = \`\${displayed.length} Stories\`;

      const listContainer = document.getElementById("feed-list-container");
      listContainer.innerHTML = "";

      if (displayed.length === 0) {
        listContainer.innerHTML = \`
          <div class="p-8 text-center text-slate-400">
            <p class="text-base font-bold text-slate-600 dark:text-slate-300">No news stories found</p>
            <p class="text-[12.5px] mt-1">Try broadening your search term or clearing active filters.</p>
            \${rawQuery ? \`<button onclick="clearSearch()" class="mt-3 px-3 py-1 bg-brand-600 text-white rounded-md text-xs font-bold">Clear Search</button>\` : ''}
          </div>
        \`;
        document.getElementById("feed-detail-container").innerHTML = \`<div class="p-8 text-center text-slate-400 text-[13.5px]">Select a story to view analysis.</div>\`;
        return;
      }

      if (selectedStoryIndex >= displayed.length) selectedStoryIndex = 0;

      displayed.forEach((s, idx) => {
        const isSelected = idx === selectedStoryIndex;
        const numStr = (idx + 1).toString().padStart(2, '0');
        const dot = s.sentiment === "BULLISH" ? "bg-emerald-500" : s.sentiment === "BEARISH" ? "bg-rose-500" : "bg-slate-400";
        const tickerBadges = s.tickers.map(t => \`<span class="px-1.5 py-0.2 text-[10px] font-mono font-bold rounded bg-brand-50 text-brand-700 border border-brand-200 dark:bg-brand-400/10 dark:text-brand-300">\${t}</span>\`).join('');

        const btn = document.createElement("button");
        btn.className = \`w-full text-left px-3.5 py-2.5 transition-colors flex items-start gap-2.5 border-b border-slate-100 dark:border-slate-800/80 last:border-b-0 \${isSelected ? 'bg-brand-50/90 dark:bg-brand-500/15 border-l-4 border-l-brand-600' : 'hover:bg-slate-50 dark:hover:bg-slate-800/50'}\`;
        btn.onclick = () => {
          selectedStoryIndex = idx;
          renderFeedList();
        };

        btn.innerHTML = \`
          <span class="shrink-0 text-[11.5px] font-mono font-semibold text-slate-400 tabular-nums mt-0.5">\${numStr}</span>
          <div class="flex-1 min-w-0">
            <div class="flex items-center justify-between gap-1 mb-1">
              <div class="flex items-center gap-1.5">
                <span class="w-2 h-2 rounded-full \${dot}"></span>
                <span class="text-[10.5px] font-mono text-slate-500 dark:text-slate-400 uppercase font-bold tracking-wide">\${s.category}</span>
              </div>
              <span class="text-[10.5px] font-mono text-slate-400">\${s.page_numbers}</span>
            </div>
            <h4 class="text-[14px] font-bold leading-snug \${isSelected ? 'text-brand-900 dark:text-brand-200' : 'text-slate-900 dark:text-slate-100'} line-clamp-2">\${highlightSearchTokens(s.headline, queryTokens)}</h4>
            \${s.tickers.length > 0 ? \`<div class="flex items-center gap-1 mt-1.5">\${tickerBadges}</div>\` : ''}
          </div>
        \`;
        listContainer.appendChild(btn);
      });

      renderActiveStoryDetail(displayed[selectedStoryIndex], queryTokens);
    }

    function renderActiveStoryDetail(story, queryTokens = []) {
      const container = document.getElementById("feed-detail-container");
      if (!story) return;

      const isBullish = story.sentiment === "BULLISH";
      const isBearish = story.sentiment === "BEARISH";
      const sentBadge = isBullish 
        ? \`<span class="px-2.5 py-1 rounded text-[11px] font-mono font-bold bg-emerald-50 text-emerald-700 border border-emerald-200 dark:bg-emerald-950/50 dark:text-emerald-300">🟢 BULLISH CATALYST</span>\`
        : isBearish 
        ? \`<span class="px-2.5 py-1 rounded text-[11px] font-mono font-bold bg-rose-50 text-rose-700 border border-rose-200 dark:bg-rose-950/50 dark:text-rose-300">🔴 BEARISH DOWNSIDE</span>\`
        : \`<span class="px-2.5 py-1 rounded text-[11px] font-mono font-bold bg-slate-100 text-slate-600 border border-slate-200 dark:bg-slate-800 dark:text-slate-300">⚪ NEUTRAL WATCHLIST</span>\`;

      const tickerBadges = story.tickers.map(t => \`<span class="px-2 py-0.5 text-[11px] font-mono font-bold rounded-md bg-brand-50 text-brand-700 border border-brand-200 dark:bg-brand-400/15 dark:text-brand-300">\${t}</span>\`).join('');

      container.innerHTML = \`
        <div class="flex items-center justify-between gap-2 flex-wrap pb-2.5 border-b border-slate-100 dark:border-slate-800">
          <div class="flex items-center gap-2">
            <span class="text-[11.5px] font-mono font-bold px-2.5 py-0.5 rounded bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-200">\${story.category}</span>
            <span class="text-[12px] text-slate-400 font-mono font-medium">\${story.page_numbers}</span>
          </div>
          <div class="flex items-center gap-2.5">
            \${sentBadge}
            <button onclick="copyToClipboard('\${escapeQuotes(story.headline + '\\\\n\\\\n' + story.brief_details)}')" class="text-[11.5px] text-slate-600 hover:text-slate-900 dark:text-slate-300 dark:hover:text-white font-mono flex items-center gap-1 font-semibold px-2 py-0.5 rounded border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-[#141A2E]" title="Copy to clipboard">
              📋 Copy
            </button>
          </div>
        </div>

        <h1 class="text-[20px] font-extrabold text-slate-900 dark:text-white leading-snug mt-1">\${highlightSearchTokens(highlightNumbers(story.headline), queryTokens)}</h1>

        \${story.tickers.length > 0 ? \`
          <div class="flex items-center gap-2 flex-wrap mt-0.5">
            <span class="text-[11px] font-mono text-slate-400 font-bold">STOCKS:</span>
            \${tickerBadges}
          </div>
        \` : ''}

        <!-- Executive Overview -->
        <div class="mt-2.5 p-4 rounded-xl bg-brand-50/70 dark:bg-brand-950/25 border border-brand-200/90 dark:border-brand-500/30 shadow-2xs">
          <p class="text-[11.5px] font-mono font-bold uppercase tracking-wider text-brand-800 dark:text-brand-400 mb-1.5 flex items-center gap-1.5">
            <span>⚡</span> <span>Executive Intelligence</span>
          </p>
          <p class="text-[14.5px] text-slate-800 dark:text-slate-200 leading-relaxed font-normal">\${highlightSearchTokens(highlightNumbers(story.brief_details), queryTokens)}</p>
        </div>

        <!-- Catalyst Bullets -->
        <div class="mt-3">
          <p class="text-[11.5px] font-mono font-bold uppercase tracking-wider text-slate-400 mb-2">Key Analyst Bullets</p>
          <ul class="space-y-2">
            \${(story.bullet_points || []).map(bp => \`
              <li class="flex items-start gap-2.5 text-[14px] text-slate-700 dark:text-slate-300 leading-relaxed bg-slate-50 dark:bg-[#11172A] p-2.5 rounded-lg border border-slate-200/80 dark:border-slate-800">
                <span class="text-brand-600 dark:text-brand-400 font-bold text-base leading-none select-none mt-0.5">›</span>
                <span>\${highlightSearchTokens(highlightNumbers(bp), queryTokens)}</span>
              </li>
            \`).join('')}
          </ul>
        </div>
      \`;
    }

    // ================= IPO TABLE RENDERING =================
    function filterIpoTable(tag) {
      currentIpoFilter = tag;
      document.querySelectorAll("[id^='ipo-stage-']").forEach(btn => {
        btn.className = "px-2.5 py-0.5 rounded text-slate-600 dark:text-slate-400";
      });
      const activeBtn = document.getElementById(\`ipo-stage-\${tag.toLowerCase()}\`);
      if (activeBtn) activeBtn.className = "px-2.5 py-0.5 rounded bg-brand-600 text-white shadow-xs";
      renderIpoTable();
    }

    function renderIpoTable() {
      const tbody = document.getElementById("ipo-table-body");
      tbody.innerHTML = "";
      const rawQuery = document.getElementById("global-search").value.trim().toLowerCase();
      const queryTokens = rawQuery ? rawQuery.split(/\\s+/).filter(Boolean) : [];

      const filtered = ipoList.filter(item => {
        const matchTag = currentIpoFilter === "ALL" || item.filterTag === currentIpoFilter;
        
        const searchable = (item.company + " " + item.headline + " " + item.details + " " + item.size + " " + item.source).toLowerCase();
        const matchQuery = queryTokens.length === 0 || queryTokens.every(tok => searchable.includes(tok));
        
        return matchTag && matchQuery;
      });

      document.getElementById("ipo-table-visible-count").textContent = filtered.length;

      if (filtered.length === 0) {
        tbody.innerHTML = \`<tr><td colspan="8" class="py-10 text-center text-slate-400 font-medium text-[13.5px]">No IPO records found matching criteria.</td></tr>\`;
        return;
      }

      filtered.forEach((ipo, idx) => {
        const tr = document.createElement("tr");
        tr.className = "table-row-hover transition-colors border-b border-slate-100 dark:border-slate-800/80";
        const numStr = (idx + 1).toString().padStart(2, '0');
        const demandColor = ipo.demand.includes("x") ? "text-emerald-700 dark:text-emerald-400 font-bold bg-emerald-50 dark:bg-emerald-950/40 px-2 py-0.5 rounded border border-emerald-200 dark:border-emerald-800" : "text-slate-600 dark:text-slate-400";

        tr.innerHTML = \`
          <td class="py-3 px-3.5 font-mono text-[12px] text-slate-400 font-semibold">\${numStr}</td>
          <td class="py-3 px-3.5 font-bold text-slate-900 dark:text-white">
            <div class="flex items-center gap-2">
              <span class="w-6 h-6 rounded-md bg-brand-50 dark:bg-brand-950/60 text-brand-600 dark:text-brand-400 font-bold text-[10.5px] font-mono flex items-center justify-center shrink-0 border border-brand-200/50">
                \${ipo.company.slice(0, 2).toUpperCase()}
              </span>
              <div>
                <p class="text-[14px] leading-tight font-bold text-slate-900 dark:text-white">\${highlightSearchTokens(ipo.company, queryTokens)}</p>
                <p class="text-[11.5px] font-mono text-slate-400 font-normal truncate max-w-[240px] mt-0.5">\${highlightSearchTokens(ipo.headline, queryTokens)}</p>
              </div>
            </div>
          </td>
          <td class="py-3 px-3.5 font-mono font-bold text-slate-900 dark:text-slate-100 text-[13.5px] whitespace-nowrap">\${ipo.size}</td>
          <td class="py-3 px-3.5 whitespace-nowrap">
            <span class="px-2 py-0.5 rounded text-[11.5px] font-mono font-bold border \${ipo.stageBadge}">
              \${ipo.stage}
            </span>
          </td>
          <td class="py-3 px-3.5 font-mono text-[12px] whitespace-nowrap"><span class="\${demandColor}">\${ipo.demand}</span></td>
          <td class="py-3 px-3.5 max-w-md">
            <p class="text-[13px] text-slate-700 dark:text-slate-300 line-clamp-2 leading-relaxed font-normal">
              \${highlightSearchTokens(highlightNumbers(ipo.details), queryTokens)}
            </p>
          </td>
          <td class="py-3 px-3.5 font-mono text-[11.5px] text-slate-400 whitespace-nowrap">\${ipo.source}</td>
          <td class="py-3 px-3.5 text-center whitespace-nowrap">
            <button onclick="copyToClipboard('\${escapeQuotes(ipo.headline + '\\\\n\\\\n' + ipo.details)}')" class="px-2.5 py-1 rounded border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-[#182035] hover:bg-brand-50 hover:text-brand-600 text-[11px] font-mono font-semibold transition-colors">
              📋 Copy
            </button>
          </td>
        \`;
        tbody.appendChild(tr);
      });
    }

    function exportIpoCsv() {
      let csv = "ID,Company,Issue Size,Stage,Subscription Demand,Details,Source\\n";
      ipoList.forEach(item => {
        csv += \`"\${item.id}","\${item.company.replace(/"/g, '""')}","\${item.size}","\${item.stage}","\${item.demand}","\${item.details.replace(/"/g, '""')}","\${item.source}"\\n\`;
      });
      const blob = new Blob([csv], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.setAttribute('href', url);
      a.setAttribute('download', \`FinBrief_IPO_Tracker_\${new Date().toISOString().slice(0,10)}.csv\`);
      a.click();
    }

    function highlightNumbers(text) {
      if (!text) return "";
      return text.replace(/(\\b\\d+(?:\\.\\d+)?%|\\b₹\\s?[\\d,]+(?:\\.\\d+)?(?:\\s?(?:cr|crore|lakh|bn|billion|tn|trillion))?|\\b\\\$[\\d,]+(?:\\.\\d+)?(?:\\s?(?:bn|billion|million|mn|tn))?|\\b[\\d,]+(?:\\.\\d+)?\\s?(?:crore|lakh|billion|million)\\b)/gi, '<span class="text-brand-600 dark:text-amber-400 font-bold font-mono">\$1</span>');
    }

    function highlightSearchTokens(text, tokens) {
      if (!text || !tokens || tokens.length === 0) return text;
      let result = text;
      tokens.forEach(tok => {
        if (!tok || tok.length < 2) return;
        const regex = new RegExp(\`(\${escapeRegExp(tok)})\`, 'gi');
        result = result.replace(regex, '<mark>\$1</mark>');
      });
      return result;
    }

    function escapeRegExp(string) {
      return string.replace(/[.*+?^\${}()|[\\]\\\\]/g, '\\\\\$&');
    }

    function escapeQuotes(str) {
      return str.replace(/'/g, "\\\\'").replace(/"/g, '&quot;');
    }

    function copyToClipboard(text) {
      navigator.clipboard.writeText(text);
      alert("Copied to clipboard!");
    }

    document.addEventListener("keydown", (e) => {
      if (e.target.tagName === "INPUT" || e.target.tagName === "SELECT") return;
      if (e.key === "j" || e.key === "ArrowDown") {
        e.preventDefault();
        selectedStoryIndex++;
        renderFeedList();
      } else if (e.key === "k" || e.key === "ArrowUp") {
        e.preventDefault();
        if (selectedStoryIndex > 0) selectedStoryIndex--;
        renderFeedList();
      } else if (e.key === "1") switchView('feed');
      else if (e.key === "2") switchView('ipo');
      else if (e.key === "/") { e.preventDefault(); document.getElementById("global-search").focus(); }
    });

    initTheme();
    fetchDates();
    loadData();
  </script>
</body>
</html>
`;

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    // API Routes
    if (url.pathname === '/api/report') {
      const dateParam = url.searchParams.get('date');
      const targetFile = dateParam ? `news_report_unified_${dateParam}.json` : 'news_report_unified_latest.json';
      const r2Url = `https://pub-c81167dd545d49d0a2cd964a8bd6a1cd.r2.dev/reports/${targetFile}`;
      try {
        const resp = await fetch(r2Url, {
          headers: { 'User-Agent': 'FinPress-Cloudflare-Worker' }
        });
        return new Response(resp.body, {
          status: resp.status,
          headers: {
            'Content-Type': 'application/json; charset=utf-8',
            'Access-Control-Allow-Origin': '*',
            'Cache-Control': 'public, max-age=300'
          }
        });
      } catch (e) {
        return new Response(JSON.stringify({ error: 'Failed to fetch report' }), { status: 500 });
      }
    }

    if (url.pathname === '/api/dates') {
      return new Response(JSON.stringify(['2026-09-27']), {
        headers: {
          'Content-Type': 'application/json; charset=utf-8',
          'Access-Control-Allow-Origin': '*'
        }
      });
    }

    // Default: Serve Trader Terminal UI
    return new Response(HTML, {
      headers: {
        'Content-Type': 'text/html; charset=utf-8',
        'Cache-Control': 'public, max-age=60'
      }
    });
  }
};
