from PyQt5.QtWidgets import QMenuBar, QMenu, QAction, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt, pyqtSignal
import os
import re

class MenuBar(QMenuBar):
    theme_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.themes_dir = os.path.join("resources", "themes")
        self.theme_actions = []
        self.create_file_menu()
        self.create_edit_menu()
        self.create_view_menu()
        self.create_help_menu()
    
    def create_file_menu(self):
        file_menu = self.addMenu("File")
        
        self.new_project_action = QAction("New Project", self)
        self.new_project_action.setShortcut("Ctrl+N")
        self.new_project_action.triggered.connect(self.new_project)
        file_menu.addAction(self.new_project_action)
        
        self.open_file_action = QAction("Open File", self)
        self.open_file_action.setShortcut("Ctrl+O")
        self.open_file_action.triggered.connect(self.open_file)
        file_menu.addAction(self.open_file_action)
        
        self.save_project_action = QAction("Save Project", self)
        self.save_project_action.setShortcut("Ctrl+S")
        self.save_project_action.triggered.connect(self.save_project)
        file_menu.addAction(self.save_project_action)
        
        file_menu.addSeparator()
        
        self.export_action = QAction("Export", self)
        self.export_action.setShortcut("Ctrl+E")
        self.export_action.triggered.connect(self.export_project)
        file_menu.addAction(self.export_action)
        
        file_menu.addSeparator()
        
        self.exit_action = QAction("Exit", self)
        self.exit_action.setShortcut("Ctrl+Q")
        self.exit_action.triggered.connect(self.parent.close)
        file_menu.addAction(self.exit_action)
    
    def create_edit_menu(self):
        edit_menu = self.addMenu("Edit")
        
        self.undo_action = QAction("Undo", self)
        self.undo_action.setShortcut("Ctrl+Z")
        self.undo_action.triggered.connect(self.undo)
        edit_menu.addAction(self.undo_action)
        
        self.redo_action = QAction("Redo", self)
        self.redo_action.setShortcut("Ctrl+Y")
        self.redo_action.triggered.connect(self.redo)
        edit_menu.addAction(self.redo_action)
        
        edit_menu.addSeparator()
        
        self.cut_action = QAction("Cut", self)
        self.cut_action.setShortcut("Ctrl+X")
        self.cut_action.triggered.connect(self.cut)
        edit_menu.addAction(self.cut_action)
        
        self.copy_action = QAction("Copy", self)
        self.copy_action.setShortcut("Ctrl+C")
        self.copy_action.triggered.connect(self.copy)
        edit_menu.addAction(self.copy_action)
        
        self.paste_action = QAction("Paste", self)
        self.paste_action.setShortcut("Ctrl+V")
        self.paste_action.triggered.connect(self.paste)
        edit_menu.addAction(self.paste_action)
        
        edit_menu.addSeparator()
        
        self.select_all_action = QAction("Select All", self)
        self.select_all_action.setShortcut("Ctrl+A")
        self.select_all_action.triggered.connect(self.select_all)
        edit_menu.addAction(self.select_all_action)
    
    def create_view_menu(self):
        view_menu = self.addMenu("View")
        themes_menu = view_menu.addMenu("Themes")
        self.theme_actions.clear()
        
        current_theme = self.parent.settings.value("theme", "")
        
        # مسار ملف الثيمات الموحد
        theme_file_path = os.path.join(self.themes_dir, "all_themes.css")
        
        if os.path.exists(theme_file_path):
            try:
                with open(theme_file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # استخراج أسماء الثيمات باستخدام التعبير النمطي
                theme_pattern = r'/\*THEME:\s*([^\*]+)\*/'
                theme_names = re.findall(theme_pattern, content)
                
                for theme_name in theme_names:
                    theme_name = theme_name.strip()
                    
                    # إضافة علامة * للثيم النشط
                    display_name = theme_name
                    if theme_name == current_theme:
                        display_name = "* " + theme_name
                    
                    action = QAction(display_name, self, checkable=True)
                    if theme_name == current_theme:
                        action.setChecked(True)
                    
                    # ربط الحدث باسم الثيم واسم الملف
                    action.triggered.connect(
                        lambda checked, t=theme_name: self.set_theme(t, "all_themes.css")
                    )
                    
                    themes_menu.addAction(action)
                    self.theme_actions.append(action)
                    
            except Exception as e:
                print(f"Error reading themes: {e}")
                action = QAction("Error loading themes", self)
                action.setEnabled(False)
                themes_menu.addAction(action)
        else:
            print(f"Theme file not found: {theme_file_path}")
            action = QAction("No themes found", self)
            action.setEnabled(False)
            themes_menu.addAction(action)
    
    def set_theme(self, theme_name, file_name):
        self.apply_theme(theme_name, file_name)
        
        # تحديث العلامة في القائمة
        current_theme = self.parent.settings.value("theme", "")
        for act in self.theme_actions:
            # إزالة أي علامات موجودة
            clean_text = act.text().replace("* ", "").replace("• ", "").replace("✓ ", "")
            act.setText(clean_text)
            
            # إضافة العلامة للثيم الحالي فقط
            if clean_text == current_theme:
                act.setText("* " + clean_text)
    
    def apply_theme(self, theme_name, file_name):
        theme_path = os.path.join(self.themes_dir, file_name)
        if os.path.exists(theme_path):
            try:
                with open(theme_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # البحث عن بداية الثيم المحدد
                start_marker = f"/*THEME: {theme_name}*/"
                start_index = content.find(start_marker)
                
                if start_index == -1:
                    print(f"Theme '{theme_name}' not found")
                    return
                
                # البحث عن بداية الثيم التالي أو نهاية الملف
                next_theme_pattern = r'/\*THEME:'
                next_match = re.search(next_theme_pattern, content[start_index + 1:])
                
                if next_match:
                    end_index = start_index + 1 + next_match.start()
                else:
                    end_index = len(content)
                
                # استخراج CSS للثيم المحدد
                theme_css = content[start_index:end_index].strip()
                
                # تطبيق الثيم
                self.parent.setStyleSheet(theme_css)
                self.parent.settings.setValue("theme", theme_name)
                self.theme_changed.emit(file_name)
                # الإصلاح هنا
                self.parent.statusBar().showMessage(f"Theme applied: {theme_name}", 2000)
                
            except Exception as e:
                QMessageBox.warning(self.parent, "Theme Error", f"Could not apply theme: {e}")
        else:
            print(f"Theme file not found: {theme_path}")
    
    def create_help_menu(self):
        help_menu = self.addMenu("Help")
        
        self.help_action = QAction("Help", self)
        self.help_action.setShortcut("F1")
        self.help_action.triggered.connect(self.show_help)
        help_menu.addAction(self.help_action)
        
        help_menu.addSeparator()
        
        self.about_action = QAction("About", self)
        self.about_action.triggered.connect(self.show_about)
        help_menu.addAction(self.about_action)
    
    def new_project(self):
        reply = QMessageBox.question(
            self.parent, "New Project",
            "Are you sure you want to create a new project? Any unsaved changes will be lost.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if hasattr(self.parent, 'timeline_panel'):
                for track in self.parent.timeline_panel.tracks:
                    for item in track['items']:
                        self.parent.timeline_panel.scene.removeItem(item)
                    track['items'].clear()
                
                self.parent.timeline_panel.tracks = []
                self.parent.timeline_panel.add_track()
            
            if hasattr(self.parent, 'media_panel'):
                self.parent.media_panel.media_list.clear()
            
            # الإصلاح هنا
            self.parent.statusBar().showMessage("New project created", 2000)
    
    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self.parent, "Open Media File", "",
            "Media Files (*.mp4 *.avi *.mov *.mkv *.mp3 *.wav *.flac *.jpg *.png *.gif);;All Files (*)"
        )
        
        if file_path:
            if hasattr(self.parent, 'media_panel'):
                self.parent.media_panel.add_media_item(file_path)
            
            # الإصلاح هنا
            self.parent.statusBar().showMessage(f"Opened: {os.path.basename(file_path)}", 2000)
    
    def save_project(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self.parent, "Save Project", "",
            "OpenCut Project (*.ocp);;All Files (*)"
        )
        
        if file_path:
            # الإصلاح هنا
            self.parent.statusBar().showMessage(f"Project saved to: {file_path}", 2000)
    
    def export_project(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self.parent, "Export Video", "",
            "MP4 Video (*.mp4);;AVI Video (*.avi);;MOV Video (*.mov);;All Files (*)"
        )
        
        if file_path:
            # الإصلاح هنا
            self.parent.statusBar().showMessage(f"Exporting to: {file_path}", 2000)
    
    def undo(self):
        # الإصلاح هنا
        self.parent.statusBar().showMessage("Undo", 2000)
    
    def redo(self):
        # الإصلاح هنا
        self.parent.statusBar().showMessage("Redo", 2000)
    
    def cut(self):
        # الإصلاح هنا
        self.parent.statusBar().showMessage("Cut", 2000)
    
    def copy(self):
        # الإصلاح هنا
        self.parent.statusBar().showMessage("Copy", 2000)
    
    def paste(self):
        # الإصلاح هنا
        self.parent.statusBar().showMessage("Paste", 2000)
    
    def select_all(self):
        if hasattr(self.parent, 'timeline_panel'):
            self.parent.timeline_panel.select_all()
        if hasattr(self.parent, 'media_panel'):
            self.parent.media_panel.media_list.selectAll()
        
        # الإصلاح هنا
        self.parent.statusBar().showMessage("All items selected", 2000)
    
    def show_help(self):
        QMessageBox.information(
            self.parent, "Help",
            "OpenCut Video Editor Help\n\n"
            "1. Add media files using the 'Add File' button\n"
            "2. Select files and click 'Send to Timeline'\n"
            "3. Drag and drop files to rearrange them\n"
            "4. Use the player to preview your edits\n"
            "5. Export your project when finished"
        )
    
    def show_about(self):
        about_file = "resources/about.txt"
        about_text = "OpenCut Video Editor v1.0\n\nA lightweight video editor built with PyQt5"
        
        if os.path.exists(about_file):
            try:
                with open(about_file, 'r', encoding='utf-8') as f:
                    about_text = f.read()
            except Exception as e:
                print(f"Error reading about file: {e}")
        
        QMessageBox.about(self.parent, "About OpenCut", about_text)