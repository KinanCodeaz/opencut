from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QMessageBox, QFileDialog
from PyQt5.QtCore import Qt, QSize, QSettings
from PyQt5.QtGui import QIcon, QKeySequence
from .menu_bar import MenuBar
from .media_panel import MediaPanel
from .player_panel import PlayerPanel
from .timeline_panel import TimelinePanel
import os
import shutil

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # إعدادات النافذة الرئيسية
        self.setWindowTitle("PyVideo Editor")
        self.setMinimumSize(1200, 800)
        
        # نظام التاريخ للتراجع والإعادة
        self.history = []  # قائمة لتخزين العمليات
        self.history_index = -1  # مؤشر التاريخ
        self.max_history = 15  # أقصى عدد للعمليات في التاريخ
        
        # إعدادات البرنامج
        self.settings = QSettings("PyVideoEditor", "App")
        
        # إنشاء المكونات الرئيسية
        self.menu_bar = MenuBar(self)
        self.setMenuBar(self.menu_bar)
        
        # إنشاء الحاوية المركزية
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # إنشاء التخطيط الرئيسي
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(2, 2, 2, 2)  # تقليل الهوامش
        main_layout.setSpacing(2)  # تقليل المسافات بين المكونات
        
        # إنشاء تقسيم أفقي للواجهة (قابل لتغيير الحجم)
        horizontal_splitter = QSplitter(Qt.Horizontal)
        horizontal_splitter.setChildrenCollapsible(False)  # منع تصغير النوافذ إلى الصفر
        
        # إضافة لوحة الميديا (على اليسار) - تمرير مرجع النافذة الرئيسية
        self.media_panel = MediaPanel(self)
        self.media_panel.setMinimumWidth(200)  # الحد الأدنى للعرض
        self.media_panel.setMaximumWidth(400)  # الحد الأقصى للعرض
        horizontal_splitter.addWidget(self.media_panel)
        
        # إنشاء تقسيم رأسي للجانب الأيمن (قابل لتغيير الحجم)
        vertical_splitter = QSplitter(Qt.Vertical)
        vertical_splitter.setChildrenCollapsible(False)  # منع تصغير النوافذ إلى الصفر
        
        # إضافة لوحة المشغل (في الأعلى) - زيادة الارتفاع
        self.player_panel = PlayerPanel()
        self.player_panel.setMinimumHeight(400)  # زيادة الحد الأدنى للارتفاع
        vertical_splitter.addWidget(self.player_panel)
        
        # إضافة لوحة التايم لاين (في الأسفل) - زيادة الارتفاع قليلاً
        self.timeline_panel = TimelinePanel()
        self.timeline_panel.setMinimumHeight(180)  # زيادة الحد الأدنى للارتفاع
        self.timeline_panel.setMaximumHeight(300)  # زيادة الحد الأقصى للارتفاع
        vertical_splitter.addWidget(self.timeline_panel)
        
        # إضافة التقسيم الرأسي إلى التقسيم الأفقي
        horizontal_splitter.addWidget(vertical_splitter)
        
        # إضافة التقسيم الأفقي إلى التخطيط الرئيسي
        main_layout.addWidget(horizontal_splitter)
        
        # تعيين نسب التقسيم الأولية (تحسين توزيع المساحات)
        horizontal_splitter.setSizes([250, 950])  # 20% للميديا، 80% للباقي
        vertical_splitter.setSizes([650, 250])    # 72% للمشغل، 28% للتايم لاين (زيادة مساحة المشغل)
        
        # تطبيق الثيم المحفوظ أو الافتراضي
        saved_theme = self.settings.value("theme", "Midnight Pro (Premiere Pro Style)")
        self.apply_theme(saved_theme)
    
    def closeEvent(self, event):
        """حفظ الإعدادات وحذف الصور المصغرة عند إغلاق البرنامج"""
        # حفظ التيم الحالي
        current_theme = self.settings.value("theme", "Midnight Pro (Premiere Pro Style)")
        self.settings.setValue("theme", current_theme)
        
        # حذف مجلد الصور المصغرة
        thumbnails_dir = "resources/thumbnails"
        if os.path.exists(thumbnails_dir):
            try:
                shutil.rmtree(thumbnails_dir)
                print("Thumbnails directory deleted successfully")
            except Exception as e:
                print(f"Error deleting thumbnails directory: {e}")
        
        event.accept()
    
    def keyPressEvent(self, event):
        """معالجة ضغطات المفاتيح"""
        # ESC لإلغاء التحديد
        if event.key() == Qt.Key_Escape:
            self.cancel_selection()
        
        super().keyPressEvent(event)
    
    def apply_theme(self, theme_name):
        """تطبيق الثيم المحدد على الواجهة"""
        theme_path = "resources/themes/all_themes.css"
        try:
            with open(theme_path, "r") as f:
                content = f.read()
            
            # استخراج الثيم المحدد
            start_marker = f"/* THEME: {theme_name} */"
            start_index = content.find(start_marker)
            
            if start_index == -1:
                print(f"Theme '{theme_name}' not found")
                return
            
            # العثور على بداية الثيم التالي أو نهاية الملف
            next_theme_index = content.find("/* THEME:", start_index + len(start_marker))
            
            if next_theme_index == -1:
                theme_css = content[start_index + len(start_marker):].strip()
            else:
                theme_css = content[start_index + len(start_marker):next_theme_index].strip()
            
            self.setStyleSheet(theme_css)
            self.statusBar().showMessage(f"Theme applied: {theme_name}", 2000)
            
            # حفظ الثيم المحدد
            self.settings.setValue("theme", theme_name)
        except FileNotFoundError:
            print(f"Theme file not found: {theme_path}")
    
    def get_available_themes(self):
        """الحصول على قائمة بالتيمات المتاحة"""
        theme_path = "resources/themes/all_themes.css"
        try:
            with open(theme_path, "r") as f:
                content = f.read()
            
            themes = []
            start_index = 0
            
            while True:
                # البحث عن بداية اسم الثيم
                start_marker = "/* THEME: "
                start_index = content.find(start_marker, start_index)
                
                if start_index == -1:
                    break
                
                # استخراج اسم الثيم
                end_index = content.find(" */", start_index)
                if end_index == -1:
                    break
                
                theme_name = content[start_index + len(start_marker):end_index].strip()
                themes.append(theme_name)
                
                start_index = end_index + 1
            
            return themes
        except FileNotFoundError:
            print(f"Theme file not found: {theme_path}")
            return []
    
    # نظام التاريخ للتراجع والإعادة
    def add_to_history(self, action_name, undo_func, redo_func):
        """إضافة عملية إلى سجل التاريخ"""
        # إزالة العمليات بعد المؤشر الحالي
        self.history = self.history[:self.history_index + 1]
        
        # إضافة العملية الجديدة
        self.history.append({
            'name': action_name,
            'undo': undo_func,
            'redo': redo_func
        })
        
        # تحديث المؤشر
        self.history_index += 1
        
        # الحفاظ على الحد الأقصى للتاريخ
        if len(self.history) > self.max_history:
            self.history.pop(0)
            self.history_index -= 1
    
    def undo(self):
        """التراجع عن آخر عملية"""
        if self.history_index >= 0:
            action = self.history[self.history_index]
            action['undo']()
            self.history_index -= 1
            self.statusBar().showMessage(f"Undone: {action['name']}", 2000)
        else:
            self.statusBar().showMessage("Nothing to undo", 2000)
    
    def redo(self):
        """إعادة آخر عملية تم التراجع عنها"""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            action = self.history[self.history_index]
            action['redo']()
            self.statusBar().showMessage(f"Redone: {action['name']}", 2000)
        else:
            self.statusBar().showMessage("Nothing to redo", 2000)
    
    # وظائف قائمة الملفات
    def new_project(self):
        """إنشاء مشروع جديد"""
        reply = QMessageBox.question(
            self, 'New Project',
            'Are you sure you want to create a new project? Unsaved changes will be lost.',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # مسح التاريخ
            self.history = []
            self.history_index = -1
            
            # مسح لوحة الميديا
            self.media_panel.media_list.clear()
            
            # مسح التايم لاين
            # سيتم تنفيذ هذا لاحقاً
            self.statusBar().showMessage("New project created", 2000)
    
    def open_file(self):
        """فتح ملف"""
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("Media Files (*.mp4 *.avi *.mov *.mkv *.mp3 *.wav *.jpg *.png *.gif)")
        
        if file_dialog.exec_():
            selected_files = file_dialog.selectedFiles()
            for file_path in selected_files:
                # إضافة الملف إلى لوحة الميديا
                file_name = file_path.split('/')[-1].split('\\')[-1]  # استخراج اسم الملف فقط
                self.media_panel.media_list.addItem(file_name)
            
            self.statusBar().showMessage(f"Opened {len(selected_files)} file(s)", 2000)
            
            # إضافة إلى التاريخ
            self.add_to_history(
                "Open Files",
                lambda: self.statusBar().showMessage("Undo open files", 2000),
                lambda: self.statusBar().showMessage("Redo open files", 2000)
            )
    
    def save_project(self):
        """حفظ المشروع"""
        file_dialog = QFileDialog()
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.setNameFilter("PyVideo Project (*.pvp)")
        file_dialog.setDefaultSuffix("pvp")
        
        if file_dialog.exec_():
            project_path = file_dialog.selectedFiles()[0]
            
            # حفظ المشروع (سيتم تنفيذ التفاصيل لاحقاً)
            self.statusBar().showMessage(f"Project saved to {project_path}", 2000)
            
            # إضافة إلى التاريخ
            self.add_to_history(
                "Save Project",
                lambda: self.statusBar().showMessage("Undo save project", 2000),
                lambda: self.statusBar().showMessage("Redo save project", 2000)
            )
    
    def export_project(self):
        """تصدير المشروع"""
        file_dialog = QFileDialog()
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.setNameFilter("Video Files (*.mp4)")
        file_dialog.setDefaultSuffix("mp4")
        
        if file_dialog.exec_():
            export_path = file_dialog.selectedFiles()[0]
            
            # تصدير المشروع (سيتم تنفيذ التفاصيل لاحقاً)
            self.statusBar().showMessage(f"Project exported to {export_path}", 2000)
            
            # إضافة إلى التاريخ
            self.add_to_history(
                "Export Project",
                lambda: self.statusBar().showMessage("Undo export project", 2000),
                lambda: self.statusBar().showMessage("Redo export project", 2000)
            )
    
    # وظائف قائمة التحرير
    def cut(self):
        """قص العناصر المحددة"""
        selected_items = self.media_panel.media_list.selectedItems()
        if selected_items:
            # نسخ العناصر المحددة
            self.copied_items = [item.text() for item in selected_items]
            
            # حذف العناصر المحددة
            for item in selected_items:
                self.media_panel.media_list.takeItem(self.media_panel.media_list.row(item))
            
            self.statusBar().showMessage(f"Cut {len(selected_items)} item(s)", 2000)
            
            # إضافة إلى التاريخ
            self.add_to_history(
                "Cut Items",
                lambda: self.statusBar().showMessage("Undo cut items", 2000),
                lambda: self.statusBar().showMessage("Redo cut items", 2000)
            )
    
    def copy(self):
        """نسخ العناصر المحددة"""
        selected_items = self.media_panel.media_list.selectedItems()
        if selected_items:
            self.copied_items = [item.text() for item in selected_items]
            self.statusBar().showMessage(f"Copied {len(selected_items)} item(s)", 2000)
            
            # إضافة إلى التاريخ
            self.add_to_history(
                "Copy Items",
                lambda: self.statusBar().showMessage("Undo copy items", 2000),
                lambda: self.statusBar().showMessage("Redo copy items", 2000)
            )
    
    def paste(self):
        """لصق العناصر"""
        if hasattr(self, 'copied_items') and self.copied_items:
            for item_text in self.copied_items:
                self.media_panel.media_list.addItem(item_text)
            
            self.statusBar().showMessage(f"Pasted {len(self.copied_items)} item(s)", 2000)
            
            # إضافة إلى التاريخ
            self.add_to_history(
                "Paste Items",
                lambda: self.statusBar().showMessage("Undo paste items", 2000),
                lambda: self.statusBar().showMessage("Redo paste items", 2000)
            )
    
    def select_all(self):
        """تحديد كل العناصر في النافذة النشطة"""
        # تحديد كل العناصر في لوحة الميديا
        self.media_panel.media_list.selectAll()
        
        # تحديد كل العناصر في التايم لاين
        # سيتم تنفيذ هذا لاحقاً
        self.statusBar().showMessage("All items selected", 2000)
        
        # إضافة إلى التاريخ
        self.add_to_history(
            "Select All",
            lambda: self.statusBar().showMessage("Undo select all", 2000),
            lambda: self.statusBar().showMessage("Redo select all", 2000)
        )
    
    def cancel_selection(self):
        """إلغاء التحديد"""
        # إلغاء التحديد في لوحة الميديا
        self.media_panel.media_list.clearSelection()
        
        # إلغاء التحديد في التايم لاين
        # سيتم تنفيذ هذا لاحقاً
        self.statusBar().showMessage("Selection canceled", 2000)
    
    # وظائف قائمة المساعدة
    def show_help(self):
        """عرض نافذة المساعدة"""
        QMessageBox.information(
            self, "Help",
            "PyVideo Editor Help\n\n"
            "Shortcuts:\n"
            "Ctrl+O - Open file\n"
            "Ctrl+S - Save project\n"
            "Ctrl+M - Export project\n"
            "Ctrl+Q - Exit\n"
            "Ctrl+Z - Undo\n"
            "Ctrl+Y - Redo\n"
            "Ctrl+X - Cut\n"
            "Ctrl+C - Copy\n"
            "Ctrl+V - Paste\n"
            "Ctrl+A - Select all\n"
            "F1 - Help\n"
            "ESC - Cancel selection"
        )
    
    def show_about(self):
        """عرض نافذة حول البرنامج"""
        try:
            with open("resources/about.txt", "r") as f:
                about_text = f.read()
            QMessageBox.about(self, "About PyVideo Editor", about_text)
        except FileNotFoundError:
            QMessageBox.about(
                self, "About PyVideo Editor",
                "PyVideo Editor\nVersion 1.0.0\n\n"
                "A lightweight video editor built with PyQt5."
            )