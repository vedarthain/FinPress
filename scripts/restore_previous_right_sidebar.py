import re

def update_all():
    with open('web/index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Update Column 3 Container: Keep the vertical pill when collapsed, and the 3-card tree format when open
    old_aside_pattern = r'<!-- COLUMN 3: RIGHT HAND SIDE PANEL.*?-->.*?<!-- ================= VIEW 2: TABULAR IPO CENTRAL'
    
    new_aside = """<!-- COLUMN 3: RIGHT HAND SIDE PANEL (TREE VIEW: CATEGORIES [OPEN], SECTORS & STOCKS [COLLAPSED] + HAMBURGER COLLAPSE) -->
        <div class="flex items-start gap-1 lg:sticky lg:top-[44px] lg:max-h-[calc(100vh-3.5rem)]">
          
          <!-- A. Vertical Pill when Collapsed (Hamburger kind of collapse) -->
          <button id="sidebar-vertical-pill" onclick="toggleSidebar()" class="hidden flex-col items-center gap-2 py-4 px-1.5 rounded-full border border-[#DFC0A5] dark:border-slate-700 bg-[#FBE8D8] dark:bg-[#0E1322] text-[#1C1917] dark:text-slate-200 hover:bg-[#F3DECC] dark:hover:bg-slate-800 shadow-sm cursor-pointer select-none transition-all shrink-0 w-8" title="Expand Categories, Sectors & Stocks">
            <span class="text-xs font-bold text-amber-900 dark:text-amber-400">☰</span>
            <span class="font-mono text-[10px] font-bold tracking-wider uppercase [writing-mode:vertical-lr] rotate-180 text-[#3D2412] dark:text-slate-300 py-1">
              CATEGORIES & DESKS
            </span>
          </button>

          <!-- B. Full Right Sidebar when Open (The 3 Tree-format Cards) -->
          <aside id="view-feed-aside" class="flex flex-col gap-2 min-w-[240px] max-w-[280px] lg:max-h-[calc(100vh-3.5rem)] lg:overflow-y-auto transition-all">
            
            <!-- Top Header of Column 3 with Hamburger & Hide -->
            <div class="flex items-center justify-between px-2.5 py-1.5 rounded-lg bg-[#FBE8D8] dark:bg-[#151D33] border border-[#DFC0A5] dark:border-slate-800 shadow-2xs">
              <div class="flex items-center gap-1.5 font-mono text-[11.5px] font-bold text-[#1C1917] dark:text-slate-100">
                <span class="text-amber-800 dark:text-amber-400 font-extrabold text-sm">☰</span>
                <span>Filters & Desks</span>
              </div>
              <button onclick="toggleSidebar()" class="px-2 py-0.5 rounded hover:bg-black/10 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 hover:text-black font-mono text-[11px] font-bold flex items-center gap-1 cursor-pointer transition-colors" title="Collapse Sidebar to Hamburger Pill">
                <span>✕ Hide</span>
              </button>
            </div>

            <!-- Tree Container (Renders the 3 Tree Cards) -->
            <div id="tree-sidebar-container" class="flex flex-col gap-2 font-mono">
              <!-- Dynamically populated: 1. Categories Card, 2. Sectors Card, 3. Stocks Card -->
            </div>

          </aside>

        </div>

      </section>

      <!-- ================= VIEW 2: TABULAR IPO CENTRAL"""

    html = re.sub(old_aside_pattern, new_aside, html, flags=re.DOTALL)

    # 2. Restore the previous tree sidebar function
    old_sidebar_fn_pattern = r'// ================= ACCORDION SIDEBAR.*?function clearAllStockAndSectorFilters'
    
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
          btn.className = `w-full text-left px-2 py-1 rounded flex items-center justify-between transition-colors ${isSelected ? 'bg-indigo-600 text-white font-bold shadow-xs' : 'text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800/60 font-medium'}`;
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

    function clearAllStockAndSectorFilters"""

    html = re.sub(old_sidebar_fn_pattern, new_sidebar_fn, html, flags=re.DOTALL)

    with open('web/index.html', 'w', encoding='utf-8') as f:
        f.write(html)

    print("Restored previous right sidebar format with vertical hamburger collapse!")

if __name__ == '__main__':
    update_all()
