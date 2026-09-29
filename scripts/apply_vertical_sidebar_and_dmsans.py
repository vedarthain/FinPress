import re

def update_all():
    with open('web/index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Update Column 1 Headlines to DM Sans 500 (medium) weight
    old_col1_headline = r'<h4 class="text-\[13px\] \$\{isSelected \? \'font-bold text-\[#581C87\] dark:text-white\' : \'font-semibold text-slate-900 dark:text-slate-100\'\} tracking-tight truncate flex-1 min-w-0"'
    new_col1_headline = r"""<h4 class="text-[13.5px] font-sans font-medium ${isSelected ? 'text-[#581C87] dark:text-[#E9D5FF]' : 'text-[#090D16] dark:text-[#F8FAFC]'} tracking-tight truncate flex-1 min-w-0" """
    html = re.sub(old_col1_headline, new_col1_headline, html)

    # Also update any other font weights in Column 1 wire
    html = html.replace("font-mono font-extrabold text-slate-900 dark:text-slate-100", "font-sans font-medium text-[#090D16] dark:text-slate-100")

    # 2. Update Column 3 (<aside id="view-feed-aside">) to match the attached collapse & expand UI
    old_aside_pattern = r'<aside id="view-feed-aside".*?</aside>'
    
    new_aside = """<!-- COLUMN 3: RIGHT HAND SIDE PANEL (COLLAPSIBLE VERTICAL PILL & ACCORDION DRAWER) -->
        <div class="flex items-start gap-1 lg:sticky lg:top-[44px] lg:max-h-[calc(100vh-3.5rem)]">
          
          <!-- A. Vertical Pill when Collapsed (Matching Image 1) -->
          <button id="sidebar-vertical-pill" onclick="toggleSidebar()" class="hidden flex-col items-center gap-2 py-4 px-1.5 rounded-full border border-slate-300 dark:border-slate-700 bg-white dark:bg-[#0E1322] text-[#090D16] dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 shadow-sm cursor-pointer select-none transition-all shrink-0 w-8" title="Expand Categories, Sectors & Stocks">
            <span class="text-xs font-bold text-slate-700 dark:text-slate-300">☰</span>
            <span class="font-sans text-[10px] font-medium tracking-wider uppercase [writing-mode:vertical-lr] rotate-180 text-slate-700 dark:text-slate-300 py-1">
              CATEGORIES & DESKS
            </span>
          </button>

          <!-- B. Full Drawer when Open (Matching Image 2) -->
          <aside id="view-feed-aside" class="flex flex-col rounded-xl bg-white dark:bg-[#0E1322] border border-slate-200 dark:border-slate-800 shadow-xs overflow-hidden w-full min-w-[240px] max-w-[280px] lg:max-h-[calc(100vh-3.5rem)] lg:overflow-y-auto transition-all">
            
            <!-- Header (Matching Image 2: Title, Count, Collapse Chevron < ) -->
            <div class="flex items-center justify-between px-3 py-2.5 bg-white dark:bg-[#0E1322] border-b border-slate-100 dark:border-slate-800">
              <span class="text-[11.5px] font-sans font-bold uppercase tracking-wider text-slate-900 dark:text-slate-100">
                CATEGORIES & DESKS
              </span>
              <div class="flex items-center gap-2 text-[11px] font-mono text-slate-500 dark:text-slate-400">
                <span id="sidebar-total-stat">14 · Total</span>
                <button onclick="toggleSidebar()" class="w-6 h-6 rounded flex items-center justify-center hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-500 hover:text-black dark:hover:text-white font-bold cursor-pointer text-base leading-none transition-colors" title="Collapse to Pill (‹)">
                  ‹
                </button>
              </div>
            </div>

            <!-- Search Input Box (Matching Image 2) -->
            <div class="p-2 border-b border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/40">
              <div class="relative">
                <input type="text" id="sidebar-filter-input" oninput="onSidebarFilterInput(this.value)" placeholder="Search category or stock..." class="w-full text-[12px] pl-6 pr-2 py-1 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-[#0E1322] text-[#090D16] dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:border-indigo-500 font-sans"/>
                <span class="absolute left-2 top-1.5 text-slate-400 text-[10.5px]">🔍</span>
              </div>
            </div>

            <!-- Expand / Collapse All Toggle (Matching Image 2) -->
            <div class="flex items-center justify-between px-3 py-1.5 bg-white dark:bg-[#0E1322] text-[11px] font-sans border-b border-slate-100 dark:border-slate-800">
              <span id="active-filter-indicator" class="text-amber-700 dark:text-amber-400 font-medium text-[10.5px]"></span>
              <button onclick="toggleAllTreeSections()" id="expand-collapse-all-btn" class="text-slate-600 dark:text-slate-400 hover:text-black dark:hover:text-white font-medium flex items-center gap-1 cursor-pointer">
                <span>⊞</span> <span id="expand-all-text">Expand all</span>
              </button>
            </div>

            <!-- Dynamic Accordion Rows (Matching Image 2) -->
            <div id="sidebar-accordion-container" class="divide-y divide-slate-100 dark:divide-slate-800/80 flex flex-col font-sans">
              <!-- Dynamically populated accordion items with left blue border for active -->
            </div>

          </aside>

        </div>"""

    html = re.sub(old_aside_pattern, new_aside, html, flags=re.DOTALL)

    # 3. Update JavaScript Sidebar Accordion Renderer to match Image 2
    old_sidebar_code_pattern = r'// ================= TREE-VIEW SIDEBAR.*?function clearAllStockAndSectorFilters'
    
    new_sidebar_code = """// ================= ACCORDION SIDEBAR (MATCHING ATTACHED IMAGE 2) =================
    let treeState = {
      categories: true,  // Open by default
      desks: true,
      sectors: false,    // Collapsed by default
      stocks: false      // Collapsed by default
    };

    let sidebarSearchTerm = "";

    function onSidebarFilterInput(val) {
      sidebarSearchTerm = val.trim().toLowerCase();
      renderCategoriesAndStocksSidebar();
    }

    function toggleTreeNode(section) {
      treeState[section] = !treeState[section];
      renderCategoriesAndStocksSidebar();
    }

    function toggleAllTreeSections() {
      const allOpen = treeState.categories && treeState.desks && treeState.sectors && treeState.stocks;
      const nextState = !allOpen;
      treeState.categories = nextState;
      treeState.desks = nextState;
      treeState.sectors = nextState;
      treeState.stocks = nextState;
      renderCategoriesAndStocksSidebar();
    }

    function renderCategoriesAndStocksSidebar() {
      const container = document.getElementById("sidebar-accordion-container");
      if (!container) return;

      container.innerHTML = "";

      const coreStories = stories.filter(s => s.category !== "IPO" && s.category !== "Corporate Events" && s.category !== "Corporate Appointments" && !s.isOpinion);
      const totalIpos = ipoList.length;
      const anchorCount = coreStories.filter(s => s.isFrontPage).length;
      const corpEventsCount = stories.filter(s => s.category === "Corporate Events").length;
      const corpApptsCount = stories.filter(s => s.category === "Corporate Appointments").length;
      const corpCount = corpEventsCount + corpApptsCount;
      const opinionsCount = stories.filter(s => s.isOpinion).length;

      // Group 1: Core News Desks
      const coreNewsItems = [
        { id: "ALL", label: "All News", count: coreStories.length },
        { id: "ANCHOR", label: "Front Page", count: anchorCount },
        { id: "Sector", label: "Sector News", count: stories.filter(s => s.category === "Sector" && !s.isOpinion).length },
        { id: "Economy", label: "Economy", count: stories.filter(s => s.category === "Economy" && !s.isOpinion).length },
        { id: "Policy", label: "Policy & Regulations", count: stories.filter(s => s.category === "Policy" && !s.isOpinion).length },
        { id: "Market", label: "Market Pulse", count: stories.filter(s => s.category === "Market" && !s.isOpinion).length },
        { id: "Trade", label: "Trade & FX", count: stories.filter(s => s.category === "Trade" && !s.isOpinion).length },
        { id: "International News", label: "International", count: stories.filter(s => s.category === "International News" && !s.isOpinion).length },
        { id: "Others", label: "General Features", count: stories.filter(s => s.category === "Others" && !s.isOpinion).length }
      ];

      // Group 2: Specialized Desks
      const deskItems = [
        { id: "IPO_ALL", label: "IPO Central", count: totalIpos },
        { id: "CORPORATE_ALL", label: "Corporate Desk", count: corpCount },
        { id: "EVENTS", label: "Corp Events", count: corpEventsCount },
        { id: "APPOINTMENTS", label: "Appointments", count: corpApptsCount },
        { id: "OPINIONS", label: "Opinions Desk", count: opinionsCount }
      ];

      // Group 3: Industry Sectors
      const secCounts = {};
      stories.forEach(s => {
        (s.sectors || []).forEach(sec => secCounts[sec] = (secCounts[sec] || 0) + 1);
      });
      const sortedSecs = Object.keys(secCounts).sort((a,b) => secCounts[b] - secCounts[a]);

      // Group 4: Company Stocks
      const stockCounts = {};
      stories.forEach(s => {
        (s.stocks || []).forEach(stk => stockCounts[stk] = (stockCounts[stk] || 0) + 1);
      });
      const sortedStocks = Object.keys(stockCounts).sort((a,b) => stockCounts[b] - stockCounts[a]);

      const statEl = document.getElementById("sidebar-total-stat");
      if (statEl) statEl.textContent = `${coreNewsItems.length + deskItems.length} · ${sortedStocks.length}`;

      const expandText = document.getElementById("expand-all-text");
      const allOpen = treeState.categories && treeState.desks && treeState.sectors && treeState.stocks;
      if (expandText) expandText.textContent = allOpen ? "Collapse all" : "Expand all";

      const filterIndicator = document.getElementById("active-filter-indicator");
      if (filterIndicator) {
        if (activeStockFilter || activeSectorFilter || selectedFeedCategory !== 'ALL') {
          filterIndicator.innerHTML = `<button onclick="clearAllStockAndSectorFilters(); onCategorySelect('ALL');" class="hover:underline font-bold text-amber-700 dark:text-amber-400">Clear filters (✕)</button>`;
        } else {
          filterIndicator.textContent = "";
        }
      }

      // Helper to build Accordion Group row matching Image 2
      function createAccordionGroup(title, count, isExpanded, onToggle, items, renderItemFn) {
        const groupWrapper = document.createElement("div");
        groupWrapper.className = "flex flex-col";

        const isGroupActive = items.some(it => it.isSelected);

        const headerBtn = document.createElement("button");
        headerBtn.className = `w-full text-left px-3 py-2.5 flex items-center justify-between transition-colors select-none ${
          isGroupActive 
            ? 'border-l-4 border-indigo-600 bg-slate-100/90 dark:bg-slate-800/80 font-bold text-slate-900 dark:text-white' 
            : 'border-l-4 border-transparent hover:bg-slate-50 dark:hover:bg-slate-800/40 text-slate-800 dark:text-slate-200 font-medium'
        }`;
        headerBtn.onclick = onToggle;
        headerBtn.innerHTML = `
          <div class="flex items-center gap-2">
            <span class="text-[10px] text-slate-500 dark:text-slate-400 transition-transform ${isExpanded ? 'rotate-90' : ''}">▶</span>
            <span class="text-[13px] font-sans font-medium">${title}</span>
            <span class="text-[11.5px] font-normal text-slate-400 dark:text-slate-500 font-sans">(${count})</span>
          </div>
        `;
        groupWrapper.appendChild(headerBtn);

        if (isExpanded) {
          const bodyDiv = document.createElement("div");
          bodyDiv.className = "pl-6 pr-2 py-1 flex flex-col gap-0.5 bg-slate-50/40 dark:bg-slate-900/30 border-t border-slate-100/80 dark:border-slate-800/50";
          items.forEach(it => {
            const itemRow = renderItemFn(it);
            if (itemRow) bodyDiv.appendChild(itemRow);
          });
          groupWrapper.appendChild(bodyDiv);
        }

        return groupWrapper;
      }

      // 1. Core Categories Section
      const filteredCore = coreNewsItems.filter(it => !sidebarSearchTerm || it.label.toLowerCase().includes(sidebarSearchTerm));
      if (filteredCore.length > 0) {
        const coreGroup = createAccordionGroup(
          "News Categories",
          coreNewsItems.length,
          treeState.categories || !!sidebarSearchTerm,
          () => toggleTreeNode('categories'),
          filteredCore.map(it => ({ ...it, isSelected: selectedFeedCategory === it.id })),
          (it) => {
            const btn = document.createElement("button");
            btn.className = `w-full text-left px-2 py-1 rounded text-[12px] font-sans flex items-center justify-between transition-colors ${
              it.isSelected ? 'bg-indigo-600 text-white font-bold shadow-xs' : 'text-slate-700 dark:text-slate-300 hover:bg-slate-200/60 dark:hover:bg-slate-800 font-medium'
            }`;
            btn.innerHTML = `
              <span class="truncate">${it.label}</span>
              <span class="text-[11px] opacity-75 font-mono">(${it.count})</span>
            `;
            btn.onclick = () => {
              if (it.id === 'ANCHOR') switchView('anchor');
              else onCategorySelect(it.isSelected ? 'ALL' : it.id);
            };
            return btn;
          }
        );
        container.appendChild(coreGroup);
      }

      // 2. Specialized Desks Section
      const filteredDesks = deskItems.filter(it => !sidebarSearchTerm || it.label.toLowerCase().includes(sidebarSearchTerm));
      if (filteredDesks.length > 0) {
        const deskGroup = createAccordionGroup(
          "Specialized Desks",
          deskItems.length,
          treeState.desks || !!sidebarSearchTerm,
          () => toggleTreeNode('desks'),
          filteredDesks.map(it => ({ ...it, isSelected: selectedFeedCategory === it.id || (it.id === 'IPO_ALL' && currentView === 'ipo') || (it.id === 'CORPORATE_ALL' && currentView === 'corporate') })),
          (it) => {
            const btn = document.createElement("button");
            btn.className = `w-full text-left px-2 py-1 rounded text-[12px] font-sans flex items-center justify-between transition-colors ${
              it.isSelected ? 'bg-amber-700 text-white font-bold shadow-xs' : 'text-slate-700 dark:text-slate-300 hover:bg-amber-100/60 dark:hover:bg-amber-950/40 font-medium'
            }`;
            btn.innerHTML = `
              <span class="truncate">${it.label}</span>
              <span class="text-[11px] opacity-75 font-mono">(${it.count})</span>
            `;
            btn.onclick = () => {
              if (it.id === 'IPO_ALL') onDeskSelect('ipo');
              else if (it.id === 'CORPORATE_ALL') onDeskSelect('corporate');
              else if (it.id === 'EVENTS') selectCorporateSub('EVENTS');
              else if (it.id === 'APPOINTMENTS') selectCorporateSub('APPOINTMENTS');
              else if (it.id === 'OPINIONS') onDeskSelect('opinions');
            };
            return btn;
          }
        );
        container.appendChild(deskGroup);
      }

      // 3. Industry Sectors Section
      const filteredSectors = sortedSecs.filter(sec => !sidebarSearchTerm || sec.toLowerCase().includes(sidebarSearchTerm));
      if (filteredSectors.length > 0) {
        const secGroup = createAccordionGroup(
          "Industry Sectors",
          sortedSecs.length,
          treeState.sectors || !!sidebarSearchTerm,
          () => toggleTreeNode('sectors'),
          filteredSectors.map(sec => ({ id: sec, label: sec, count: secCounts[sec], isSelected: activeSectorFilter === sec })),
          (it) => {
            const btn = document.createElement("button");
            btn.className = `w-full text-left px-2 py-1 rounded text-[12px] font-sans flex items-center justify-between transition-colors ${
              it.isSelected ? 'bg-indigo-600 text-white font-bold shadow-xs' : 'text-slate-700 dark:text-slate-300 hover:bg-indigo-100/60 dark:hover:bg-indigo-950/40 font-medium'
            }`;
            btn.innerHTML = `
              <span class="truncate">${it.label}</span>
              <span class="text-[11px] opacity-75 font-mono">(${it.count})</span>
            `;
            btn.onclick = () => {
              activeSectorFilter = activeSectorFilter === it.id ? null : it.id;
              selectedStoryIndex = 0;
              currentFeedPage = 1;
              renderCategoriesAndStocksSidebar();
              if (currentLayoutMode === "split") renderFeedList();
              else renderMatrixTable();
            };
            return btn;
          }
        );
        container.appendChild(secGroup);
      }

      // 4. Company Stocks Section
      const filteredStocks = sortedStocks.filter(stk => !sidebarSearchTerm || stk.toLowerCase().includes(sidebarSearchTerm));
      if (filteredStocks.length > 0) {
        const stockGroup = createAccordionGroup(
          "Company Stocks",
          sortedStocks.length,
          treeState.stocks || !!sidebarSearchTerm,
          () => toggleTreeNode('stocks'),
          filteredStocks.map(stk => ({ id: stk, label: stk, count: stockCounts[stk], isSelected: activeStockFilter === stk })),
          (it) => {
            const btn = document.createElement("button");
            btn.className = `w-full text-left px-2 py-1 rounded text-[12px] font-sans flex items-center justify-between transition-colors ${
              it.isSelected ? 'bg-amber-600 text-white font-bold shadow-xs' : 'text-slate-700 dark:text-slate-300 hover:bg-amber-100/60 dark:hover:bg-amber-950/40 font-medium'
            }`;
            btn.innerHTML = `
              <span class="truncate">${it.label}</span>
              <span class="text-[11px] opacity-75 font-mono">(${it.count})</span>
            `;
            btn.onclick = () => {
              activeStockFilter = activeStockFilter === it.id ? null : it.id;
              selectedStoryIndex = 0;
              currentFeedPage = 1;
              renderCategoriesAndStocksSidebar();
              if (currentLayoutMode === "split") renderFeedList();
              else renderMatrixTable();
            };
            return btn;
          }
        );
        container.appendChild(stockGroup);
      }
    }

    function clearAllStockAndSectorFilters"""

    html = re.sub(old_sidebar_code_pattern, new_sidebar_code, html, flags=re.DOTALL)

    # 4. Update applySidebarVisibility in JS to toggle the vertical pill vs full drawer
    old_vis_fn = r'function applySidebarVisibility\(\) \{.*?\n    \}'
    new_vis_fn = """function applySidebarVisibility() {
      const aside = document.getElementById("view-feed-aside");
      const pill = document.getElementById("sidebar-vertical-pill");
      const viewFeed = document.getElementById("view-feed");
      const openBtn = document.getElementById("feed-open-sidebar-btn");

      if (aside && viewFeed) {
        if (isSidebarVisible) {
          aside.classList.remove("hidden");
          if (pill) pill.classList.add("hidden");
          viewFeed.className = "grid grid-cols-1 lg:grid-cols-[280px_minmax(0,1fr)_260px] xl:grid-cols-[300px_minmax(0,1fr)_275px] gap-2.5 items-start";
          if (openBtn) {
            openBtn.classList.add("hidden");
            openBtn.classList.remove("flex");
          }
        } else {
          aside.classList.add("hidden");
          if (pill) pill.classList.remove("hidden");
          viewFeed.className = "grid grid-cols-1 lg:grid-cols-[280px_minmax(0,1fr)_auto] xl:grid-cols-[300px_minmax(0,1fr)_auto] gap-2.5 items-start";
          if (openBtn) {
            openBtn.classList.remove("hidden");
            openBtn.classList.add("flex");
          }
        }
      }
    }"""

    html = re.sub(old_vis_fn, new_vis_fn, html, flags=re.DOTALL)

    with open('web/index.html', 'w', encoding='utf-8') as f:
        f.write(html)

    print("Successfully updated web/index.html with vertical pill collapse & accordion drawer matching images!")

if __name__ == '__main__':
    update_all()
