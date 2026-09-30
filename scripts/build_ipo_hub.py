import re

with open('web/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace the existing #view-ipo markup with the full-featured Business Standard style IPO Hub
ipo_markup_old = r'<!-- ================= VIEW 2: TABULAR IPO CENTRAL ================= -->[\s\S]*?</section>'

ipo_markup_new = """<!-- ================= VIEW 2: BUSINESS STANDARD STYLE IPO HUB ================= -->
      <section id="view-ipo" class="hidden flex-col gap-2.5 flex-1 min-h-0 h-full overflow-hidden w-full">
        
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
                <button onclick="setIpoFilterCategory('ALL')" id="ipo-filter-all" class="px-2.5 py-1 rounded-md bg-slate-200 dark:bg-slate-800 text-slate-900 dark:text-white font-bold">All Issues</button>
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

      </section>"""

html = re.sub(ipo_markup_old, ipo_markup_new, html)

# Now add JavaScript for the complete BS-style IPO Hub rendering
ipo_script_addon = """
    let activeIpoMode = 'tracker'; // 'tracker' or 'listed'
    let activeIpoCategory = 'ALL';  // 'ALL', 'MAINBOARD', 'SME'
    let ipoSearchQuery = '';

    // Sample institutional benchmark dataset for 'Already Listed' IPOs (recent high-profile issues)
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
    ];

    function setIpoViewMode(mode) {
      activeIpoMode = mode;
      const trackerBtn = document.getElementById("ipo-mode-tracker-btn");
      const listedBtn = document.getElementById("ipo-mode-listed-btn");
      const trackerWrap = document.getElementById("ipo-tracker-table-wrap");
      const listedWrap = document.getElementById("ipo-listed-table-wrap");
      const subfilter = document.getElementById("ipo-subfilter-container");

      if (mode === 'tracker') {
        trackerBtn.className = "px-3 py-1.5 rounded-lg bg-[#1C1917] text-white dark:bg-indigo-600 dark:text-white shadow-xs transition-all flex items-center gap-1.5 cursor-pointer";
        listedBtn.className = "px-3 py-1.5 rounded-lg text-slate-700 dark:text-slate-300 hover:text-black dark:hover:text-white hover:bg-white/60 dark:hover:bg-slate-800 transition-all flex items-center gap-1.5 cursor-pointer";
        trackerWrap.classList.remove("hidden");
        listedWrap.classList.add("hidden");
        if (subfilter) subfilter.classList.remove("hidden");
        renderIpoTrackerTable();
      } else {
        listedBtn.className = "px-3 py-1.5 rounded-lg bg-[#1C1917] text-white dark:bg-indigo-600 dark:text-white shadow-xs transition-all flex items-center gap-1.5 cursor-pointer";
        trackerBtn.className = "px-3 py-1.5 rounded-lg text-slate-700 dark:text-slate-300 hover:text-black dark:hover:text-white hover:bg-white/60 dark:hover:bg-slate-800 transition-all flex items-center gap-1.5 cursor-pointer";
        listedWrap.classList.remove("hidden");
        trackerWrap.classList.add("hidden");
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
            <button onclick="openStoryModalById(${item.storyId || 1})" class="px-2.5 py-1 rounded bg-slate-100 dark:bg-slate-800 hover:bg-indigo-50 text-indigo-600 dark:text-indigo-400 font-mono text-[11px] font-bold border border-slate-200 dark:border-slate-700">
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
"""

if 'let activeIpoMode' not in html:
    html = html.replace('</script>', ipo_script_addon + '\n</script>')

# Make switchView('ipo') trigger renderIpoTrackerTable
html = html.replace('if (currentView === "ipo") {', 'if (currentView === "ipo") {\n        renderIpoTrackerTable();')

with open('web/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("IPO Hub updated successfully in web/index.html!")
