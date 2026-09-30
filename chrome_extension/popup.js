const WORKER_ENDPOINT = "https://finpress.deb5045ai.workers.dev/api/session/bs";

document.getElementById("sync-btn").addEventListener("click", async () => {
  const btn = document.getElementById("sync-btn");
  const statusBox = document.getElementById("status-box");

  btn.disabled = true;
  btn.innerHTML = "<span>⏳</span> <span>Reading cookies...</span>";
  statusBox.className = "status info";
  statusBox.style.display = "block";
  statusBox.textContent = "Extracting Business Standard subscriber cookies...";

  try {
    // 1. Query all cookies under .business-standard.com and epaper.business-standard.com
    const bsCookies = await chrome.cookies.getAll({ domain: "business-standard.com" });
    const epaperCookies = await chrome.cookies.getAll({ domain: "epaper.business-standard.com" });
    
    const combined = [...bsCookies, ...epaperCookies];
    
    // Deduplicate by name + domain
    const seen = new Set();
    const uniqueCookies = [];
    for (const c of combined) {
      const key = `${c.name}@${c.domain}`;
      if (!seen.has(key)) {
        seen.add(key);
        uniqueCookies.push({
          name: c.name,
          value: c.value,
          domain: c.domain,
          path: c.path,
          expires: c.expirationDate || -1,
          httpOnly: c.httpOnly || false,
          secure: c.secure || true,
          sameSite: c.sameSite === "no_restriction" ? "None" : (c.sameSite === "strict" ? "Strict" : "Lax")
        });
      }
    }

    if (uniqueCookies.length === 0) {
      throw new Error("No Business Standard cookies found. Please make sure you are logged in to epaper.business-standard.com in Chrome first.");
    }

    btn.innerHTML = "<span>☁️</span> <span>Uploading to R2...</span>";
    statusBox.textContent = `Found ${uniqueCookies.length} cookies. Syncing to Cloudflare R2...`;

    // 2. Upload to Cloudflare Worker
    const response = await fetch(WORKER_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ cookies: uniqueCookies })
    });

    const result = await response.json();

    if (result.success) {
      btn.innerHTML = "<span>✅</span> <span>Synced Successfully!</span>";
      statusBox.className = "status success";
      statusBox.innerHTML = `<b>Success!</b> Synced ${uniqueCookies.length} cookies.<br>Saved to Cloudflare R2.<br><small>GitHub Actions / Pipeline can now download today's paper.</small>`;
    } else {
      throw new Error(result.error || "Failed to upload session to Cloudflare R2.");
    }
  } catch (err) {
    btn.disabled = false;
    btn.innerHTML = "<span>⚠️</span> <span>Retry Sync</span>";
    statusBox.className = "status error";
    statusBox.textContent = `Error: ${err.message}`;
  }
});
