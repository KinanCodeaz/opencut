from PyQt5.QtCore import QThread, QObject, pyqtSignal
import weakref

class ThreadManager(QObject):
    def __init__(self):
        super().__init__()
        self.threads = weakref.WeakSet()
    
    def add_thread(self, thread):
        """إضافة خيط للمتابعة"""
        self.threads.add(thread)
        thread.finished.connect(lambda: self.remove_thread(thread))
    
    def remove_thread(self, thread):
        """إزالة خيط من المتابعة"""
        if thread in self.threads:
            self.threads.discard(thread)
    
    def cleanup_all(self):
        """تنظيف جميع الخيوط"""
        for thread in list(self.threads):
            if thread.isRunning():
                thread.quit()
                thread.wait(1000)
        
        self.threads.clear()

# إنشاء نسخة واحدة من ThreadManager
thread_manager = ThreadManager()