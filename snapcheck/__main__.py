import os
from . import SnapcheckWebBackend
import sys

def web_server_gui(web_backend):
    import http, http.server
    from soma.web import SomaHTTPHandler

    class Handler(SomaHTTPHandler, web_backend=web_backend):
        pass

    httpd = http.server.HTTPServer(("", 8080), Handler)
    httpd.serve_forever()


def qt_web_gui(web_backend):
    import sys
    from soma.qt_gui.qt_backend import Qt
    from soma.web import SomaBrowserWidget

    s = os.path.split(os.path.dirname(__file__)) + ("static",)
    starting_url = f'file://{"/".join(s)}/index.html'
    app = Qt.QApplication(sys.argv)
    w = SomaBrowserWidget(
        starting_url=starting_url,
        web_backend=web_backend,
    )
    w.show()
    app.exec_()


if len(sys.argv) > 1 and sys.argv[0] in ('-w', '--web'):
    web_backend = SnapcheckWebBackend(database=sys.argv[2])
    web_server_gui(web_backend)
else:
    web_backend = SnapcheckWebBackend(database=sys.argv[1])
    qt_web_gui(web_backend)
