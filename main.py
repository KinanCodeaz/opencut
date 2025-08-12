import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtMultimedia import QMediaPlayer
from ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # إعدادات التطبيق
    app.setApplicationName("PyVideoEditor")
    app.setApplicationVersion("1.0.0")
    
    # إنشاء النافذة الرئيسية
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()