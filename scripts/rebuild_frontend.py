import re
import subprocess

def rebuild():
    # Load original base from git HEAD
    git_html = subprocess.check_output(['git', 'show', 'HEAD:web/index.html']).decode('utf-8')

    # Extract DOM part
    parts = git_html.split('<!-- ================= CLIENT JAVASCRIPT ================= -->')
    dom_part = parts[0]
    after_dom = parts[1]
    
    # Clean <head> in dom_part
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
      height: 100%;
      height: 100dvh;
      margin: 0;
      padding: 0;
      overflow: hidden;
      touch-action: manipulation;
      -webkit-text-size-adjust: 100%;
    }
    body { font-family: 'DM Sans', 'Plus Jakarta Sans', system-ui, -apple-system, BlinkMacSystemFont, sans-serif; font-size: 13px; font-weight: 400; color: #090D16; -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; text-rendering: optimizeLegibility; }
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
</head>'''
    dom_part = re.sub(head_pattern, clean_head, dom_part, flags=re.DOTALL)

    # Clean body and layout containers for 100% height to bottom
    dom_part = dom_part.replace(
        '<body class="h-screen overflow-hidden bg-[#F1F5F9] text-slate-900 dark:bg-[#070B14] dark:text-slate-100 transition-colors duration-150 flex flex-col">\n  <div class="h-screen max-h-screen flex flex-col overflow-hidden w-full">',
        '<body class="h-screen h-[100dvh] max-h-screen overflow-hidden bg-[#F1F5F9] text-slate-900 dark:bg-[#070B14] dark:text-slate-100 transition-colors duration-150 flex flex-col m-0 p-0 w-full">'
    )

    # Adjust main container to zero wasted bottom margin
    dom_part = re.sub(
        r'<main class="[^"]*">',
        '<main class="w-full px-2 pt-1 pb-1 flex-1 flex flex-col gap-1 min-h-0 overflow-hidden">',
        dom_part
    )

    # Ensure view-feed has 3 side-by-side columns stretching full height
    dom_part = re.sub(
        r'<section id="view-feed" class="[^"]*">',
        '<section id="view-feed" class="grid grid-cols-[320px_minmax(0,1fr)_260px] xl:grid-cols-[350px_minmax(0,1fr)_275px] 2xl:grid-cols-[380px_minmax(0,1fr)_290px] gap-2 items-stretch w-full flex-1 min-h-0 h-full overflow-hidden">',
        dom_part
    )

    # MIDDLE COLUMN (FEED DETAIL WRAPPER): NO SCROLLING, UN-SCROLLABLE FULL-VIEW PANEL
    dom_part = re.sub(
        r'<div id="feed-detail-wrapper" class="[^"]*">',
        '<div id="feed-detail-wrapper" class="w-full rounded-lg bg-white dark:bg-[#0E1322] border border-slate-200 dark:border-slate-800 p-2.5 sm:p-3 shadow-xs flex flex-col h-full min-h-0 overflow-hidden">',
        dom_part
    )

    # Ensure feed-detail-container fills full height without scroll
    dom_part = re.sub(
        r'<div id="feed-detail-container" class="[^"]*">',
        '<div id="feed-detail-container" class="w-full h-full flex flex-col justify-between overflow-hidden">',
        dom_part
    )

    # Wrap column 3 in matching full-height rounded card
    dom_part = re.sub(
        r'<aside id="view-feed-aside" class="[^"]*">',
        '<aside id="view-feed-aside" class="w-full rounded-lg bg-white dark:bg-[#0E1322] border border-slate-200 dark:border-slate-800 p-2 shadow-xs flex flex-col h-full min-h-0 overflow-y-auto shrink-0">',
        dom_part
    )

    # Remove extra trailing </div> if inner div wrapper was removed
    if '</div>\n\n  <!-- ================= STORY FULL DETAILS MODAL' in dom_part:
        dom_part = dom_part.replace('</div>\n\n  <!-- ================= STORY FULL DETAILS MODAL', '<!-- ================= STORY FULL DETAILS MODAL')

    # Base script extraction from git
    script_part = after_dom.split('</script>')[0].replace('<script>', '', 1).strip()
    
    # Slice exactly up to the end of triggerGitHubPipeline
    init_pos = script_part.find('initTheme();')
    base_script = script_part[:init_pos].strip()

    # Top global variables
    top_declarations = '''    let rawReport = null;
    let stories = [];
    let ipoList = [];
    let currentView = "feed";
    let selectedFeedCategory = "ALL";
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
    ];'''

    # Replace old declarations with top_declarations
    allowed_sec_idx = base_script.find('const allowedSections = [')
    base_script = top_declarations + '\n\n    ' + base_script[allowed_sec_idx:]

    # Upgrade renderActiveStoryDetail in base_script to fit seamlessly with NO scrolling in the middle column
    new_render_detail = r'''
    function openStoryCutoutModal(storyId) {
      const s = (stories || []).find(st => st.id === storyId) || stories[0];
      if (!s) return;
      if (s.cutout_url) {
        openImageModal(s.cutout_url, s.headline);
      } else {
        showStoryModal(s);
      }
    }

    function renderActiveStoryDetail(story, queryTokens = []) {
      const container = document.getElementById("feed-detail-container");
      if (!story) return;

      const isBullish = story.sentiment === "BULLISH";
      const isBearish = story.sentiment === "BEARISH";
      
      const sentBadge = isBullish 
        ? `<span class="px-2 py-0.5 rounded text-[10.5px] font-mono font-bold bg-emerald-100 text-emerald-950 border border-emerald-300 dark:bg-emerald-950/70 dark:text-emerald-200">🟢 BULLISH</span>`
        : isBearish 
        ? `<span class="px-2 py-0.5 rounded text-[10.5px] font-mono font-bold bg-rose-100 text-rose-950 border border-rose-300 dark:bg-rose-950/70 dark:text-rose-200">🔴 BEARISH</span>`
        : `<span class="px-2 py-0.5 rounded text-[10.5px] font-mono font-bold bg-slate-200 text-slate-900 border border-slate-300 dark:bg-slate-800 dark:text-slate-200">⚪ NEUTRAL</span>`;

      const tickerBadges = (story.tickers || []).slice(0, 3).map(t => `<span class="px-2 py-0.5 text-[10.5px] font-mono font-bold rounded bg-indigo-50 text-indigo-900 border border-indigo-200 dark:bg-indigo-950/60 dark:text-indigo-200">${t}</span>`).join('');

      const briefSentences = (story.brief_details || "").split(/(?<=[.?!])\s+/).filter(Boolean).slice(0, 3);
      const bullets = (story.bullet_points || story.detailed_points || []).slice(0, 4);

      container.innerHTML = `
        <!-- TOP ROW: METADATA & BADGES -->
        <div class="flex items-center justify-between gap-1.5 pb-1 border-b border-slate-200 dark:border-slate-800 shrink-0 text-[11.5px] font-mono">
          <div class="flex items-center gap-1.5 flex-wrap">
            <span class="font-semibold px-2 py-0.5 rounded bg-slate-200 text-slate-900 dark:bg-slate-800 dark:text-white">${story.category}</span>
            ${story.isFrontPage ? `<span class="font-semibold px-2 py-0.5 rounded bg-amber-200 text-amber-950 dark:bg-amber-950/80 dark:text-amber-200">📰 PAGE 1 ANCHOR</span>` : ''}
            <span class="font-semibold px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800/80 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700">${formatPageSource(story.page_numbers)}</span>
          </div>
          <div class="flex items-center gap-1.5">
            <button id="feed-open-sidebar-btn" onclick="toggleSidebar()" class="hidden font-bold px-2 py-0.5 rounded border border-[#DFC0A5] dark:border-slate-700 bg-[#FBE8D8] dark:bg-[#1E1B4B] text-[#1C1917] dark:text-[#E0E7FF] hover:bg-[#F3DECC] shadow-2xs items-center gap-1 cursor-pointer transition-all" title="Open 3rd Column Filters & Desks"><span>☰</span> <span>Filters</span></button>
            ${sentBadge}
            <button onclick="copyStoryById(${story.id})" class="text-slate-800 hover:text-slate-950 dark:text-slate-200 dark:hover:text-white font-mono flex items-center gap-1 font-semibold px-2 py-0.5 rounded border border-slate-300 dark:border-slate-700 bg-white dark:bg-[#141A2E] shadow-2xs cursor-pointer" title="Copy story summary">
              📋 Copy
            </button>
          </div>
        </div>

        <!-- HEADLINE -->
        <h1 class="text-[16px] sm:text-[17.5px] font-bold text-[#05080F] dark:text-white leading-snug tracking-tight my-1.5 shrink-0 flex items-center flex-wrap gap-1.5">
          <span>${highlightSearchTokens(highlightNumbers(story.headline), queryTokens)}</span>
          ${(story.tickers && story.tickers.length > 0) ? tickerBadges : ''}
        </h1>

        <!-- 2-COLUMN SIDE-BY-SIDE GRID (FLEX-1 TO FIT VIEWPORT WITH ZERO SCROLLING) -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-2.5 items-stretch flex-1 min-h-0 overflow-hidden my-1">
          
          <!-- LEFT COLUMN (lg:col-span-6): EXECUTIVE GIST & TRADER CATALYST -->
          <div class="lg:col-span-6 flex flex-col gap-2 h-full min-h-0 justify-between">
            
            <!-- ⚡ SECTION 1: EXECUTIVE GIST -->
            <div class="rounded-lg border border-indigo-200 dark:border-indigo-800/80 bg-indigo-50/50 dark:bg-[#13182E] p-2.5 shadow-2xs flex flex-col flex-1 min-h-0">
              <div class="flex items-center justify-between border-b border-indigo-200/80 dark:border-indigo-900/60 pb-1 mb-1.5">
                <span class="text-[11.5px] font-mono font-extrabold uppercase tracking-wider text-indigo-950 dark:text-indigo-200 flex items-center gap-1">
                  <span>⚡</span> <span>1. Executive Gist</span>
                </span>
                <span class="text-[10px] font-mono font-bold px-1.5 py-0.2 rounded bg-indigo-200/80 text-indigo-950 dark:bg-indigo-900/80 dark:text-indigo-200">Core Points</span>
              </div>
              <div class="space-y-1.5 flex-1 min-h-0 overflow-y-auto">
                ${briefSentences.map(sent => `
                  <div class="flex items-start gap-1.5 bg-white/95 dark:bg-[#0E1322] p-2 rounded border border-indigo-100 dark:border-slate-800 text-[13px] sm:text-[13.5px] text-[#090D16] dark:text-[#F8FAFC] leading-snug font-normal shadow-2xs font-sans tracking-tight">
                    <span class="text-indigo-600 dark:text-indigo-400 font-bold select-none text-xs mt-0.5">▸</span>
                    <span class="leading-snug">${highlightSearchTokens(highlightNumbers(sent), queryTokens)}</span>
                  </div>
                `).join('')}
              </div>
            </div>

            <!-- 💡 SECTION 2: TRADER CATALYST & IMPACT ANALYSIS -->
            <div class="p-2.5 rounded-lg border ${isBullish ? 'border-emerald-400 bg-emerald-50/60 dark:bg-[#064E3B]/20 dark:border-emerald-700' : isBearish ? 'border-rose-400 bg-rose-50/60 dark:bg-[#881337]/20 dark:border-rose-700' : 'border-slate-300 bg-slate-50 dark:bg-slate-900/40 dark:border-slate-700'} shadow-2xs flex flex-col shrink-0">
              <div class="flex items-center justify-between border-b ${isBullish ? 'border-emerald-200 dark:border-emerald-900/60' : isBearish ? 'border-rose-200 dark:border-rose-900/60' : 'border-slate-200 dark:border-slate-800'} pb-1 mb-1">
                <span class="text-[11.5px] font-mono font-extrabold uppercase tracking-wider ${isBullish ? 'text-emerald-950 dark:text-emerald-300' : isBearish ? 'text-rose-950 dark:text-rose-300' : 'text-slate-900 dark:text-slate-200'} flex items-center gap-1">
                  <span>💡</span> <span>2. Catalyst & Impact</span>
                </span>
                <span class="text-[10px] font-mono font-bold uppercase px-1.5 py-0.2 rounded ${isBullish ? 'bg-emerald-200 text-emerald-950 dark:bg-emerald-900 dark:text-emerald-200' : isBearish ? 'bg-rose-200 text-rose-950 dark:bg-rose-900 dark:text-rose-200' : 'bg-slate-200 text-slate-900 dark:bg-slate-800 dark:text-slate-200'}">${story.sentiment}</span>
              </div>
              <div class="bg-white/95 dark:bg-[#0E1322] p-2 rounded border ${isBullish ? 'border-emerald-200/60 dark:border-slate-800' : isBearish ? 'border-rose-200/60 dark:border-slate-800' : 'border-slate-200 dark:border-slate-800'} text-[13px] sm:text-[13.5px] text-[#090D16] dark:text-[#F8FAFC] leading-snug font-normal shadow-2xs font-sans tracking-tight">
                ${highlightSearchTokens(highlightNumbers(story.sentimentReasoning || story.catalyst || ""), queryTokens)}
              </div>
            </div>

          </div>

          <!-- RIGHT COLUMN (lg:col-span-6): KEY ANALYST DATA POINTS -->
          <div class="lg:col-span-6 flex flex-col h-full min-h-0">
            
            <!-- 📌 SECTION 3: KEY ANALYST DATA POINTS -->
            <div class="rounded-lg border border-[#C9B7A5] dark:border-[#524434] bg-[#FDFBF7] dark:bg-[#191512] p-2.5 shadow-2xs flex flex-col h-full min-h-0">
              <div class="flex items-center justify-between border-b border-[#E8DCCE] dark:border-[#382E25] pb-1 mb-1.5">
                <span class="text-[11.5px] font-mono font-extrabold uppercase tracking-wider text-[#2E1F14] dark:text-[#F3ECE4] flex items-center gap-1">
                  <span>📌</span> <span>3. Key Analyst Data Points</span>
                </span>
                <span class="text-[10px] font-mono font-bold px-1.5 py-0.2 rounded bg-[#EFE5D9] text-[#291B10] dark:bg-[#32261C] dark:text-[#E8DCCF] border border-[#CCAFA0]/50">Metrics & Facts</span>
              </div>
              <ul class="space-y-1.5 flex-1 min-h-0 overflow-y-auto">
                ${bullets.map(bp => `
                  <li class="flex items-start gap-1.5 text-[13px] sm:text-[13.5px] text-[#090D16] dark:text-[#F8FAFC] leading-snug bg-white/95 dark:bg-[#0E1322] p-2 rounded border border-[#EBE2D8] dark:border-slate-800 shadow-2xs font-normal font-sans tracking-tight">
                    <span class="text-[#8C5E3C] dark:text-[#CBB09C] font-bold select-none text-xs mt-0.5">›</span>
                    <span class="leading-snug">${highlightSearchTokens(highlightNumbers(bp), queryTokens)}</span>
                  </li>
                `).join('')}
              </ul>
            </div>

          </div>

        </div>

        <!-- 📰 SECTION 4: SLEEK COMPACT NEWSPAPER ARTICLE CUTOUT BAR (CLICK TO ZOOM / VIEW MODAL) -->
        <div class="rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50/90 dark:bg-[#11172A] p-2 flex items-center justify-between shrink-0 my-1 shadow-2xs">
          <div class="flex items-center gap-2">
            <span class="text-amber-600 dark:text-amber-400 text-sm">✂️</span>
            <span class="text-[12px] font-mono font-bold text-slate-800 dark:text-slate-200">
              4. Newspaper Cutout: <span class="font-normal text-slate-500 dark:text-slate-400">${story.cutout_url ? 'Authentic Clipping Available' : 'Financial Desk Print Box'}</span>
            </span>
          </div>
          <div class="flex items-center gap-1.5">
            <button onclick="openStoryCutoutModal(${story.id})" class="text-[11px] font-mono font-bold px-2.5 py-0.5 rounded bg-indigo-50 dark:bg-indigo-950/70 text-indigo-700 dark:text-indigo-300 hover:bg-indigo-100 border border-indigo-200 dark:border-indigo-800 shadow-2xs cursor-pointer flex items-center gap-1">
              <span>🔍</span> <span>View Full Cutout ↗</span>
            </button>
          </div>
        </div>

        <!-- 🏁 END OF STORY FOOTER BAR -->
        <div class="pt-1.5 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between text-[11px] font-mono text-slate-400 shrink-0 mt-auto">
          <span class="flex items-center gap-1 font-bold text-slate-600 dark:text-slate-300">
            <span>🏁</span> <span>Story #${story.id} (${formatPageSource(story.page_numbers)})</span>
          </span>
          <div class="flex items-center gap-1.5">
            <button onclick="navigateStory(-1)" class="px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 font-bold border border-slate-300 dark:border-slate-700 shadow-2xs text-[10.5px]">◀ Prev (K)</button>
            <button onclick="navigateStory(1)" class="px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 font-bold border border-slate-300 dark:border-slate-700 shadow-2xs text-[10.5px]">Next (J) ▶</button>
          </div>
        </div>
      `;
    }
'''

    # Replace renderActiveStoryDetail in base_script using lambda to avoid escape issue
    detail_regex = r'function renderActiveStoryDetail\(story, queryTokens = \[\]\) \{.*?^\s*\}\s*$'
    base_script = re.sub(detail_regex, lambda m: new_render_detail, base_script, flags=re.DOTALL | re.MULTILINE)

    ipo_functions_clean = '''
    // ================= IPO HUB TAB & SEARCH FUNCTIONS =================
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
      ipoSearchQuery = (val || '').trim().toLowerCase();
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
        list = list.filter(i => (i.exchange || '').includes("Mainboard") || !(i.exchange || '').includes("SME"));
      } else if (activeIpoCategory === 'SME') {
        list = list.filter(i => (i.exchange || '').includes("SME") || (i.exchange || '').includes("Emerge"));
      }

      if (ipoSearchQuery) {
        list = list.filter(i => {
          const full = ((i.company || '') + " " + (i.exchange || '') + " " + (i.stage || '') + " " + (i.details || '')).toLowerCase();
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
            <button onclick="openStoryModalById(${item.storyId || item.id || 1})" class="px-2.5 py-1 rounded bg-slate-100 dark:bg-slate-800 hover:bg-indigo-50 text-indigo-600 dark:text-indigo-400 font-mono text-[11px] font-bold border border-slate-200 dark:border-slate-700">
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

    modal_and_utility_code = '''
    // ================= MODAL & UTILITY FUNCTIONS =================
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

    init_execution_block = '''
    // ================= INITIALIZATION =================
    initTheme();
    initFontSize();
    initBsBookmarklet();
    fetchDates();
    loadData();
'''

    final_script = f'''  <!-- ================= CLIENT JAVASCRIPT ================= -->
  <script>
{base_script}

{ipo_functions_clean}

{modal_and_utility_code}

{init_execution_block}
  </script>'''

    zoom_modal = '''
  <!-- ================= IMAGE CUTOUT ZOOM MODAL ================= -->
  <div id="image-zoom-modal" class="fixed inset-0 z-50 bg-black/85 backdrop-blur-sm hidden items-center justify-center p-4 cursor-pointer" onclick="closeImageModal()">
    <div class="relative max-w-5xl w-full max-h-[95vh] flex flex-col items-center bg-slate-900/90 p-4 rounded-2xl border border-slate-700 shadow-2xl" onclick="event.stopPropagation()">
      <div class="w-full flex items-center justify-between pb-2 border-b border-slate-700 text-slate-100 font-mono text-[13px]">
        <span id="image-zoom-caption" class="font-bold truncate mr-4">Newspaper Article Cutout</span>
        <div class="flex items-center gap-2">
          <button onclick="closeImageModal()" class="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 text-[12px] font-bold">✕ Close</button>
        </div>
      </div>
      <div class="w-full overflow-auto max-h-[85vh] p-2 flex items-center justify-center mt-2">
        <img id="image-zoom-img" src="" alt="Cutout" class="max-w-full max-h-[80vh] object-contain rounded shadow-lg"/>
      </div>
    </div>
  </div>

</body>
</html>'''

    final_html = dom_part + final_script + '\n' + zoom_modal

    with open('web/index.html', 'w', encoding='utf-8') as f:
        f.write(final_html)

    print("Rebuilt web/index.html cleanly with un-scrollable middle column layout!")

if __name__ == '__main__':
    rebuild()
