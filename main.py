import sys
import traceback
from PyQt5.QtWidgets import QApplication, QMessageBox

try:
    from ui.main_window import MainWindow
    
    def main():
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())
    
    if __name__ == "__main__":
        main()
        
except Exception as e:
    # طباعة الخطأ الكامل
    print("Full error traceback:")
    traceback.print_exc()
    
    # عرض رسالة خطأ للمستخدم
    app = QApplication(sys.argv)
    QMessageBox.critical(None, "Error", f"An error occurred: {str(e)}")
    sys.exit(1)