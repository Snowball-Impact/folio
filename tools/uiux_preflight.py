from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]

def env_keys() -> set[str]:
    keys: set[str] = set()
    for path in (ROOT / '.env', ROOT / 'svelte_app' / '.env'):
        if not path.exists():
            continue
        for raw in path.read_text(encoding='utf-8').splitlines():
            line = raw.strip()
            if line and not line.startswith('#') and '=' in line:
                keys.add(line.split('=', 1)[0].strip())
    return keys

def port_listeners(port: int) -> int:
    try:
        result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True, check=False)
    except OSError:
        return -1
    rows = set()
    for line in result.stdout.splitlines():
        if 'LISTENING' not in line or f':{port}' not in line:
            continue
        parts = line.split()
        if len(parts) >= 5 and parts[3] == 'LISTENING':
            rows.add(parts[4])
    return len(rows)

def check_server(base_url: str, port: int) -> tuple[bool, str]:
    listeners = port_listeners(port)
    if listeners == 0:
        return False, f'no listener on port {port}'
    if listeners > 1:
        return False, f'{listeners} listeners on port {port}'
    try:
        with urlopen(base_url.rstrip('/') + '/', timeout=5) as response:
            status = response.status
            return status == 200, f'HTTP {status}'
    except (OSError, URLError) as exc:
        return False, f'HTTP probe failed: {type(exc).__name__}'

def main() -> int:
    parser = argparse.ArgumentParser(description='Preflight checks for FOLIO UIUX capture runs.')
    parser.add_argument('--base-url', default='http://127.0.0.1:5174')
    parser.add_argument('--port', type=int, default=5174)
    parser.add_argument('--require-server', action='store_true')
    parser.add_argument('--strict', action='store_true')
    args = parser.parse_args()

    results: list[dict[str, str]] = []
    def add(name: str, status: str, detail: str) -> None:
        results.append({'name': name, 'status': status, 'detail': detail})

    try:
        json.loads((ROOT / 'svelte_app' / 'package.json').read_text(encoding='utf-8-sig'))
        add('package_json', 'pass', 'valid JSON')
    except (OSError, json.JSONDecodeError) as exc:
        add('package_json', 'fail', type(exc).__name__)

    pbix = ROOT / 'artifacts' / 'test.pbix'
    add('pbix_fixture', 'pass' if pbix.is_file() and pbix.suffix.lower() == '.pbix' else 'fail', 'artifacts/test.pbix')
    keys = env_keys()
    has_id = bool({'FOLIO_TEST_ID', 'test_id'} & keys)
    has_pw = bool({'FOLIO_TEST_PW', 'test_pw'} & keys)
    add('test_account_keys', 'pass' if has_id and has_pw else 'fail', 'key presence checked; values hidden')

    if args.require_server:
        ok, detail = check_server(args.base_url, args.port)
        add('server', 'pass' if ok else 'fail', detail)
    else:
        add('server', 'pass', 'not required; pass --require-server to probe')

    add('browser_runtime', 'unknown', 'external_check_required; not inferred from local files')

    for result in results:
        state = result['status'].upper()
        print(f"[{state}] {result['name']}: {result['detail']}")
    failed = [result for result in results if result['status'] == 'fail']
    unknown = [result for result in results if result['status'] == 'unknown']
    summary_status = 'fail' if failed else 'blocked_unknown' if args.strict and unknown else 'pass_with_unknown' if unknown else 'pass'
    print(json.dumps({'status': summary_status, 'failed': len(failed), 'unknown': len(unknown)}, ensure_ascii=False))
    if failed:
        return 1
    if args.strict and unknown:
        return 2
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
