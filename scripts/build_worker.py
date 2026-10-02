import json

def build():
    with open('web/index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)

    worker_code = f"""// Cloudflare Worker for FinPress
const HTML = {json.dumps(html)};

export default {{
  async fetch(request, env, ctx) {{
    const url = new URL(request.url);

    // Handle CORS preflight
    if (request.method === 'OPTIONS') {{
      return new Response(null, {{
        headers: {{
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        }}
      }});
    }}

    // API: Trigger GitHub Actions Pipeline Endpoint
    if (url.pathname === '/api/trigger-pipeline' && request.method === 'POST') {{
      try {{
        let payload = {{}};
        try {{ payload = await request.json(); }} catch(e) {{}}
        const token = payload.token || env.GH_TOKEN || env.GITHUB_TOKEN;
        
        if (!token) {{
          return new Response(JSON.stringify({{
            success: false,
            needsToken: true,
            error: 'GitHub Personal Access Token is required to trigger GitHub Actions.'
          }}), {{
            status: 401,
            headers: {{
              'Content-Type': 'application/json; charset=utf-8',
              'Access-Control-Allow-Origin': '*'
            }}
          }});
        }}

        const workflow = payload.workflow || '2_fetch_business_standard.yml';
        const ghResp = await fetch(`https://api.github.com/repos/vedarthain/FinPress/actions/workflows/${{workflow}}/dispatches`, {{
          method: 'POST',
          headers: {{
            'Accept': 'application/vnd.github.v3+json',
            'Authorization': `Bearer ${{token}}`,
            'User-Agent': 'FinPress-Cloudflare-Worker',
            'Content-Type': 'application/json'
          }},
          body: JSON.stringify({{ ref: 'main' }})
        }});

        if (ghResp.status === 204 || ghResp.ok) {{
          return new Response(JSON.stringify({{
            success: true,
            message: 'GitHub Actions workflow triggered successfully!'
          }}), {{
            headers: {{
              'Content-Type': 'application/json; charset=utf-8',
              'Access-Control-Allow-Origin': '*'
            }}
          }});
        }} else {{
          const errText = await ghResp.text();
          return new Response(JSON.stringify({{
            success: false,
            error: `GitHub API returned status ${{ghResp.status}}: ${{errText}}`
          }}), {{
            status: ghResp.status,
            headers: {{
              'Content-Type': 'application/json; charset=utf-8',
              'Access-Control-Allow-Origin': '*'
            }}
          }});
        }}
      }} catch (err) {{
        return new Response(JSON.stringify({{
          success: false,
          error: err.message
        }}), {{
          status: 500,
          headers: {{
            'Content-Type': 'application/json; charset=utf-8',
            'Access-Control-Allow-Origin': '*'
          }}
        }});
      }}
    }}

    // API: Web Cron Job Trigger Endpoint (Supports simple GET/POST for cron-job.org / EasyCron)
    if (url.pathname === '/api/cron' || url.pathname === '/api/trigger-cron') {{
      const token = url.searchParams.get('token') || env.GH_TOKEN || env.GITHUB_TOKEN;
      if (!token) {{
        return new Response(JSON.stringify({{
          success: false,
          error: 'Missing token. Pass ?token=YOUR_GITHUB_PAT in the cron URL, or configure GH_TOKEN in Cloudflare.'
        }}), {{
          status: 401,
          headers: {{ 'Content-Type': 'application/json; charset=utf-8', 'Access-Control-Allow-Origin': '*' }}
        }});
      }}

      try {{
        const ghResp = await fetch('https://api.github.com/repos/vedarthain/FinPress/actions/workflows/daily_master_pipeline.yml/dispatches', {{
          method: 'POST',
          headers: {{
            'Accept': 'application/vnd.github.v3+json',
            'Authorization': `Bearer ${{token}}`,
            'User-Agent': 'FinPress-Web-Cron',
            'Content-Type': 'application/json'
          }},
          body: JSON.stringify({{ ref: 'main' }})
        }});

        const ok = ghResp.status === 204 || ghResp.ok;
        return new Response(JSON.stringify({{
          success: ok,
          timestamp: new Date().toISOString(),
          message: ok ? '⚡ Daily Master Newspaper Pipeline triggered successfully via Web Cron!' : `GitHub API status: ${{ghResp.status}}`
        }}), {{
          headers: {{ 'Content-Type': 'application/json; charset=utf-8', 'Access-Control-Allow-Origin': '*' }}
        }});
      }} catch (err) {{
        return new Response(JSON.stringify({{ success: false, error: err.message }}), {{
          status: 500,
          headers: {{ 'Content-Type': 'application/json; charset=utf-8', 'Access-Control-Allow-Origin': '*' }}
        }});
      }}
    }}

    // API: Business Standard 1-Click Session Sync Endpoint
    if (url.pathname === '/api/session/bs' && request.method === 'POST') {{
      try {{
        const payload = await request.json();
        let cookiesList = [];

        if (Array.isArray(payload.cookies)) {{
          cookiesList = payload.cookies;
        }} else if (payload.cookieString || typeof payload === 'string' || payload.cookies) {{
          const rawStr = payload.cookieString || payload.cookies || (typeof payload === 'string' ? payload : '');
          const parts = rawStr.split(';').map(p => p.trim()).filter(Boolean);
          for (const part of parts) {{
            const eqIdx = part.indexOf('=');
            if (eqIdx > 0) {{
              const name = part.substring(0, eqIdx).trim();
              const value = part.substring(eqIdx + 1).trim();
              cookiesList.push({{
                name: name,
                value: value,
                domain: '.business-standard.com',
                path: '/',
                expires: -1,
                httpOnly: false,
                secure: true,
                sameSite: 'Lax'
              }});
            }}
          }}
        }}

        const storageState = {{
          cookies: cookiesList,
          origins: [
            {{
              origin: 'https://epaper.business-standard.com',
              localStorage: []
            }},
            {{
              origin: 'https://www.business-standard.com',
              localStorage: []
            }}
          ]
        }};

        // Write directly to Cloudflare R2 bucket binding
        if (env.BUCKET) {{
          await env.BUCKET.put('sessions/bs_storage_state.json', JSON.stringify(storageState, null, 2), {{
            httpMetadata: {{
              contentType: 'application/json; charset=utf-8'
            }}
          }});
        }}

        // Trigger GitHub Actions repository_dispatch if token is configured
        let gaTriggered = false;
        const ghToken = payload.token || env.GH_TOKEN || env.GITHUB_TOKEN;
        if (ghToken) {{
          try {{
            const ghResp = await fetch('https://api.github.com/repos/vedarthain/FinPress/actions/workflows/2_fetch_business_standard.yml/dispatches', {{
              method: 'POST',
              headers: {{
                'Accept': 'application/vnd.github.v3+json',
                'Authorization': `Bearer ${{ghToken}}`,
                'User-Agent': 'FinPress-Cloudflare-Worker',
                'Content-Type': 'application/json'
              }},
              body: JSON.stringify({{ ref: 'main' }})
            }});
            gaTriggered = (ghResp.status === 204 || ghResp.ok);
          }} catch (ghErr) {{
            console.error('GH Dispatch error:', ghErr);
          }}
        }}

        return new Response(JSON.stringify({{
          success: true,
          message: 'Business Standard session synced to Cloudflare R2 successfully!',
          cookiesCount: cookiesList.length,
          gaTriggered: gaTriggered
        }}), {{
          headers: {{
            'Content-Type': 'application/json; charset=utf-8',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization'
          }}
        }});
      }} catch (err) {{
        return new Response(JSON.stringify({{
          success: false,
          error: err.message || 'Failed to process session payload'
        }}), {{
          status: 400,
          headers: {{
            'Content-Type': 'application/json; charset=utf-8',
            'Access-Control-Allow-Origin': '*'
          }}
        }});
      }}
    }}

    // API proxy to Cloudflare R2 / latest report
    if (url.pathname === '/api/latest' || url.pathname.startsWith('/api/report')) {{
      const dateParam = url.searchParams.get('date');
      const targetFile = dateParam ? `news_report_unified_${{dateParam}}.json` : 'news_report_unified_latest.json';
      const r2Url = `https://pub-c81167dd545d49d0a2cd964a8bd6a1cd.r2.dev/reports/${{targetFile}}?t=${{Date.now()}}`;
      try {{
        const resp = await fetch(r2Url, {{
          headers: {{ 'User-Agent': 'FinPress-Cloudflare-Worker' }},
          cf: {{ cacheTtl: 0, cacheEverything: false }}
        }});
        return new Response(resp.body, {{
          status: resp.status,
          headers: {{
            'Content-Type': 'application/json; charset=utf-8',
            'Access-Control-Allow-Origin': '*',
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
          }}
        }});
      }} catch (e) {{
        return new Response(JSON.stringify({{ error: 'Failed to fetch report' }}), {{ status: 500 }});
      }}
    }}

    if (url.pathname === '/api/dates') {{
      let dates = [];
      try {{
        const listed = await env.BUCKET.list({{ prefix: 'reports/news_report_unified_' }});
        dates = listed.objects
          .map(o => o.key.match(/news_report_unified_(\\d{{4}}-\\d{{2}}-\\d{{2}})\\.json$/))
          .filter(Boolean)
          .map(m => m[1])
          .sort()
          .reverse();
      }} catch (e) {{
        console.error('Failed to list R2 dates:', e);
      }}
      return new Response(JSON.stringify(dates), {{
        headers: {{
          'Content-Type': 'application/json; charset=utf-8',
          'Access-Control-Allow-Origin': '*',
          'Cache-Control': 'no-cache, no-store, must-revalidate'
        }}
      }});
    }}

    // API: R2 Storage Housekeeping & 3GB Quota Management
    if (url.pathname === '/api/housekeeping/r2') {{
      try {{
        if (!env.BUCKET) {{
          return new Response(JSON.stringify({{ error: 'R2 BUCKET binding not found' }}), {{ status: 500 }});
        }}

        const maxLimitBytes = 3 * 1024 * 1024 * 1024; // 3.0 GB Hard Threshold
        const targetBytes = Math.floor(2.2 * 1024 * 1024 * 1024); // 2.2 GB Target

        let objects = [];
        let cursor = undefined;
        do {{
          const listed = await env.BUCKET.list({{ cursor, limit: 1000 }});
          objects = objects.concat(listed.objects);
          cursor = listed.truncated ? listed.cursor : undefined;
        }} while (cursor);

        let totalBytes = objects.reduce((acc, o) => acc + o.size, 0);
        let categories = {{ pdfs: 0, reports: 0, cutouts: 0, sessions: 0, other: 0 }};
        
        objects.forEach(o => {{
          const k = o.key.toLowerCase();
          if (k.startsWith('pdfs/') || k.endsWith('.pdf')) categories.pdfs += o.size;
          else if (k.startsWith('reports/') || k.endsWith('.json') || k.endsWith('.md')) categories.reports += o.size;
          else if (k.startsWith('cutouts/') || k.endsWith('.png') || k.endsWith('.jpg')) categories.cutouts += o.size;
          else if (k.startsWith('sessions/')) categories.sessions += o.size;
          else categories.other += o.size;
        }});

        const shouldPrune = url.searchParams.get('prune') === 'true' || totalBytes > maxLimitBytes;
        let deletedKeys = [];
        let freedBytes = 0;

        if (shouldPrune) {{
          const allKeySet = new Set(objects.map(o => o.key));
          
          // 1. Root duplicate PDFs
          for (const o of objects) {{
            if (!o.key.startsWith('pdfs/') && o.key.endsWith('.pdf') && allKeySet.has('pdfs/' + o.key)) {{
              deletedKeys.push(o.key);
              freedBytes += o.size;
            }}
          }}

          // 2. Oldest PDFs if still over target
          let projectedBytes = totalBytes - freedBytes;
          if (projectedBytes > targetBytes) {{
            const candidatePdfs = objects
              .filter(o => (o.key.startsWith('pdfs/') || o.key.endsWith('.pdf')) && !deletedKeys.includes(o.key))
              .sort((a, b) => new Date(a.uploaded).getTime() - new Date(b.uploaded).getTime());

            for (const o of candidatePdfs) {{
              if (projectedBytes <= targetBytes) break;
              deletedKeys.push(o.key);
              freedBytes += o.size;
              projectedBytes -= o.size;
            }}
          }}

          if (deletedKeys.length > 0) {{
            await Promise.all(deletedKeys.map(k => env.BUCKET.delete(k)));
          }}
        }}

        const finalTotalBytes = totalBytes - freedBytes;

        return new Response(JSON.stringify({{
          success: true,
          status: finalTotalBytes > maxLimitBytes ? 'EXCEEDED' : 'HEALTHY',
          limit_gb: 3.0,
          current_total_mb: Math.round((finalTotalBytes / (1024 * 1024)) * 100) / 100,
          current_total_gb: Math.round((finalTotalBytes / (1024 * 1024 * 1024)) * 10000) / 10000,
          headroom_gb: Math.round(((maxLimitBytes - finalTotalBytes) / (1024 * 1024 * 1024)) * 100) / 100,
          categories_mb: {{
            pdfs: Math.round((categories.pdfs / (1024 * 1024)) * 100) / 100,
            reports: Math.round((categories.reports / (1024 * 1024)) * 100) / 100,
            cutouts: Math.round((categories.cutouts / (1024 * 1024)) * 100) / 100,
            sessions: Math.round((categories.sessions / (1024 * 1024)) * 100) / 100,
            other: Math.round((categories.other / (1024 * 1024)) * 100) / 100
          }},
          pruned_count: deletedKeys.length,
          freed_mb: Math.round((freedBytes / (1024 * 1024)) * 100) / 100
        }}, null, 2), {{
          headers: {{
            'Content-Type': 'application/json; charset=utf-8',
            'Access-Control-Allow-Origin': '*',
            'Cache-Control': 'no-cache, no-store, must-revalidate'
          }}
        }});
      }} catch (err) {{
        return new Response(JSON.stringify({{ success: false, error: err.message }}), {{
          status: 500,
          headers: {{ 'Content-Type': 'application/json; charset=utf-8', 'Access-Control-Allow-Origin': '*' }}
        }});
      }}
    }}

    // Default: Serve Trader Terminal UI
    return new Response(HTML, {{
      headers: {{
        'Content-Type': 'text/html; charset=utf-8',
        'Cache-Control': 'no-cache, no-store, must-revalidate, max-age=0',
        'Pragma': 'no-cache',
        'Expires': '0'
      }}
    }});
  }},

  // Automatic Cloudflare Cron Trigger (Runs daily at 5:45 AM & 6:15 AM IST + R2 Housekeeping)
  async scheduled(event, env, ctx) {{
    // 1. Enforce R2 3GB Quota Housekeeping
    if (env.BUCKET) {{
      try {{
        let objects = [];
        let cursor = undefined;
        do {{
          const listed = await env.BUCKET.list({{ cursor, limit: 1000 }});
          objects = objects.concat(listed.objects);
          cursor = listed.truncated ? listed.cursor : undefined;
        }} while (cursor);

        const maxLimitBytes = 3 * 1024 * 1024 * 1024;
        const targetBytes = Math.floor(2.2 * 1024 * 1024 * 1024);
        let totalBytes = objects.reduce((acc, o) => acc + o.size, 0);

        if (totalBytes > targetBytes) {{
          const candidatePdfs = objects
            .filter(o => o.key.startsWith('pdfs/') || o.key.endsWith('.pdf'))
            .sort((a, b) => new Date(a.uploaded).getTime() - new Date(b.uploaded).getTime());

          let keysToDelete = [];
          let freed = 0;
          for (const o of candidatePdfs) {{
            if (totalBytes - freed <= targetBytes) break;
            keysToDelete.push(o.key);
            freed += o.size;
          }}
          if (keysToDelete.length > 0) {{
            await Promise.all(keysToDelete.map(k => env.BUCKET.delete(k)));
            console.log(`Cloudflare Cron R2 Housekeeping: Pruned ${{keysToDelete.length}} items, freed ${{Math.round(freed/1024/1024)}} MB.`);
          }}
        }}
      }} catch (e) {{
        console.error('Cloudflare Cron R2 Housekeeping error:', e);
      }}
    }}

    // 2. Trigger Daily Master Pipeline
    const ghToken = env.GH_TOKEN || env.GITHUB_TOKEN;
    if (ghToken) {{
      try {{
        await fetch('https://api.github.com/repos/vedarthain/FinPress/actions/workflows/daily_master_pipeline.yml/dispatches', {{
          method: 'POST',
          headers: {{
            'Accept': 'application/vnd.github.v3+json',
            'Authorization': `Bearer ${{ghToken}}`,
            'User-Agent': 'FinPress-Cloudflare-Cron',
            'Content-Type': 'application/json'
          }},
          body: JSON.stringify({{ ref: 'main' }})
        }});
      }} catch(err) {{
        console.error('Cloudflare Cron Trigger error:', err);
      }}
    }}
  }}
}};
"""
    with open('worker.js', 'w', encoding='utf-8') as f:
        f.write(worker_code)
    print("Worker and index.html built successfully.")

if __name__ == '__main__':
    build()
