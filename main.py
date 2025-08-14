import sys
from PyQt5.QtWidgets import QApplication, QDesktopWidget
from PyQt5.QtGui import QIcon
from ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # إعدادات التطبيق
    app.setApplicationName("PyVideoEditor")
    app.setApplicationVersion("1.0.0")
    
    # إضافة أيقونة التطبيق
    app.setWindowIcon(QIcon("resources/icons/icons_soft.png"))
    
    # إنشاء النافذة الرئيسية
    window = MainWindow()
    
    # فتح النافذة في منتصف الشاشة
    desktop = QDesktopWidget()
    screen_size = desktop.screenGeometry()
    window_size = window.size()
    
    x = (screen_size.width() - window_size.width()) // 2
    y = (screen_size.height() - window_size.height()) // 2
    
    window.move(x, y)
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()