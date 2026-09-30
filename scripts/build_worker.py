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
      const dates = ['2026-09-29', '2026-09-28', '2026-09-27'];
      return new Response(JSON.stringify(dates), {{
        headers: {{
          'Content-Type': 'application/json; charset=utf-8',
          'Access-Control-Allow-Origin': '*',
          'Cache-Control': 'no-cache, no-store, must-revalidate'
        }}
      }});
    }}

    // Default: Serve Trader Terminal UI
    return new Response(HTML, {{
      headers: {{
        'Content-Type': 'text/html; charset=utf-8',
        'Cache-Control': 'no-cache, no-store, must-revalidate'
      }}
    }});
  }},

  // Automatic Cloudflare Cron Trigger (Runs daily at 5:45 AM & 6:15 AM IST)
  async scheduled(event, env, ctx) {{
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
