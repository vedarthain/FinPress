import re

def update_all():
    with open('web/index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Update Grid Layout and Column 3 Container
    # Remove the top hamburger box when open, squeeze width towards extreme right
    old_aside_pattern = r'<!-- COLUMN 3: RIGHT HAND SIDE PANEL.*?-->.*?<!-- ================= VIEW 2: TABULAR IPO CENTRAL'
    
    new_aside = """<!-- COLUMN 3: RIGHT HAND SIDE PANEL (SQUEEZED TO EXTREME RIGHT, COMPACT TREE VIEW) -->
        <aside id="view-feed-aside" class="flex flex-col gap-1.5 w-full min-w-[195px] max-w-[225px] lg:sticky lg:top-[44px] lg:max-h-[calc(100vh-3.5rem)] lg:overflow-y-auto transition-all shrink-0">
          
          <!-- Tree Container (Renders the 3 Tree Cards directly without extra hamburger top box) -->
          <div id="tree-sidebar-container" class="flex flex-col gap-1.5 font-sans">
            <!-- Dynamically populated: 1. Categories Card, 2. Sectors Card, 3. Stocks Card -->
          </div>

        </aside>

      </section>

      <!-- ================= VIEW 2: TABULAR IPO CENTRAL"""

    html = re.sub(old_aside_pattern, new_aside, html, flags=re.DOTALL)

    # 2. Update Grid Columns in HTML for view-feed
    html = re.sub(
        r'id="view-feed"\s+class="grid grid-cols-1 lg:grid-cols-\[.*?\] xl:grid-cols-\[.*?\] (?:2xl:grid-cols-\[.*?\] )?gap-2(?:\.5)? items-start"',
        'id="view-feed" class="grid grid-cols-1 lg:grid-cols-[275px_minmax(0,1fr)_205px] xl:grid-cols-[290px_minmax(0,1fr)_215px] 2xl:grid-cols-[310px_minmax(0,1fr)_225px] gap-2 items-start"',
        html
    )

    # 3. Update JavaScript Tree Renderer to squeeze space between names and numbers
    old_sidebar_fn_pattern = r'// ================= TREE-VIEW SIDEBAR.*?function clearAllStockAndSectorFilters'
    
    new_sidebar_fn = """// ================= SQUEEZED COMPACT TREE-VIEW SIDEBAR =================
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
        <div class="px-2.5 py-1.5 bg-slate-50 dark:bg-slate-900/90 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between cursor-pointer select-none" onclick="toggleTreeNode('categories')">
          <div class="flex items-center gap-1 text-[11px] font-sans font-bold text-slate-900 dark:text-slate-100">
            <span class="text-amber-600 dark:text-amber-400 text-[9.5px]">${isCatOpen ? '▼' : '▶'}</span>
            <span>📁 News Categories</span>
            <span class="text-[10px] text-slate-400 dark:text-slate-500 font-mono">(${coreNewsItems.length + deskItems.length})</span>
          </div>
          ${selectedFeedCategory !== 'ALL' ? `<button onclick="event.stopPropagation(); onCategorySelect('ALL');" class="text-[9.5px] font-mono text-amber-600 dark:text-amber-400 font-bold hover:underline">Reset (✕)</button>` : ''}
        </div>
      `;

      if (isCatOpen) {
        const catBody = document.createElement("div");
        catBody.className = "p-1.5 flex flex-col gap-1 text-[11px] font-sans";

        // Sub-group: Core News Desks
        const coreDiv = document.createElement("div");
        coreDiv.className = "flex flex-col gap-0.5";
        coreDiv.innerHTML = `<span class="text-[9.5px] font-bold uppercase text-slate-400 dark:text-slate-500 px-1 mb-0.5 tracking-wider">📰 Core Desks</span>`;

        coreNewsItems.forEach(item => {
          const isSelected = selectedFeedCategory === item.id;
          const btn = document.createElement("button");
          btn.className = `w-full text-left px-1.5 py-0.5 rounded flex items-center justify-between transition-colors cursor-pointer ${isSelected ? 'bg-indigo-600 text-white font-bold shadow-xs' : 'text-[#090D16] dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800/60 font-medium'}`;
          btn.innerHTML = `
            <span class="flex items-center gap-1 min-w-0 truncate">
              <span class="text-slate-400 select-none text-[10px] ${isSelected ? 'text-white' : ''}">├─</span>
              <span class="truncate">${item.label}</span>
            </span>
            <span class="text-[10px] font-mono shrink-0 ml-1 ${isSelected ? 'text-white/90' : 'text-slate-400 dark:text-slate-500'}">(${item.count})</span>
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
        deskDiv.className = "flex flex-col gap-0.5 pt-1 border-t border-slate-100 dark:border-slate-800";
        deskDiv.innerHTML = `<span class="text-[9.5px] font-bold uppercase text-amber-700 dark:text-amber-400 px-1 mb-0.5 tracking-wider">🏛️ Specialized Desks</span>`;

        deskItems.forEach(item => {
          const isSelected = selectedFeedCategory === item.id || (item.id === 'IPO_ALL' && currentView === 'ipo') || (item.id === 'CORPORATE_ALL' && currentView === 'corporate');
          const btn = document.createElement("button");
          btn.className = `w-full text-left px-1.5 py-0.5 rounded flex items-center justify-between transition-colors cursor-pointer ${isSelected ? 'bg-amber-700 text-white font-bold shadow-xs' : 'text-[#090D16] dark:text-slate-200 hover:bg-amber-50/60 dark:hover:bg-amber-950/30 font-medium'}`;
          btn.innerHTML = `
            <span class="flex items-center gap-1 min-w-0 truncate">
              <span class="text-slate-400 select-none text-[10px] ${isSelected ? 'text-white' : ''}">├─</span>
              <span class="truncate">${item.label}</span>
            </span>
            <span class="text-[10px] font-mono shrink-0 ml-1 ${isSelected ? 'text-white/90' : 'text-amber-700 dark:text-amber-400'}">(${item.count})</span>
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
        <div class="px-2.5 py-1.5 bg-slate-50 dark:bg-slate-900/90 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between cursor-pointer select-none" onclick="toggleTreeNode('sectors')">
          <div class="flex items-center gap-1 text-[11px] font-sans font-bold text-slate-900 dark:text-slate-100">
            <span class="text-indigo-600 dark:text-indigo-400 text-[9.5px]">${isSecOpen ? '▼' : '▶'}</span>
            <span>📈 Industry Sectors</span>
            <span class="text-[10px] text-slate-400 dark:text-slate-500 font-mono">(${sortedSecs.length})</span>
          </div>
          ${activeSectorFilter ? `<button onclick="event.stopPropagation(); activeSectorFilter = null; renderCategoriesAndStocksSidebar(); renderFeedList();" class="text-[9.5px] font-mono text-indigo-600 dark:text-indigo-400 font-bold hover:underline">Clear (✕)</button>` : ''}
        </div>
      `;

      if (isSecOpen) {
        const secBody = document.createElement("div");
        secBody.className = "p-1.5 flex flex-col gap-0.5 text-[11px] font-sans max-h-[260px] overflow-y-auto";

        sortedSecs.forEach(sec => {
          const isSelected = activeSectorFilter === sec;
          const btn = document.createElement("button");
          btn.className = `w-full text-left px-1.5 py-0.5 rounded flex items-center justify-between transition-colors cursor-pointer ${isSelected ? 'bg-indigo-600 text-white font-bold shadow-xs' : 'text-[#090D16] dark:text-slate-200 hover:bg-indigo-50/60 dark:hover:bg-indigo-950/30 font-medium'}`;
          btn.innerHTML = `
            <span class="flex items-center gap-1 min-w-0 truncate">
              <span class="text-slate-400 select-none text-[10px] ${isSelected ? 'text-white' : ''}">├─</span>
              <span class="truncate">${sec}</span>
            </span>
            <span class="text-[10px] font-mono shrink-0 ml-1 ${isSelected ? 'text-white/90' : 'text-slate-400 dark:text-slate-500'}">(${secCounts[sec]})</span>
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
        <div class="px-2.5 py-1.5 bg-slate-50 dark:bg-slate-900/90 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between cursor-pointer select-none" onclick="toggleTreeNode('stocks')">
          <div class="flex items-center gap-1 text-[11px] font-sans font-bold text-slate-900 dark:text-slate-100">
            <span class="text-amber-600 dark:text-amber-400 text-[9.5px]">${isStockOpen ? '▼' : '▶'}</span>
            <span>🏢 Company Stocks</span>
            <span class="text-[10px] text-slate-400 dark:text-slate-500 font-mono">(${sortedStocks.length})</span>
          </div>
          ${activeStockFilter ? `<button onclick="event.stopPropagation(); activeStockFilter = null; renderCategoriesAndStocksSidebar(); renderFeedList();" class="text-[9.5px] font-mono text-indigo-600 dark:text-indigo-400 font-bold hover:underline">Clear (✕)</button>` : ''}
        </div>
      `;

      if (isStockOpen) {
        const stockBody = document.createElement("div");
        stockBody.className = "p-1.5 flex flex-col gap-0.5 text-[11px] font-sans max-h-[260px] overflow-y-auto";

        sortedStocks.forEach(stk => {
          const isSelected = activeStockFilter === stk;
          const btn = document.createElement("button");
          btn.className = `w-full text-left px-1.5 py-0.5 rounded flex items-center justify-between transition-colors cursor-pointer ${isSelected ? 'bg-amber-600 text-white font-bold shadow-xs' : 'text-[#090D16] dark:text-slate-200 hover:bg-amber-50/60 dark:hover:bg-amber-950/30 font-medium'}`;
          btn.innerHTML = `
            <span class="flex items-center gap-1 min-w-0 truncate">
              <span class="text-slate-400 select-none text-[10px] ${isSelected ? 'text-white' : ''}">├─</span>
              <span class="truncate">${stk}</span>
            </span>
            <span class="text-[10px] font-mono shrink-0 ml-1 ${isSelected ? 'text-white/90' : 'text-slate-400 dark:text-slate-500'}">(${stockCounts[stk]})</span>
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

    print("Successfully squeezed right sidebar and reduced spaces between names and numbers!")

if __name__ == '__main__':
    update_all()
