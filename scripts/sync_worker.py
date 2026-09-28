import json

def sync():
    with open('web/index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # Sync to root index.html
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Updated index.html")

    # Sync to worker.js
    with open('worker.js', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Find where const HTML = starts and where the next code starts
    # In worker.js, line 2 was `const HTML = "..."`
    # Let's inspect worker.js logic after HTML
    with open('worker.js', 'r', encoding='utf-8') as f:
        content = f.read()

    prefix = 'const HTML = '
    if prefix in content:
        start_idx = content.find(prefix) + len(prefix)
        # Find where the fetch handler starts: export default { or addEventListener
        handler_marker = '\nexport default {'
        if handler_marker not in content:
            handler_marker = '\naddEventListener('
        
        handler_idx = content.find(handler_marker)
        if handler_idx != -1:
            json_html = json.dumps(html)
            new_worker = content[:start_idx] + json_html + ';' + content[handler_idx:]
            with open('worker.js', 'w', encoding='utf-8') as f:
                f.write(new_worker)
            print("Successfully updated worker.js!")
        else:
            print("Could not find handler marker in worker.js")
    else:
        print("Could not find const HTML = in worker.js")

if __name__ == '__main__':
    sync()
