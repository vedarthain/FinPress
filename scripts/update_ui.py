import re

def update_html():
    with open('web/index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Replace the dual top ribbons with a single consolidated top header ribbon
    old_top_header_pattern = r'<!-- ================= 1\. TOPMOST MARKET PULSE & CALENDAR RIBBON ================= -->.*?<!-- ================= MAIN THREE-COLUMN WORKSPACE'
    
    new_top_header = """<!-- ================= 1. UNIFIED TOP NAVIGATION & CONTROLS RIBBON ================= -->
    <header class="sticky top-0 z-50 bg-[#0B0F19] dark:bg-[#070B14] border-b border-slate-800 text-slate-100 shadow-md px-3 py-1.5 flex items-center justify-between gap-2.5 overflow-x-auto whitespace-nowrap text-[12px] font-mono">
      
      <!-- Left: FinPress Branding & Front Page Tab -->
      <div class="flex items-center gap-2 shrink-0">
        <div class="flex items-center gap-1.5 shrink-0 cursor-pointer" onclick="switchView('feed')">
          <div class="w-6.5 h-6.5 rounded bg-amber-600 flex items-center justify-center shadow-xs border border-amber-500/50">
            <span class="text-white text-[11px] font-extrabold tracking-tight font-mono">FP</span>
          </div>
          <span class="text-[15px] font-extrabold tracking-tight text-white font-mono mr-1">
            Fin<span class="text-amber-400">Press</span>
          </span>
        </div>

        <!-- Front Page Tab (Right next to FinPress) -->
        <nav class="flex items-center bg-slate-900/90 p-0.5 rounded-lg border border-slate-700">
          <button id="tab-btn-anchor" onclick="switchView('anchor')" class="px-2.5 py-0.5 rounded-md transition-all text-slate-300 hover:text-white hover:bg-slate-800 flex items-center gap-1.5 font-semibold">
            <span>📰 Front Page</span>
            <span id="tab-anchor-count" class="px-1.5 py-0.2 rounded text-[10px] bg-amber-500/20 text-amber-300 font-bold">0</span>
          </button>
        </nav>
      </div>

      <!-- Center Controls (All News Dropdown + Specialized Desks + Sentiment Filters) -->
      <div class="flex items-center gap-2 shrink-0">
        <div id="feed-controls" class="flex items-center gap-2">
          <!-- 1. All News Dropdown -->
          <select id="category-select" onchange="onCategorySelect(this.value)" class="text-[11.5px] font-medium px-2.5 py-1 rounded-md border border-slate-700 bg-slate-900 text-slate-100 focus:outline-none focus:ring-1 focus:ring-amber-500 cursor-pointer shadow-2xs font-mono">
            <option value="ALL">⚡ All News (0)</option>
            <option value="Sector">Sector (0)</option>
            <option value="Economy">Economy (0)</option>
            <option value="Policy">Policy (0)</option>
            <option value="Market">Market (0)</option>
            <option value="Trade">Trade & FX (0)</option>
            <option value="International News">International (0)</option>
            <option value="Others">General Features (0)</option>
          </select>

          <!-- 2. Specialized Desks Dropdown -->
          <select id="desk-select" onchange="onDeskSelect(this.value)" class="text-[11.5px] font-bold px-2.5 py-1 rounded-md border border-amber-500/60 bg-amber-950/40 text-amber-300 focus:outline-none focus:ring-1 focus:ring-amber-400 cursor-pointer shadow-2xs font-mono">
            <option value="" disabled selected>🏛️ Specialized Desks ▾</option>
            <option value="ipo">🚀 IPO Central (0)</option>
            <option value="corporate">🏢 Corporate (0)</option>
            <option value="opinions">✍️ Opinions (0)</option>
          </select>

          <!-- Sentiment Filter Buttons -->
          <div class="flex items-center bg-slate-900 p-0.5 rounded-lg border border-slate-800 text-[11px] font-mono">
            <button id="sent-all" onclick="setFeedSentiment('ALL')" class="px-2.5 py-0.5 rounded-md bg-slate-700 text-white shadow-xs font-bold">
              All (<span id="feed-count-all">0</span>)
            </button>
            <button id="sent-bullish" onclick="setFeedSentiment('BULLISH')" class="px-2 py-0.5 rounded-md text-emerald-400 hover:bg-emerald-950/40 flex items-center gap-0.5 font-medium">
              <span>🟢</span> (<span id="feed-count-bullish">0</span>)
            </button>
            <button id="sent-bearish" onclick="setFeedSentiment('BEARISH')" class="px-2 py-0.5 rounded-md text-rose-400 hover:bg-rose-950/40 flex items-center gap-0.5 font-medium">
              <span>🔴</span> (<span id="feed-count-bearish">0</span>)
            </button>
          </div>
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

    html = re.sub(old_top_header_pattern, new_top_header, html, flags=re.DOTALL)

    # 2. Update Column 2 and Column 3 sticky top values and layout
    html = html.replace('lg:sticky lg:top-[70px]', 'lg:sticky lg:top-[44px]')

    # 3. Replace Column 3 HTML structure so Categories, Sectors, and Stocks are clearly structured without inner scroll cutoffs
    old_col3_pattern = r'<!-- COLUMN 3: RIGHT HAND SIDE PANEL \(CATEGORIES & STOCKS IN FOCUS\) -->.*?</aside>'
    new_col3 = """<!-- COLUMN 3: RIGHT HAND SIDE PANEL (CATEGORIES, SECTORS & STOCKS AT A GLANCE) -->
        <aside class="flex flex-col gap-2 lg:sticky lg:top-[44px] lg:max-h-[calc(100vh-3.5rem)] lg:overflow-y-auto">
          
          <!-- 1. Categories in Focus Card (All News + Specialized Desks) -->
          <div class="rounded-lg bg-white dark:bg-[#0E1322] border border-slate-200 dark:border-slate-800 p-2.5 shadow-xs flex flex-col gap-1.5">
            <div class="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-1">
              <span class="text-[11px] font-bold uppercase tracking-wider text-slate-900 dark:text-slate-100 flex items-center gap-1 font-mono">
                <span>📁</span> <span>Categories in Focus</span>
              </span>
              <button id="clear-category-filter" onclick="onCategorySelect('ALL')" class="hidden text-[10px] font-mono text-amber-600 dark:text-amber-400 font-bold hover:underline">
                Reset (✕)
              </button>
            </div>
            <div id="categories-focus-list" class="flex flex-wrap gap-1 pt-0.5">
              <!-- Dynamically populated category & desk chips -->
            </div>
          </div>

          <!-- 2. Industry Sectors in Focus Card -->
          <div class="rounded-lg bg-white dark:bg-[#0E1322] border border-slate-200 dark:border-slate-800 p-2.5 shadow-xs flex flex-col gap-1.5">
            <div class="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-1">
              <span class="text-[11px] font-bold uppercase tracking-wider text-indigo-900 dark:text-indigo-300 flex items-center gap-1 font-mono">
                <span>📈</span> <span>Industry Sectors</span>
              </span>
              <span id="sectors-count-label" class="text-[10px] font-mono text-slate-400 font-bold">0 Sectors</span>
            </div>
            <div id="industry-sectors-focus-list" class="flex flex-wrap gap-1 pt-0.5">
              <!-- Dynamically populated industry sector chips -->
            </div>
          </div>

          <!-- 3. Company Stocks in Focus Card -->
          <div class="rounded-lg bg-white dark:bg-[#0E1322] border border-slate-200 dark:border-slate-800 p-2.5 shadow-xs flex flex-col gap-1.5">
            <div class="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-1">
              <span class="text-[11px] font-bold uppercase tracking-wider text-amber-900 dark:text-amber-400 flex items-center gap-1 font-mono">
                <span>🏢</span> <span>Stocks in Focus</span>
              </span>
              <div class="flex items-center gap-1.5">
                <span id="stocks-count-label" class="text-[10px] font-mono text-slate-400 font-bold">0 Tickers</span>
                <button id="clear-stock-filter" onclick="clearAllStockAndSectorFilters()" class="hidden text-[10px] font-mono text-indigo-600 dark:text-indigo-400 font-bold hover:underline">
                  Clear (✕)
                </button>
              </div>
            </div>
            <div id="stocks-focus-list" class="flex flex-wrap gap-1 pt-0.5">
              <!-- Dynamically populated company stock chips -->
            </div>
          </div>

        </aside>"""

    html = re.sub(old_col3_pattern, new_col3, html, flags=re.DOTALL)

    # 4. Update Story Modal so Catalyst is directly below Executive Gist
    old_modal_cards_pattern = r'<!-- ⚡ EXECUTIVE GIST \(INDIGO CARD\) -->.*?<!-- 💡 TRADER CATALYST \(DYNAMIC EMERALD/ROSE/SLATE CARD\) -->\s*<div id="story-modal-catalyst-box".*?</div>\s*</div>'
    
    new_modal_cards = """<!-- ⚡ EXECUTIVE GIST (INDIGO CARD) -->
      <div class="p-3 rounded-xl bg-indigo-50/80 dark:bg-[#10182E] border border-indigo-200/90 dark:border-indigo-800 shadow-2xs">
        <p class="text-[11px] font-mono uppercase tracking-wider font-extrabold text-indigo-950 dark:text-indigo-300 mb-1 flex items-center gap-1">
          <span>⚡</span> <span>1. Executive Gist (Core Takeaway)</span>
        </p>
        <div id="story-modal-brief" class="space-y-1.5"></div>
      </div>

      <!-- 💡 TRADER CATALYST (DYNAMIC EMERALD/ROSE/SLATE CARD - DIRECTLY BELOW GIST) -->
      <div id="story-modal-catalyst-box" class="p-3 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-[#11172A] shadow-2xs">
        <p class="text-[11px] font-mono uppercase tracking-wider font-bold text-slate-600 dark:text-slate-300 mb-1 flex items-center gap-1">
          <span>💡</span> <span>2. Trader Catalyst & Market Impact</span>
        </p>
        <div id="story-modal-catalyst" class="text-xs text-slate-800 dark:text-slate-200 leading-relaxed font-medium bg-white dark:bg-[#0B1020] p-2.5 rounded-lg border border-slate-200/80 dark:border-slate-800"></div>
      </div>

      <!-- 📌 KEY ANALYST DATA POINTS (NEWSPAPER BROADSHEET CARD) -->
      <div class="p-3 rounded-xl bg-[#F5EFEB] dark:bg-[#1E1914]/70 border border-[#B8A38E]/80 dark:border-[#524434] shadow-2xs">
        <p class="text-[11px] font-mono uppercase tracking-wider font-extrabold text-[#2E1F14] dark:text-[#F3ECE4] mb-1.5 flex items-center gap-1">
          <span>📌</span> <span>3. Key Analyst Data Points</span>
        </p>
        <ul id="story-modal-bullets" class="space-y-1.5">
          <!-- Bullets -->
        </ul>
      </div>"""

    html = re.sub(old_modal_cards_pattern, new_modal_cards, html, flags=re.DOTALL)

    # 5. Update renderActiveStoryDetail in JavaScript
    old_render_detail_pattern = r'<!-- 2-COLUMN SIDE-BY-SIDE GRID FOR SECTION 1 & SECTION 2 -->.*?<!-- 💡 SECTION 3 \(BELOW\): CATALYST RATIONALE & TRADER IMPACT -->\s*<div class="mt-3 p-3.5 rounded-xl border-2.*?</div>\s*</div>'

    new_render_detail = """<!-- 2-COLUMN SIDE-BY-SIDE GRID: LEFT (GIST + CATALYST) & RIGHT (KEY ANALYST DATA POINTS) -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-3 items-start mt-2">
          
          <!-- LEFT COLUMN (lg:col-span-6): CORE TRADER TAKEAWAY + CATALYST DIRECTLY BELOW -->
          <div class="lg:col-span-6 flex flex-col gap-2.5">
            
            <!-- ⚡ SECTION 1: EXECUTIVE GIST (CORE TAKEAWAY) -->
            <div class="rounded-xl border-2 border-indigo-400/80 dark:border-indigo-700 bg-indigo-50/70 dark:bg-[#151930] p-3 shadow-xs flex flex-col gap-2">
              <div class="flex items-center justify-between border-b border-indigo-200/90 dark:border-indigo-900/60 pb-1">
                <span class="text-[11.5px] font-mono font-extrabold uppercase tracking-wider text-indigo-950 dark:text-indigo-200 flex items-center gap-1.5">
                  <span>⚡</span> <span>1. Executive Gist</span>
                </span>
                <span class="text-[10px] font-mono font-bold px-2 py-0.2 rounded bg-indigo-200/80 text-indigo-950 dark:bg-indigo-900/80 dark:text-indigo-200">Quick Read</span>
              </div>
              <div class="space-y-1.5">
                ${briefSentences.map(sent => `
                  <div class="flex items-start gap-1.5 text-[13.5px] text-slate-950 dark:text-slate-100 leading-snug font-medium">
                    <span class="text-indigo-600 dark:text-indigo-400 font-bold select-none mt-0.5">▸</span>
                    <span>${highlightSearchTokens(highlightNumbers(sent), queryTokens)}</span>
                  </div>
                `).join('')}
              </div>
            </div>

            <!-- 💡 SECTION 2: TRADER CATALYST & IMPACT ANALYSIS (PLACED DIRECTLY BELOW EXECUTIVE GIST!) -->
            <div class="p-3 rounded-xl border-2 ${isBullish ? 'border-emerald-500 bg-emerald-50/80 dark:bg-[#064E3B]/30 dark:border-emerald-600' : isBearish ? 'border-rose-500 bg-rose-50/80 dark:bg-[#881337]/30 dark:border-rose-600' : 'border-slate-400 bg-slate-50 dark:bg-slate-900/50 dark:border-slate-700'} shadow-xs flex flex-col gap-2">
              <div class="flex items-center justify-between border-b ${isBullish ? 'border-emerald-200 dark:border-emerald-900/60' : isBearish ? 'border-rose-200 dark:border-rose-900/60' : 'border-slate-200 dark:border-slate-800'} pb-1">
                <span class="text-[11.5px] font-mono font-extrabold uppercase tracking-wider ${isBullish ? 'text-emerald-950 dark:text-emerald-300' : isBearish ? 'text-rose-950 dark:text-rose-300' : 'text-slate-900 dark:text-slate-200'} flex items-center gap-1.5">
                  <span>💡</span> <span>2. Catalyst & Market Impact</span>
                </span>
                <span class="text-[10px] font-mono font-extrabold uppercase px-2 py-0.2 rounded ${isBullish ? 'bg-emerald-200 text-emerald-950 dark:bg-emerald-900 dark:text-emerald-200' : isBearish ? 'bg-rose-200 text-rose-950 dark:bg-rose-900 dark:text-rose-200' : 'bg-slate-200 text-slate-900 dark:bg-slate-800 dark:text-slate-200'}">${story.sentiment} THESIS</span>
              </div>
              <div class="text-[13.5px] text-slate-950 dark:text-slate-100 leading-snug font-medium">
                ${highlightSearchTokens(highlightNumbers(story.sentimentReasoning), queryTokens)}
              </div>
            </div>

          </div>

          <!-- RIGHT COLUMN (lg:col-span-6): KEY ANALYST DATA POINTS -->
          <div class="lg:col-span-6 flex flex-col gap-2">
            
            <!-- 📌 SECTION 3: KEY ANALYST DATA POINTS -->
            <div class="rounded-xl border-2 border-[#B8A38E] dark:border-[#524434] bg-[#FDFBF7] dark:bg-[#191512] p-3 shadow-xs flex flex-col gap-2">
              <div class="flex items-center justify-between border-b border-[#E8DCCE] dark:border-[#382E25] pb-1">
                <span class="text-[11.5px] font-mono font-extrabold uppercase tracking-wider text-[#2E1F14] dark:text-[#F3ECE4] flex items-center gap-1.5">
                  <span>📌</span> <span>3. Key Analyst Data Points</span>
                </span>
                <span class="text-[10px] font-mono font-bold px-2 py-0.2 rounded bg-[#EFE5D9] text-[#291B10] dark:bg-[#32261C] dark:text-[#E8DCCF] border border-[#CCAFA0]/50">Metrics & Facts</span>
              </div>
              <ul class="space-y-2">
                ${(story.bullet_points || []).map(bp => `
                  <li class="flex items-start gap-1.5 text-[13.5px] text-slate-950 dark:text-slate-100 leading-snug font-medium">
                    <span class="text-[#8C5E3C] dark:text-[#CBB09C] font-bold select-none mt-0.5">›</span>
                    <span>${highlightSearchTokens(highlightNumbers(bp), queryTokens)}</span>
                  </li>
                `).join('')}
              </ul>
            </div>

          </div>

        </div>"""

    html = re.sub(old_render_detail_pattern, new_render_detail, html, flags=re.DOTALL)

    # 6. Make chips in renderCategoriesAndStocksSidebar compact and clear
    # Replace chip classes in JS
    html = html.replace('btn.className = `px-2 py-0.5 rounded text-[11px]', 'btn.className = `px-1.5 py-0.5 rounded text-[10.5px]')
    
    with open('web/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("web/index.html updated successfully!")

if __name__ == '__main__':
    update_html()
