import re

def update_all():
    with open('web/index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Update Google Fonts in <head> to include DM Sans with full weights
    old_fonts = '<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">'
    new_fonts = '<link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,100..1000;1,9..40,100..1000&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">'
    html = html.replace(old_fonts, new_fonts)

    # 2. Update Tailwind config font-sans to use DM Sans
    html = re.sub(
        r'sans: \[.*?\]',
        "sans: ['\"DM Sans\"', '\"Plus Jakarta Sans\"', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'sans-serif']",
        html
    )

    # 3. Update body style font-family and dark high-contrast text color
    html = re.sub(
        r'body\s*\{\s*font-family:[^;]+;',
        "body { font-family: 'DM Sans', 'Plus Jakarta Sans', system-ui, -apple-system, BlinkMacSystemFont, sans-serif; font-size: 14px; font-weight: 400; color: #090D16;",
        html
    )

    # 4. Remove toggle-sidebar-btn from top navigation header
    html = re.sub(
        r'<!-- Toggle 3rd Column Button \(Hide / Show\) -->\s*<button id="toggle-sidebar-btn".*?</button>\s*',
        '',
        html,
        flags=re.DOTALL
    )

    # 5. Add Sandwich menu button to Column 2 header (visible when 3rd col is hidden)
    col2_header_pattern = r'<div class="flex items-center gap-1\.5">\s*(\$\{sentBadge\})\s*<button onclick="copyToClipboard'
    col2_header_repl = r'<div class="flex items-center gap-1.5">\n            <button id="feed-open-sidebar-btn" onclick="toggleSidebar()" class="hidden text-[11.5px] font-mono font-bold px-2.5 py-0.5 rounded border border-[#DFC0A5] dark:border-slate-700 bg-[#FBE8D8] dark:bg-[#1E1B4B] text-[#1C1917] dark:text-[#E0E7FF] hover:bg-[#F3DECC] shadow-2xs items-center gap-1.5 cursor-pointer transition-all" title="Open 3rd Column Filters & Desks"><span>☰</span> <span>Filters</span></button>\n            \1\n            <button onclick="copyToClipboard'
    html = re.sub(col2_header_pattern, col2_header_repl, html)

    # 6. Update Column 3 (<aside>) header with the Sandwich Button
    old_col3_pattern = r'<aside id="view-feed-aside".*?>\s*<!-- Tree Container -->\s*<div id="tree-sidebar-container" class="flex flex-col gap-2">'
    new_col3_header = """<aside id="view-feed-aside" class="flex flex-col gap-2 lg:sticky lg:top-[44px] lg:max-h-[calc(100vh-3.5rem)] lg:overflow-y-auto transition-all">
          
          <!-- Top Header of Column 3 with Sandwich Button & Collapse -->
          <div class="flex items-center justify-between px-2.5 py-1.5 rounded-lg bg-[#FBE8D8] dark:bg-[#151D33] border border-[#DFC0A5] dark:border-slate-800 shadow-2xs">
            <div class="flex items-center gap-1.5 font-mono text-[11.5px] font-bold text-[#1C1917] dark:text-slate-100">
              <span class="text-amber-800 dark:text-amber-400 font-extrabold text-sm">☰</span>
              <span>Filters & Desks</span>
            </div>
            <button onclick="toggleSidebar()" class="px-2 py-0.5 rounded hover:bg-black/10 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 hover:text-black font-mono text-[11px] font-bold flex items-center gap-1 cursor-pointer transition-colors" title="Hide 3rd Column">
              <span>✕ Hide</span>
            </button>
          </div>

          <!-- Tree Container -->
          <div id="tree-sidebar-container" class="flex flex-col gap-2">"""

    html = re.sub(old_col3_pattern, new_col3_header, html)

    # 7. Update applySidebarVisibility in JS
    old_sidebar_fn = r'function applySidebarVisibility\(\) \{.*?\n    \}'
    new_sidebar_fn = """function applySidebarVisibility() {
      const aside = document.getElementById("view-feed-aside");
      const viewFeed = document.getElementById("view-feed");
      const openBtn = document.getElementById("feed-open-sidebar-btn");

      if (aside && viewFeed) {
        if (isSidebarVisible) {
          aside.classList.remove("hidden");
          viewFeed.className = "grid grid-cols-1 lg:grid-cols-[285px_minmax(0,1fr)_240px] xl:grid-cols-[305px_minmax(0,1fr)_255px] 2xl:grid-cols-[320px_minmax(0,1fr)_270px] gap-2.5 items-start";
          if (openBtn) {
            openBtn.classList.add("hidden");
            openBtn.classList.remove("flex");
          }
        } else {
          aside.classList.add("hidden");
          viewFeed.className = "grid grid-cols-1 lg:grid-cols-[300px_minmax(0,1fr)] xl:grid-cols-[320px_minmax(0,1fr)] gap-2.5 items-start";
          if (openBtn) {
            openBtn.classList.remove("hidden");
            openBtn.classList.add("flex");
          }
        }
      }
    }"""

    html = re.sub(old_sidebar_fn, new_sidebar_fn, html, flags=re.DOTALL)

    # 8. Darken the description text and apply DM Sans standard 400 weight in renderActiveStoryDetail
    html = html.replace('text-[#24374E] dark:text-[#E2E8F0]', 'text-[#090D16] dark:text-[#F8FAFC]')
    html = html.replace('font-normal font-sans', 'font-normal font-sans')
    html = html.replace('text-slate-950 dark:text-slate-50', 'text-[#05080F] dark:text-white')

    with open('web/index.html', 'w', encoding='utf-8') as f:
        f.write(html)

    print("Successfully updated web/index.html with DM Sans font and Sandwich toggle button on 3rd column!")

if __name__ == '__main__':
    update_all()
