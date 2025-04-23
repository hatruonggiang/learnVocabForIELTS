from PyQt6.QtCore import QObject, pyqtSignal

class GenericWorker(QObject):
    progress = pyqtSignal(str)
    finished = pyqtSignal(object)
    
    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        try:
            result = self.func(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            self.progress.emit(f"❌ Error: {str(e)}")
            self.finished.emit(None)
