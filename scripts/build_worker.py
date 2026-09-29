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
