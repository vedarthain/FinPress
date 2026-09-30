import re

with open('web/index.html', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Add IPO Hub button into top navigation header
old_header_btn = '<button onclick="triggerGitHubPipeline()"'
new_header_btn = """<!-- IPO Hub Toggle Button -->
        <button onclick="switchView(currentView === 'ipo' ? 'feed' : 'ipo')" id="top-ipo-hub-btn" class="px-3 py-1 rounded-lg bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white font-mono text-[12px] font-bold flex items-center gap-1.5 shadow-md transition-transform active:scale-95 cursor-pointer" title="Open Business Standard style IPO Tracker & Listed Performance">
          <span>🚀</span> <span>IPO Hub</span>
        </button>

        <button onclick="triggerGitHubPipeline()" """

if 'id="top-ipo-hub-btn"' not in code:
    code = code.replace(old_header_btn, new_header_btn)

# 2. Update switchView function
old_switch_view = r'function switchView\(viewName\) \{[\s\S]*?renderFeedList\(\);\s*\}'
new_switch_view = """function switchView(viewName) {
      currentView = viewName;
      const tabAnchor = document.getElementById("tab-btn-anchor");
      const viewFeed = document.getElementById("view-feed");
      const viewIpo = document.getElementById("view-ipo");
      const viewMatrix = document.getElementById("view-matrix");
      const corpBanner = document.getElementById("corporate-subtabs-banner");
      const ipoBanner = document.getElementById("ipo-subtabs-banner");
      const topIpoBtn = document.getElementById("top-ipo-hub-btn");

      selectedStoryIndex = 0;
      currentFeedPage = 1;

      if (viewName === "ipo" || viewName === "ipo_hub") {
        if (topIpoBtn) {
          topIpoBtn.className = "px-3 py-1 rounded-lg bg-amber-600 text-white font-mono text-[12px] font-bold flex items-center gap-1.5 shadow-md transition-transform active:scale-95 cursor-pointer ring-2 ring-amber-400";
          topIpoBtn.innerHTML = "<span>📰</span> <span>Back to News</span>";
        }
        if (viewFeed) { viewFeed.classList.add("hidden"); viewFeed.classList.remove("grid"); }
        if (viewMatrix) { viewMatrix.classList.add("hidden"); viewMatrix.classList.remove("flex"); }
        if (viewIpo) { viewIpo.classList.remove("hidden"); viewIpo.classList.add("flex"); }
        setIpoViewMode(activeIpoMode || 'tracker');
        return;
      }

      if (topIpoBtn) {
        topIpoBtn.className = "px-3 py-1 rounded-lg bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white font-mono text-[12px] font-bold flex items-center gap-1.5 shadow-md transition-transform active:scale-95 cursor-pointer";
        topIpoBtn.innerHTML = "<span>🚀</span> <span>IPO Hub</span>";
      }

      if (viewIpo) { viewIpo.classList.add("hidden"); viewIpo.classList.remove("flex"); }
      if (viewMatrix) { viewMatrix.classList.add("hidden"); viewMatrix.classList.remove("flex"); }
      if (viewFeed) { viewFeed.classList.remove("hidden"); viewFeed.classList.add("grid"); }

      if (viewName === "feed" || viewName === "all") {
        selectedFeedCategory = "ALL";
        if (corpBanner) corpBanner.classList.add("hidden");
        if (ipoBanner) ipoBanner.classList.add("hidden");
      } else if (viewName === "anchor") {
        selectedFeedCategory = "ANCHOR";
        if (corpBanner) corpBanner.classList.add("hidden");
        if (ipoBanner) ipoBanner.classList.add("hidden");
      } else if (viewName === "corporate") {
        selectedFeedCategory = "CORPORATE_ALL";
        if (corpBanner) { corpBanner.classList.remove("hidden"); corpBanner.classList.add("flex"); }
      } else if (viewName === "opinions") {
        selectedFeedCategory = "OPINIONS";
        if (corpBanner) corpBanner.classList.add("hidden");
      }

      renderFeedList();
    }"""

code = re.sub(old_switch_view, new_switch_view, code)

with open('web/index.html', 'w', encoding='utf-8') as f:
    f.write(code)

print("Polished switchView and top ribbon IPO Hub button!")
