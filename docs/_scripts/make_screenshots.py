"""Take the screenshots of the application for the documentation (docs/_static/screenshots).

Run it in the lepton-dev-env environment, after building the frontend (``npm run build``):

    python docs/_scripts/make_screenshots.py

It creates demo snaps in a temporary home directory, starts the backend, serves the built frontend
and displays it in a Qt web view without display (offscreen). It opens a snap from the Files panel,
then saves the screenshots.
"""

import os
import subprocess
import sys
import tempfile
import threading
import time
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "examples" / "test_data"
FRONTEND_DIR = ROOT / "dist"
OUTPUT_DIR = ROOT / "docs" / "_static" / "screenshots"
HOST = "127.0.0.1"
BACKEND_PORT = 8095
FRONTEND_PORT = 3095
WINDOW_SIZE = (1400, 860)
SNAP_NAME = "mni_qc_S01.snpk"

sys.path.insert(0, str(ROOT / "python"))


def create_demo_snaps(home: Path):
    """Create the snaps displayed in the screenshots, partially rated."""
    from snapcheck.snap import Board, ImageElement, Snap
    from snapcheck.snap.rating import Rating, RatingScale, RatingScaleItem

    scale = RatingScale(
        description="Quality",
        ratings=[
            RatingScaleItem(name="Too bad", value=0, color="#330C00"),
            RatingScaleItem(name="Bad", value=1, color="#5f3c00"),
            RatingScaleItem(name="Good", value=2, color="#5A5400"),
            RatingScaleItem(name="Perfect", value=3, color="#364900"),
        ],
    )
    for subject in ("S01", "S02", "S03"):
        axial = Rating(name="Axial view", description="Quality of the axial view", scale=scale, value=3)
        coronal = Rating(name="Coronal view", scale=scale, value=2, comment="Slightly blurred")
        lightbox = Rating(name="Lightbox", scale=scale)
        observations = Rating(name="Observations", comment="Template v1.0")
        boards = [
            Board(
                title="Axial & coronal views",
                description="Check the contrast and the orientation of the views.",
                elements=[
                    ImageElement(title="Axial", src=str(DATA_DIR / "mni_axial.png"), intended_ratings=[axial]),
                    ImageElement(title="Coronal", src=str(DATA_DIR / "mni_coronal.png"), intended_ratings=[coronal]),
                ],
            ),
            Board(
                title="Lightbox",
                description="Check all the slices.",
                elements=[ImageElement(src=str(DATA_DIR / "mni_lightbox.png"), intended_ratings=[lightbox])],
            ),
        ]
        snap = Snap(
            title=f"MNI template QC - {subject}",
            ratings=[observations],
            boards=boards,
        )
        snap.save(str(home / f"mni_qc_{subject}.snpk"))


def serve_frontend() -> ThreadingHTTPServer:
    """Serve the built frontend in a thread."""

    class QuietHandler(SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            pass

    server = ThreadingHTTPServer((HOST, FRONTEND_PORT), partial(QuietHandler, directory=str(FRONTEND_DIR)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def wait_for(url: str, tries: int = 100):
    for _ in range(tries):
        try:
            requests.get(url, timeout=1)
            return
        except requests.exceptions.ConnectionError:
            time.sleep(0.2)
    sys.exit(f"{url} did not answer")


def take_screenshots():
    from PyQt5.QtCore import QPoint, QTimer, QUrl
    from PyQt5.QtTest import QTest
    from PyQt5.QtWebEngineWidgets import QWebEngineView
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    view = QWebEngineView()
    view.resize(*WINDOW_SIZE)
    view.show()

    def run_js(script: str, delay_ms: int, then):
        QTimer.singleShot(delay_ms, lambda: view.page().runJavaScript(script, lambda _: then()))

    def save(name: str, then):
        def _save():
            path = OUTPUT_DIR / name
            view.grab().save(str(path))
            print(f"Saved {path.relative_to(ROOT)}")
            then()

        QTimer.singleShot(1500, _save)

    # Open the snap with a double click in the Files panel
    open_snap = f"""
        const item = [...document.querySelectorAll('.files-browser-items li')]
            .find((li) => li.textContent.trim() === '{SNAP_NAME}');
        if (item) item.dispatchEvent(new MouseEvent('dblclick', {{ bubbles: true }}));
    """
    # Open the context menu of the first element of the board
    context_menu = """
        const element = document.querySelector('.board-element');
        const rect = element.getBoundingClientRect();
        element.dispatchEvent(new MouseEvent('contextmenu', {
            bubbles: true, clientX: rect.left + rect.width / 2, clientY: rect.top + rect.height / 3,
        }));
    """
    # Position of the first rating of the menu, hovered to open its levels
    rating_item_position = """
        (() => {
            const item = [...document.querySelectorAll('.contextual-menu-item')]
                .find((el) => el.textContent.startsWith('Axial view'));
            const rect = item.getBoundingClientRect();
            return [rect.left + rect.width / 2, rect.top + rect.height / 2];
        })()
    """

    def hover(position):
        # A real mouse move, as React ignores the synthetic hover events
        QTest.mouseMove(view.focusProxy(), QPoint(int(position[0]), int(position[1])))
        save("context_menu.png", app.quit)

    def step_open():
        run_js(open_snap, 0, lambda: save("main_window.png", step_menu))

    def step_menu():
        run_js(context_menu, 500, lambda: QTimer.singleShot(300, open_levels))

    def open_levels():
        view.page().runJavaScript(rating_item_position, hover)

    view.loadFinished.connect(lambda ok: QTimer.singleShot(3000, step_open))
    view.load(QUrl(f"http://{HOST}:{FRONTEND_PORT}/?api=http://{HOST}:{BACKEND_PORT}"))
    app.exec_()


def main():
    if not (FRONTEND_DIR / "index.html").is_file():
        sys.exit(f"The frontend is not built in {FRONTEND_DIR}: run npm run build")
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    os.environ.setdefault("QTWEBENGINE_DISABLE_SANDBOX", "1")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="snapcheck_screenshots_") as home:
        home = Path(home)
        create_demo_snaps(home)

        # The Files panel opens the home directory of the backend
        env = dict(
            os.environ,
            HOME=str(home),
            SNAP_ALLOW_ORIGINS=f"http://{HOST}:{FRONTEND_PORT}",
            PYTHONPATH=os.pathsep.join([str(ROOT / "python"), os.environ.get("PYTHONPATH", "")]),
        )
        backend = subprocess.Popen(
            [sys.executable, "-m", "snapserve", "--host", HOST, "--port", str(BACKEND_PORT)],
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        server = serve_frontend()
        try:
            wait_for(f"http://{HOST}:{BACKEND_PORT}/docs")
            take_screenshots()
        finally:
            server.shutdown()
            backend.terminate()
            backend.wait()


if __name__ == "__main__":
    main()
