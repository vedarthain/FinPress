import re

def update_all():
    with open('web/index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Update Grid and Aside Container: Move 3rd column to extreme right hand side
    old_aside_pattern = r'<!-- COLUMN 3: RIGHT HAND SIDE PANEL.*?-->.*?<!-- ================= VIEW 2: TABULAR IPO CENTRAL'
    
    new_aside = """<!-- COLUMN 3: RIGHT HAND SIDE PANEL (EXTREME RIGHT, INCREASED FONT, COLOR-CODED CLUSTERED STOCKS) -->
        <aside id="view-feed-aside" class="flex flex-col gap-1.5 w-full min-w-[215px] max-w-[245px] ml-auto lg:sticky lg:top-[44px] lg:max-h-[calc(100vh-3.5rem)] lg:overflow-y-auto transition-all shrink-0">
          
          <!-- Tree Container (Renders 1. Categories Card, 2. Sectors Card, 3. Clustered Stocks Card) -->
          <div id="tree-sidebar-container" class="flex flex-col gap-1.5 font-sans">
            <!-- Dynamically populated -->
          </div>

        </aside>

      </section>

      <!-- ================= VIEW 2: TABULAR IPO CENTRAL"""

    html = re.sub(old_aside_pattern, new_aside, html, flags=re.DOTALL)

    # 2. Update Grid layout class for view-feed
    html = re.sub(
        r'id="view-feed"\s+class="grid grid-cols-1 lg:grid-cols-\[.*?\] xl:grid-cols-\[.*?\] (?:2xl:grid-cols-\[.*?\] )?gap-2(?:\.5)? items-start"',
        'id="view-feed" class="grid grid-cols-1 lg:grid-cols-[280px_minmax(0,1fr)_215px] xl:grid-cols-[295px_minmax(0,1fr)_230px] 2xl:grid-cols-[315px_minmax(0,1fr)_245px] gap-2 items-start w-full"',
        html
    )

    # 3. Increase font size in Column 2 (Descriptions: 16.5px - 17px)
    old_detail_pattern = r'<!-- 2-COLUMN SIDE-BY-SIDE GRID: LEFT \(GIST \+ CATALYST\) & RIGHT \(KEY ANALYST DATA POINTS\) -->.*?function highlightNumbers'
    
    new_detail = """<!-- 2-COLUMN SIDE-BY-SIDE GRID: LEFT (GIST + CATALYST) & RIGHT (KEY ANALYST DATA POINTS) -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-3.5 items-start mt-2.5">
          
          <!-- LEFT COLUMN (lg:col-span-6): CORE TRADER TAKEAWAY + CATALYST DIRECTLY BELOW -->
          <div class="lg:col-span-6 flex flex-col gap-3.5">
            
            <!-- ⚡ SECTION 1: EXECUTIVE GIST (LARGER FONT: 17px & AIRY LINE SPACING) -->
            <div class="rounded-xl border-2 border-indigo-300 dark:border-indigo-800 bg-indigo-50/60 dark:bg-[#13182E] p-4 shadow-xs flex flex-col gap-2.5">
              <div class="flex items-center justify-between border-b border-indigo-200/90 dark:border-indigo-900/60 pb-1.5">
                <span class="text-[13px] font-mono font-extrabold uppercase tracking-wider text-indigo-950 dark:text-indigo-200 flex items-center gap-1.5">
                  <span>⚡</span> <span>1. Executive Gist</span>
                </span>
                <span class="text-[11.5px] font-mono font-bold px-2 py-0.5 rounded bg-indigo-200/80 text-indigo-950 dark:bg-indigo-900/80 dark:text-indigo-200">Key Takeaway</span>
              </div>
              <div class="space-y-3">
                ${briefSentences.map(sent => `
                  <div class="flex items-start gap-2.5 bg-white/95 dark:bg-[#0E1322] p-3.5 rounded-lg border border-indigo-100 dark:border-slate-800 text-[16.5px] sm:text-[17px] text-[#090D16] dark:text-[#F8FAFC] leading-[1.7] font-normal shadow-2xs font-sans tracking-tight">
                    <span class="text-indigo-600 dark:text-indigo-400 font-bold select-none mt-0.5 text-base">▸</span>
                    <span class="leading-[1.7]">${highlightSearchTokens(highlightNumbers(sent), queryTokens)}</span>
                  </div>
                `).join('')}
              </div>
            </div>

            <!-- 💡 SECTION 2: TRADER CATALYST & IMPACT ANALYSIS (LARGER FONT: 17px) -->
            <div class="p-4 rounded-xl border-2 ${isBullish ? 'border-emerald-500 bg-emerald-50/70 dark:bg-[#064E3B]/30 dark:border-emerald-600' : isBearish ? 'border-rose-500 bg-rose-50/70 dark:bg-[#881337]/30 dark:border-rose-600' : 'border-slate-400 bg-slate-50 dark:bg-slate-900/50 dark:border-slate-700'} shadow-xs flex flex-col gap-2.5">
              <div class="flex items-center justify-between border-b ${isBullish ? 'border-emerald-200 dark:border-emerald-900/60' : isBearish ? 'border-rose-200 dark:border-rose-900/60' : 'border-slate-200 dark:border-slate-800'} pb-1.5">
                <span class="text-[13px] font-mono font-extrabold uppercase tracking-wider ${isBullish ? 'text-emerald-950 dark:text-emerald-300' : isBearish ? 'text-rose-950 dark:text-rose-300' : 'text-slate-900 dark:text-slate-200'} flex items-center gap-1.5">
                  <span>💡</span> <span>2. Catalyst & Market Impact</span>
                </span>
                <span class="text-[11.5px] font-mono font-extrabold uppercase px-2.5 py-0.5 rounded ${isBullish ? 'bg-emerald-200 text-emerald-950 dark:bg-emerald-900 dark:text-emerald-200' : isBearish ? 'bg-rose-200 text-rose-950 dark:bg-rose-900 dark:text-rose-200' : 'bg-slate-200 text-slate-900 dark:bg-slate-800 dark:text-slate-200'}">${story.sentiment} THESIS</span>
              </div>
              <div class="bg-white/95 dark:bg-[#0E1322] p-3.5 rounded-lg border ${isBullish ? 'border-emerald-200/60 dark:border-slate-800' : isBearish ? 'border-rose-200/60 dark:border-slate-800' : 'border-slate-200 dark:border-slate-800'} text-[16.5px] sm:text-[17px] text-[#090D16] dark:text-[#F8FAFC] leading-[1.7] font-normal shadow-2xs font-sans tracking-tight">
                ${highlightSearchTokens(highlightNumbers(story.sentimentReasoning), queryTokens)}
              </div>
            </div>

          </div>

          <!-- RIGHT COLUMN (lg:col-span-6): KEY ANALYST DATA POINTS -->
          <div class="lg:col-span-6 flex flex-col gap-2">
            
            <!-- 📌 SECTION 3: KEY ANALYST DATA POINTS (LARGER FONT: 17px) -->
            <div class="rounded-xl border-2 border-[#C9B7A5] dark:border-[#524434] bg-[#FDFBF7] dark:bg-[#191512] p-4 shadow-xs flex flex-col gap-2.5">
              <div class="flex items-center justify-between border-b border-[#E8DCCE] dark:border-[#382E25] pb-1.5">
                <span class="text-[13px] font-mono font-extrabold uppercase tracking-wider text-[#2E1F14] dark:text-[#F3ECE4] flex items-center gap-1.5">
                  <span>📌</span> <span>3. Key Analyst Data Points</span>
                </span>
                <span class="text-[11.5px] font-mono font-bold px-2 py-0.5 rounded bg-[#EFE5D9] text-[#291B10] dark:bg-[#32261C] dark:text-[#E8DCCF] border border-[#CCAFA0]/50">Metrics & Facts</span>
              </div>
              <ul class="space-y-3">
                ${(story.bullet_points || []).map(bp => `
                  <li class="flex items-start gap-2.5 text-[16.5px] sm:text-[17px] text-[#090D16] dark:text-[#F8FAFC] leading-[1.7] bg-white/95 dark:bg-[#0E1322] p-3.5 rounded-lg border border-[#EBE2D8] dark:border-slate-800 shadow-2xs font-normal font-sans tracking-tight">
                    <span class="text-[#8C5E3C] dark:text-[#CBB09C] font-bold select-none mt-0.5 text-base">›</span>
                    <span class="leading-[1.7]">${highlightSearchTokens(highlightNumbers(bp), queryTokens)}</span>
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

    # 4. Stock Cluster Mapping and Clustered/Color-Coded Rendering in Sidebar
    old_sidebar_code_pattern = r'// ================= SQUEEZED COMPACT TREE-VIEW SIDEBAR.*?function clearAllStockAndSectorFilters'

    new_sidebar_code = """// ================= SQUEEZED TREE-VIEW SIDEBAR WITH COLOR-CODED CLUSTERED STOCKS =================
    let treeState = {
      categories: true,  // Open by default
      sectors: false,    // Collapsed by default
      stocks: false      // Collapsed by default
    };

    const stockClusterMap = {
      "HDFC BANK": { group: "Banking & Fin", color: "blue" },
      "HDFCBANK": { group: "Banking & Fin", color: "blue" },
      "ICICI BANK": { group: "Banking & Fin", color: "blue" },
      "ICICIBANK": { group: "Banking & Fin", color: "blue" },
      "SBI": { group: "Banking & Fin", color: "blue" },
      "SBIN": { group: "Banking & Fin", color: "blue" },
      "KOTAK BANK": { group: "Banking & Fin", color: "blue" },
      "AXIS BANK": { group: "Banking & Fin", color: "blue" },
      "BAJAJ FINANCE": { group: "Banking & Fin", color: "blue" },
      "CDSL": { group: "Banking & Fin", color: "blue" },
      "BSE": { group: "Banking & Fin", color: "blue" },
      "MCX": { group: "Banking & Fin", color: "blue" },
      "IREDA": { group: "Banking & Fin", color: "blue" },
      "IRFC": { group: "Banking & Fin", color: "blue" },
      "EDELWEISS": { group: "Banking & Fin", color: "blue" },

      "NTPC": { group: "Energy & Power", color: "amber" },
      "ONGC": { group: "Energy & Power", color: "amber" },
      "POWERGRID": { group: "Energy & Power", color: "amber" },
      "RELIANCE": { group: "Energy & Power", color: "amber" },
      "COAL INDIA": { group: "Energy & Power", color: "amber" },
      "COALINDIA": { group: "Energy & Power", color: "amber" },
      "BCCL": { group: "Energy & Power", color: "amber" },
      "NCL": { group: "Energy & Power", color: "amber" },
      "ADANI": { group: "Energy & Power", color: "amber" },
      "NATRAJ ENERGY": { group: "Energy & Power", color: "amber" },
      "NAYARA": { group: "Energy & Power", color: "amber" },

      "TCS": { group: "IT & Tech", color: "purple" },
      "INFOSYS": { group: "IT & Tech", color: "purple" },
      "INFY": { group: "IT & Tech", color: "purple" },
      "WIPRO": { group: "IT & Tech", color: "purple" },
      "TECH MAHINDRA": { group: "IT & Tech", color: "purple" },
      "HCLTECH": { group: "IT & Tech", color: "purple" },
      "COFORGE": { group: "IT & Tech", color: "purple" },
      "ESDS SOFTWARE": { group: "IT & Tech", color: "purple" },
      "ORACLE": { group: "IT & Tech", color: "purple" },
      "NVIDIA": { group: "IT & Tech", color: "purple" },
      "META": { group: "IT & Tech", color: "purple" },
      "ALIBABA": { group: "IT & Tech", color: "purple" },
      "BYTEDANCE": { group: "IT & Tech", color: "purple" },
      "MONGODB": { group: "IT & Tech", color: "purple" },
      "ZOMATO": { group: "IT & Tech", color: "purple" },
      "PAYTM": { group: "IT & Tech", color: "purple" },
      "SWIGGY": { group: "IT & Tech", color: "purple" },

      "TATA MOTORS": { group: "Auto & EV", color: "emerald" },
      "MARUTI": { group: "Auto & EV", color: "emerald" },
      "BAJAJ AUTO": { group: "Auto & EV", color: "emerald" },
      "HERO MOTOCORP": { group: "Auto & EV", color: "emerald" },
      "EICHER": { group: "Auto & EV", color: "emerald" },
      "OLA ELECTRIC": { group: "Auto & EV", color: "emerald" },
      "OLA ELEC": { group: "Auto & EV", color: "emerald" },

      "HAL": { group: "Defence & Engg", color: "sky" },
      "BEL": { group: "Defence & Engg", color: "sky" },
      "BHEL": { group: "Defence & Engg", color: "sky" },
      "BDL": { group: "Defence & Engg", color: "sky" },
      "L&T": { group: "Defence & Engg", color: "sky" },
      "LT": { group: "Defence & Engg", color: "sky" },
      "RVNL": { group: "Defence & Engg", color: "sky" },
      "POLYCAB": { group: "Defence & Engg", color: "sky" },
      "DIXON": { group: "Defence & Engg", color: "sky" },
      "V-GUARD": { group: "Defence & Engg", color: "sky" },
      "INDO-MIM": { group: "Defence & Engg", color: "sky" },

      "TATA STEEL": { group: "Metals & Mining", color: "slate" },
      "JSW STEEL": { group: "Metals & Mining", color: "slate" },
      "SAIL": { group: "Metals & Mining", color: "slate" },
      "HINDALCO": { group: "Metals & Mining", color: "slate" },
      "VEDANTA": { group: "Metals & Mining", color: "slate" },

      "SUN PHARMA": { group: "Pharma", color: "teal" },
      "CIPLA": { group: "Pharma", color: "teal" },
      "DR REDDY": { group: "Pharma", color: "teal" },
      "NATCO PHARMA": { group: "Pharma", color: "teal" },
      "GUJARAT THEMIS": { group: "Pharma", color: "teal" },

      "ITC": { group: "Consumer & Retail", color: "rose" },
      "TITAN": { group: "Consumer & Retail", color: "rose" },
      "TRENT": { group: "Consumer & Retail", color: "rose" },
      "DMART": { group: "Consumer & Retail", color: "rose" },
      "ASIAN PAINTS": { group: "Consumer & Retail", color: "rose" },
      "ULTRATECH": { group: "Consumer & Retail", color: "rose" },

      "BHARTI AIRTEL": { group: "Telecom & Aviation", color: "indigo" },
      "AIRTEL": { group: "Telecom & Aviation", color: "indigo" },
      "AIR INDIA": { group: "Telecom & Aviation", color: "indigo" },
      "JIO": { group: "Telecom & Aviation", color: "indigo" },

      "DLF": { group: "Realty & Conglom", color: "amber" },
      "GODREJ": { group: "Realty & Conglom", color: "amber" },
      "TATA SONS": { group: "Realty & Conglom", color: "amber" },
      "TATA TRUSTS": { group: "Realty & Conglom", color: "amber" }
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

      // --- SECTION 1: CATEGORIES TREE CARD (OPEN BY DEFAULT - 1 LEVEL LARGER FONT) ---
      const catCard = document.createElement("div");
      catCard.className = "rounded-lg bg-white dark:bg-[#0E1322] border border-slate-200 dark:border-slate-800 shadow-xs overflow-hidden";
      
      const isCatOpen = treeState.categories;
      catCard.innerHTML = `
        <div class="px-2.5 py-1.5 bg-slate-50 dark:bg-slate-900/90 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between cursor-pointer select-none" onclick="toggleTreeNode('categories')">
          <div class="flex items-center gap-1.5 text-[13.5px] font-sans font-bold text-slate-900 dark:text-slate-100">
            <span class="text-amber-600 dark:text-amber-400 text-[11px]">${isCatOpen ? '▼' : '▶'}</span>
            <span>📁 Categories</span>
            <span class="text-[11.5px] text-slate-500 dark:text-slate-400 font-mono">(${coreNewsItems.length + deskItems.length})</span>
          </div>
          ${selectedFeedCategory !== 'ALL' ? `<button onclick="event.stopPropagation(); onCategorySelect('ALL');" class="text-[10.5px] font-mono text-amber-600 dark:text-amber-400 font-bold hover:underline">Reset (✕)</button>` : ''}
        </div>
      `;

      if (isCatOpen) {
        const catBody = document.createElement("div");
        catBody.className = "p-1.5 flex flex-col gap-1 text-[13.5px] font-sans";

        // Sub-group: Core News Desks
        const coreDiv = document.createElement("div");
        coreDiv.className = "flex flex-col gap-0.5";
        coreDiv.innerHTML = `<span class="text-[11px] font-bold uppercase text-slate-400 dark:text-slate-500 px-1 mb-0.5 tracking-wider">📰 Core Desks</span>`;

        coreNewsItems.forEach(item => {
          const isSelected = selectedFeedCategory === item.id;
          const btn = document.createElement("button");
          btn.className = `w-full text-left px-2 py-1 rounded flex items-center justify-between transition-colors cursor-pointer ${isSelected ? 'bg-indigo-600 text-white font-bold shadow-xs' : 'text-[#090D16] dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800/60 font-medium'}`;
          btn.innerHTML = `
            <span class="flex items-center gap-1.5 min-w-0 truncate">
              <span class="text-slate-400 select-none text-[11px] ${isSelected ? 'text-white' : ''}">├─</span>
              <span class="truncate text-[13.5px]">${item.label}</span>
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
        const deskDiv = document.createElement("div");
        deskDiv.className = "flex flex-col gap-0.5 pt-1.5 border-t border-slate-100 dark:border-slate-800";
        deskDiv.innerHTML = `<span class="text-[11px] font-bold uppercase text-amber-700 dark:text-amber-400 px-1 mb-0.5 tracking-wider">🏛️ Specialized Desks</span>`;

        deskItems.forEach(item => {
          const isSelected = selectedFeedCategory === item.id || (item.id === 'IPO_ALL' && currentView === 'ipo') || (item.id === 'CORPORATE_ALL' && currentView === 'corporate');
          const btn = document.createElement("button");
          btn.className = `w-full text-left px-2 py-1 rounded flex items-center justify-between transition-colors cursor-pointer ${isSelected ? 'bg-amber-700 text-white font-bold shadow-xs' : 'text-[#090D16] dark:text-slate-200 hover:bg-amber-50/60 dark:hover:bg-amber-950/30 font-medium'}`;
          btn.innerHTML = `
            <span class="flex items-center gap-1.5 min-w-0 truncate">
              <span class="text-slate-400 select-none text-[11px] ${isSelected ? 'text-white' : ''}">├─</span>
              <span class="truncate text-[13.5px]">${item.label}</span>
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
          <div class="flex items-center gap-1.5 text-[13.5px] font-sans font-bold text-slate-900 dark:text-slate-100">
            <span class="text-indigo-600 dark:text-indigo-400 text-[11px]">${isSecOpen ? '▼' : '▶'}</span>
            <span>📈 Industry Sectors</span>
            <span class="text-[11.5px] text-slate-500 dark:text-slate-400 font-mono">(${sortedSecs.length})</span>
          </div>
          ${activeSectorFilter ? `<button onclick="event.stopPropagation(); activeSectorFilter = null; renderCategoriesAndStocksSidebar(); renderFeedList();" class="text-[10.5px] font-mono text-indigo-600 dark:text-indigo-400 font-bold hover:underline">Clear (✕)</button>` : ''}
        </div>
      `;

      if (isSecOpen) {
        const secBody = document.createElement("div");
        secBody.className = "p-1.5 flex flex-col gap-0.5 text-[13.5px] font-sans max-h-[260px] overflow-y-auto";

        sortedSecs.forEach(sec => {
          const isSelected = activeSectorFilter === sec;
          const btn = document.createElement("button");
          btn.className = `w-full text-left px-2 py-1 rounded flex items-center justify-between transition-colors cursor-pointer ${isSelected ? 'bg-indigo-600 text-white font-bold shadow-xs' : 'text-[#090D16] dark:text-slate-200 hover:bg-indigo-50/60 dark:hover:bg-indigo-950/30 font-medium'}`;
          btn.innerHTML = `
            <span class="flex items-center gap-1.5 min-w-0 truncate">
              <span class="text-slate-400 select-none text-[11px] ${isSelected ? 'text-white' : ''}">├─</span>
              <span class="truncate text-[13.5px]">${sec}</span>
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

      // --- SECTION 3: COMPANY STOCKS CLUSTERED & COLOR-CODED ---
      const stockCounts = {};
      stories.forEach(s => {
        (s.stocks || []).forEach(stk => stockCounts[stk] = (stockCounts[stk] || 0) + 1);
      });
      const activeStockKeys = Object.keys(stockCounts);

      // Group detected stocks by similar cluster
      const clusters = {};
      activeStockKeys.forEach(stk => {
        const info = stockClusterMap[stk] || { group: "Other Companies", color: "slate" };
        const gName = info.group;
        if (!clusters[gName]) clusters[gName] = { color: info.color, stocks: [] };
        clusters[gName].stocks.push({ ticker: stk, count: stockCounts[stk] });
      });

      // Sort clusters and stocks inside each cluster
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
          <div class="flex items-center gap-1.5 text-[13.5px] font-sans font-bold text-slate-900 dark:text-slate-100">
            <span class="text-amber-600 dark:text-amber-400 text-[11px]">${isStockOpen ? '▼' : '▶'}</span>
            <span>🏢 Company Stocks</span>
            <span class="text-[11.5px] text-slate-500 dark:text-slate-400 font-mono">(${activeStockKeys.length})</span>
          </div>
          ${activeStockFilter ? `<button onclick="event.stopPropagation(); activeStockFilter = null; renderCategoriesAndStocksSidebar(); renderFeedList();" class="text-[10.5px] font-mono text-indigo-600 dark:text-indigo-400 font-bold hover:underline">Clear (✕)</button>` : ''}
        </div>
      `;

      if (isStockOpen) {
        const stockBody = document.createElement("div");
        stockBody.className = "p-1.5 flex flex-col gap-1.5 text-[13px] font-sans max-h-[320px] overflow-y-auto";

        clusterEntries.forEach(([gName, gData]) => {
          const gDiv = document.createElement("div");
          gDiv.className = "flex flex-col gap-0.5";
          
          // Color coding themes
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

          const activeColor = colorStyles[gData.color] || colorStyles.slate;

          gDiv.innerHTML = `<span class="text-[10.5px] font-bold uppercase px-1 text-slate-500 dark:text-slate-400 tracking-wider mb-0.5">${gName}</span>`;

          gData.stocks.sort((a, b) => b.count - a.count).forEach(stkItem => {
            const isSelected = activeStockFilter === stkItem.ticker;
            const btn = document.createElement("button");
            
            const btnStyle = isSelected
              ? "bg-amber-600 text-white font-bold shadow-xs border border-amber-600"
              : `hover:opacity-90 border font-medium ${activeColor}`;

            btn.className = `w-full text-left px-2 py-0.5 rounded text-[12.5px] flex items-center justify-between transition-colors cursor-pointer mb-0.5 ${btnStyle}`;
            btn.innerHTML = `
              <span class="flex items-center gap-1 min-w-0 truncate">
                <span class="truncate font-mono font-bold">${stkItem.ticker}</span>
              </span>
              <span class="text-[11px] font-mono shrink-0 ml-1 ${isSelected ? 'text-white' : 'opacity-80'}">(${stkItem.count})</span>
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

    function clearAllStockAndSectorFilters"""

    html = re.sub(old_sidebar_code_pattern, new_sidebar_code, html, flags=re.DOTALL)

    with open('web/index.html', 'w', encoding='utf-8') as f:
        f.write(html)

    print("Successfully updated with clustered color-coded stocks and bumped font sizes!")

if __name__ == '__main__':
    update_all()
