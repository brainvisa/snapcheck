import os
from soma.qt_gui.qt_backend.Qt import QVariant
from soma.web import WebBackend, json_exception, pyqtSlot


class SnapcheckWebBackend(WebBackend):
    def __init__(self, database):
        super().__init__()
        s = os.path.split(os.path.dirname(__file__)) + ("static",)
        self.static_path.append("/".join(s))

    @pyqtSlot(result=QVariant)
    @json_exception
    def global_info(self):
        return {'modalities': ['amri', 'rsfmri', 'dwi']}
