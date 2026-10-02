import re
import subprocess

def rebuild():
    # Load clean base from commit 01c7cbd
    git_html = subprocess.check_output(['git', 'show', '01c7cbd:web/index.html']).decode('utf-8')

    parts = git_html.split('<!-- ================= CLIENT JAVASCRIPT ================= -->')
    dom_part = parts[0]
    script_part = parts[1]

    # 1. Clean <head> with guaranteed fixed-viewport edge-to-edge layout and workspace-grid
    head_pattern = r'<head>(.*?)</head>'
    clean_head = '''<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=5, viewport-fit=cover"/>
  <title>FinPress Institutional Workspace — Trader Terminal</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,100..1000;1,9..40,100..1000&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          fontFamily: {
            sans: ['"DM Sans"', '"Plus Jakarta Sans"', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
            mono: ['"JetBrains Mono"', 'monospace'],
          },
          colors: {
            brand: { 50: '#EEF2FF', 100: '#E0E7FF', 500: '#6366F1', 600: '#4F46E5', 700: '#4338CA' }
          }
        }
      }
    };
  </script>
  <style>
    *, *::before, *::after {
      box-sizing: border-box !important;
    }
    html, body {
      width: 100vw !important;
      max-width: 100vw !important;
      height: 100vh !important;
      height: 100dvh !important;
      margin: 0 !important;
      padding: 0 !important;
      overflow: hidden !important;
      touch-action: manipulation;
      -webkit-text-size-adjust: 100%;
      background-color: #F1F5F9;
    }
    body {
      font-family: 'DM Sans', 'Plus Jakarta Sans', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
      font-size: 13px;
      font-weight: 400;
      color: #090D16;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
      text-rendering: optimizeLegibility;
      background-color: #F1F5F9;
    }
    .dark body {
      background-color: #070B14;
    }
    .font-mono { font-family: 'JetBrains Mono', monospace; }
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #CBD5E1; border-radius: 4px; }
    .dark ::-webkit-scrollbar-thumb { background: #334155; }
    .table-row-hover:hover { background-color: rgba(99, 102, 241, 0.05); }
    .dark .table-row-hover:hover { background-color: rgba(99, 102, 241, 0.10); }
    mark { background-color: #FEF08A; color: #854D0E; padding: 0 2px; border-radius: 2px; font-weight: 700; }
    .dark mark { background-color: #854D0E; color: #FEF08A; }

    /* Strict visibility classes */
    .hidden {
      display: none !important;
    }

    /* Fixed Viewport Edge-to-Edge Layout */
    #app-root {
      width: 100vw !important;
      max-width: 100vw !important;
      height: 100vh !important;
      height: 100dvh !important;
      display: flex !important;
      flex-direction: column !important;
      overflow: hidden !important;
      margin: 0 !important;
      padding: 0 !important;
    }
    #app-header {
      width: 100vw !important;
      max-width: 100vw !important;
      height: 48px !important;
      min-height: 48px !important;
      flex-shrink: 0 !important;
    }
    #app-main {
      width: 100vw !important;
      max-width: 100vw !important;
      flex: 1 1 0% !important;
      padding: 6px 8px 8px 8px !important;
      display: flex !important;
      flex-direction: column !important;
      overflow: hidden !important;
      min-height: 0 !important;
      background-color: #F1F5F9;
    }
    .dark #app-main {
      background-color: #070B14;
    }

    /* Main Workspace Grid (Views Container + Permanent 3rd Column Sidebar) */
    #workspace-grid {
      width: 100% !important;
      max-width: 100% !important;
      height: 100% !important;
      display: grid !important;
      grid-template-columns: minmax(0, 1fr) 280px !important;
      grid-template-rows: 100% !important;
      gap: 8px !important;
      overflow: hidden !important;
      min-height: 0 !important;
      flex: 1 1 0% !important;
    }
    @media (min-width: 1280px) {
      #workspace-grid {
        grid-template-columns: minmax(0, 1fr) 300px !important;
      }
    }
    @media (min-width: 1536px) {
      #workspace-grid {
        grid-template-columns: minmax(0, 1fr) 340px !important;
      }
    }
    @media (min-width: 1920px) {
      #workspace-grid {
        grid-template-columns: minmax(0, 1fr) 380px !important;
      }
    }
    @media (min-width: 2560px) {
      #workspace-grid {
        grid-template-columns: minmax(0, 1fr) 420px !important;
      }
    }
    #workspace-grid.sidebar-collapsed {
      grid-template-columns: minmax(0, 1fr) !important;
    }

    #workspace-views {
      width: 100% !important;
      max-width: 100% !important;
      height: 100% !important;
      min-width: 0 !important;
      overflow: hidden !important;
      display: flex !important;
      flex-direction: column !important;
      flex: 1 1 0% !important;
    }

    #view-feed:not(.hidden) {
      width: 100% !important;
      max-width: 100% !important;
      height: 100% !important;
      display: grid !important;
      grid-template-columns: 340px minmax(0, 1fr) !important;
      grid-template-rows: 100% !important;
      gap: 8px !important;
      overflow: hidden !important;
      min-height: 0 !important;
      flex: 1 1 0% !important;
    }
    @media (min-width: 1280px) {
      #view-feed:not(.hidden) {
        grid-template-columns: 380px minmax(0, 1fr) !important;
      }
    }
    @media (min-width: 1536px) {
      #view-feed:not(.hidden) {
        grid-template-columns: 420px minmax(0, 1fr) !important;
      }
    }
    @media (min-width: 1920px) {
      #view-feed:not(.hidden) {
        grid-template-columns: 460px minmax(0, 1fr) !important;
      }
    }
    @media (min-width: 2560px) {
      #view-feed:not(.hidden) {
        grid-template-columns: 520px minmax(0, 1fr) !important;
      }
    }

    #view-ipo:not(.hidden) {
      width: 100% !important;
      max-width: 100% !important;
      height: 100% !important;
      display: flex !important;
      flex-direction: column !important;
      gap: 8px !important;
      overflow: hidden !important;
      min-height: 0 !important;
      flex: 1 1 0% !important;
    }

    #view-matrix:not(.hidden) {
      width: 100% !important;
      max-width: 100% !important;
      height: 100% !important;
      display: flex !important;
      flex-direction: column !important;
      gap: 8px !important;
      overflow: hidden !important;
      min-height: 0 !important;
      flex: 1 1 0% !important;
    }

    #col-news-wire {
      height: 100% !important;
      display: flex !important;
      flex-direction: column !important;
      overflow: hidden !important;
      min-height: 0 !important;
    }
    #feed-list-container {
      flex: 1 1 0% !important;
      min-height: 0 !important;
      overflow-y: auto !important;
    }

    #feed-detail-wrapper {
      height: 100% !important;
      display: flex !important;
      flex-direction: column !important;
      overflow: hidden !important;
      min-height: 0 !important;
    }
    #feed-detail-container {
      flex: 1 1 0% !important;
      min-height: 0 !important;
      overflow-y: auto !important;
    }

    #view-feed-aside {
      height: 100% !important;
      display: flex !important;
      flex-direction: column !important;
      overflow: hidden !important;
      min-height: 0 !important;
    }
    #tree-sidebar-container {
      flex: 1 1 0% !important;
      min-height: 0 !important;
      overflow-y: auto !important;
    }

    @media (max-width: 1023px) {
      #workspace-grid {
        grid-template-columns: 100% !important;
        grid-template-rows: auto auto !important;
        overflow-y: auto !important;
      }
      #view-feed:not(.hidden) {
        grid-template-columns: 100% !important;
        grid-template-rows: auto auto !important;
        overflow-y: auto !important;
      }
      #app-main {
        overflow-y: auto !important;
      }
    }
  </style>
</head>'''
    dom_part = re.sub(head_pattern, clean_head, dom_part, flags=re.DOTALL)

    # 1.1 Replace body wrapper, header and main elements with explicit fixed-viewport classes and IDs
    dom_part = re.sub(r'<div class="min-h-screen[^"]*">', '<div id="app-root" class="w-screen h-screen flex flex-col overflow-hidden m-0 p-0 bg-[#F1F5F9] dark:bg-[#070B14]">', dom_part, count=1)
    dom_part = re.sub(r'<header[^>]*>', '<header id="app-header" class="shrink-0 w-full bg-[#070B14] border-b border-slate-800 text-slate-100 shadow-lg px-3 sm:px-4 py-2 flex items-center justify-between gap-3 overflow-x-auto whitespace-nowrap text-[13px] font-mono z-50">', dom_part, count=1)
    dom_part = re.sub(r'<main[^>]*>', '<main id="app-main" class="flex-1 w-full flex flex-col overflow-hidden min-h-0 bg-[#F1F5F9] dark:bg-[#070B14] p-1.5 sm:p-2">', dom_part, count=1)

    # 2. Update Header: Add dedicated Quick IPO Hub Launch Button
    header_find = '<div class="flex items-center gap-2">'
    header_replace = '''<div class="flex items-center gap-2">
        <button id="top-ipo-hub-btn" onclick="switchView(currentView === 'ipo' ? 'feed' : 'ipo')" class="px-3 py-1 rounded-lg bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white font-mono text-[12px] font-bold flex items-center gap-1.5 shadow-md transition-transform active:scale-95 cursor-pointer" title="Launch Specialized IPO Intelligence Hub">
          <span>🚀</span> <span>IPO Hub</span>
        </button>'''
    if header_find in dom_part and 'id="top-ipo-hub-btn"' not in dom_part:
        dom_part = dom_part.replace(header_find, header_replace, 1)

    # 3. Clean and isolate 3rd Column Sidebar (#view-feed-aside)
    aside_start = dom_part.find('<aside id="view-feed-aside"')
    aside_end = dom_part.find('</aside>', aside_start) + len('</aside>')
    clean_aside = dom_part[aside_start:aside_end]

    # Remove the aside from inside view-feed
    dom_part = dom_part[:aside_start] + dom_part[aside_end:]

    # Clean up view-feed and view-matrix
    dom_part = re.sub(r'<section id="view-feed"[^>]*>', '<section id="view-feed">', dom_part)
    dom_part = re.sub(r'<section id="view-matrix"[^>]*>', '<section id="view-matrix" class="hidden">', dom_part)

    # 4. Create Dedicated Full-Page IPO Hub Section (#view-ipo)
    view_ipo_html = '''      <!-- DEDICATED IPO INTELLIGENCE HUB SECTION -->
      <section id="view-ipo" class="hidden rounded-xl border border-slate-300 dark:border-slate-800 bg-white dark:bg-[#0E1322] shadow-xs p-3">
        
        <!-- IPO Header Bar & Filters -->
        <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 pb-2.5 border-b border-slate-200 dark:border-slate-800 shrink-0">
          
          <div class="flex items-center gap-2">
            <div class="flex items-center gap-1.5 p-0.5 rounded-lg bg-slate-100 dark:bg-slate-900 border border-slate-300 dark:border-slate-800 text-xs font-mono font-bold shadow-2xs">
              <button id="ipo-mode-tracker-btn" onclick="setIpoViewMode('tracker')" class="px-3 py-1.5 rounded-lg bg-[#1C1917] text-white dark:bg-indigo-600 dark:text-white shadow-xs transition-all flex items-center gap-1.5 cursor-pointer">
                <span>🚀</span> <span>Primary Issues & Pipeline</span>
              </button>
              <button id="ipo-mode-listed-btn" onclick="setIpoViewMode('listed')" class="px-3 py-1.5 rounded-lg text-slate-700 dark:text-slate-300 hover:text-black dark:hover:text-white hover:bg-white/60 dark:hover:bg-slate-800 transition-all flex items-center gap-1.5 cursor-pointer">
                <span>📈</span> <span>Listing Performance Track</span>
              </button>
            </div>
          </div>

          <div class="flex items-center gap-2 w-full sm:w-auto">
            <!-- Search in IPO Hub -->
            <div class="relative flex-1 sm:w-64">
              <input type="text" id="ipo-hub-search" oninput="onIpoSearchInput(this.value)" placeholder="Search company, exchange, stage..." class="w-full text-xs px-2.5 py-1.5 rounded-lg bg-slate-100 dark:bg-slate-900 border border-slate-300 dark:border-slate-700 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:border-indigo-500 font-mono shadow-2xs">
            </div>

            <!-- Subfilter (Mainboard / SME) -->
            <div id="ipo-subfilter-container" class="flex items-center gap-1 bg-slate-100 dark:bg-slate-900 p-0.5 rounded-lg border border-slate-300 dark:border-slate-800 text-[11px] font-mono">
              <button id="ipo-filter-all" onclick="setIpoFilterCategory('ALL')" class="px-2.5 py-1 rounded-md bg-slate-900 text-white dark:bg-indigo-600 dark:text-white font-bold shadow-2xs">All</button>
              <button id="ipo-filter-mb" onclick="setIpoFilterCategory('MAINBOARD')" class="px-2.5 py-1 rounded-md text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800">Mainboard</button>
              <button id="ipo-filter-sme" onclick="setIpoFilterCategory('SME')" class="px-2.5 py-1 rounded-md text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800">SME Emerge</button>
            </div>
          </div>

        </div>

        <!-- IPO KPI Metrics Strip -->
        <div id="ipo-kpi-strip" class="grid grid-cols-2 sm:grid-cols-4 gap-2.5 py-2 shrink-0">
          <div class="p-2.5 rounded-lg bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800/80 flex items-center justify-between">
            <div>
              <span class="text-[11px] font-mono text-slate-400 uppercase tracking-wider block">Total Active Issues</span>
              <span id="ipo-kpi-total" class="text-lg font-bold font-mono text-slate-900 dark:text-white">--</span>
            </div>
            <span class="text-xl">📊</span>
          </div>
          <div class="p-2.5 rounded-lg bg-emerald-50/60 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-900/40 flex items-center justify-between">
            <div>
              <span class="text-[11px] font-mono text-emerald-700 dark:text-emerald-400 uppercase tracking-wider block">Open for Bidding</span>
              <span id="ipo-kpi-bidding" class="text-lg font-bold font-mono text-emerald-900 dark:text-emerald-300">--</span>
            </div>
            <span class="text-xl">🟢</span>
          </div>
          <div class="p-2.5 rounded-lg bg-amber-50/60 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-900/40 flex items-center justify-between">
            <div>
              <span class="text-[11px] font-mono text-amber-700 dark:text-amber-400 uppercase tracking-wider block">DRHP Filed / Pipeline</span>
              <span id="ipo-kpi-drhp" class="text-lg font-bold font-mono text-amber-900 dark:text-amber-300">--</span>
            </div>
            <span class="text-xl">📋</span>
          </div>
          <div class="p-2.5 rounded-lg bg-purple-50/60 dark:bg-purple-950/30 border border-purple-200 dark:border-purple-900/40 flex items-center justify-between">
            <div>
              <span class="text-[11px] font-mono text-purple-700 dark:text-purple-400 uppercase tracking-wider block">Avg Grey Market Prem.</span>
              <span id="ipo-kpi-gmp" class="text-lg font-bold font-mono text-purple-900 dark:text-purple-300">+38.5%</span>
            </div>
            <span class="text-xl">🔥</span>
          </div>
        </div>

        <!-- Dynamic Tables View Container -->
        <div class="flex-1 min-h-0 flex flex-col overflow-hidden">
          
          <!-- Primary Issues Table Container -->
          <div id="ipo-tracker-table-wrap" class="flex-1 min-h-0 overflow-y-auto rounded-lg border border-slate-200 dark:border-slate-800">
            <table class="w-full text-left text-xs border-collapse">
              <thead class="sticky top-0 z-10 bg-slate-100 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 font-mono text-[11px] uppercase tracking-wider text-slate-500 dark:text-slate-400 select-none">
                <tr>
                  <th class="py-2.5 px-3 text-center w-12">#</th>
                  <th class="py-2.5 px-3 min-w-[200px]">Company / Issuer</th>
                  <th class="py-2.5 px-3">Bidding Dates</th>
                  <th class="py-2.5 px-3">Price Band</th>
                  <th class="py-2.5 px-3">Issue Size</th>
                  <th class="py-2.5 px-3">Lot Size</th>
                  <th class="py-2.5 px-3">Subscription (Times)</th>
                  <th class="py-2.5 px-3">Status / Stage</th>
                  <th class="py-2.5 px-3 text-center">Intel</th>
                </tr>
              </thead>
              <tbody id="ipo-table-body" class="divide-y divide-slate-100 dark:divide-slate-800/80 font-sans">
                <!-- Populated dynamically -->
              </tbody>
            </table>
          </div>

          <!-- Already Listed Benchmark Performance Table Container -->
          <div id="ipo-listed-table-wrap" class="hidden flex-1 min-h-0 overflow-y-auto rounded-lg border border-slate-200 dark:border-slate-800">
            <table class="w-full text-left text-xs border-collapse">
              <thead class="sticky top-0 z-10 bg-slate-100 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 font-mono text-[11px] uppercase tracking-wider text-slate-500 dark:text-slate-400 select-none">
                <tr>
                  <th class="py-2.5 px-3 text-center w-12">#</th>
                  <th class="py-2.5 px-3 min-w-[180px]">Company Name</th>
                  <th class="py-2.5 px-3">Listing Date</th>
                  <th class="py-2.5 px-3">Issue Price</th>
                  <th class="py-2.5 px-3">Listing Price</th>
                  <th class="py-2.5 px-3">Listing Day Gain</th>
                  <th class="py-2.5 px-3">CMP (Live)</th>
                  <th class="py-2.5 px-3">Current Gain %</th>
                  <th class="py-2.5 px-3">Performance Tier</th>
                </tr>
              </thead>
              <tbody id="ipo-listed-table-body" class="divide-y divide-slate-100 dark:divide-slate-800/80 font-sans">
                <!-- Populated dynamically -->
              </tbody>
            </table>
          </div>

        </div>

      </section>'''

    # Wrap views in workspace-grid and workspace-views
    vf_idx = dom_part.find('<section id="view-feed">')
    main_end_idx = dom_part.find('</main>')

    views_content = dom_part[vf_idx:main_end_idx].strip()
    if 'id="view-ipo"' not in views_content:
        views_content += '\n\n' + view_ipo_html

    workspace_html = f'''      <!-- Main Workspace Grid (Views Container + Permanent 3rd Column Sidebar) -->
      <div id="workspace-grid">
        
        <!-- Left & Center Area (Views Container) -->
        <div id="workspace-views">
          {views_content}
        </div>

        {clean_aside}

      </div>'''

    dom_part = dom_part[:vf_idx] + workspace_html + '\n\n    ' + dom_part[main_end_idx:]

    # 5. Clean script_part
    clean_script = script_part.split('</script>')[0].replace('<script>', '', 1).strip()

    # Add top global variables (Defaulting to News Front Page)
    clean_script = '''    let rawReport = null;
    let stories = [];
    let ipoList = [];
    let currentView = "feed";
    let selectedFeedCategory = "ANCHOR";
    let selectedFeedSentiment = "ALL";
    let activeStockFilter = null;
    let activeSectorFilter = null;
    let selectedStoryIndex = 0;
    let currentFeedPage = 1;
    const FEED_PAGE_SIZE = 12;
    let currentIpoFilter = "ALL";
    let currentSearchQuery = "";
    let availableDates = [];
    let currentDateIndex = 0;
    let activeIpoMode = "tracker"; // 'tracker' or 'listed'
    let activeIpoCategory = "ALL";  // 'ALL', 'MAINBOARD', 'SME'
    let ipoSearchQuery = "";
    let isCutoutExpanded = false;

    // Benchmark dataset for 'Already Listed' IPOs
    const benchmarkListedIpos = [
      { id: 1, name: "Premier Energies Ltd", ticker: "PREMIERENE", date: "03 Sep 2026", issuePrice: 450, listPrice: 991, cmp: 1120, exchange: "NSE / BSE Mainboard" },
      { id: 2, name: "Bajaj Housing Finance Ltd", ticker: "BAJAJHFL", date: "16 Sep 2026", issuePrice: 70, listPrice: 150, cmp: 142, exchange: "NSE / BSE Mainboard" },
      { id: 3, name: "KRN Heat Exchanger Ltd", ticker: "KRNHEAT", date: "24 Sep 2026", issuePrice: 220, listPrice: 480, cmp: 512, exchange: "NSE / BSE Mainboard" },
      { id: 4, name: "Swiggy Ltd", ticker: "SWIGGY", date: "18 Sep 2026", issuePrice: 390, listPrice: 420, cmp: 468, exchange: "NSE / BSE Mainboard" },
      { id: 5, name: "Diffusion Engineers Ltd", ticker: "DIFFUSION", date: "26 Sep 2026", issuePrice: 168, listPrice: 195, cmp: 210, exchange: "NSE / BSE Mainboard" },
      { id: 6, name: "Manba Finance Ltd", ticker: "MANBA", date: "23 Sep 2026", issuePrice: 120, listPrice: 150, cmp: 144, exchange: "NSE / BSE Mainboard" },
      { id: 7, name: "Arkade Developers Ltd", ticker: "ARKADE", date: "20 Sep 2026", issuePrice: 128, listPrice: 175, cmp: 168, exchange: "NSE / BSE Mainboard" },
      { id: 8, name: "Western Carriers India Ltd", ticker: "WESTERN", date: "21 Sep 2026", issuePrice: 172, listPrice: 170, cmp: 158, exchange: "NSE / BSE Mainboard" },
      { id: 9, name: "Northern Arc Capital Ltd", ticker: "NORTHARC", date: "19 Sep 2026", issuePrice: 263, listPrice: 351, cmp: 325, exchange: "NSE / BSE Mainboard" }
    ];\n\n''' + clean_script[clean_script.find('const allowedSections = ['):]

    # Update switchView in clean_script
    switch_view_code = '''    function switchView(viewName) {
      currentView = viewName;
      const tabAnchor = document.getElementById("tab-btn-anchor");
      const viewFeed = document.getElementById("view-feed");
      const viewIpo = document.getElementById("view-ipo");
      const viewMatrix = document.getElementById("view-matrix");
      const corpBanner = document.getElementById("corporate-subtabs-banner");
      const ipoBanner = document.getElementById("ipo-subtabs-banner");
      const deskSelect = document.getElementById("desk-select");
      const categorySelect = document.getElementById("category-select");
      const topIpoBtn = document.getElementById("top-ipo-hub-btn");

      selectedStoryIndex = 0;
      currentFeedPage = 1;

      if (viewName === "ipo" || viewName === "ipo_hub") {
        if (topIpoBtn) {
          topIpoBtn.className = "px-3 py-1 rounded-lg bg-amber-600 text-white font-mono text-[12px] font-bold flex items-center gap-1.5 shadow-md transition-transform active:scale-95 cursor-pointer ring-2 ring-amber-400";
          topIpoBtn.innerHTML = "<span>📰</span> <span>Back to News</span>";
        }
        if (viewFeed) viewFeed.classList.add("hidden");
        if (viewMatrix) viewMatrix.classList.add("hidden");
        if (viewIpo) viewIpo.classList.remove("hidden");
        setIpoViewMode(activeIpoMode || 'tracker');
        renderCategoriesAndStocksSidebar();
        return;
      }

      if (topIpoBtn) {
        topIpoBtn.className = "px-3 py-1 rounded-lg bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white font-mono text-[12px] font-bold flex items-center gap-1.5 shadow-md transition-transform active:scale-95 cursor-pointer";
        topIpoBtn.innerHTML = "<span>🚀</span> <span>IPO Hub</span>";
      }

      if (viewIpo) viewIpo.classList.add("hidden");
      if (viewMatrix) viewMatrix.classList.add("hidden");
      if (viewFeed) viewFeed.classList.remove("hidden");

      if (viewName === "feed") {
        selectedFeedCategory = "ANCHOR";
        if (categorySelect) categorySelect.value = "ANCHOR";
        if (deskSelect) deskSelect.value = "";
        if (corpBanner) corpBanner.classList.add("hidden");
        if (ipoBanner) ipoBanner.classList.add("hidden");
      } else if (viewName === "anchor") {
        if (tabAnchor) tabAnchor.className = "px-2.5 py-1 rounded-md transition-all bg-[#1C1917] text-[#FFF8F0] dark:bg-indigo-600 dark:text-white shadow-xs flex items-center gap-1.5 font-semibold";
        selectedFeedCategory = "ANCHOR";
        if (deskSelect) deskSelect.value = "";
        if (corpBanner) corpBanner.classList.add("hidden");
        if (ipoBanner) ipoBanner.classList.add("hidden");
      } else if (viewName === "corporate") {
        if (deskSelect) deskSelect.value = "corporate";
        if (ipoBanner) ipoBanner.classList.add("hidden");
        if (corpBanner) {
          corpBanner.classList.remove("hidden");
          corpBanner.classList.add("flex");
          selectCorporateSub("ALL");
          return;
        }
      } else if (viewName === "opinions") {
        if (deskSelect) deskSelect.value = "opinions";
        selectedFeedCategory = "OPINIONS";
        if (corpBanner) corpBanner.classList.add("hidden");
        if (ipoBanner) ipoBanner.classList.add("hidden");
      }

      renderCategoriesAndStocksSidebar();
      renderFeedList();
    }'''

    start_sw = clean_script.find('function switchView(')
    end_sw = clean_script.find('function onDeskSelect(')
    if start_sw != -1 and end_sw != -1:
        clean_script = clean_script[:start_sw] + switch_view_code + '\n\n    ' + clean_script[end_sw:]

    # Update onCategorySelect
    cat_sel_code = '''    function onCategorySelect(val) {
      if (currentView === "ipo") {
        currentView = "feed";
        const topIpoBtn = document.getElementById("top-ipo-hub-btn");
        if (topIpoBtn) {
          topIpoBtn.className = "px-3 py-1 rounded-lg bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white font-mono text-[12px] font-bold flex items-center gap-1.5 shadow-md transition-transform active:scale-95 cursor-pointer";
          topIpoBtn.innerHTML = "<span>🚀</span> <span>IPO Hub</span>";
        }
        const viewIpo = document.getElementById("view-ipo");
        if (viewIpo) viewIpo.classList.add("hidden");
        const viewFeed = document.getElementById("view-feed");
        if (viewFeed) viewFeed.classList.remove("hidden");
      }

      selectedStoryIndex = 0;
      currentFeedPage = 1;
      selectedFeedCategory = val;
      activeStockFilter = null;
      activeSectorFilter = null;
      
      const deskSelect = document.getElementById("desk-select");
      if (deskSelect) deskSelect.value = "";
      
      const corpBanner = document.getElementById("corporate-subtabs-banner");
      if (corpBanner) corpBanner.classList.add("hidden");
      const ipoBanner = document.getElementById("ipo-subtabs-banner");
      if (ipoBanner) ipoBanner.classList.add("hidden");
      
      const tabAnchor = document.getElementById("tab-btn-anchor");
      if (tabAnchor) tabAnchor.className = "px-2.5 py-1 rounded-md transition-all text-slate-800 dark:text-slate-300 hover:text-black dark:hover:text-white hover:bg-white/60 dark:hover:bg-slate-800 flex items-center gap-1.5 font-medium";
      
      const catSelect = document.getElementById("category-select");
      if (catSelect && val !== "ALL" && !val.startsWith("IPO") && !val.startsWith("CORPORATE") && val !== "OPINIONS" && val !== "ANCHOR") {
        catSelect.value = val;
      } else if (catSelect && val === "ANCHOR") {
        catSelect.value = "ANCHOR";
      }

      renderCategoriesAndStocksSidebar();
      renderFeedList();
    }'''

    start_cat = clean_script.find('function onCategorySelect(')
    end_cat = clean_script.find('function isFillerHeadline(', start_cat)
    if start_cat != -1 and end_cat != -1:
        clean_script = clean_script[:start_cat] + cat_sel_code + '\n\n    ' + clean_script[end_cat:]

    # Enhanced parseStory with FE and BS publication detection
    parse_story_code = '''    function parseStory(story, idx) {
      if (!story || isFillerHeadline(story.headline || "")) return null;

      const brief_details = story.brief_details || story.brief || "";
      const bullet_points = Array.isArray(story.bullet_points) ? story.bullet_points : (Array.isArray(story.detailed_points) ? story.detailed_points : []);
      const rawPage = Array.isArray(story.page_numbers) ? story.page_numbers.join(" ") : String(story.page_numbers || "");
      const sourcePaper = String(story.source_paper || "");
      const pageStr = (rawPage + " " + sourcePaper).toLowerCase();
      const fullText = ((story.headline || "") + " " + brief_details + " " + bullet_points.join(" ")).toLowerCase();

      // Source Paper Flags
      const hasFe = pageStr.includes("fe") || pageStr.includes("financial express") || sourcePaper.toLowerCase().includes("express");
      const hasBs = pageStr.includes("bs") || pageStr.includes("business standard") || sourcePaper.toLowerCase().includes("standard");

      // Strict Market Section Rule: Bank disclosures/Statutory notices belong in Corporate Events
      let category = story.category;
      if (category === "Market" || category === "Others") {
        const noticeTerms = ["disclosure", "public notice", "statutory notice", "possession notice", "postal ballot", "e-voting", "annual general meeting", "agm notice", "egm notice", "co-op bank", "co-operative bank", "financial and regulatory disclosure", "auction notice"];
        if (noticeTerms.some(t => fullText.includes(t))) {
          category = "Corporate Events";
        }
      }

      // Detect Opinions / Editorial
      const isOpinion = pageStr.includes("opinion") || pageStr.includes("edit") || pageStr.includes("column") || pageStr.includes("commentary") || fullText.includes("op-ed") || fullText.includes("editorial view");

      // Strict Front Page Anchors: Must be Page 1 and strictly genuine NEWS
      const isPage1Location = pageStr.includes("page 1") || pageStr.includes("page 01") || pageStr.includes("p.1") || pageStr.includes("front") || pageStr.includes("lead");
      const isAnnouncementOrIpo = category === "IPO" || category === "Corporate Events" || category === "Corporate Appointments" || isOpinion || fullText.includes("drhp") || fullText.includes("statutory notice") || fullText.includes("public notice") || fullText.includes("disclosure");
      const isFrontPage = (isPage1Location || idx < 4) && !isAnnouncementOrIpo;

      let ipoData = null;
      if (category === "IPO") {
        ipoData = parseIpoItem(story, idx);
      }

      const bullishTriggers = [
        { k: "order win", r: "Contract / Order Inflow expands near-term revenue visibility." },
        { k: "mou", r: "Strategic MoU / Partnership accelerates joint development and market reach." },
        { k: "expansion", r: "Capacity Expansion / New facility enhances long-term operational throughput." },
        { k: "profit up", r: "Strong bottom-line growth signals healthy operational leverage." },
        { k: "revenue up", r: "Topline growth indicates robust market demand and pricing power." },
        { k: "approval", r: "Key regulatory/government clearance removes project bottleneck." },
        { k: "dividend", r: "Shareholder payout / capital return signals healthy balance-sheet liquidity." },
        { k: "exemption", r: "Policy duty waiver / tax exemption improves gross margins." },
        { k: "surge", r: "Sharp positive volume/demand breakout across core business segments." }
      ];

      const bearishRisks = [
        { k: "penalty", r: "Regulatory penalty / Show-cause notice creates near-term compliance headwind." },
        { k: "fine", r: "Monetary penalty imposes financial liability and compliance friction." },
        { k: "probe", r: "Regulatory/tax scrutiny introduces headline risk and governance scrutiny." },
        { k: "loss", r: "Widening losses or margin compression weigh on fundamental valuation." },
        { k: "slump", r: "Demand deceleration or volume contraction creates earnings drag." },
        { k: "falls", r: "Topline or net margin contraction signals weakening operating leverage." },
        { k: "tax hike", r: "Increased duty/tax burdens directly compress profit spreads." },
        { k: "curb", r: "Export/import curbs or policy restrictions limit addressable business." }
      ];

      let matchedBullish = [];
      bullishTriggers.forEach(t => { if (fullText.includes(t.k)) matchedBullish.push(t.r); });

      let matchedBearish = [];
      bearishRisks.forEach(t => { if (fullText.includes(t.k)) matchedBearish.push(t.r); });

      let sentiment = "NEUTRAL";
      let sentimentReasoning = "Baseline monitoring trigger: Ongoing operational development, sector-wide baseline trend, or corporate filing to track for subsequent quarterly performance.";

      if (matchedBullish.length > matchedBearish.length) {
        sentiment = "BULLISH";
        sentimentReasoning = matchedBullish.slice(0, 2).join(" Additionally, ");
      } else if (matchedBearish.length > matchedBullish.length) {
        sentiment = "BEARISH";
        sentimentReasoning = matchedBearish.slice(0, 2).join(" Additionally, ");
      }

      const detectedStocks = [];
      const detectedSectors = [];
      const upperText = ((story.headline || "") + " " + brief_details + " " + bullet_points.join(" ")).toUpperCase();

      stockDictionary.forEach(stk => {
        if (new RegExp(`\\\\b${stk.replace('&', '\\\\&')}\\\\b`, 'i').test(upperText)) {
          detectedStocks.push(stk);
        }
      });

      sectorDictionary.forEach(sec => {
        if (new RegExp(`\\\\b${sec.replace('&', '\\\\&')}\\\\b`, 'i').test(upperText)) {
          detectedSectors.push(sec);
        }
      });

      let catalyst = (bullet_points && bullet_points.length > 0) ? bullet_points[0] : (brief_details.slice(0, 160) + "...");

      const uniqueStocks = [...new Set(detectedStocks)].slice(0, 3);
      const uniqueSectors = [...new Set(detectedSectors)].slice(0, 3);
      const allTickers = [...new Set([...uniqueStocks, ...uniqueSectors])].slice(0, 4);

      return {
        ...story,
        id: idx + 1,
        brief_details: brief_details,
        brief: brief_details,
        bullet_points: bullet_points,
        detailed_points: bullet_points,
        category: category || "Others",
        sentiment,
        sentimentReasoning,
        stocks: uniqueStocks,
        sectors: uniqueSectors,
        tickers: allTickers,
        catalyst,
        isFrontPage,
        isOpinion,
        hasFe,
        hasBs,
        source_paper: sourcePaper,
        ipoTag: ipoData ? ipoData.filterTag : null,
        ipoData: ipoData
      };
    }'''

    start_ps = clean_script.find('function parseStory(')
    end_ps = clean_script.find('function parseIpoItem(')
    if start_ps != -1 and end_ps != -1:
        clean_script = clean_script[:start_ps] + parse_story_code + '\n\n    ' + clean_script[end_ps:]

    # Enhanced updateDropdownOptions with Publication filters
    dropdown_code = '''    function updateDropdownOptions(coreCount, ipoCount, corpCount, opCount) {
      const feCount = stories.filter(s => s.hasFe).length;
      const bsCount = stories.filter(s => s.hasBs).length;

      const catSelect = document.getElementById("category-select");
      if (catSelect) {
        const counts = {
          Sector: stories.filter(s => s.category === "Sector" && !s.isOpinion).length,
          Economy: stories.filter(s => s.category === "Economy" && !s.isOpinion).length,
          Policy: stories.filter(s => s.category === "Policy" && !s.isOpinion).length,
          Market: stories.filter(s => s.category === "Market" && !s.isOpinion).length,
          Trade: stories.filter(s => s.category === "Trade" && !s.isOpinion).length,
          "International News": stories.filter(s => s.category === "International News" && !s.isOpinion).length,
          Others: stories.filter(s => s.category === "Others" && !s.isOpinion).length
        };
        catSelect.innerHTML = `
          <option value="ANCHOR">📰 News (Front Page) (${stories.filter(s => s.isFrontPage).length})</option>
          <option value="SOURCE_FE">📰 Financial Express (${feCount})</option>
          <option value="SOURCE_BS">📰 Business Standard (${bsCount})</option>
          <option value="ALL">📑 All Unified Stories (${stories.length})</option>
          <option value="Sector">Sector (${counts.Sector})</option>
          <option value="Economy">Economy (${counts.Economy})</option>
          <option value="Policy">Policy (${counts.Policy})</option>
          <option value="Market">Market (${counts.Market})</option>
          <option value="Trade">Trade & FX (${counts.Trade})</option>
          <option value="International News">International (${counts["International News"]})</option>
          <option value="Others">General Features (${counts.Others})</option>
        `;
        if (selectedFeedCategory !== "ANCHOR" && !selectedFeedCategory.startsWith("CORPORATE") && !selectedFeedCategory.startsWith("IPO") && selectedFeedCategory !== "OPINIONS") {
          catSelect.value = selectedFeedCategory;
        } else {
          catSelect.value = "ALL";
        }
      }

      const deskSelect = document.getElementById("desk-select");
      if (deskSelect) {
        deskSelect.innerHTML = `
          <option value="" disabled ${currentView === 'feed' && selectedFeedCategory !== 'OPINIONS' && !selectedFeedCategory.startsWith('CORPORATE') && !selectedFeedCategory.startsWith('IPO') ? 'selected' : ''}>🏛️ Specialized Desks ▾</option>
          <option value="ipo" ${currentView === 'ipo' || selectedFeedCategory.startsWith('IPO') ? 'selected' : ''}>🚀 IPO Central (${ipoCount})</option>
          <option value="corporate" ${currentView === 'corporate' || selectedFeedCategory.startsWith('CORPORATE') ? 'selected' : ''}>🏢 Corporate (${corpCount})</option>
          <option value="opinions" ${selectedFeedCategory === 'OPINIONS' ? 'selected' : ''}>✍️ Opinions (${opCount})</option>
        `;
      }
    }'''

    start_dd = clean_script.find('function updateDropdownOptions(')
    end_dd = clean_script.find('function initMetrics(')
    if start_dd != -1 and end_dd != -1:
        clean_script = clean_script[:start_dd] + dropdown_code + '\n\n    ' + clean_script[end_dd:]

    # Enhanced getFilteredStories with SOURCE_FE and SOURCE_BS support
    filtered_stories_code = '''    function getFilteredStories() {
      const rawQuery = document.getElementById("global-search").value.trim().toLowerCase();
      const queryTokens = rawQuery ? rawQuery.split(/\\s+/).filter(Boolean) : [];
      
      return stories.filter(s => {
        const searchableText = (
          s.headline + " " + 
          s.brief_details + " " + 
          (s.bullet_points || []).join(" ") + " " + 
          s.category + " " + 
          (s.page_numbers || "") + " " + 
          (s.source_paper || "") + " " +
          (s.hasFe ? "fe financial express " : "") +
          (s.hasBs ? "bs business standard " : "") +
          (s.tickers || []).join(" ")
        ).toLowerCase();

        const matchQuery = queryTokens.length === 0 || queryTokens.every(tok => searchableText.includes(tok));
        
        let matchSec = true;
        if (activeStockFilter || activeSectorFilter || queryTokens.length > 0) {
          matchSec = true; // When filtering by stock, sector, or search, search across ALL stories!
        } else if (selectedFeedCategory === "ALL") {
          matchSec = true; // Complete 100% Unabridged Multi-Source News Feed (zero stories omitted)
        } else if (selectedFeedCategory === "SOURCE_FE") {
          matchSec = s.hasFe;
        } else if (selectedFeedCategory === "SOURCE_BS") {
          matchSec = s.hasBs;
        } else if (selectedFeedCategory === "CORE") {
          matchSec = s.category !== "IPO" && s.category !== "Corporate Events" && s.category !== "Corporate Appointments" && !s.isOpinion;
        } else if (selectedFeedCategory === "ANCHOR") {
          matchSec = s.isFrontPage;
        } else if (selectedFeedCategory === "IPO_ALL") {
          matchSec = s.category === "IPO";
        } else if (selectedFeedCategory === "IPO_DRHP") {
          matchSec = s.category === "IPO" && (s.ipoTag === "DRHP" || !s.ipoTag);
        } else if (selectedFeedCategory === "IPO_BIDDING") {
          matchSec = s.category === "IPO" && s.ipoTag === "BIDDING";
        } else if (selectedFeedCategory === "IPO_NOTICES") {
          matchSec = s.category === "IPO" && s.ipoTag === "NOTICES";
        } else if (selectedFeedCategory === "CORPORATE_ALL") {
          matchSec = s.category === "Corporate Events" || s.category === "Corporate Appointments";
        } else if (selectedFeedCategory === "EVENTS") {
          matchSec = s.category === "Corporate Events";
        } else if (selectedFeedCategory === "APPOINTMENTS") {
          matchSec = s.category === "Corporate Appointments";
        } else if (selectedFeedCategory === "OPINIONS") {
          matchSec = s.isOpinion;
        } else if (selectedFeedCategory === "Others") {
          matchSec = s.category === "Others";
        } else {
          matchSec = s.category === selectedFeedCategory;
        }

        const matchSent = selectedFeedSentiment === "ALL" || s.sentiment === selectedFeedSentiment;
        const matchStock = !activeStockFilter || (s.stocks && s.stocks.includes(activeStockFilter)) || (s.tickers && s.tickers.includes(activeStockFilter)) || ((s.headline + " " + (s.brief_details || "")).toUpperCase().includes(activeStockFilter));
        const matchSector = !activeSectorFilter || (s.sectors && s.sectors.includes(activeSectorFilter)) || (s.category && s.category.toUpperCase().includes(activeSectorFilter)) || ((s.headline + " " + (s.brief_details || "")).toUpperCase().includes(activeSectorFilter));

        return matchSec && matchSent && matchStock && matchSector && matchQuery;
      });
    }'''

    start_gfs = clean_script.find('function getFilteredStories(')
    end_gfs = clean_script.find('function navigateStory(')
    if start_gfs != -1 and end_gfs != -1:
        clean_script = clean_script[:start_gfs] + filtered_stories_code + '\n\n    ' + clean_script[end_gfs:]

    # Enhanced renderCategoriesAndStocksSidebar with Publication Source filter
    sidebar_code = '''    function renderCategoriesAndStocksSidebar() {
      const container = document.getElementById("tree-sidebar-container");
      if (!container) return;

      container.innerHTML = "";

      const coreStories = stories.filter(s => s.category !== "IPO" && s.category !== "Corporate Events" && s.category !== "Corporate Appointments" && !s.isOpinion);
      const totalIpos = ipoList.length;
      const anchorCount = coreStories.filter(s => s.isFrontPage).length;
      const corpEventsCount = stories.filter(s => s.category === "Corporate Events").length;
      const corpApptsCount = stories.filter(s => s.category === "Corporate Appointments").length;
      const corpCount = corpEventsCount + corpApptsCount;
      const opinionsCount = stories.filter(s => s.isOpinion).length;

      const feCount = stories.filter(s => s.hasFe).length;
      const bsCount = stories.filter(s => s.hasBs).length;

      // TOP QUICK FILTER TABS
      const navDiv = document.createElement("div");
      navDiv.className = "sticky top-0 z-20 bg-slate-100/95 dark:bg-[#070B14]/95 backdrop-blur-xs p-1 rounded-lg border border-slate-300 dark:border-slate-800 flex items-center justify-between gap-1 text-[11px] font-mono shadow-2xs mb-0.5";
      navDiv.innerHTML = `
        <button onclick="setRightPanelView('ALL')" class="flex-1 py-1 rounded text-center transition-all ${activeRightPanelView === 'ALL' ? 'bg-[#1C1917] text-white dark:bg-indigo-600 font-bold shadow-xs' : 'text-slate-700 dark:text-slate-300 hover:bg-white/80 dark:hover:bg-slate-800 font-medium'}">All</button>
        <button onclick="setRightPanelView('CATEGORIES')" class="flex-1 py-1 rounded text-center transition-all ${activeRightPanelView === 'CATEGORIES' ? 'bg-[#1C1917] text-white dark:bg-indigo-600 font-bold shadow-xs' : 'text-slate-700 dark:text-slate-300 hover:bg-white/80 dark:hover:bg-slate-800 font-medium'}">📁 Desks</button>
        <button onclick="setRightPanelView('SECTORS')" class="flex-1 py-1 rounded text-center transition-all ${activeRightPanelView === 'SECTORS' ? 'bg-[#1C1917] text-white dark:bg-indigo-600 font-bold shadow-xs' : 'text-slate-700 dark:text-slate-300 hover:bg-white/80 dark:hover:bg-slate-800 font-medium'}">📈 Sectors</button>
        <button onclick="setRightPanelView('STOCKS')" class="flex-1 py-1 rounded text-center transition-all ${activeRightPanelView === 'STOCKS' ? 'bg-[#1C1917] text-white dark:bg-indigo-600 font-bold shadow-xs' : 'text-slate-700 dark:text-slate-300 hover:bg-white/80 dark:hover:bg-slate-800 font-medium'}">🏢 Stocks</button>
      `;
      container.appendChild(navDiv);

      // --- SECTION 1: CATEGORIES & PUBLICATIONS TREE CARD ---
      if (activeRightPanelView === 'ALL' || activeRightPanelView === 'CATEGORIES') {
        const catCard = document.createElement("div");
        catCard.className = "rounded-lg bg-white dark:bg-[#0E1322] border border-slate-200 dark:border-slate-800 shadow-xs overflow-hidden";
        
        const isCatOpen = treeState.categories;
        catCard.innerHTML = `
          <div class="px-2.5 py-1.5 bg-slate-50 dark:bg-slate-900/90 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between cursor-pointer select-none" onclick="toggleTreeNode('categories')">
            <div class="flex items-center gap-1.5 text-[13px] font-sans font-bold text-slate-900 dark:text-slate-100">
              <span class="text-amber-600 dark:text-amber-400 text-[11px]">${isCatOpen ? '▼' : '▶'}</span>
              <span>📁 Desks & Sources</span>
            </div>
            ${selectedFeedCategory !== 'ALL' ? `<button onclick="event.stopPropagation(); onCategorySelect('ALL');" class="text-[10.5px] font-mono text-amber-600 dark:text-amber-400 font-bold hover:underline">Reset (✕)</button>` : ''}
          </div>
        `;

        if (isCatOpen) {
          const catBody = document.createElement("div");
          catBody.className = "p-1.5 flex flex-col gap-1 text-[13px] font-sans";

          // Sub-group: Publication Source Filter
          const pubDiv = document.createElement("div");
          pubDiv.className = "flex flex-col gap-0.5 mb-1 pb-1.5 border-b border-slate-100 dark:border-slate-800";
          pubDiv.innerHTML = `<span class="text-[10.5px] font-bold uppercase text-blue-700 dark:text-blue-400 px-1 mb-0.5 tracking-wider">🗞️ Filter by Publication</span>`;

          const pubItems = [
            { id: "SOURCE_FE", label: "📰 Financial Express Only", count: feCount, badge: "FE" },
            { id: "SOURCE_BS", label: "📰 Business Standard Only", count: bsCount, badge: "BS" },
            { id: "ALL", label: "📑 All Unified Stories", count: stories.length, badge: "ALL" }
          ];

          pubItems.forEach(item => {
            const isSelected = selectedFeedCategory === item.id;
            const btn = document.createElement("button");
            btn.className = `w-full text-left px-2 py-1 rounded flex items-center justify-between transition-colors cursor-pointer ${isSelected ? 'bg-blue-600 text-white font-bold shadow-xs' : 'text-[#090D16] dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800/60 font-medium'}`;
            btn.innerHTML = `
              <span class="flex items-center gap-1.5 min-w-0 truncate">
                <span class="text-slate-400 select-none text-[11px] ${isSelected ? 'text-white' : ''}">├─</span>
                <span class="truncate text-[13px]">${item.label}</span>
              </span>
              <span class="text-[11.5px] font-mono shrink-0 ml-1 ${isSelected ? 'text-white/90' : 'text-slate-400 dark:text-slate-500'}">(${item.count})</span>
            `;
            btn.onclick = () => onCategorySelect(isSelected && item.id !== 'ALL' ? 'ALL' : item.id);
            pubDiv.appendChild(btn);
          });
          catBody.appendChild(pubDiv);

          // Sub-group: Core News Desks
          const coreNewsItems = [
            { id: "ANCHOR", label: "📰 News (Front Page)", count: anchorCount },
            { id: "Sector", label: "🏢 Sector News", count: stories.filter(s => s.category === "Sector").length },
            { id: "Economy", label: "📈 Economy", count: stories.filter(s => s.category === "Economy").length },
            { id: "Policy", label: "🏛️ Policy & Rules", count: stories.filter(s => s.category === "Policy").length },
            { id: "Market", label: "📊 Market Pulse", count: stories.filter(s => s.category === "Market").length },
            { id: "Trade", label: "🚢 Trade & FX", count: stories.filter(s => s.category === "Trade").length },
            { id: "International News", label: "🌐 International", count: stories.filter(s => s.category === "International News").length },
            { id: "Others", label: "📑 Features", count: stories.filter(s => s.category === "Others").length }
          ];

          const coreDiv = document.createElement("div");
          coreDiv.className = "flex flex-col gap-0.5";
          coreDiv.innerHTML = `<span class="text-[10.5px] font-bold uppercase text-slate-400 dark:text-slate-500 px-1 mb-0.5 tracking-wider">📰 Core Desks</span>`;

          coreNewsItems.forEach(item => {
            const isSelected = selectedFeedCategory === item.id;
            const btn = document.createElement("button");
            btn.className = `w-full text-left px-2 py-1 rounded flex items-center justify-between transition-colors cursor-pointer ${isSelected ? 'bg-indigo-600 text-white font-bold shadow-xs' : 'text-[#090D16] dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800/60 font-medium'}`;
            btn.innerHTML = `
              <span class="flex items-center gap-1.5 min-w-0 truncate">
                <span class="text-slate-400 select-none text-[11px] ${isSelected ? 'text-white' : ''}">├─</span>
                <span class="truncate text-[13px]">${item.label}</span>
              </span>
              <span class="text-[11.5px] font-mono shrink-0 ml-1 ${isSelected ? 'text-white/90' : 'text-slate-400 dark:text-slate-500'}">(${item.count})</span>
            `;
            btn.onclick = () => {
              if (item.id === 'ANCHOR') switchView('anchor');
              else onCategorySelect(isSelected ? 'ALL' : item.id);
            };
            coreDiv.appendChild(btn);
          });
          catBody.appendChild(coreDiv);

          // Sub-group: Specialized Desks
          const deskItems = [
            { id: "IPO_ALL", label: "🚀 IPO Central", count: totalIpos },
            { id: "CORPORATE_ALL", label: "🏢 Corporate Desk", count: corpCount },
            { id: "EVENTS", label: "📢 Corp Events", count: corpEventsCount },
            { id: "APPOINTMENTS", label: "👔 Appointments", count: corpApptsCount },
            { id: "OPINIONS", label: "✍️ Opinions Desk", count: opinionsCount }
          ];

          const deskDiv = document.createElement("div");
          deskDiv.className = "flex flex-col gap-0.5 pt-1.5 border-t border-slate-100 dark:border-slate-800";
          deskDiv.innerHTML = `<span class="text-[10.5px] font-bold uppercase text-amber-700 dark:text-amber-400 px-1 mb-0.5 tracking-wider">🏛️ Specialized Desks</span>`;

          deskItems.forEach(item => {
            const isSelected = selectedFeedCategory === item.id || (item.id === 'IPO_ALL' && currentView === 'ipo') || (item.id === 'CORPORATE_ALL' && currentView === 'corporate');
            const btn = document.createElement("button");
            btn.className = `w-full text-left px-2 py-1 rounded flex items-center justify-between transition-colors cursor-pointer ${isSelected ? 'bg-amber-700 text-white font-bold shadow-xs' : 'text-[#090D16] dark:text-slate-200 hover:bg-amber-50/60 dark:hover:bg-amber-950/30 font-medium'}`;
            btn.innerHTML = `
              <span class="flex items-center gap-1.5 min-w-0 truncate">
                <span class="text-slate-400 select-none text-[11px] ${isSelected ? 'text-white' : ''}">├─</span>
                <span class="truncate text-[13px]">${item.label}</span>
              </span>
              <span class="text-[11.5px] font-mono shrink-0 ml-1 ${isSelected ? 'text-white/90' : 'text-amber-700 dark:text-amber-400'}">(${item.count})</span>
            `;
            btn.onclick = () => {
              if (item.id === 'IPO_ALL') onDeskSelect('ipo');
              else if (item.id === 'CORPORATE_ALL') onDeskSelect('corporate');
              else if (item.id === 'EVENTS') selectCorporateSub('EVENTS');
              else if (item.id === 'APPOINTMENTS') selectCorporateSub('APPOINTMENTS');
              else if (item.id === 'OPINIONS') onDeskSelect('opinions');
            };
            deskDiv.appendChild(btn);
          });
          catBody.appendChild(deskDiv);

          catCard.appendChild(catBody);
        }
        container.appendChild(catCard);
      }

      // --- SECTION 2: INDUSTRY SECTORS TREE CARD ---
      if (activeRightPanelView === 'ALL' || activeRightPanelView === 'SECTORS') {
        const secCounts = {};
        stories.forEach(s => {
          (s.sectors || []).forEach(sec => secCounts[sec] = (secCounts[sec] || 0) + 1);
        });
        const sortedSecs = Object.keys(secCounts).sort((a,b) => secCounts[b] - secCounts[a]);

        const secCard = document.createElement("div");
        secCard.className = "rounded-lg bg-white dark:bg-[#0E1322] border border-slate-200 dark:border-slate-800 shadow-xs overflow-hidden";
        
        const isSecOpen = treeState.sectors;
        secCard.innerHTML = `
          <div class="px-2.5 py-1.5 bg-slate-50 dark:bg-slate-900/90 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between cursor-pointer select-none" onclick="toggleTreeNode('sectors')">
            <div class="flex items-center gap-1.5 text-[13px] font-sans font-bold text-slate-900 dark:text-slate-100">
              <span class="text-indigo-600 dark:text-indigo-400 text-[11px]">${isSecOpen ? '▼' : '▶'}</span>
              <span>📈 Industry Sectors</span>
              <span class="text-[11.5px] text-slate-500 dark:text-slate-400 font-mono">(${sortedSecs.length})</span>
            </div>
            ${activeSectorFilter ? `<button onclick="event.stopPropagation(); activeSectorFilter = null; renderCategoriesAndStocksSidebar(); renderFeedList();" class="text-[10.5px] font-mono text-indigo-600 dark:text-indigo-400 font-bold hover:underline">Clear (✕)</button>` : ''}
          </div>
        `;

        if (isSecOpen) {
          const secBody = document.createElement("div");
          secBody.className = "p-1.5 flex flex-col gap-0.5 text-[13px] font-sans";

          sortedSecs.forEach(sec => {
            const isSelected = activeSectorFilter === sec;
            const btn = document.createElement("button");
            btn.className = `w-full text-left px-2 py-1 rounded flex items-center justify-between transition-colors cursor-pointer ${isSelected ? 'bg-indigo-600 text-white font-bold shadow-xs' : 'text-[#090D16] dark:text-slate-200 hover:bg-indigo-50/60 dark:hover:bg-indigo-950/30 font-medium'}`;
            btn.innerHTML = `
              <span class="flex items-center gap-1.5 min-w-0 truncate">
                <span class="text-slate-400 select-none text-[11px] ${isSelected ? 'text-white' : ''}">├─</span>
                <span class="truncate text-[13px]">${sec}</span>
              </span>
              <span class="text-[11.5px] font-mono shrink-0 ml-1 ${isSelected ? 'text-white/90' : 'text-slate-400 dark:text-slate-500'}">(${secCounts[sec]})</span>
            `;
            btn.onclick = () => {
              activeSectorFilter = activeSectorFilter === sec ? null : sec;
              selectedStoryIndex = 0;
              currentFeedPage = 1;
              renderCategoriesAndStocksSidebar();
              if (currentLayoutMode === "split") renderFeedList();
              else renderMatrixTable();
            };
            secBody.appendChild(btn);
          });
          secCard.appendChild(secBody);
        }
        container.appendChild(secCard);
      }

      // --- SECTION 3: COMPANY STOCKS CLUSTERED & COLOR-CODED ---
      if (activeRightPanelView === 'ALL' || activeRightPanelView === 'STOCKS') {
        const stockCounts = {};
        stories.forEach(s => {
          (s.stocks || []).forEach(stk => stockCounts[stk] = (stockCounts[stk] || 0) + 1);
        });
        const activeStockKeys = Object.keys(stockCounts);

        const clusters = {};
        activeStockKeys.forEach(stk => {
          if (stockSearchFilterText && !stk.includes(stockSearchFilterText)) return;
          const info = stockClusterMap[stk] || { group: "Other Companies", color: "slate" };
          const gName = info.group;
          if (!clusters[gName]) clusters[gName] = { color: info.color, stocks: [] };
          clusters[gName].stocks.push({ ticker: stk, count: stockCounts[stk] });
        });

        const clusterEntries = Object.entries(clusters).sort((a, b) => {
          const totalA = a[1].stocks.reduce((acc, s) => acc + s.count, 0);
          const totalB = b[1].stocks.reduce((acc, s) => acc + s.count, 0);
          return totalB - totalA;
        });

        const stockCard = document.createElement("div");
        stockCard.className = "rounded-lg bg-white dark:bg-[#0E1322] border border-slate-200 dark:border-slate-800 shadow-xs overflow-hidden";
        
        const isStockOpen = treeState.stocks;
        stockCard.innerHTML = `
          <div class="px-2.5 py-1.5 bg-slate-50 dark:bg-slate-900/90 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between cursor-pointer select-none" onclick="toggleTreeNode('stocks')">
            <div class="flex items-center gap-1.5 text-[13px] font-sans font-bold text-slate-900 dark:text-slate-100">
              <span class="text-amber-600 dark:text-amber-400 text-[11px]">${isStockOpen ? '▼' : '▶'}</span>
              <span>🏢 Company Stocks</span>
              <span class="text-[11.5px] text-slate-500 dark:text-slate-400 font-mono">(${activeStockKeys.length})</span>
            </div>
            ${activeStockFilter ? `<button onclick="event.stopPropagation(); activeStockFilter = null; renderCategoriesAndStocksSidebar(); renderFeedList();" class="text-[10.5px] font-mono text-indigo-600 dark:text-indigo-400 font-bold hover:underline">Clear (✕)</button>` : ''}
          </div>
        `;

        if (isStockOpen) {
          const stockBody = document.createElement("div");
          stockBody.className = "p-1.5 flex flex-col gap-1.5 text-[12.5px] font-sans";

          const searchDiv = document.createElement("div");
          searchDiv.className = "px-0.5 pb-1 border-b border-slate-100 dark:border-slate-800 flex items-center gap-1";
          searchDiv.innerHTML = `
            <input type="text" id="sidebar-stock-search" value="${stockSearchFilterText}" oninput="onStockSearchInput(this.value)" placeholder="🔍 Search stock..." class="w-full text-[11px] px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-900 border border-slate-300 dark:border-slate-700 text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:border-amber-500 font-mono shadow-2xs"/>
            ${stockSearchFilterText ? `<button onclick="onStockSearchInput('')" class="text-slate-400 hover:text-slate-700 dark:hover:text-white text-[11px] font-bold px-1">✕</button>` : ''}
          `;
          stockBody.appendChild(searchDiv);

          const colorStyles = {
            blue: "bg-blue-50 text-blue-900 border-blue-200 dark:bg-blue-950/40 dark:text-blue-300 dark:border-blue-800",
            amber: "bg-amber-50 text-amber-900 border-amber-200 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-800",
            purple: "bg-purple-50 text-purple-900 border-purple-200 dark:bg-purple-950/40 dark:text-purple-300 dark:border-purple-800",
            emerald: "bg-emerald-50 text-emerald-900 border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800",
            sky: "bg-sky-50 text-sky-900 border-sky-200 dark:bg-sky-950/40 dark:text-sky-300 dark:border-sky-800",
            slate: "bg-slate-100 text-slate-900 border-slate-300 dark:bg-slate-800 dark:text-slate-200 dark:border-slate-700",
            teal: "bg-teal-50 text-teal-900 border-teal-200 dark:bg-teal-950/40 dark:text-teal-300 dark:border-teal-800",
            rose: "bg-rose-50 text-rose-900 border-rose-200 dark:bg-rose-950/40 dark:text-rose-300 dark:border-rose-800",
            indigo: "bg-indigo-50 text-indigo-900 border-indigo-200 dark:bg-indigo-950/40 dark:text-indigo-300 dark:border-indigo-800"
          };

          if (clusterEntries.length === 0) {
            const noMatch = document.createElement("div");
            noMatch.className = "p-2 text-[11px] text-slate-400 font-mono text-center";
            noMatch.textContent = "No stocks matching search";
            stockBody.appendChild(noMatch);
          }

          clusterEntries.forEach(([gName, gData]) => {
            const gDiv = document.createElement("div");
            gDiv.className = "flex flex-col gap-0.5";
            
            const activeColor = colorStyles[gData.color] || colorStyles.slate;

            gDiv.innerHTML = `<span class="text-[10px] font-bold uppercase px-1 text-slate-500 dark:text-slate-400 tracking-wider mb-0.5">${gName}</span>`;

            gData.stocks.sort((a, b) => b.count - a.count).forEach(stkItem => {
              const isSelected = activeStockFilter === stkItem.ticker;
              const btn = document.createElement("button");
              
              const btnStyle = isSelected
                ? "bg-amber-600 text-white font-bold shadow-xs border border-amber-600"
                : `hover:opacity-90 border font-medium ${activeColor}`;

              btn.className = `w-full text-left px-2 py-0.5 rounded text-[12px] flex items-center justify-between transition-colors cursor-pointer mb-0.5 ${btnStyle}`;
              btn.innerHTML = `
                <span class="flex items-center gap-1 min-w-0 truncate">
                  <span class="truncate font-mono font-bold">${stkItem.ticker}</span>
                </span>
                <span class="text-[10.5px] font-mono shrink-0 ml-1 ${isSelected ? 'text-white' : 'opacity-80'}">(${stkItem.count})</span>
              `;
              btn.onclick = () => {
                activeStockFilter = activeStockFilter === stkItem.ticker ? null : stkItem.ticker;
                selectedStoryIndex = 0;
                currentFeedPage = 1;
                renderCategoriesAndStocksSidebar();
                if (currentLayoutMode === "split") renderFeedList();
                else renderMatrixTable();
              };
              gDiv.appendChild(btn);
            });

            stockBody.appendChild(gDiv);
          });

          stockCard.appendChild(stockBody);
        }
        container.appendChild(stockCard);
      }
    }'''

    start_sb = clean_script.find('function renderCategoriesAndStocksSidebar(')
    end_sb = clean_script.find('function clearAllStockAndSectorFilters(')
    if start_sb != -1 and end_sb != -1:
        clean_script = clean_script[:start_sb] + sidebar_code + '\n\n    ' + clean_script[end_sb:]

    # Enhanced renderFeedList with FE and BS badges
    feed_list_code = '''    function renderFeedList() {
      const rawQuery = document.getElementById("global-search").value.trim().toLowerCase();
      const queryTokens = rawQuery ? rawQuery.split(/\\s+/).filter(Boolean) : [];
      
      const displayed = getFilteredStories();
      const totalStories = displayed.length;
      const totalPages = Math.ceil(totalStories / FEED_PAGE_SIZE) || 1;

      if (currentFeedPage > totalPages) currentFeedPage = totalPages;
      if (currentFeedPage < 1) currentFeedPage = 1;

      const startIndex = (currentFeedPage - 1) * FEED_PAGE_SIZE;
      const endIndex = Math.min(startIndex + FEED_PAGE_SIZE, totalStories);
      const pageStories = displayed.slice(startIndex, endIndex);

      // Header indicator
      const countBadge = document.getElementById("feed-list-count");
      if (countBadge) {
        countBadge.textContent = totalStories > 0 ? `${startIndex + 1}-${endIndex} of ${totalStories}` : `0 Stories`;
      }

      // Pagination Controls
      const pagInfo = document.getElementById("feed-pagination-info");
      if (pagInfo) {
        pagInfo.textContent = `Page ${currentFeedPage} / ${totalPages} (${totalStories})`;
      }
      const prevBtn = document.getElementById("feed-prev-page");
      const nextBtn = document.getElementById("feed-next-page");
      if (prevBtn) {
        prevBtn.disabled = currentFeedPage <= 1;
        prevBtn.className = currentFeedPage <= 1 
          ? "px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-[10.5px] font-medium text-slate-400 dark:text-slate-600 border border-slate-200 dark:border-slate-800 cursor-not-allowed opacity-50"
          : "px-2 py-0.5 rounded bg-white dark:bg-slate-800 hover:bg-amber-50 text-[10.5px] font-semibold text-slate-900 dark:text-slate-200 border border-slate-300 dark:border-slate-700 shadow-2xs cursor-pointer";
      }
      if (nextBtn) {
        nextBtn.disabled = currentFeedPage >= totalPages;
        nextBtn.className = currentFeedPage >= totalPages 
          ? "px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-[10.5px] font-medium text-slate-400 dark:text-slate-600 border border-slate-200 dark:border-slate-800 cursor-not-allowed opacity-50"
          : "px-2 py-0.5 rounded bg-white dark:bg-slate-800 hover:bg-amber-50 text-[10.5px] font-semibold text-slate-900 dark:text-slate-200 border border-slate-300 dark:border-slate-700 shadow-2xs cursor-pointer";
      }

      const listContainer = document.getElementById("feed-list-container");
      listContainer.innerHTML = "";

      if (totalStories === 0) {
        listContainer.innerHTML = `
          <div class="p-8 text-center text-slate-400">
            <p class="text-base font-semibold text-slate-700 dark:text-slate-300">No news stories found</p>
            <p class="text-[12.5px] mt-1 text-slate-500">Try broadening your search term or selecting another section.</p>
            ${rawQuery ? `<button onclick="clearSearch()" class="mt-3 px-3 py-1 bg-amber-700 text-white rounded-md text-xs font-semibold">Clear Search</button>` : ''}
          </div>
        `;
        document.getElementById("feed-detail-container").innerHTML = `<div class="p-8 text-center text-slate-400 text-[13.5px]">Select a story to view analysis.</div>`;
        return;
      }

      if (selectedStoryIndex < startIndex || selectedStoryIndex >= endIndex) {
        selectedStoryIndex = startIndex;
      }

      pageStories.forEach((s, localIdx) => {
        const globalIdx = startIndex + localIdx;
        const isSelected = globalIdx === selectedStoryIndex;
        const numStr = (globalIdx + 1).toString().padStart(2, '0');
        const dot = s.sentiment === "BULLISH" ? "bg-emerald-500" : s.sentiment === "BEARISH" ? "bg-rose-500" : "bg-slate-400";

        const feBadge = s.hasFe ? `<span class="px-1.5 py-0.2 rounded text-[10px] font-mono font-extrabold bg-blue-100 text-blue-900 border border-blue-300 dark:bg-blue-950 dark:text-blue-300 shrink-0">FE</span>` : '';
        const bsBadge = s.hasBs ? `<span class="px-1.5 py-0.2 rounded text-[10px] font-mono font-extrabold bg-amber-100 text-amber-900 border border-amber-300 dark:bg-amber-950 dark:text-amber-300 shrink-0">BS</span>` : '';

        const activeStyle = "bg-[#FAF5FF] dark:bg-[#1E1B4B]/70 border-2 border-[#8B5CF6] dark:border-[#A78BFA] shadow-xs text-[#6B21A8] dark:text-[#E9D5FF]";
        const inactiveStyle = "bg-white dark:bg-[#0D1322] border border-slate-200 dark:border-slate-800 hover:border-purple-300 dark:hover:border-purple-900/60 hover:bg-[#FAF5FF]/50 dark:hover:bg-slate-800/50 text-slate-900 dark:text-slate-100";

        const btn = document.createElement("button");
        btn.className = `w-full text-left px-3 py-2.5 rounded-lg transition-all flex items-center gap-2.5 mb-1.5 last:mb-0 cursor-pointer ${isSelected ? activeStyle : inactiveStyle}`;
        btn.onclick = () => {
          selectedStoryIndex = globalIdx;
          renderFeedList();
          if (window.innerWidth < 1024) {
            const detailWrapper = document.getElementById("feed-detail-wrapper");
            if (detailWrapper) {
              detailWrapper.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
          }
        };

        btn.innerHTML = `
          <div class="flex items-center gap-1.5 shrink-0">
            <span class="text-[12.5px] font-mono font-bold ${isSelected ? 'text-[#8B5CF6] dark:text-[#C4B5FD]' : 'text-slate-400'} tabular-nums w-5">${numStr}</span>
            <span class="w-2.5 h-2.5 rounded-full ${dot}"></span>
            ${feBadge}
            ${bsBadge}
          </div>
          <h4 class="text-[14.5px] sm:text-[15px] font-sans font-medium ${isSelected ? 'text-[#581C87] dark:text-[#E9D5FF]' : 'text-[#090D16] dark:text-[#F8FAFC]'} tracking-tight truncate flex-1 min-w-0 leading-snug" title="${escapeQuotes(s.headline)}">
            ${highlightSearchTokens(s.headline, queryTokens)}
          </h4>
        `;
        listContainer.appendChild(btn);
      });

      renderActiveStoryDetail(displayed[selectedStoryIndex], queryTokens);
      saveNavigationState();
    }'''

    start_fl = clean_script.find('function renderFeedList(')
    end_fl = clean_script.find('function formatPageSource(')
    if start_fl != -1 and end_fl != -1:
        clean_script = clean_script[:start_fl] + feed_list_code + '\n\n    ' + clean_script[end_fl:]

    # Update renderActiveStoryDetail in clean_script (Clean layout with explicit FE & BS badges)
    detail_fn_code = r'''
    function renderActiveStoryDetail(story, queryTokens = []) {
      const container = document.getElementById("feed-detail-container");
      if (!container) return;

      if (!story) {
        container.innerHTML = `
          <div class="h-full flex flex-col items-center justify-center text-center p-8 text-slate-400">
            <span class="text-4xl mb-3">📰</span>
            <p class="font-mono text-sm font-semibold">Select any story from the News Wire on the left to read full intelligence breakdown.</p>
          </div>
        `;
        return;
      }

      const isBullish = (story.sentiment || '').includes('BULLISH');
      const isBearish = (story.sentiment || '').includes('BEARISH');
      
      const sentBadge = isBullish 
        ? `<span class="px-2.5 py-0.5 rounded text-[11px] font-mono font-bold bg-emerald-100 text-emerald-950 border border-emerald-300 dark:bg-emerald-950/70 dark:text-emerald-200">🟢 BULLISH</span>`
        : isBearish 
        ? `<span class="px-2.5 py-0.5 rounded text-[11px] font-mono font-bold bg-rose-100 text-rose-950 border border-rose-300 dark:bg-rose-950/70 dark:text-rose-200">🔴 BEARISH</span>`
        : `<span class="px-2.5 py-0.5 rounded text-[11px] font-mono font-bold bg-slate-200 text-slate-900 border border-slate-300 dark:bg-slate-800 dark:text-slate-200">⚪ NEUTRAL</span>`;

      const tickerBadges = (story.tickers || []).slice(0, 4).map(t => `<span class="px-2.5 py-0.5 text-[11px] font-mono font-bold rounded bg-indigo-50 text-indigo-900 border border-indigo-200 dark:bg-indigo-950/60 dark:text-indigo-200">${t}</span>`).join('');

      const briefSentences = (story.brief_details || "").split(/(?<=[.?!])\s+/).filter(Boolean);
      const bullets = story.bullet_points || story.detailed_points || [];

      container.innerHTML = `
        <!-- TOP ROW: METADATA & ACTION BUTTONS -->
        <div class="flex items-center justify-between gap-2 pb-2.5 border-b border-slate-200 dark:border-slate-800 shrink-0 text-[12px] font-mono">
          <div class="flex items-center gap-1.5 flex-wrap">
            <span class="font-semibold px-2.5 py-0.5 rounded bg-slate-200 text-slate-900 dark:bg-slate-800 dark:text-white">${story.category}</span>
            ${story.isFrontPage ? `<span class="font-semibold px-2.5 py-0.5 rounded bg-amber-200 text-amber-950 dark:bg-amber-950/80 dark:text-amber-200">📰 PAGE 1 ANCHOR</span>` : ''}
            ${story.hasFe ? `<span class="font-bold px-2 py-0.5 rounded bg-blue-100 text-blue-900 border border-blue-300 dark:bg-blue-950 dark:text-blue-200">Financial Express</span>` : ''}
            ${story.hasBs ? `<span class="font-bold px-2 py-0.5 rounded bg-amber-100 text-amber-900 border border-amber-300 dark:bg-amber-950 dark:text-amber-200">Business Standard</span>` : ''}
            <span class="font-semibold px-2.5 py-0.5 rounded bg-slate-100 dark:bg-slate-800/80 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700">${formatPageSource(story.page_numbers)}</span>
          </div>
          <div class="flex items-center gap-2">
            ${sentBadge}
            <button onclick="copyStoryById(${story.id})" class="text-slate-800 hover:text-slate-950 dark:text-slate-200 dark:hover:text-white font-mono flex items-center gap-1 font-semibold px-2.5 py-0.5 rounded border border-slate-300 dark:border-slate-700 bg-white dark:bg-[#141A2E] shadow-2xs cursor-pointer" title="Copy story summary">
              📋 Copy
            </button>
          </div>
        </div>

        <!-- HEADLINE -->
        <h1 class="text-[19px] sm:text-[21px] font-bold text-[#05080F] dark:text-white leading-snug tracking-tight my-3 shrink-0 flex items-center flex-wrap gap-2">
          <span>${highlightSearchTokens(highlightNumbers(story.headline), queryTokens)}</span>
          ${(story.tickers && story.tickers.length > 0) ? tickerBadges : ''}
        </h1>

        <!-- MAIN CONTENT GRID -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-3.5 items-start my-1">
          
          <!-- LEFT COLUMN (lg:col-span-6): EXECUTIVE GIST & TRADER CATALYST -->
          <div class="lg:col-span-6 flex flex-col gap-3.5">
            
            <!-- ⚡ SECTION 1: EXECUTIVE GIST -->
            <div class="rounded-xl border-2 border-indigo-300 dark:border-indigo-800 bg-indigo-50/60 dark:bg-[#13182E] p-3.5 sm:p-4 shadow-xs flex flex-col gap-2.5">
              <div class="flex items-center justify-between border-b border-indigo-200/90 dark:border-indigo-900/60 pb-1.5">
                <span class="text-[12.5px] font-mono font-extrabold uppercase tracking-wider text-indigo-950 dark:text-indigo-200 flex items-center gap-1.5">
                  <span>⚡</span> <span>1. Executive Gist</span>
                </span>
                <span class="text-[11px] font-mono font-bold px-2 py-0.5 rounded bg-indigo-200/80 text-indigo-950 dark:bg-indigo-900/80 dark:text-indigo-200">Key Takeaway</span>
              </div>
              <div class="space-y-2.5">
                ${briefSentences.map(sent => `
                  <div class="flex items-start gap-2.5 bg-white/95 dark:bg-[#0E1322] p-3 rounded-lg border border-indigo-100 dark:border-slate-800 text-[15px] sm:text-[15.5px] text-[#090D16] dark:text-[#F8FAFC] leading-relaxed font-normal shadow-2xs font-sans tracking-tight">
                    <span class="text-indigo-600 dark:text-indigo-400 font-bold select-none mt-0.5 text-sm">▸</span>
                    <span class="leading-relaxed">${highlightSearchTokens(highlightNumbers(sent), queryTokens)}</span>
                  </div>
                `).join('')}
              </div>
            </div>

            <!-- 💡 SECTION 2: TRADER CATALYST & IMPACT ANALYSIS -->
            <div class="p-3.5 sm:p-4 rounded-xl border-2 ${isBullish ? 'border-emerald-500 bg-emerald-50/70 dark:bg-[#064E3B]/30 dark:border-emerald-600' : isBearish ? 'border-rose-500 bg-rose-50/70 dark:bg-[#881337]/30 dark:border-rose-600' : 'border-slate-400 bg-slate-50 dark:bg-slate-900/50 dark:border-slate-700'} shadow-xs flex flex-col gap-2.5">
              <div class="flex items-center justify-between border-b ${isBullish ? 'border-emerald-200 dark:border-emerald-900/60' : isBearish ? 'border-rose-200 dark:border-rose-900/60' : 'border-slate-200 dark:border-slate-800'} pb-1.5">
                <span class="text-[12.5px] font-mono font-extrabold uppercase tracking-wider ${isBullish ? 'text-emerald-950 dark:text-emerald-300' : isBearish ? 'text-rose-950 dark:text-rose-300' : 'text-slate-900 dark:text-slate-200'} flex items-center gap-1.5">
                  <span>💡</span> <span>2. Catalyst & Market Impact</span>
                </span>
                <span class="text-[11px] font-mono font-extrabold uppercase px-2.5 py-0.5 rounded ${isBullish ? 'bg-emerald-200 text-emerald-950 dark:bg-emerald-900 dark:text-emerald-200' : isBearish ? 'bg-rose-200 text-rose-950 dark:bg-rose-900 dark:text-rose-200' : 'bg-slate-200 text-slate-900 dark:bg-slate-800 dark:text-slate-200'}">${story.sentiment} THESIS</span>
              </div>
              <div class="bg-white/95 dark:bg-[#0E1322] p-3 rounded-lg border ${isBullish ? 'border-emerald-200/60 dark:border-slate-800' : isBearish ? 'border-rose-200/60 dark:border-slate-800' : 'border-slate-200 dark:border-slate-800'} text-[15px] sm:text-[15.5px] text-[#090D16] dark:text-[#F8FAFC] leading-relaxed font-normal shadow-2xs font-sans tracking-tight">
                ${highlightSearchTokens(highlightNumbers(story.sentimentReasoning || story.catalyst || ""), queryTokens)}
              </div>
            </div>

          </div>

          <!-- RIGHT COLUMN (lg:col-span-6): KEY ANALYST DATA POINTS -->
          <div class="lg:col-span-6 flex flex-col gap-2">
            
            <!-- 📌 SECTION 3: KEY ANALYST DATA POINTS -->
            <div class="rounded-xl border-2 border-[#C9B7A5] dark:border-[#524434] bg-[#FDFBF7] dark:bg-[#191512] p-3.5 sm:p-4 shadow-xs flex flex-col gap-2.5">
              <div class="flex items-center justify-between border-b border-[#E8DCCE] dark:border-[#382E25] pb-1.5">
                <span class="text-[12.5px] font-mono font-extrabold uppercase tracking-wider text-[#2E1F14] dark:text-[#F3ECE4] flex items-center gap-1.5">
                  <span>📌</span> <span>3. Key Analyst Data Points</span>
                </span>
                <span class="text-[11px] font-mono font-bold px-2 py-0.5 rounded bg-[#EFE5D9] text-[#291B10] dark:bg-[#32261C] dark:text-[#E8DCCF] border border-[#CCAFA0]/50">Metrics & Facts</span>
              </div>
              <ul class="space-y-2.5">
                ${bullets.map(b => `
                  <li class="flex items-start gap-2.5 bg-white/90 dark:bg-[#13100D] p-3 rounded-lg border border-[#E3D5C5] dark:border-[#3D3228] text-[15px] sm:text-[15.5px] text-[#23170E] dark:text-[#F1E8DF] leading-relaxed font-sans shadow-2xs tracking-tight">
                    <span class="text-[#8C6239] dark:text-[#C59B6D] shrink-0 font-bold mt-0.5 text-base">•</span>
                    <span class="leading-relaxed">${highlightSearchTokens(highlightNumbers(b), queryTokens)}</span>
                  </li>
                `).join('')}
              </ul>
            </div>

          </div>

        </div>

        <!-- 🏁 END OF STORY FOOTER BAR -->
        <div class="mt-4 pt-3 pb-4 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between text-xs font-mono text-slate-400 shrink-0">
          <span class="flex items-center gap-1.5 font-bold text-slate-600 dark:text-slate-300">
            <span>🏁</span> <span>End of Story #${story.id} (${formatPageSource(story.page_numbers)})</span>
          </span>
          <div class="flex items-center gap-2">
            <button onclick="navigateStory(-1)" class="px-2.5 py-1 rounded bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 font-bold border border-slate-300 dark:border-slate-700 shadow-2xs">◀ Prev Story (K)</button>
            <button onclick="navigateStory(1)" class="px-2.5 py-1 rounded bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 font-bold border border-slate-300 dark:border-slate-700 shadow-2xs">Next Story (J) ▶</button>
          </div>
        </div>
      `;
    }'''

    start_det = clean_script.find('function renderActiveStoryDetail')
    end_det = clean_script.find('function renderRawArticleText')
    if end_det == -1:
        end_det = clean_script.find('function highlightNumbers')
    if start_det != -1 and end_det != -1:
        clean_script = clean_script[:start_det] + detail_fn_code + '\n\n    ' + clean_script[end_det:]

    # IPO Hub functions
    ipo_hub_functions = '''
    // ================= IPO HUB CONTROLLER FUNCTIONS =================
    function setIpoViewMode(mode) {
      activeIpoMode = mode;
      const trackerBtn = document.getElementById("ipo-mode-tracker-btn");
      const listedBtn = document.getElementById("ipo-mode-listed-btn");
      const trackerWrap = document.getElementById("ipo-tracker-table-wrap");
      const listedWrap = document.getElementById("ipo-listed-table-wrap");
      const subfilter = document.getElementById("ipo-subfilter-container");

      if (mode === 'tracker') {
        if (trackerBtn) trackerBtn.className = "px-3 py-1.5 rounded-lg bg-[#1C1917] text-white dark:bg-indigo-600 dark:text-white shadow-xs transition-all flex items-center gap-1.5 cursor-pointer";
        if (listedBtn) listedBtn.className = "px-3 py-1.5 rounded-lg text-slate-700 dark:text-slate-300 hover:text-black dark:hover:text-white hover:bg-white/60 dark:hover:bg-slate-800 transition-all flex items-center gap-1.5 cursor-pointer";
        if (trackerWrap) trackerWrap.classList.remove("hidden");
        if (listedWrap) listedWrap.classList.add("hidden");
        if (subfilter) subfilter.classList.remove("hidden");
        renderIpoTrackerTable();
      } else {
        if (listedBtn) listedBtn.className = "px-3 py-1.5 rounded-lg bg-[#1C1917] text-white dark:bg-indigo-600 dark:text-white shadow-xs transition-all flex items-center gap-1.5 cursor-pointer";
        if (trackerBtn) trackerBtn.className = "px-3 py-1.5 rounded-lg text-slate-700 dark:text-slate-300 hover:text-black dark:hover:text-white hover:bg-white/60 dark:hover:bg-slate-800 transition-all flex items-center gap-1.5 cursor-pointer";
        if (listedWrap) listedWrap.classList.remove("hidden");
        if (trackerWrap) trackerWrap.classList.add("hidden");
        if (subfilter) subfilter.classList.add("hidden");
        renderAlreadyListedTable();
      }
    }

    function setIpoFilterCategory(cat) {
      activeIpoCategory = cat;
      ['all', 'mb', 'sme'].forEach(c => {
        const btn = document.getElementById(`ipo-filter-${c}`);
        if (!btn) return;
        if ((c === 'all' && cat === 'ALL') || (c === 'mb' && cat === 'MAINBOARD') || (c === 'sme' && cat === 'SME')) {
          btn.className = "px-2.5 py-1 rounded-md bg-slate-900 text-white dark:bg-indigo-600 dark:text-white font-bold shadow-2xs";
        } else {
          btn.className = "px-2.5 py-1 rounded-md text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800";
        }
      });
      renderIpoTrackerTable();
    }

    function onIpoSearchInput(val) {
      ipoSearchQuery = (val || '').toLowerCase().trim();
      if (activeIpoMode === 'tracker') renderIpoTrackerTable();
      else renderAlreadyListedTable();
    }

    function renderIpoTrackerTable() {
      const tbody = document.getElementById("ipo-table-body");
      const countLabel = document.getElementById("ipo-table-visible-count");
      if (!tbody) return;

      tbody.innerHTML = "";
      let list = ipoList || [];

      if (activeIpoCategory === 'MAINBOARD') {
        list = list.filter(i => !(i.exchange || '').includes("SME") && !(i.exchange || '').includes("Emerge"));
      } else if (activeIpoCategory === 'SME') {
        list = list.filter(i => (i.exchange || '').includes("SME") || (i.exchange || '').includes("Emerge"));
      }

      if (ipoSearchQuery) {
        list = list.filter(i => {
          const full = (i.company + " " + i.exchange + " " + i.stage + " " + (i.details || '')).toLowerCase();
          return full.includes(ipoSearchQuery);
        });
      }

      if (countLabel) countLabel.textContent = list.length;

      // Update KPI counters
      const kpiTotal = document.getElementById("ipo-kpi-total");
      const kpiBidding = document.getElementById("ipo-kpi-bidding");
      const kpiDrhp = document.getElementById("ipo-kpi-drhp");
      if (kpiTotal) kpiTotal.textContent = (ipoList || []).length;
      if (kpiBidding) kpiBidding.textContent = (ipoList || []).filter(i => (i.stage || '').includes("Bidding")).length;
      if (kpiDrhp) kpiDrhp.textContent = (ipoList || []).filter(i => (i.stage || '').includes("DRHP")).length;

      if (list.length === 0) {
        tbody.innerHTML = `<tr><td colspan="9" class="py-12 text-center text-slate-400 font-mono">No active IPO issues match the selected criteria.</td></tr>`;
        return;
      }

      list.forEach((item, idx) => {
        const isSme = (item.exchange || '').includes("SME") || (item.exchange || '').includes("Emerge");
        const stageColor = (item.stage || '').includes("Bidding") 
          ? "bg-emerald-100 text-emerald-950 border-emerald-300 dark:bg-emerald-950/80 dark:text-emerald-300"
          : (item.stage || '').includes("DRHP")
          ? "bg-amber-100 text-amber-950 border-amber-300 dark:bg-amber-950/80 dark:text-amber-300"
          : "bg-blue-100 text-blue-950 border-blue-300 dark:bg-blue-950/80 dark:text-blue-300";

        const tr = document.createElement("tr");
        tr.className = "hover:bg-slate-50/80 dark:hover:bg-slate-800/40 transition-colors";
        tr.innerHTML = `
          <td class="py-3 px-3 text-center font-mono font-bold text-slate-400">${idx + 1}</td>
          <td class="py-3 px-3">
            <div class="font-bold text-[#090D16] dark:text-white leading-tight">${item.company}</div>
            <div class="flex items-center gap-1.5 mt-1">
              <span class="text-[10px] font-mono font-bold px-1.5 py-0.2 rounded ${isSme ? 'bg-purple-100 text-purple-950 dark:bg-purple-950 dark:text-purple-300' : 'bg-indigo-100 text-indigo-950 dark:bg-indigo-950 dark:text-indigo-300'}">${isSme ? 'SME EMERGE' : 'MAINBOARD'}</span>
              <span class="text-[11px] font-mono text-slate-400">${item.exchange || 'NSE / BSE'}</span>
            </div>
          </td>
          <td class="py-3 px-3 font-mono text-[12px] text-slate-600 dark:text-slate-300">
            <div>Open: <b>${item.openDate || 'Oct 2026'}</b></div>
            <div class="text-slate-400">Close: ${item.closeDate || 'Oct 2026'}</div>
          </td>
          <td class="py-3 px-3 font-mono font-bold text-slate-900 dark:text-slate-100">${item.priceBand || '₹140 - ₹148'}</td>
          <td class="py-3 px-3 font-mono font-bold text-indigo-600 dark:text-indigo-400">${item.size || '₹500 Cr'}</td>
          <td class="py-3 px-3 font-mono text-slate-600 dark:text-slate-400">${item.lotSize || '100 Shares'}</td>
          <td class="py-3 px-3 font-mono">
            <div class="flex items-center gap-1.5">
              <span class="font-bold text-emerald-600 dark:text-emerald-400 text-[12.5px]">${item.subscription || '14.5x'}</span>
              <span class="text-[10px] text-slate-400">Total</span>
            </div>
            <div class="text-[10.5px] text-slate-400">QIB: 22x | NII: 15x | Retail: 6x</div>
          </td>
          <td class="py-3 px-3">
            <span class="px-2.5 py-0.5 rounded-full text-[11px] font-mono font-bold border ${stageColor}">
              ${item.stage || '📋 DRHP Filed'}
            </span>
          </td>
          <td class="py-3 px-3 text-center">
            <button onclick="openStoryModalById(${item.storyId || 1})" class="px-2.5 py-1 rounded bg-slate-100 dark:bg-slate-800 hover:bg-indigo-50 text-indigo-600 dark:text-indigo-400 font-mono text-[11px] font-bold border border-slate-200 dark:border-slate-700 cursor-pointer">
              Details ↗
            </button>
          </td>
        `;
        tbody.appendChild(tr);
      });
    }

    function renderAlreadyListedTable() {
      const tbody = document.getElementById("ipo-listed-table-body");
      const countLabel = document.getElementById("ipo-table-visible-count");
      if (!tbody) return;

      tbody.innerHTML = "";
      let list = benchmarkListedIpos;

      if (ipoSearchQuery) {
        list = list.filter(i => (i.name + " " + i.ticker).toLowerCase().includes(ipoSearchQuery));
      }

      if (countLabel) countLabel.textContent = list.length;

      list.forEach((item, idx) => {
        const listGainPct = (((item.listPrice - item.issuePrice) / item.issuePrice) * 100).toFixed(1);
        const totalGainPct = (((item.cmp - item.issuePrice) / item.issuePrice) * 100).toFixed(1);
        const isListPos = listGainPct >= 0;
        const isTotalPos = totalGainPct >= 0;

        const tr = document.createElement("tr");
        tr.className = "hover:bg-slate-50/80 dark:hover:bg-slate-800/40 transition-colors";
        tr.innerHTML = `
          <td class="py-3 px-3 text-center font-mono font-bold text-slate-400">${idx + 1}</td>
          <td class="py-3 px-3">
            <div class="font-bold text-[#090D16] dark:text-white leading-tight">${item.name}</div>
            <div class="flex items-center gap-1.5 mt-0.5">
              <span class="text-[10.5px] font-mono font-bold text-indigo-600 dark:text-indigo-400">${item.ticker}</span>
              <span class="text-[10px] text-slate-400">${item.exchange}</span>
            </div>
          </td>
          <td class="py-3 px-3 font-mono text-[12px] text-slate-600 dark:text-slate-300">${item.date}</td>
          <td class="py-3 px-3 font-mono font-bold text-slate-900 dark:text-slate-100">₹${item.issuePrice}</td>
          <td class="py-3 px-3 font-mono font-bold text-slate-900 dark:text-slate-100">₹${item.listPrice}</td>
          <td class="py-3 px-3 font-mono font-bold ${isListPos ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600'}">
            <span>${isListPos ? '+' : ''}${listGainPct}%</span>
            <span class="text-[10px] text-slate-400 block font-normal">(+₹${item.listPrice - item.issuePrice})</span>
          </td>
          <td class="py-3 px-3 font-mono font-bold text-slate-900 dark:text-slate-100">₹${item.cmp}</td>
          <td class="py-3 px-3 font-mono font-bold ${isTotalPos ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600'}">
            <span>${isTotalPos ? '+' : ''}${totalGainPct}%</span>
            <span class="text-[10px] text-slate-400 block font-normal">(+₹${item.cmp - item.issuePrice})</span>
          </td>
          <td class="py-3 px-3">
            <span class="px-2 py-0.5 rounded text-[10.5px] font-mono font-bold ${totalGainPct > 50 ? 'bg-amber-100 text-amber-950 dark:bg-amber-950 dark:text-amber-300 border border-amber-300' : 'bg-emerald-100 text-emerald-950 dark:bg-emerald-950 dark:text-emerald-300 border border-emerald-300'}">
              ${totalGainPct > 50 ? '🔥 MULTIBAGGER' : '🟢 PREMIUM'}
            </span>
          </td>
        `;
        tbody.appendChild(tr);
      });
    }

    function openStoryModalById(storyId) {
      const s = (stories || []).find(st => st.id === storyId) || stories[0];
      if (s) showStoryModal(s);
    }
'''
    if 'function renderIpoTrackerTable' not in clean_script:
        clean_script += '\n\n' + ipo_hub_functions

    # Override toggleSidebar and applySidebarVisibility to keep CSS Grid clean
    sidebar_toggle_code = '''    function toggleSidebar() {
      isSidebarVisible = !isSidebarVisible;
      localStorage.setItem('finpress_sidebar_visible', isSidebarVisible);
      applySidebarVisibility();
    }

    function applySidebarVisibility() {
      const aside = document.getElementById("view-feed-aside");
      const grid = document.getElementById("workspace-grid");
      const pill = document.getElementById("sidebar-vertical-pill");
      const openBtn = document.getElementById("feed-open-sidebar-btn");
      if (!aside) return;

      if (isSidebarVisible) {
        aside.classList.remove("hidden");
        if (grid) grid.classList.remove("sidebar-collapsed");
        if (pill) pill.classList.add("hidden");
        if (openBtn) {
          openBtn.classList.add("hidden");
          openBtn.classList.remove("flex");
        }
      } else {
        aside.classList.add("hidden");
        if (grid) grid.classList.add("sidebar-collapsed");
        if (pill) pill.classList.remove("hidden");
        if (openBtn) {
          openBtn.classList.remove("hidden");
          openBtn.classList.add("flex");
        }
      }
    }'''

    start_side = clean_script.find('function toggleSidebar()')
    end_side = clean_script.find('function initTheme()', start_side)
    if start_side != -1 and end_side != -1:
        clean_script = clean_script[:start_side] + sidebar_toggle_code + '\n\n    ' + clean_script[end_side:]

    # Story & IPO modals
    modals_code = '''
    function showStoryModal(story) {
      if (!story) return;
      const modal = document.getElementById("story-modal");
      if (!modal) return;

      const catEl = document.getElementById("story-modal-category");
      const sentEl = document.getElementById("story-modal-sentiment");
      const pageEl = document.getElementById("story-modal-pages");
      const hlEl = document.getElementById("story-modal-headline");
      const tickersEl = document.getElementById("story-modal-tickers-container");
      const briefEl = document.getElementById("story-modal-brief");
      const catBoxEl = document.getElementById("story-modal-catalyst");
      const bullEl = document.getElementById("story-modal-bullets");
      const srcEl = document.getElementById("story-modal-source");

      if (catEl) catEl.textContent = story.category || "General";
      if (sentEl) {
        const isBull = (story.sentiment || "").includes("BULLISH");
        const isBear = (story.sentiment || "").includes("BEARISH");
        sentEl.className = `px-2 py-0.5 rounded text-[10.5px] font-mono font-bold ${
          isBull ? "bg-emerald-50 text-emerald-800 border border-emerald-200 dark:bg-emerald-950 dark:text-emerald-300" :
          isBear ? "bg-rose-50 text-rose-800 border border-rose-200 dark:bg-rose-950 dark:text-rose-300" :
          "bg-slate-100 text-slate-800 border border-slate-200 dark:bg-slate-800 dark:text-slate-200"
        }`;
        sentEl.textContent = story.sentiment || "NEUTRAL";
      }
      if (pageEl) pageEl.textContent = formatPageSource(story.page_numbers || "FE / BS");
      if (hlEl) hlEl.textContent = story.headline || "Story Details";
      if (tickersEl) {
        tickersEl.innerHTML = (story.tickers || []).map(t => `<span class="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-indigo-50 text-indigo-700 border border-indigo-200 dark:bg-indigo-950 dark:text-indigo-300">${t}</span>`).join("");
      }
      if (briefEl) briefEl.innerHTML = `<p class="text-xs text-slate-700 dark:text-slate-300 leading-relaxed font-normal">${story.brief_details || story.brief || ""}</p>`;
      if (catBoxEl) catBoxEl.innerHTML = story.catalyst || story.brief_details || "";
      if (bullEl) {
        const pts = story.bullet_points || story.detailed_points || [];
        bullEl.innerHTML = pts.map(p => `<li class="flex items-start gap-1.5 text-xs text-[#3E2B1E] dark:text-[#E2D8CC] leading-relaxed"><span class="text-amber-800 shrink-0 font-bold">•</span><span>${p}</span></li>`).join("");
      }
      if (srcEl) srcEl.textContent = (story.source_paper || "FE / BS") + " Intelligence";

      modal.classList.remove("hidden");
      modal.classList.add("flex");
    }

    function closeStoryModal() {
      const modal = document.getElementById("story-modal");
      if (modal) {
        modal.classList.add("hidden");
        modal.classList.remove("flex");
      }
    }

    function openIpoModal(item) {
      if (!item) return;
      const modal = document.getElementById("ipo-modal");
      if (!modal) return;
      const compEl = document.getElementById("modal-ipo-company");
      const exchEl = document.getElementById("modal-ipo-exchange");
      const stageEl = document.getElementById("modal-ipo-stage");
      const priceEl = document.getElementById("modal-ipo-price");
      const sizeEl = document.getElementById("modal-ipo-size");
      const lotEl = document.getElementById("modal-ipo-lot");
      const subEl = document.getElementById("modal-ipo-sub");
      const descEl = document.getElementById("modal-ipo-desc");

      if (compEl) compEl.textContent = item.company || "IPO Issue";
      if (exchEl) exchEl.textContent = item.exchange || "NSE / BSE";
      if (stageEl) stageEl.textContent = item.stage || "DRHP";
      if (priceEl) priceEl.textContent = item.priceBand || item.issuePrice || "₹--";
      if (sizeEl) sizeEl.textContent = item.size || "₹--";
      if (lotEl) lotEl.textContent = item.lotSize || "--";
      if (subEl) subEl.textContent = item.subscription || item.demand || "--";
      if (descEl) descEl.textContent = item.details || item.brief || item.headline || "";

      modal.classList.remove("hidden");
      modal.classList.add("flex");
    }

    function closeIpoModal() {
      const modal = document.getElementById("ipo-modal");
      if (modal) {
        modal.classList.add("hidden");
        modal.classList.remove("flex");
      }
    }

    function copyStoryById(storyId) {
      const s = (stories || []).find(st => st.id === storyId);
      if (!s) return;
      const lines = [
        s.headline || '',
        '',
        'Key Details:',
        s.brief_details || s.brief || '',
        '',
        'Bullet Points:'
      ];
      (s.bullet_points || []).forEach(b => lines.push('- ' + b));
      lines.push('');
      lines.push('Source: ' + (s.page_numbers || 'FE / BS') + ' | Sentiment: ' + (s.sentiment || ''));
      copyToClipboard(lines.join('\\n'));
    }

    function renderIpoTable() {
      renderIpoTrackerTable();
    }

    function renderCorporateDeskTable() {
      renderFeedList();
    }
'''
    if 'function showStoryModal' not in clean_script:
        clean_script += '\n\n' + modals_code

    final_script = f'''  <!-- ================= CLIENT JAVASCRIPT ================= -->
  <script>
{clean_script}
  </script>'''

    closing_html = '''
</body>
</html>'''

    final_html = dom_part + final_script + closing_html

    with open('web/index.html', 'w', encoding='utf-8') as f:
        f.write(final_html)

    print("Rebuilt web/index.html cleanly!")

if __name__ == '__main__':
    rebuild()
