import re

def apply_updates():
    with open('web/index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Update Top Header: FinPress Brand + Market Pulse on Left, Search/Calendar/Status on Right
    old_header_pattern = r'<!-- ================= 1\. UNIFIED TOP NAVIGATION & CONTROLS RIBBON ================= -->.*?<!-- ================= MAIN THREE-COLUMN WORKSPACE'
    
    new_header = """<!-- ================= 1. UNIFIED TOP NAVIGATION & CONTROLS RIBBON ================= -->
    <header class="sticky top-0 z-50 bg-[#0B0F19] dark:bg-[#070B14] border-b border-slate-800 text-slate-100 shadow-md px-3 py-1.5 flex items-center justify-between gap-3 overflow-x-auto whitespace-nowrap text-[12px] font-mono">
      
      <!-- Left: FinPress Branding & Live Market Pulse -->
      <div class="flex items-center gap-3 shrink-0">
        <div class="flex items-center gap-1.5 shrink-0 cursor-pointer" onclick="onCategorySelect('ALL')" title="Reset to All News">
          <div class="w-6.5 h-6.5 rounded bg-amber-600 flex items-center justify-center shadow-xs border border-amber-500/50">
            <span class="text-white text-[11px] font-extrabold tracking-tight font-mono">FP</span>
          </div>
          <span class="text-[15px] font-extrabold tracking-tight text-white font-mono mr-1">
            Fin<span class="text-amber-400">Press</span>
          </span>
        </div>

        <!-- Live Market Pulse Key Data -->
        <div class="flex items-center gap-3 text-[11.5px] border-l border-slate-800 pl-3">
          <span class="text-slate-300 font-medium">NIFTY <b class="text-emerald-400 font-bold font-mono">24,835 (+0.64%)</b></span>
          <span class="text-slate-300 font-medium">BANK NIFTY <b class="text-emerald-400 font-bold font-mono">54,120 (+0.82%)</b></span>
          <span class="text-slate-300 font-medium">INDIA VIX <b class="text-rose-400 font-bold font-mono">12.85 (-3.2%)</b></span>
          <span class="text-slate-300 font-medium">BRENT <b class="text-amber-300 font-bold font-mono">$74.2/bbl</b></span>
          <span class="text-slate-300 font-medium">USD/INR <b class="text-slate-100 font-bold font-mono">₹83.65</b></span>
        </div>
      </div>

      <!-- Right: Search + Calendar + Status + Total + Font + Theme -->
      <div class="flex items-center gap-2 shrink-0">
        <div class="relative w-36 sm:w-44">
          <input type="text" id="global-search" oninput="onSearchInput()" placeholder="Search stock or news..." class="w-full text-[11.5px] pl-6 pr-5 py-1 rounded-md border border-slate-700 bg-slate-900 text-slate-100 placeholder-slate-400 focus:outline-none focus:border-amber-500 font-mono shadow-2xs"/>
          <span class="absolute left-1.5 top-1.5 text-slate-400 text-[10.5px]">🔍</span>
          <button id="clear-search-btn" onclick="clearSearch()" class="hidden absolute right-1.5 top-1 text-slate-400 hover:text-white text-[11px] font-bold p-0.5">✕</button>
        </div>

        <!-- Historical Calendar & Edition Navigation -->
        <div class="flex items-center gap-0.5 bg-slate-900 p-0.5 rounded-md border border-slate-700/80 font-mono text-[11.5px]">
          <button onclick="navigateDate(-1)" class="px-1.5 py-0.5 rounded hover:bg-slate-800 text-slate-300 hover:text-white font-bold" title="Previous Date (◀)">◀</button>
          <div class="flex items-center gap-1 px-1 py-0.5 bg-black/60 rounded border border-slate-800">
            <span class="text-slate-400 text-[10.5px]">📅</span>
            <input type="date" id="calendar-picker" onchange="onCalendarSelect(this.value)" class="bg-transparent text-slate-100 font-bold font-mono text-[11.5px] focus:outline-none cursor-pointer [color-scheme:dark] max-w-[105px]"/>
          </div>
          <button onclick="navigateDate(1)" class="px-1.5 py-0.5 rounded hover:bg-slate-800 text-slate-300 hover:text-white font-bold" title="Next Date (▶)">▶</button>
        </div>

        <div id="source-health-container" class="flex items-center gap-1 font-mono text-[10.5px]"></div>

        <span id="total-news-counter-badge" class="px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-extrabold font-mono text-[11.5px]">
          🔥 <b id="top-total-count">0</b>
        </span>

        <!-- Font Size Controls -->
        <div class="flex items-center bg-slate-900 p-0.5 rounded-md border border-slate-700 text-[11px] font-mono font-semibold">
          <button onclick="adjustFontSize(-1)" class="px-1.5 py-0.5 rounded text-slate-300 hover:text-white hover:bg-slate-800" title="Decrease Font Size (A-)">A-</button>
          <span id="font-size-label" class="px-1 text-[9.5px] text-slate-400 select-none">100%</span>
          <button onclick="adjustFontSize(1)" class="px-1.5 py-0.5 rounded text-slate-300 hover:text-white hover:bg-slate-800" title="Increase Font Size (A+)">A+</button>
        </div>

        <button onclick="toggleTheme()" class="w-6.5 h-6.5 rounded-md border border-slate-700 bg-slate-900 text-slate-300 hover:text-white flex items-center justify-center text-[11px] shadow-xs" title="Toggle Light/Dark Theme">
          <span id="theme-icon">🌙</span>
        </button>
      </div>

    </header>

    <!-- ================= MAIN THREE-COLUMN WORKSPACE"""

    html = re.sub(old_header_pattern, new_header, html, flags=re.DOTALL)

    # 2. Update Column 3 HTML container for Tree Structure
    old_col3_pattern = r'<!-- COLUMN 3: RIGHT HAND SIDE PANEL.*?-->.*?</aside>'
    new_col3 = """<!-- COLUMN 3: RIGHT HAND SIDE PANEL (TREE VIEW: CATEGORIES [OPEN], SECTORS & STOCKS [COLLAPSED]) -->
        <aside class="flex flex-col gap-2 lg:sticky lg:top-[44px] lg:max-h-[calc(100vh-3.5rem)] lg:overflow-y-auto">
          
          <!-- Tree Container -->
          <div id="tree-sidebar-container" class="flex flex-col gap-2">
            <!-- Dynamically populated collapsible tree structure -->
          </div>

        </aside>"""

    html = re.sub(old_col3_pattern, new_col3, html, flags=re.DOTALL)

    # 3. Update JavaScript tree state and renderCategoriesAndStocksSidebar
    old_sidebar_fn_pattern = r'// ================= RIGHT HAND SIDEBAR: CATEGORIES & STOCKS IN FOCUS =================.*?function setFeedSentiment\(sent\) {'
    
    new_sidebar_fn = """// ================= TREE-VIEW SIDEBAR: CATEGORIES [OPEN], SECTORS & STOCKS [COLLAPSED] =================
    let treeState = {
      categories: true,  // Open by default
      sectors: false,    // Collapsed by default
      stocks: false      // Collapsed by default
    };

    function toggleTreeNode(section) {
      treeState[section] = !treeState[section];
      renderCategoriesAndStocksSidebar();
    }

    function renderCategoriesAndStocksSidebar() {
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

      // Group 1: News Categories (Open by default)
      const coreNewsItems = [
        { id: "ALL", label: "⚡ All News", count: coreStories.length },
        { id: "ANCHOR", label: "📰 Front Page", count: anchorCount },
        { id: "Sector", label: "🏢 Sector News", count: stories.filter(s => s.category === "Sector" && !s.isOpinion).length },
        { id: "Economy", label: "📈 Economy", count: stories.filter(s => s.category === "Economy" && !s.isOpinion).length },
        { id: "Policy", label: "🏛️ Policy & Rules", count: stories.filter(s => s.category === "Policy" && !s.isOpinion).length },
        { id: "Market", label: "📊 Market Pulse", count: stories.filter(s => s.category === "Market" && !s.isOpinion).length },
        { id: "Trade", label: "🚢 Trade & FX", count: stories.filter(s => s.category === "Trade" && !s.isOpinion).length },
        { id: "International News", label: "🌐 International", count: stories.filter(s => s.category === "International News" && !s.isOpinion).length },
        { id: "Others", label: "📑 Features", count: stories.filter(s => s.category === "Others" && !s.isOpinion).length }
      ];

      const deskItems = [
        { id: "IPO_ALL", label: "🚀 IPO Central", count: totalIpos },
        { id: "CORPORATE_ALL", label: "🏢 Corporate Desk", count: corpCount },
        { id: "EVENTS", label: "📢 Corp Events", count: corpEventsCount },
        { id: "APPOINTMENTS", label: "👔 Appointments", count: corpApptsCount },
        { id: "OPINIONS", label: "✍️ Opinions Desk", count: opinionsCount }
      ];

      // --- SECTION 1: CATEGORIES TREE CARD (OPEN BY DEFAULT) ---
      const catCard = document.createElement("div");
      catCard.className = "rounded-lg bg-white dark:bg-[#0E1322] border border-slate-200 dark:border-slate-800 shadow-xs overflow-hidden";
      
      const isCatOpen = treeState.categories;
      catCard.innerHTML = `
        <div class="px-3 py-2 bg-slate-50 dark:bg-slate-900/90 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between cursor-pointer select-none" onclick="toggleTreeNode('categories')">
          <div class="flex items-center gap-1.5 font-mono text-[11.5px] font-bold text-slate-900 dark:text-slate-100">
            <span class="text-amber-600 dark:text-amber-400 text-xs">${isCatOpen ? '▼' : '▶'}</span>
            <span>📁 News Categories</span>
            <span class="px-1.5 py-0.2 rounded text-[10px] bg-slate-200 dark:bg-slate-800 text-slate-600 dark:text-slate-400">${coreNewsItems.length + deskItems.length}</span>
          </div>
          ${selectedFeedCategory !== 'ALL' ? `<button onclick="event.stopPropagation(); onCategorySelect('ALL');" class="text-[10px] font-mono text-amber-600 dark:text-amber-400 font-bold hover:underline">Reset (✕)</button>` : ''}
        </div>
      `;

      if (isCatOpen) {
        const catBody = document.createElement("div");
        catBody.className = "p-2 flex flex-col gap-2 font-mono text-[11px]";

        // Sub-group: Core News Desks
        const coreDiv = document.createElement("div");
        coreDiv.className = "flex flex-col gap-0.5";
        coreDiv.innerHTML = `<span class="text-[10px] font-bold uppercase text-slate-400 dark:text-slate-500 px-1 mb-0.5 tracking-wider">📰 Core Desks</span>`;

        coreNewsItems.forEach(item => {
          const isSelected = selectedFeedCategory === item.id;
          const btn = document.createElement("button");
          btn.className = `w-full text-left px-2 py-1 rounded flex items-center justify-between transition-colors ${isSelected ? 'bg-amber-600 text-white font-bold shadow-xs' : 'text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800/60 font-medium'}`;
          btn.innerHTML = `
            <span class="flex items-center gap-1.5 truncate">
              <span class="text-slate-400 select-none ${isSelected ? 'text-white' : ''}">├─</span>
              <span class="truncate">${item.label}</span>
            </span>
            <span class="px-1.5 py-0.2 rounded text-[10px] ${isSelected ? 'bg-white/25 text-white' : 'bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400'}">${item.count}</span>
          `;
          btn.onclick = () => {
            if (item.id === 'ANCHOR') switchView('anchor');
            else onCategorySelect(isSelected ? 'ALL' : item.id);
          };
          coreDiv.appendChild(btn);
        });
        catBody.appendChild(coreDiv);

        // Sub-group: Specialized Desks
        const deskDiv = document.createElement("div");
        deskDiv.className = "flex flex-col gap-0.5 pt-1.5 border-t border-slate-100 dark:border-slate-800";
        deskDiv.innerHTML = `<span class="text-[10px] font-bold uppercase text-amber-700 dark:text-amber-400 px-1 mb-0.5 tracking-wider">🏛️ Specialized Desks</span>`;

        deskItems.forEach(item => {
          const isSelected = selectedFeedCategory === item.id || (item.id === 'IPO_ALL' && currentView === 'ipo') || (item.id === 'CORPORATE_ALL' && currentView === 'corporate');
          const btn = document.createElement("button");
          btn.className = `w-full text-left px-2 py-1 rounded flex items-center justify-between transition-colors ${isSelected ? 'bg-amber-700 text-white font-bold shadow-xs' : 'text-slate-700 dark:text-slate-300 hover:bg-amber-50/60 dark:hover:bg-amber-950/30 font-medium'}`;
          btn.innerHTML = `
            <span class="flex items-center gap-1.5 truncate">
              <span class="text-slate-400 select-none ${isSelected ? 'text-white' : ''}">├─</span>
              <span class="truncate">${item.label}</span>
            </span>
            <span class="px-1.5 py-0.2 rounded text-[10px] ${isSelected ? 'bg-white/25 text-white' : 'bg-amber-100/70 dark:bg-amber-950/50 text-amber-900 dark:text-amber-300'}">${item.count}</span>
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

      // --- SECTION 2: INDUSTRY SECTORS TREE CARD (COLLAPSED BY DEFAULT) ---
      const secCounts = {};
      stories.forEach(s => {
        (s.sectors || []).forEach(sec => secCounts[sec] = (secCounts[sec] || 0) + 1);
      });
      const sortedSecs = Object.keys(secCounts).sort((a,b) => secCounts[b] - secCounts[a]);

      const secCard = document.createElement("div");
      secCard.className = "rounded-lg bg-white dark:bg-[#0E1322] border border-slate-200 dark:border-slate-800 shadow-xs overflow-hidden";
      
      const isSecOpen = treeState.sectors;
      secCard.innerHTML = `
        <div class="px-3 py-2 bg-slate-50 dark:bg-slate-900/90 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between cursor-pointer select-none" onclick="toggleTreeNode('sectors')">
          <div class="flex items-center gap-1.5 font-mono text-[11.5px] font-bold text-slate-900 dark:text-slate-100">
            <span class="text-indigo-600 dark:text-indigo-400 text-xs">${isSecOpen ? '▼' : '▶'}</span>
            <span>📈 Industry Sectors</span>
            <span class="px-1.5 py-0.2 rounded text-[10px] bg-slate-200 dark:bg-slate-800 text-slate-600 dark:text-slate-400">${sortedSecs.length}</span>
          </div>
          ${activeSectorFilter ? `<button onclick="event.stopPropagation(); activeSectorFilter = null; renderCategoriesAndStocksSidebar(); renderFeedList();" class="text-[10px] font-mono text-indigo-600 dark:text-indigo-400 font-bold hover:underline">Clear (✕)</button>` : ''}
        </div>
      `;

      if (isSecOpen) {
        const secBody = document.createElement("div");
        secBody.className = "p-2 flex flex-col gap-0.5 font-mono text-[11px] max-h-[260px] overflow-y-auto";

        sortedSecs.forEach(sec => {
          const isSelected = activeSectorFilter === sec;
          const btn = document.createElement("button");
          btn.className = `w-full text-left px-2 py-1 rounded flex items-center justify-between transition-colors ${isSelected ? 'bg-indigo-600 text-white font-bold shadow-xs' : 'text-slate-700 dark:text-slate-300 hover:bg-indigo-50/60 dark:hover:bg-indigo-950/30 font-medium'}`;
          btn.innerHTML = `
            <span class="flex items-center gap-1.5 truncate">
              <span class="text-slate-400 select-none ${isSelected ? 'text-white' : ''}">├─</span>
              <span class="truncate">${sec}</span>
            </span>
            <span class="px-1.5 py-0.2 rounded text-[10px] ${isSelected ? 'bg-white/25 text-white' : 'bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400'}">${secCounts[sec]}</span>
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

      // --- SECTION 3: COMPANY STOCKS TREE CARD (COLLAPSED BY DEFAULT) ---
      const stockCounts = {};
      stories.forEach(s => {
        (s.stocks || []).forEach(stk => stockCounts[stk] = (stockCounts[stk] || 0) + 1);
      });
      const sortedStocks = Object.keys(stockCounts).sort((a,b) => stockCounts[b] - stockCounts[a]);

      const stockCard = document.createElement("div");
      stockCard.className = "rounded-lg bg-white dark:bg-[#0E1322] border border-slate-200 dark:border-slate-800 shadow-xs overflow-hidden";
      
      const isStockOpen = treeState.stocks;
      stockCard.innerHTML = `
        <div class="px-3 py-2 bg-slate-50 dark:bg-slate-900/90 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between cursor-pointer select-none" onclick="toggleTreeNode('stocks')">
          <div class="flex items-center gap-1.5 font-mono text-[11.5px] font-bold text-slate-900 dark:text-slate-100">
            <span class="text-amber-600 dark:text-amber-400 text-xs">${isStockOpen ? '▼' : '▶'}</span>
            <span>🏢 Company Stocks</span>
            <span class="px-1.5 py-0.2 rounded text-[10px] bg-slate-200 dark:bg-slate-800 text-slate-600 dark:text-slate-400">${sortedStocks.length}</span>
          </div>
          ${activeStockFilter ? `<button onclick="event.stopPropagation(); activeStockFilter = null; renderCategoriesAndStocksSidebar(); renderFeedList();" class="text-[10px] font-mono text-indigo-600 dark:text-indigo-400 font-bold hover:underline">Clear (✕)</button>` : ''}
        </div>
      `;

      if (isStockOpen) {
        const stockBody = document.createElement("div");
        stockBody.className = "p-2 flex flex-col gap-0.5 font-mono text-[11px] max-h-[260px] overflow-y-auto";

        sortedStocks.forEach(stk => {
          const isSelected = activeStockFilter === stk;
          const btn = document.createElement("button");
          btn.className = `w-full text-left px-2 py-1 rounded flex items-center justify-between transition-colors ${isSelected ? 'bg-amber-600 text-white font-bold shadow-xs' : 'text-slate-700 dark:text-slate-300 hover:bg-amber-50/60 dark:hover:bg-amber-950/30 font-medium'}`;
          btn.innerHTML = `
            <span class="flex items-center gap-1.5 truncate">
              <span class="text-slate-400 select-none ${isSelected ? 'text-white' : ''}">├─</span>
              <span class="truncate">${stk}</span>
            </span>
            <span class="px-1.5 py-0.2 rounded text-[10px] ${isSelected ? 'bg-white/25 text-white' : 'bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400'}">${stockCounts[stk]}</span>
          `;
          btn.onclick = () => {
            activeStockFilter = activeStockFilter === stk ? null : stk;
            selectedStoryIndex = 0;
            currentFeedPage = 1;
            renderCategoriesAndStocksSidebar();
            if (currentLayoutMode === "split") renderFeedList();
            else renderMatrixTable();
          };
          stockBody.appendChild(btn);
        });
        stockCard.appendChild(stockBody);
      }
      container.appendChild(stockCard);
    }

    function clearAllStockAndSectorFilters() {
      activeStockFilter = null;
      activeSectorFilter = null;
      selectedStoryIndex = 0;
      currentFeedPage = 1;
      renderCategoriesAndStocksSidebar();
      if (currentLayoutMode === "split") renderFeedList();
      else renderMatrixTable();
    }

    function clearStockFilter() {
      clearAllStockAndSectorFilters();
    }

    function setFeedSentiment(sent) {"""

    html = re.sub(old_sidebar_fn_pattern, new_sidebar_fn, html, flags=re.DOTALL)

    # 4. Enhance Spacing in Column 2 & Modal (Line spacing, distinct sentence spacing)
    old_detail_pattern = r'<!-- 2-COLUMN SIDE-BY-SIDE GRID: LEFT \(GIST \+ CATALYST\) & RIGHT \(KEY ANALYST DATA POINTS\) -->.*?function highlightNumbers'
    
    new_detail = """<!-- 2-COLUMN SIDE-BY-SIDE GRID: LEFT (GIST + CATALYST) & RIGHT (KEY ANALYST DATA POINTS) -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-3.5 items-start mt-2.5">
          
          <!-- LEFT COLUMN (lg:col-span-6): CORE TRADER TAKEAWAY + CATALYST DIRECTLY BELOW -->
          <div class="lg:col-span-6 flex flex-col gap-3.5">
            
            <!-- ⚡ SECTION 1: EXECUTIVE GIST (CORE TAKEAWAY WITH AIRY LINE SPACING) -->
            <div class="rounded-xl border-2 border-indigo-400/80 dark:border-indigo-700 bg-indigo-50/70 dark:bg-[#151930] p-3.5 shadow-xs flex flex-col gap-2.5">
              <div class="flex items-center justify-between border-b border-indigo-200/90 dark:border-indigo-900/60 pb-1.5">
                <span class="text-[12px] font-mono font-extrabold uppercase tracking-wider text-indigo-950 dark:text-indigo-200 flex items-center gap-1.5">
                  <span>⚡</span> <span>1. Executive Gist</span>
                </span>
                <span class="text-[10.5px] font-mono font-bold px-2 py-0.5 rounded bg-indigo-200/80 text-indigo-950 dark:bg-indigo-900/80 dark:text-indigo-200">Key Takeaway</span>
              </div>
              <div class="space-y-2.5">
                ${briefSentences.map(sent => `
                  <div class="flex items-start gap-2.5 bg-white/95 dark:bg-[#10162A] p-2.5 rounded-lg border border-indigo-200/60 dark:border-slate-800 text-[13.5px] sm:text-[14px] text-slate-900 dark:text-slate-100 leading-relaxed font-normal shadow-2xs">
                    <span class="text-indigo-600 dark:text-indigo-400 font-bold select-none mt-0.5">▸</span>
                    <span class="leading-relaxed">${highlightSearchTokens(highlightNumbers(sent), queryTokens)}</span>
                  </div>
                `).join('')}
              </div>
            </div>

            <!-- 💡 SECTION 2: TRADER CATALYST & IMPACT ANALYSIS (PLACED DIRECTLY BELOW EXECUTIVE GIST!) -->
            <div class="p-3.5 rounded-xl border-2 ${isBullish ? 'border-emerald-500 bg-emerald-50/80 dark:bg-[#064E3B]/30 dark:border-emerald-600' : isBearish ? 'border-rose-500 bg-rose-50/80 dark:bg-[#881337]/30 dark:border-rose-600' : 'border-slate-400 bg-slate-50 dark:bg-slate-900/50 dark:border-slate-700'} shadow-xs flex flex-col gap-2.5">
              <div class="flex items-center justify-between border-b ${isBullish ? 'border-emerald-200 dark:border-emerald-900/60' : isBearish ? 'border-rose-200 dark:border-rose-900/60' : 'border-slate-200 dark:border-slate-800'} pb-1.5">
                <span class="text-[12px] font-mono font-extrabold uppercase tracking-wider ${isBullish ? 'text-emerald-950 dark:text-emerald-300' : isBearish ? 'text-rose-950 dark:text-rose-300' : 'text-slate-900 dark:text-slate-200'} flex items-center gap-1.5">
                  <span>💡</span> <span>2. Catalyst & Market Impact</span>
                </span>
                <span class="text-[10.5px] font-mono font-extrabold uppercase px-2 py-0.5 rounded ${isBullish ? 'bg-emerald-200 text-emerald-950 dark:bg-emerald-900 dark:text-emerald-200' : isBearish ? 'bg-rose-200 text-rose-950 dark:bg-rose-900 dark:text-rose-200' : 'bg-slate-200 text-slate-900 dark:bg-slate-800 dark:text-slate-200'}">${story.sentiment} THESIS</span>
              </div>
              <div class="bg-white/95 dark:bg-[#10162A] p-3 rounded-lg border ${isBullish ? 'border-emerald-200/60 dark:border-slate-800' : isBearish ? 'border-rose-200/60 dark:border-slate-800' : 'border-slate-200 dark:border-slate-800'} text-[13.5px] sm:text-[14px] text-slate-900 dark:text-slate-100 leading-relaxed font-normal shadow-2xs">
                ${highlightSearchTokens(highlightNumbers(story.sentimentReasoning), queryTokens)}
              </div>
            </div>

          </div>

          <!-- RIGHT COLUMN (lg:col-span-6): KEY ANALYST DATA POINTS -->
          <div class="lg:col-span-6 flex flex-col gap-2">
            
            <!-- 📌 SECTION 3: KEY ANALYST DATA POINTS (WITH PROPER LINE & BULLET SPACING) -->
            <div class="rounded-xl border-2 border-[#B8A38E] dark:border-[#524434] bg-[#FDFBF7] dark:bg-[#191512] p-3.5 shadow-xs flex flex-col gap-2.5">
              <div class="flex items-center justify-between border-b border-[#E8DCCE] dark:border-[#382E25] pb-1.5">
                <span class="text-[12px] font-mono font-extrabold uppercase tracking-wider text-[#2E1F14] dark:text-[#F3ECE4] flex items-center gap-1.5">
                  <span>📌</span> <span>3. Key Analyst Data Points</span>
                </span>
                <span class="text-[10.5px] font-mono font-bold px-2 py-0.5 rounded bg-[#EFE5D9] text-[#291B10] dark:bg-[#32261C] dark:text-[#E8DCCF] border border-[#CCAFA0]/50">Metrics & Facts</span>
              </div>
              <ul class="space-y-2.5">
                ${(story.bullet_points || []).map(bp => `
                  <li class="flex items-start gap-2.5 text-[13.5px] sm:text-[14px] text-slate-900 dark:text-slate-100 leading-relaxed bg-white/95 dark:bg-[#10162A] p-2.5 rounded-lg border border-[#EBE2D8] dark:border-slate-800 shadow-2xs font-normal">
                    <span class="text-[#8C5E3C] dark:text-[#CBB09C] font-bold select-none mt-0.5 text-base">›</span>
                    <span class="leading-relaxed">${highlightSearchTokens(highlightNumbers(bp), queryTokens)}</span>
                  </li>
                `).join('')}
              </ul>
            </div>

          </div>

        </div>
      `;
    }

    function highlightNumbers"""

    html = re.sub(old_detail_pattern, new_detail, html, flags=re.DOTALL)

    with open('web/index.html', 'w', encoding='utf-8') as f:
        f.write(html)

    print("Successfully updated web/index.html with Tree View and Line Spacing!")

if __name__ == '__main__':
    apply_updates()
