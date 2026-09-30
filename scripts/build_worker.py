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
        const ghToken = env.GH_TOKEN || env.GITHUB_TOKEN;
        if (ghToken) {{
          try {{
            const ghResp = await fetch('https://api.github.com/repos/vedarthain/FinPress/dispatches', {{
              method: 'POST',
              headers: {{
                'Accept': 'application/vnd.github.v3+json',
                'Authorization': `Bearer ${{ghToken}}`,
                'User-Agent': 'FinPress-Cloudflare-Worker',
                'Content-Type': 'application/json'
              }},
              body: JSON.stringify({{
                event_type: 'trigger-bs-pipeline',
                client_payload: {{
                  source: 'finpress_bookmarklet_sync',
                  cookies_count: cookiesList.length,
                  timestamp: new Date().toISOString()
                }}
              }})
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
  }}
}};
"""
    with open('worker.js', 'w', encoding='utf-8') as f:
        f.write(worker_code)
    print("Worker and index.html built successfully.")

if __name__ == '__main__':
    build()
