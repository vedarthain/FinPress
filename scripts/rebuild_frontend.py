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
    html, body {
      width: 100vw;
      height: 100vh;
      height: 100dvh;
      margin: 0;
      padding: 0;
      overflow: hidden;
      touch-action: manipulation;
      -webkit-text-size-adjust: 100%;
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
    #app-header {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      height: 48px;
      z-index: 50;
    }
    #app-main {
      position: fixed;
      top: 48px;
      bottom: 0;
      left: 0;
      right: 0;
      padding: 8px;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      background-color: #F1F5F9;
    }
    .dark #app-main {
      background-color: #070B14;
    }

    /* Main Workspace Grid (Views Container + Permanent 3rd Column Sidebar) */
    #workspace-grid {
      width: 100%;
      height: 100%;
      display: grid !important;
      grid-template-columns: minmax(0, 1fr) 260px !important;
      grid-template-rows: 100% !important;
      gap: 8px !important;
      overflow: hidden !important;
      min-height: 0 !important;
      flex: 1 1 0% !important;
    }
    @media (min-width: 1280px) {
      #workspace-grid {
        grid-template-columns: minmax(0, 1fr) 280px !important;
      }
    }
    @media (min-width: 1536px) {
      #workspace-grid {
        grid-template-columns: minmax(0, 1fr) 300px !important;
      }
    }

    #workspace-views {
      width: 100%;
      height: 100%;
      min-width: 0 !important;
      overflow: hidden !important;
      display: flex !important;
      flex-direction: column !important;
    }

    #view-feed:not(.hidden) {
      width: 100%;
      height: 100%;
      display: grid !important;
      grid-template-columns: 320px minmax(0, 1fr) !important;
      grid-template-rows: 100% !important;
      gap: 8px !important;
      overflow: hidden !important;
    }
    @media (min-width: 1280px) {
      #view-feed:not(.hidden) {
        grid-template-columns: 350px minmax(0, 1fr) !important;
      }
    }
    @media (min-width: 1536px) {
      #view-feed:not(.hidden) {
        grid-template-columns: 380px minmax(0, 1fr) !important;
      }
    }

    #view-ipo:not(.hidden) {
      width: 100%;
      height: 100%;
      display: flex !important;
      flex-direction: column !important;
      gap: 8px !important;
      overflow: hidden !important;
    }

    #view-matrix:not(.hidden) {
      width: 100%;
      height: 100%;
      display: flex !important;
      flex-direction: column !important;
      gap: 8px !important;
      overflow: hidden !important;
    }

    #col-news-wire {
      height: 100% !important;
      display: flex !important;
      flex-direction: column !important;
      overflow: hidden !important;
    }
    #feed-list-container {
      flex: 1 1 0% !important;
      min-height: 0 !important;
      overflow-y: auto !important;
    }
    #feed-pagination {
      flex-shrink: 0 !important;
      margin-top: auto !important;
    }
    #feed-detail-wrapper {
      height: 100% !important;
      display: flex !important;
      flex-direction: column !important;
      overflow-y: auto !important;
    }
    #view-feed-aside {
      height: 100% !important;
      display: flex !important;
      flex-direction: column !important;
      overflow-y: auto !important;
      min-width: 0 !important;
      flex-shrink: 0 !important;
    }
  </style>
</head>'''
    dom_part = re.sub(head_pattern, clean_head, dom_part, flags=re.DOTALL)

    # 2. Clean body tag
    dom_part = re.sub(
        r'<body[^>]*>',
        '<body class="w-full h-full overflow-hidden bg-[#F1F5F9] text-slate-900 dark:bg-[#070B14] dark:text-slate-100 transition-colors duration-150 m-0 p-0 select-none">',
        dom_part
    )

    # Remove outer extra wrapper div if present
    dom_part = dom_part.replace('<div class="h-screen max-h-screen flex flex-col overflow-hidden w-full">', '')
    if '</div>\n\n  <!-- ================= STORY FULL DETAILS MODAL' in dom_part:
        dom_part = dom_part.replace('</div>\n\n  <!-- ================= STORY FULL DETAILS MODAL', '<!-- ================= STORY FULL DETAILS MODAL')

    # 3. Clean header tag
    dom_part = re.sub(
        r'<header class="[^"]*">',
        '<header id="app-header" class="bg-[#070B14] border-b border-slate-800 text-slate-100 shadow-lg px-4 sm:px-6 py-2 flex items-center justify-between gap-4 overflow-x-auto whitespace-nowrap text-[13px] font-mono">',
        dom_part
    )
    dom_part = dom_part.replace(
        'onclick="onCategorySelect(\'ALL\')" title="Reset to All Stories"',
        'onclick="onCategorySelect(\'ANCHOR\')" title="Reset to News (Front Page)"'
    )

    # Add IPO Hub toggle button to header if missing
    if 'id="top-ipo-hub-btn"' not in dom_part:
        ipo_btn_html = '''        <!-- IPO Hub Toggle Button -->
        <button onclick="switchView(currentView === 'ipo' ? 'feed' : 'ipo')" id="top-ipo-hub-btn" class="px-3 py-1 rounded-lg bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white font-mono text-[12px] font-bold flex items-center gap-1.5 shadow-md transition-transform active:scale-95 cursor-pointer" title="Open Business Standard style IPO Tracker & Listed Performance">
          <span>🚀</span> <span>IPO Hub</span>
        </button>'''
        dom_part = dom_part.replace(
            '<button onclick="triggerGitHubPipeline()"',
            f'{ipo_btn_html}\n\n        <button onclick="triggerGitHubPipeline()"'
        )

    # 4. Extract Aside and Clean Workspace Structure
    aside_start = dom_part.find('<aside id="view-feed-aside"')
    aside_end = dom_part.find('</aside>', aside_start) + len('</aside>')
    clean_aside = '''        <!-- COLUMN 3: RIGHT HAND SIDE PANEL (TREE DESKS & SECTORS) - PERMANENT SIDEBAR -->
        <aside id="view-feed-aside" class="w-full rounded-lg bg-white dark:bg-[#0E1322] border border-slate-200 dark:border-slate-800 p-2.5 shadow-xs">
          <!-- Tree Container (Renders 1. Categories Card, 2. Sectors Card, 3. Clustered Stocks Card) -->
          <div id="tree-sidebar-container" class="flex flex-col gap-1.5 font-sans w-full">
            <!-- Dynamically populated -->
          </div>
        </aside>'''

    # Remove aside from inside view-feed
    dom_part = dom_part[:aside_start] + dom_part[aside_end:]

    # Clean main tag
    dom_part = re.sub(
        r'<main class="[^"]*">',
        '<main id="app-main">',
        dom_part
    )

    # Clean view-feed grid
    dom_part = re.sub(
        r'<section id="view-feed" class="[^"]*">',
        '<section id="view-feed">',
        dom_part
    )

    # Clean Column 1 (Left News Wire)
    dom_part = re.sub(
        r'<!-- COLUMN 1:[^\n]*\n\s*<div class="[^"]*">',
        '<!-- COLUMN 1: HIGH-DENSITY TERMINAL NEWS WIRE -->\n        <div id="col-news-wire" class="rounded-lg bg-white dark:bg-[#0E1322] border border-slate-200 dark:border-slate-800 shadow-xs">',
        dom_part
    )

    # Clean Column 2 (Middle Reading Pane)
    dom_part = re.sub(
        r'<div id="feed-detail-wrapper" class="[^"]*">',
        '<div id="feed-detail-wrapper" class="w-full rounded-lg bg-white dark:bg-[#0E1322] border border-slate-200 dark:border-slate-800 p-4 shadow-xs">',
        dom_part
    )

    # Add BS-style IPO Hub section
    view_ipo_html = '''      <!-- ================= VIEW 2: BUSINESS STANDARD STYLE IPO HUB ================= -->
      <section id="view-ipo" class="hidden">
        
        <!-- Top Summary Cards Ribbon -->
        <div class="grid grid-cols-2 sm:grid-cols-5 gap-2 shrink-0">
          <div class="bg-white dark:bg-[#0E1322] border border-slate-200 dark:border-slate-800 p-2.5 rounded-xl shadow-2xs flex flex-col">
            <span class="text-[11px] font-mono text-slate-500 dark:text-slate-400 font-bold uppercase">Total Tracked</span>
            <div class="flex items-baseline gap-1.5 mt-0.5">
              <span id="ipo-kpi-total" class="text-[20px] font-mono font-black text-slate-900 dark:text-white">0</span>
              <span class="text-[10.5px] font-mono text-indigo-600 dark:text-indigo-400 font-semibold">Issues</span>
            </div>
          </div>
          <div class="bg-white dark:bg-[#0E1322] border border-slate-200 dark:border-slate-800 p-2.5 rounded-xl shadow-2xs flex flex-col">
            <span class="text-[11px] font-mono text-slate-500 dark:text-slate-400 font-bold uppercase">Active Bidding</span>
            <div class="flex items-baseline gap-1.5 mt-0.5">
              <span id="ipo-kpi-bidding" class="text-[20px] font-mono font-black text-emerald-600 dark:text-emerald-400">0</span>
              <span class="text-[10.5px] font-mono text-emerald-600 dark:text-emerald-400 font-semibold">Live Now</span>
            </div>
          </div>
          <div class="bg-white dark:bg-[#0E1322] border border-slate-200 dark:border-slate-800 p-2.5 rounded-xl shadow-2xs flex flex-col">
            <span class="text-[11px] font-mono text-slate-500 dark:text-slate-400 font-bold uppercase">Upcoming DRHPs</span>
            <div class="flex items-baseline gap-1.5 mt-0.5">
              <span id="ipo-kpi-drhp" class="text-[20px] font-mono font-black text-amber-600 dark:text-amber-400">0</span>
              <span class="text-[10.5px] font-mono text-amber-600 dark:text-amber-400 font-semibold">In Pipeline</span>
            </div>
          </div>
          <div class="bg-white dark:bg-[#0E1322] border border-slate-200 dark:border-slate-800 p-2.5 rounded-xl shadow-2xs flex flex-col">
            <span class="text-[11px] font-mono text-slate-500 dark:text-slate-400 font-bold uppercase">Avg Listing Gain</span>
            <div class="flex items-baseline gap-1.5 mt-0.5">
              <span id="ipo-kpi-gain" class="text-[20px] font-mono font-black text-indigo-600 dark:text-indigo-400">+38.5%</span>
              <span class="text-[10.5px] font-mono text-slate-400">Day 1</span>
            </div>
          </div>
          <div class="bg-white dark:bg-[#0E1322] border border-slate-200 dark:border-slate-800 p-2.5 rounded-xl shadow-2xs flex flex-col col-span-2 sm:col-span-1">
            <span class="text-[11px] font-mono text-slate-500 dark:text-slate-400 font-bold uppercase">Capital Mobilised</span>
            <div class="flex items-baseline gap-1.5 mt-0.5">
              <span id="ipo-kpi-capital" class="text-[20px] font-mono font-black text-slate-900 dark:text-white">₹14,500</span>
              <span class="text-[10.5px] font-mono text-slate-400">Cr (FY26)</span>
            </div>
          </div>
        </div>

        <!-- Main IPO Table Card (100% Full Height) -->
        <div class="rounded-xl bg-white dark:bg-[#0E1322] border border-slate-200 dark:border-slate-800 shadow-xs overflow-hidden flex-1 min-h-0 flex flex-col">
          
          <!-- Master Hub Header & Controls -->
          <div class="px-4 py-3 border-b border-slate-200 dark:border-slate-800 bg-slate-50/90 dark:bg-[#11172A]/90 flex items-center justify-between flex-wrap gap-3 shrink-0">
            
            <!-- Left: Dual Mode Selector (IPO Tracker vs Already Listed) -->
            <div class="flex items-center gap-3">
              <div class="flex items-center bg-slate-200/90 dark:bg-[#151D33] p-1 rounded-xl border border-slate-300 dark:border-slate-700 text-[12px] font-mono font-bold shadow-2xs">
                <button id="ipo-mode-tracker-btn" onclick="setIpoViewMode('tracker')" class="px-3 py-1.5 rounded-lg bg-[#1C1917] text-white dark:bg-indigo-600 dark:text-white shadow-xs transition-all flex items-center gap-1.5 cursor-pointer">
                  <span>🚀</span> <span>IPO Tracker</span>
                </button>
                <button id="ipo-mode-listed-btn" onclick="setIpoViewMode('listed')" class="px-3 py-1.5 rounded-lg text-slate-700 dark:text-slate-300 hover:text-black dark:hover:text-white hover:bg-white/60 dark:hover:bg-slate-800 transition-all flex items-center gap-1.5 cursor-pointer">
                  <span>📈</span> <span>Already Listed</span>
                </button>
              </div>

              <!-- Quick Sub-Category Filters -->
              <div id="ipo-subfilter-container" class="flex items-center gap-1.5 text-[11.5px] font-mono font-semibold">
                <button onclick="setIpoFilterCategory('ALL')" id="ipo-filter-all" class="px-2.5 py-1 rounded-md bg-slate-900 text-white dark:bg-indigo-600 dark:text-white font-bold shadow-2xs">All Issues</button>
                <button onclick="setIpoFilterCategory('MAINBOARD')" id="ipo-filter-mb" class="px-2.5 py-1 rounded-md text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800">Mainboard</button>
                <button onclick="setIpoFilterCategory('SME')" id="ipo-filter-sme" class="px-2.5 py-1 rounded-md text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800">SME / Emerge</button>
              </div>
            </div>

            <!-- Right: Search + Count -->
            <div class="flex items-center gap-3">
              <div class="relative w-48 sm:w-64">
                <input type="text" id="ipo-table-search" oninput="onIpoSearchInput(this.value)" placeholder="Search company or sector..." class="w-full text-[12px] pl-7 pr-6 py-1.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:border-indigo-500 font-mono shadow-2xs"/>
                <span class="absolute left-2 top-2 text-slate-400 text-[11px]">🔍</span>
              </div>
              <span class="text-[12px] font-mono text-slate-500 dark:text-slate-400 font-bold shrink-0">
                <b id="ipo-table-visible-count" class="text-indigo-600 dark:text-indigo-400">0</b> Records
              </span>
            </div>

          </div>

          <!-- TAB 1: IPO TRACKER TABLE CONTAINER -->
          <div id="ipo-tracker-table-wrap" class="flex-1 min-h-0 overflow-auto">
            <table class="w-full text-left border-collapse text-[13.5px]">
              <thead class="sticky top-0 z-10 bg-slate-100 dark:bg-[#141A2E] shadow-2xs border-b border-slate-200 dark:border-slate-800 font-mono text-[11px] uppercase tracking-wider text-slate-600 dark:text-slate-400 font-bold">
                <tr>
                  <th class="py-2.5 px-3 w-12 text-center">#</th>
                  <th class="py-2.5 px-3 min-w-[240px]">Company & Exchange</th>
                  <th class="py-2.5 px-3 min-w-[130px]">Issue Dates</th>
                  <th class="py-2.5 px-3 min-w-[110px]">Price Band</th>
                  <th class="py-2.5 px-3 min-w-[110px]">Issue Size</th>
                  <th class="py-2.5 px-3 min-w-[100px]">Lot Size</th>
                  <th class="py-2.5 px-3 min-w-[180px]">Subscription Demand</th>
                  <th class="py-2.5 px-3 min-w-[130px]">Status</th>
                  <th class="py-2.5 px-3 min-w-[100px] text-center">Action</th>
                </tr>
              </thead>
              <tbody id="ipo-table-body" class="divide-y divide-slate-100 dark:divide-slate-800/80 font-sans">
                <!-- Populated dynamically -->
              </tbody>
            </table>
          </div>

          <!-- TAB 2: ALREADY LISTED IPO PERFORMANCE TABLE CONTAINER -->
          <div id="ipo-listed-table-wrap" class="hidden flex-1 min-h-0 overflow-auto">
            <table class="w-full text-left border-collapse text-[13.5px]">
              <thead class="sticky top-0 z-10 bg-slate-100 dark:bg-[#141A2E] shadow-2xs border-b border-slate-200 dark:border-slate-800 font-mono text-[11px] uppercase tracking-wider text-slate-600 dark:text-slate-400 font-bold">
                <tr>
                  <th class="py-2.5 px-3 w-12 text-center">#</th>
                  <th class="py-2.5 px-3 min-w-[220px]">Company & Ticker</th>
                  <th class="py-2.5 px-3 min-w-[120px]">Listing Date</th>
                  <th class="py-2.5 px-3 min-w-[110px]">Issue Price</th>
                  <th class="py-2.5 px-3 min-w-[110px]">Listing Price</th>
                  <th class="py-2.5 px-3 min-w-[140px]">Listing Day Gain</th>
                  <th class="py-2.5 px-3 min-w-[110px]">Current Price (CMP)</th>
                  <th class="py-2.5 px-3 min-w-[140px]">Return Since IPO</th>
                  <th class="py-2.5 px-3 min-w-[120px]">Verdict</th>
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

    # Update renderActiveStoryDetail in clean_script (Clean layout without cutout)
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

    # Update sidebar items to start with News (Front Page) and remove All Stories
    clean_script = clean_script.replace(
        'const coreNewsItems = [\n        { id: "ALL", label: "⚡ All Stories", count: stories.length },\n        { id: "ANCHOR", label: "📰 Front Page", count: anchorCount },',
        'const coreNewsItems = [\n        { id: "ANCHOR", label: "📰 News (Front Page)", count: anchorCount },'
    )
    clean_script = clean_script.replace(
        '<option value="ALL">⚡ All Stories (${stories.length})</option>',
        '<option value="ANCHOR">📰 News (Front Page) (${stories.filter(s => s.isFrontPage).length})</option>'
    )

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
