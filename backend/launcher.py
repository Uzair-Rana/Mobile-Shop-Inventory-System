"""
Desktop launcher for the packaged installer.

On launch it:
  1. Points the app's data (DB, media, activation flag) at a per-user writable
     folder (%LOCALAPPDATA%\\MyPhoneERP) so it works from Program Files.
  2. Starts waitress immediately and opens the browser on a "Starting..." page,
     while migrations / collectstatic / default admin (admin / admin123) run.
  3. Shows a system-tray icon with "Open My Phone ERP" and "Quit".
  4. Logs to %LOCALAPPDATA%\\MyPhoneERP\\launcher.log; a second launch just
     opens the browser on the running instance.

Run directly for testing:  python launcher.py
Built into an .exe by:      pyinstaller myphone.spec
"""
import os
import sys
import socket
import threading
import time
import webbrowser


def _res(rel: str) -> str:
    """Path to a bundled resource (works both frozen and from source)."""
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)


def _data_dir() -> str:
    base = os.environ.get('LOCALAPPDATA') or os.path.expanduser('~')
    path = os.path.join(base, 'MyPhoneERP')
    os.makedirs(path, exist_ok=True)
    return path


def _free_port(preferred=8000) -> int:
    for port in (preferred, 8001, 8080, 8765, 0):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(('127.0.0.1', port))
            actual = s.getsockname()[1]
            s.close()
            return actual
        except OSError:
            continue
    return preferred


def _run_tray(url: str):
    """Show a system-tray icon. Returns False if pystray isn't available."""
    try:
        import pystray
        from PIL import Image
    except Exception:
        return False

    try:
        image = Image.open(_res('apps/web/static/web/logo.png')).convert('RGBA')
    except Exception:
        image = Image.new('RGBA', (64, 64), (225, 29, 72, 255))

    def on_open(icon, item):
        webbrowser.open(url)

    def on_quit(icon, item):
        icon.visible = False
        icon.stop()
        os._exit(0)

    menu = pystray.Menu(
        pystray.MenuItem('Open My Phone ERP', on_open, default=True),
        pystray.MenuItem('Quit', on_quit),
    )
    pystray.Icon('MyPhoneERP', image, 'My Phone ERP', menu).run()
    return True


STARTING_PAGE = b"""<!doctype html><html><head><meta charset="utf-8">
<meta http-equiv="refresh" content="2"><title>Starting My Phone ERP</title></head>
<body style="font-family:Segoe UI,sans-serif;text-align:center;padding-top:15vh;color:#333">
<h2>Starting My Phone ERP&hellip;</h2>
<p>The first launch sets up the database and can take a minute. This page refreshes automatically.</p>
</body></html>"""


def _message_box(text: str, title: str = 'My Phone ERP'):
    """Show a native error dialog (the packaged app has no console)."""
    try:
        import ctypes
        ctypes.windll.user32.MessageBoxW(None, text, title, 0x10)
    except Exception:
        print(text)


def _already_running() -> bool:
    """Single-instance guard via a named Windows mutex."""
    try:
        import ctypes
        ctypes.windll.kernel32.CreateMutexW(None, False, 'Local\\MyPhoneERP')
        return ctypes.windll.kernel32.GetLastError() == 183  # ERROR_ALREADY_EXISTS
    except Exception:
        return False


def _setup_django(state: dict):
    """Migrate, collect static and seed the admin; runs behind the starting page."""
    try:
        import django
        django.setup()

        from django.core.management import call_command
        call_command('migrate', '--noinput')

        # collectstatic only when the app build changed (it is slow when frozen).
        from django.conf import settings
        stamp = os.path.join(settings.DATA_DIR, '.static_build')
        build = str(os.path.getmtime(sys.executable))
        manifest = os.path.join(settings.STATIC_ROOT, 'staticfiles.json')
        current = open(stamp).read() if os.path.exists(stamp) else ''
        if current != build or not os.path.exists(manifest):
            call_command('collectstatic', '--noinput', '--clear', verbosity=0)
            with open(stamp, 'w') as f:
                f.write(build)

        from django.contrib.auth import get_user_model
        User = get_user_model()
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser('admin', '', 'admin123')
            print('Created default admin: username admin, password admin123')

        from devnest.wsgi import application
        state['app'] = application
    except Exception:
        import traceback
        state['error'] = traceback.format_exc()
        print(state['error'])


def main():
    data_dir = _data_dir()
    port_file = os.path.join(data_dir, '.port')

    if _already_running():
        try:
            webbrowser.open(f'http://127.0.0.1:{open(port_file).read().strip()}/')
        except OSError:
            pass
        return

    # No console when frozen: keep a log next to the data for troubleshooting.
    log_path = os.path.join(data_dir, 'launcher.log')
    sys.stdout = sys.stderr = open(log_path, 'w', encoding='utf-8', buffering=1)

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'devnest.settings')
    os.environ.setdefault('MYPHONE_DATA_DIR', data_dir)
    os.environ.setdefault('DEBUG', 'False')
    # Force the local SQLite file in DATA_DIR (env var overrides any bundled .env).
    os.environ.setdefault('DATABASE_URL', '')

    port = _free_port(8000)
    url = f'http://127.0.0.1:{port}/'
    with open(port_file, 'w') as f:
        f.write(str(port))

    state = {}

    def app(environ, start_response):
        if 'app' in state:
            return state['app'](environ, start_response)
        if 'error' in state:
            body = ('My Phone ERP failed to start.\n\n' + state['error'] +
                    f'\nLog file: {log_path}').encode('utf-8')
            start_response('500 Internal Server Error', [('Content-Type', 'text/plain; charset=utf-8')])
            return [body]
        start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8')])
        return [STARTING_PAGE]

    def _serve():
        try:
            from waitress import serve
            serve(app, host='127.0.0.1', port=port, threads=8)
        except Exception as e:
            _message_box(f'Could not start the local server on port {port}:\n{e}\n\nLog: {log_path}')
            os._exit(1)

    threading.Thread(target=_serve, daemon=True).start()
    threading.Thread(target=_setup_django, args=(state,), daemon=True).start()
    time.sleep(1)
    webbrowser.open(url)

    # Prefer the tray icon; fall back to a blocking server.
    if not _run_tray(url):
        print(f'My Phone ERP is running at {url}')
        try:
            while True:
                time.sleep(3600)
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    try:
        main()
    except Exception:
        import traceback
        _message_box('My Phone ERP failed to start:\n\n' + traceback.format_exc())
