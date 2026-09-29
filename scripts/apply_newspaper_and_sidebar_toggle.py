import re

def update_all():
    with open('web/index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Update Top Header with Newspaper Salmon Broadsheet Color + 3rd Col Hide/Unhide Toggle
    old_header_pattern = r'<!-- ================= 1\. UNIFIED TOP NAVIGATION & CONTROLS RIBBON ================= -->.*?<!-- ================= MAIN THREE-COLUMN WORKSPACE'
    
    new_header = """<!-- ================= 1. UNIFIED TOP NAVIGATION & CONTROLS RIBBON (NEWSPAPER BROADSHEET) ================= -->
    <header class="sticky top-0 z-50 bg-[#FBE8D8] dark:bg-[#0E1320] border-b-2 border-[#DFC0A5] dark:border-slate-800 text-[#1C1917] dark:text-slate-100 shadow-sm px-3 py-1.5 flex items-center justify-between gap-3 overflow-x-auto whitespace-nowrap text-[12px] font-mono">
      
      <!-- Left: FinPress Branding & Live Market Pulse -->
      <div class="flex items-center gap-3 shrink-0">
        <div class="flex items-center gap-1.5 shrink-0 cursor-pointer" onclick="onCategorySelect('ALL')" title="Reset to All News">
          <div class="w-6.5 h-6.5 rounded bg-[#1C1917] dark:bg-amber-600 flex items-center justify-center shadow-xs border border-amber-900/40">
            <span class="text-[#FDF2E9] text-[11px] font-bold tracking-tight font-mono">FP</span>
          </div>
          <span class="text-[15px] font-bold tracking-tight text-[#1C1917] dark:text-white mr-1 font-mono">
            Fin<span class="text-amber-800 dark:text-amber-400">Press</span>
          </span>
        </div>

        <!-- Live Market Pulse Key Data in Newspaper Broadsheet Tone -->
        <div class="flex items-center gap-3 text-[11.5px] border-l border-[#D5B599] dark:border-slate-800 pl-3">
          <span class="text-[#3D2817] dark:text-slate-300 font-medium">NIFTY <b class="text-emerald-700 dark:text-emerald-400 font-bold font-mono">24,835 (+0.64%)</b></span>
          <span class="text-[#3D2817] dark:text-slate-300 font-medium">BANK NIFTY <b class="text-emerald-700 dark:text-emerald-400 font-bold font-mono">54,120 (+0.82%)</b></span>
          <span class="text-[#3D2817] dark:text-slate-300 font-medium">INDIA VIX <b class="text-rose-700 dark:text-rose-400 font-bold font-mono">12.85 (-3.2%)</b></span>
          <span class="text-[#3D2817] dark:text-slate-300 font-medium">BRENT <b class="text-amber-800 dark:text-amber-300 font-bold font-mono">$74.2/bbl</b></span>
          <span class="text-[#3D2817] dark:text-slate-300 font-medium">USD/INR <b class="text-[#1C1917] dark:text-slate-100 font-bold font-mono">₹83.65</b></span>
        </div>
      </div>

      <!-- Right: Hide/Unhide 3rd Col + Search + Calendar + Status + Total + Font + Theme -->
      <div class="flex items-center gap-2 shrink-0">
        
        <!-- Toggle 3rd Column Button (Hide / Show) -->
        <button id="toggle-sidebar-btn" onclick="toggleSidebar()" class="px-2 py-1 rounded-md border border-[#D5B599] dark:border-slate-700 bg-white/85 dark:bg-slate-900 text-[#1C1917] dark:text-slate-200 hover:bg-white dark:hover:bg-slate-800 flex items-center gap-1 font-mono text-[11px] font-bold shadow-2xs cursor-pointer transition-all" title="Hide or Unhide 3rd Column (Sidebar)">
          <span>◧</span>
          <span id="sidebar-toggle-text">Hide 3rd Col</span>
        </button>

        <div class="relative w-36 sm:w-44">
          <input type="text" id="global-search" oninput="onSearchInput()" placeholder="Search stock or news..." class="w-full text-[11.5px] pl-6 pr-5 py-1 rounded-md border border-[#D5B599] dark:border-slate-700 bg-white/90 dark:bg-slate-900 text-[#1C1917] dark:text-slate-100 placeholder-[#8C6D58] dark:placeholder-slate-400 focus:outline-none focus:border-amber-700 font-mono shadow-2xs"/>
          <span class="absolute left-1.5 top-1.5 text-slate-500 text-[10.5px]">🔍</span>
          <button id="clear-search-btn" onclick="clearSearch()" class="hidden absolute right-1.5 top-1 text-slate-500 hover:text-black dark:hover:text-white text-[11px] font-bold p-0.5">✕</button>
        </div>

        <!-- Historical Calendar & Edition Navigation -->
        <div class="flex items-center gap-0.5 bg-white/80 dark:bg-slate-900 p-0.5 rounded-md border border-[#D5B599] dark:border-slate-700/80 font-mono text-[11.5px]">
          <button onclick="navigateDate(-1)" class="px-1.5 py-0.5 rounded hover:bg-black/10 dark:hover:bg-slate-800 text-[#1C1917] dark:text-slate-300 font-bold" title="Previous Date (◀)">◀</button>
          <div class="flex items-center gap-1 px-1 py-0.5 bg-[#FBE8D8]/90 dark:bg-black/60 rounded border border-[#DFC0A5] dark:border-slate-800">
            <span class="text-slate-600 dark:text-slate-400 text-[10.5px]">📅</span>
            <input type="date" id="calendar-picker" onchange="onCalendarSelect(this.value)" class="bg-transparent text-[#1C1917] dark:text-slate-100 font-bold font-mono text-[11.5px] focus:outline-none cursor-pointer [color-scheme:light] dark:[color-scheme:dark] max-w-[105px]"/>
          </div>
          <button onclick="navigateDate(1)" class="px-1.5 py-0.5 rounded hover:bg-black/10 dark:hover:bg-slate-800 text-[#1C1917] dark:text-slate-300 font-bold" title="Next Date (▶)">▶</button>
        </div>

        <div id="source-health-container" class="flex items-center gap-1 font-mono text-[10.5px]"></div>

        <span id="total-news-counter-badge" class="px-2 py-0.5 rounded bg-emerald-600/15 border border-emerald-600/30 text-emerald-900 dark:text-emerald-400 font-extrabold font-mono text-[11.5px]">
          🔥 <b id="top-total-count">0</b>
        </span>

        <!-- Font Size Controls -->
        <div class="flex items-center bg-white/80 dark:bg-slate-900 p-0.5 rounded-md border border-[#D5B599] dark:border-slate-700 text-[11px] font-mono font-semibold">
          <button onclick="adjustFontSize(-1)" class="px-1.5 py-0.5 rounded text-[#1C1917] dark:text-slate-300 hover:bg-black/10 dark:hover:bg-slate-800" title="Decrease Font Size (A-)">A-</button>
          <span id="font-size-label" class="px-1 text-[9.5px] text-slate-700 dark:text-slate-400 select-none">100%</span>
          <button onclick="adjustFontSize(1)" class="px-1.5 py-0.5 rounded text-[#1C1917] dark:text-slate-300 hover:bg-black/10 dark:hover:bg-slate-800" title="Increase Font Size (A+)">A+</button>
        </div>

        <button onclick="toggleTheme()" class="w-6.5 h-6.5 rounded-md border border-[#D5B599] dark:border-slate-700 bg-white/80 dark:bg-slate-900 text-[#1C1917] dark:text-slate-300 hover:bg-white dark:hover:text-white flex items-center justify-center text-[11px] shadow-xs" title="Toggle Light/Dark Theme">
          <span id="theme-icon">🌙</span>
        </button>
      </div>

    </header>

    <!-- ================= MAIN THREE-COLUMN WORKSPACE"""

    html = re.sub(old_header_pattern, new_header, html, flags=re.DOTALL)

    # 2. Add id="view-feed-aside" to <aside>
    html = html.replace('<aside class="flex flex-col gap-2 lg:sticky lg:top-[44px] lg:max-h-[calc(100vh-3.5rem)] lg:overflow-y-auto">', '<aside id="view-feed-aside" class="flex flex-col gap-2 lg:sticky lg:top-[44px] lg:max-h-[calc(100vh-3.5rem)] lg:overflow-y-auto transition-all">')

    # 3. Update Headline and Description Font & Styling to match image
    old_detail_body_pattern = r'<!-- 2-COLUMN SIDE-BY-SIDE GRID: LEFT \(GIST \+ CATALYST\) & RIGHT \(KEY ANALYST DATA POINTS\) -->.*?function highlightNumbers'

    new_detail_body = """<!-- 2-COLUMN SIDE-BY-SIDE GRID: LEFT (GIST + CATALYST) & RIGHT (KEY ANALYST DATA POINTS) -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-3.5 items-start mt-2.5">
          
          <!-- LEFT COLUMN (lg:col-span-6): CORE TRADER TAKEAWAY + CATALYST DIRECTLY BELOW -->
          <div class="lg:col-span-6 flex flex-col gap-3">
            
            <!-- ⚡ SECTION 1: EXECUTIVE GIST (MATCHING ATTACHED IMAGE FONT & LINE SPACING) -->
            <div class="rounded-xl border-2 border-indigo-300 dark:border-indigo-800 bg-indigo-50/60 dark:bg-[#13182E] p-3.5 shadow-xs flex flex-col gap-2.5">
              <div class="flex items-center justify-between border-b border-indigo-200/90 dark:border-indigo-900/60 pb-1.5">
                <span class="text-[12px] font-mono font-extrabold uppercase tracking-wider text-indigo-950 dark:text-indigo-200 flex items-center gap-1.5">
                  <span>⚡</span> <span>1. Executive Gist</span>
                </span>
                <span class="text-[10.5px] font-mono font-bold px-2 py-0.5 rounded bg-indigo-200/80 text-indigo-950 dark:bg-indigo-900/80 dark:text-indigo-200">Key Takeaway</span>
              </div>
              <div class="space-y-2.5">
                ${briefSentences.map(sent => `
                  <div class="flex items-start gap-2.5 bg-white/95 dark:bg-[#0E1322] p-3 rounded-lg border border-indigo-100 dark:border-slate-800 text-[14.5px] sm:text-[15px] text-[#24374E] dark:text-[#E2E8F0] leading-[1.6] font-normal shadow-2xs font-sans tracking-tight">
                    <span class="text-indigo-600 dark:text-indigo-400 font-bold select-none mt-0.5">▸</span>
                    <span class="leading-[1.6]">${highlightSearchTokens(highlightNumbers(sent), queryTokens)}</span>
                  </div>
                `).join('')}
              </div>
            </div>

            <!-- 💡 SECTION 2: TRADER CATALYST & IMPACT ANALYSIS (PLACED DIRECTLY BELOW EXECUTIVE GIST!) -->
            <div class="p-3.5 rounded-xl border-2 ${isBullish ? 'border-emerald-500 bg-emerald-50/70 dark:bg-[#064E3B]/30 dark:border-emerald-600' : isBearish ? 'border-rose-500 bg-rose-50/70 dark:bg-[#881337]/30 dark:border-rose-600' : 'border-slate-400 bg-slate-50 dark:bg-slate-900/50 dark:border-slate-700'} shadow-xs flex flex-col gap-2.5">
              <div class="flex items-center justify-between border-b ${isBullish ? 'border-emerald-200 dark:border-emerald-900/60' : isBearish ? 'border-rose-200 dark:border-rose-900/60' : 'border-slate-200 dark:border-slate-800'} pb-1.5">
                <span class="text-[12px] font-mono font-extrabold uppercase tracking-wider ${isBullish ? 'text-emerald-950 dark:text-emerald-300' : isBearish ? 'text-rose-950 dark:text-rose-300' : 'text-slate-900 dark:text-slate-200'} flex items-center gap-1.5">
                  <span>💡</span> <span>2. Catalyst & Market Impact</span>
                </span>
                <span class="text-[10.5px] font-mono font-extrabold uppercase px-2 py-0.5 rounded ${isBullish ? 'bg-emerald-200 text-emerald-950 dark:bg-emerald-900 dark:text-emerald-200' : isBearish ? 'bg-rose-200 text-rose-950 dark:bg-rose-900 dark:text-rose-200' : 'bg-slate-200 text-slate-900 dark:bg-slate-800 dark:text-slate-200'}">${story.sentiment} THESIS</span>
              </div>
              <div class="bg-white/95 dark:bg-[#0E1322] p-3 rounded-lg border ${isBullish ? 'border-emerald-200/60 dark:border-slate-800' : isBearish ? 'border-rose-200/60 dark:border-slate-800' : 'border-slate-200 dark:border-slate-800'} text-[14.5px] sm:text-[15px] text-[#24374E] dark:text-[#E2E8F0] leading-[1.6] font-normal shadow-2xs font-sans tracking-tight">
                ${highlightSearchTokens(highlightNumbers(story.sentimentReasoning), queryTokens)}
              </div>
            </div>

          </div>

          <!-- RIGHT COLUMN (lg:col-span-6): KEY ANALYST DATA POINTS -->
          <div class="lg:col-span-6 flex flex-col gap-2">
            
            <!-- 📌 SECTION 3: KEY ANALYST DATA POINTS (WITH EXACT IMAGE FONT & SPACING) -->
            <div class="rounded-xl border-2 border-[#C9B7A5] dark:border-[#524434] bg-[#FDFBF7] dark:bg-[#191512] p-3.5 shadow-xs flex flex-col gap-2.5">
              <div class="flex items-center justify-between border-b border-[#E8DCCE] dark:border-[#382E25] pb-1.5">
                <span class="text-[12px] font-mono font-extrabold uppercase tracking-wider text-[#2E1F14] dark:text-[#F3ECE4] flex items-center gap-1.5">
                  <span>📌</span> <span>3. Key Analyst Data Points</span>
                </span>
                <span class="text-[10.5px] font-mono font-bold px-2 py-0.5 rounded bg-[#EFE5D9] text-[#291B10] dark:bg-[#32261C] dark:text-[#E8DCCF] border border-[#CCAFA0]/50">Metrics & Facts</span>
              </div>
              <ul class="space-y-2.5">
                ${(story.bullet_points || []).map(bp => `
                  <li class="flex items-start gap-2.5 text-[14.5px] sm:text-[15px] text-[#24374E] dark:text-[#E2E8F0] leading-[1.6] bg-white/95 dark:bg-[#0E1322] p-3 rounded-lg border border-[#EBE2D8] dark:border-slate-800 shadow-2xs font-normal font-sans tracking-tight">
                    <span class="text-[#8C5E3C] dark:text-[#CBB09C] font-bold select-none mt-0.5 text-base">›</span>
                    <span class="leading-[1.6]">${highlightSearchTokens(highlightNumbers(bp), queryTokens)}</span>
                  </li>
                `).join('')}
              </ul>
            </div>

          </div>

        </div>
      `;
    }

    function highlightNumbers"""

    html = re.sub(old_detail_body_pattern, new_detail_body, html, flags=re.DOTALL)

    # 4. Add Sidebar Hide/Unhide JS handler
    sidebar_js = """
    let isSidebarVisible = localStorage.getItem('finpress_sidebar_visible') !== 'false';

    function toggleSidebar() {
      isSidebarVisible = !isSidebarVisible;
      localStorage.setItem('finpress_sidebar_visible', isSidebarVisible);
      applySidebarVisibility();
    }

    function applySidebarVisibility() {
      const aside = document.getElementById("view-feed-aside");
      const viewFeed = document.getElementById("view-feed");
      const btnText = document.getElementById("sidebar-toggle-text");
      const btn = document.getElementById("toggle-sidebar-btn");

      if (aside && viewFeed) {
        if (isSidebarVisible) {
          aside.classList.remove("hidden");
          viewFeed.className = "grid grid-cols-1 lg:grid-cols-[285px_minmax(0,1fr)_240px] xl:grid-cols-[305px_minmax(0,1fr)_255px] 2xl:grid-cols-[320px_minmax(0,1fr)_270px] gap-2.5 items-start";
          if (btnText) btnText.textContent = "Hide 3rd Col";
          if (btn) {
            btn.classList.remove("opacity-60", "bg-amber-100", "dark:bg-slate-800");
          }
        } else {
          aside.classList.add("hidden");
          viewFeed.className = "grid grid-cols-1 lg:grid-cols-[300px_minmax(0,1fr)] xl:grid-cols-[320px_minmax(0,1fr)] gap-2.5 items-start";
          if (btnText) btnText.textContent = "Show 3rd Col";
          if (btn) {
            btn.classList.add("opacity-80", "bg-amber-200/80", "dark:bg-indigo-900/60");
          }
        }
      }
    }
"""

    if 'function toggleSidebar()' not in html:
        html = html.replace('function initTheme() {', sidebar_js + '\n    function initTheme() {')
        html = html.replace('initMetrics();', 'initMetrics();\n        applySidebarVisibility();')

    with open('web/index.html', 'w', encoding='utf-8') as f:
        f.write(html)

    print("Successfully updated web/index.html with Newspaper theme, 3rd column toggle, and matching font!")

if __name__ == '__main__':
    update_all()
