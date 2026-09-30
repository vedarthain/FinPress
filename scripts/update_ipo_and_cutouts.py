import re

with open('web/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update Section 4 in detail container to be "4. Newspaper Article Cutout"
section4_old_pattern = r'<!-- 📄 SECTION 4: FULL RAW NEWSPAPER ARTICLE TEXT[\s\S]*?renderRawArticleHtml\(story, queryTokens\)[\s\S]*?</div>\s*</div>\s*`;'

section4_new = """<!-- 📰 SECTION 4: AUTHENTIC NEWSPAPER ARTICLE CUTOUT -->
        <div class="mt-4 rounded-xl border-2 border-slate-300 dark:border-slate-800 bg-white dark:bg-[#0A0E1A] p-4 sm:p-5 shadow-xs flex flex-col gap-3">
          
          <div class="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-2.5 flex-wrap gap-2">
            <div class="flex items-center gap-2.5">
              <span class="text-amber-600 dark:text-amber-400 text-xl">✂️</span>
              <div>
                <h3 class="text-[13.5px] font-mono font-extrabold uppercase tracking-wider text-slate-900 dark:text-white flex items-center gap-2">
                  <span>4. Newspaper Article Cutout</span>
                  <span class="text-[10.5px] font-mono font-bold px-2 py-0.5 rounded bg-amber-100 text-amber-950 dark:bg-amber-950/80 dark:text-amber-300 border border-amber-300/80 dark:border-amber-800">Print Box Clipping</span>
                </h3>
                <span class="text-[11.5px] font-mono text-slate-500 dark:text-slate-400">Authentic article box cutout from ${formatPageSource(story.page_numbers)}</span>
              </div>
            </div>

            <div class="flex items-center gap-2">
              ${story.cutout_url ? `
                <a href="${story.cutout_url}" target="_blank" class="text-[11px] font-mono font-bold px-3 py-1 rounded-md border border-indigo-300 dark:border-indigo-700 bg-indigo-50 dark:bg-indigo-950/70 text-indigo-900 dark:text-indigo-200 hover:bg-indigo-100 dark:hover:bg-indigo-900 shadow-2xs flex items-center gap-1.5 transition-all">
                  <span>🔍</span> <span>Full-Res Cutout ↗</span>
                </a>
              ` : ''}
              <button onclick="copyToClipboard('${escapeQuotes(story.headline + '\\n\\n' + (story.brief_details || story.brief || ''))}')" class="text-[11px] font-mono font-bold px-3 py-1 rounded-md border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-[#141A2E] text-slate-800 dark:text-slate-200 hover:bg-white dark:hover:bg-slate-800 shadow-2xs cursor-pointer flex items-center gap-1.5" title="Copy text">
                <span>📋</span> <span>Copy Text</span>
              </button>
            </div>
          </div>

          <!-- Cutout Render Frame -->
          ${renderArticleCutout(story, queryTokens)}

        </div>
      `;"""

if re.search(section4_old_pattern, content):
    content = re.sub(section4_old_pattern, section4_new, content)
    print("Replaced Section 4 with Article Cutout successfully!")
else:
    print("Warning: Section 4 pattern not matched directly, checking manual replacement.")

# Helper functions for article cutout rendering
cutout_helper_js = """
    function renderArticleCutout(story, queryTokens = []) {
      if (!story) return "";

      if (story.cutout_url) {
        return `
          <div class="mt-2 flex flex-col items-center justify-center p-3 sm:p-4 bg-slate-100/90 dark:bg-[#070B14] rounded-lg border border-slate-200 dark:border-slate-800/80 overflow-hidden shadow-inner">
            <div class="relative group max-w-full overflow-hidden rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-black shadow-md cursor-zoom-in" onclick="openImageModal('${story.cutout_url}', '${escapeQuotes(story.headline)}')">
              <img src="${story.cutout_url}" alt="${escapeQuotes(story.headline)}" class="w-auto max-h-[620px] object-contain mx-auto transition-transform duration-200 group-hover:scale-[1.01]"/>
              <div class="absolute bottom-2 right-2 px-3 py-1 rounded-md bg-black/80 backdrop-blur-xs text-white text-[11px] font-mono flex items-center gap-1.5 opacity-90 group-hover:opacity-100 transition-opacity">
                <span>🔍</span> <span>Click to Zoom</span>
              </div>
            </div>
            <div class="w-full flex items-center justify-between mt-2.5 pt-2 border-t border-slate-200 dark:border-slate-800 text-[11.5px] font-mono text-slate-500 dark:text-slate-400">
              <span class="flex items-center gap-1.5"><span>📰</span> <span>${formatPageSource(story.page_numbers)}</span></span>
              <span>Authentic Print Box Clipping</span>
            </div>
          </div>
        `;
      }

      // High-definition styled Newspaper Box Card for all stories without a direct image file
      const brief = story.brief_details || story.brief || "";
      const bullets = story.bullet_points || story.detailed_points || [];
      return `
        <div class="mt-2 p-5 bg-[#FAF8F5] dark:bg-[#0C101D] rounded-lg border-2 border-amber-300/80 dark:border-slate-800 flex flex-col gap-3 font-serif shadow-xs">
          <div class="flex items-center justify-between border-b border-[#E6DEC8] dark:border-slate-800 pb-2">
            <span class="text-[12px] font-mono font-bold uppercase tracking-wider text-amber-950 dark:text-amber-400 flex items-center gap-1.5">
              <span>📰</span> <span>${formatPageSource(story.page_numbers)} — Financial News Desk</span>
            </span>
            <span class="text-[11px] font-mono px-2 py-0.5 rounded bg-amber-200/60 dark:bg-slate-800 text-amber-950 dark:text-slate-300 font-semibold">Print Layout Box</span>
          </div>
          <h4 class="text-[19px] sm:text-[20px] font-bold text-[#111827] dark:text-white leading-snug font-serif tracking-tight">
            ${highlightSearchTokens(highlightNumbers(story.headline), queryTokens)}
          </h4>
          <div class="text-[16px] leading-[1.85] text-slate-900 dark:text-slate-200 space-y-3 font-serif">
            <p class="first-letter:text-[30px] first-letter:font-bold first-letter:font-mono first-letter:mr-1.5 first-letter:float-left first-letter:leading-none first-letter:text-amber-700 dark:first-letter:text-amber-400 text-justify">
              ${highlightSearchTokens(highlightNumbers(brief), queryTokens)}
            </p>
            ${bullets.map(bp => `
              <div class="pl-3.5 border-l-2 border-amber-400 dark:border-amber-500 text-[15px] text-slate-800 dark:text-slate-200 leading-[1.75] font-sans">
                ${highlightSearchTokens(highlightNumbers(bp), queryTokens)}
              </div>
            `).join('')}
          </div>
          ${story.sentimentReasoning ? `
            <div class="mt-2 p-3 rounded-md bg-amber-50 dark:bg-slate-900 border border-amber-200 dark:border-slate-800 text-[13px] font-sans text-amber-950 dark:text-slate-300">
              <b class="text-amber-900 dark:text-amber-400">Analyst Thesis:</b> ${highlightSearchTokens(highlightNumbers(story.sentimentReasoning), queryTokens)}
            </div>
          ` : ''}
        </div>
      `;
    }

    function openImageModal(imgUrl, title) {
      const modal = document.getElementById("image-zoom-modal");
      const img = document.getElementById("image-zoom-img");
      const caption = document.getElementById("image-zoom-caption");
      if (modal && img) {
        img.src = imgUrl;
        if (caption) caption.textContent = title || "Newspaper Article Cutout";
        modal.classList.remove("hidden");
        modal.classList.add("flex");
      }
    }

    function closeImageModal() {
      const modal = document.getElementById("image-zoom-modal");
      if (modal) {
        modal.classList.add("hidden");
        modal.classList.remove("flex");
      }
    }
"""

# 2. Add Image Zoom Modal to bottom of index.html if not present
image_modal_html = """
  <!-- ================= IMAGE CUTOUT ZOOM MODAL ================= -->
  <div id="image-zoom-modal" class="fixed inset-0 z-50 bg-black/85 backdrop-blur-sm hidden items-center justify-center p-4 cursor-pointer" onclick="closeImageModal()">
    <div class="relative max-w-5xl w-full max-h-[95vh] flex flex-col items-center bg-slate-900/90 p-4 rounded-2xl border border-slate-700 shadow-2xl" onclick="event.stopPropagation()">
      <div class="w-full flex items-center justify-between pb-2 border-b border-slate-700 text-slate-100 font-mono text-[13px]">
        <span id="image-zoom-caption" class="font-bold truncate mr-4">Newspaper Article Cutout</span>
        <div class="flex items-center gap-2">
          <button onclick="closeImageModal()" class="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 text-[12px] font-bold">✕ Close</button>
        </div>
      </div>
      <div class="w-full overflow-auto max-h-[85vh] p-2 flex items-center justify-center mt-2">
        <img id="image-zoom-img" src="" alt="Cutout" class="max-w-full max-h-[80vh] object-contain rounded shadow-lg"/>
      </div>
    </div>
  </div>
"""

if 'id="image-zoom-modal"' not in content:
    content = content.replace('</body>', image_modal_html + '\n</body>')

# 3. Replace renderRawArticleHtml definition with cutout helper
content = re.sub(r'function renderRawArticleHtml[\s\S]*?return formattedParas\.join\(\'\\n\'\);\s*}', cutout_helper_js, content)

with open('web/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated web/index.html successfully!")
