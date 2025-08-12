from PyQt5.QtWidgets import QMenuBar, QMenu, QAction
from PyQt5.QtGui import QKeySequence

class MenuBar(QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        
        # إنشاء القوائم
        self.create_file_menu()
        self.create_edit_menu()
        self.create_view_menu()
        self.create_tools_menu()
        self.create_help_menu()
    
    def create_file_menu(self):
        """إنشاء قائمة الملفات"""
        file_menu = self.addMenu("File")
        
        # إضافة إجراءات القائمة
        new_project_action = QAction("New Project", self)
        new_project_action.setShortcut(QKeySequence.New)
        new_project_action.triggered.connect(self.parent.new_project)
        file_menu.addAction(new_project_action)
        
        open_project_action = QAction("Open File", self)
        open_project_action.setShortcut(QKeySequence.Open)
        open_project_action.triggered.connect(self.parent.open_file)
        file_menu.addAction(open_project_action)
        
        save_project_action = QAction("Save Project", self)
        save_project_action.setShortcut(QKeySequence.Save)
        save_project_action.triggered.connect(self.parent.save_project)
        file_menu.addAction(save_project_action)
        
        export_action = QAction("Export", self)
        export_action.setShortcut("Ctrl+M")
        export_action.triggered.connect(self.parent.export_project)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.parent.close)
        file_menu.addAction(exit_action)
    
    def create_edit_menu(self):
        """إنشاء قائمة التحرير"""
        edit_menu = self.addMenu("Edit")
        
        undo_action = QAction("Undo", self)
        undo_action.setShortcut(QKeySequence.Undo)
        undo_action.triggered.connect(self.parent.undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("Redo", self)
        redo_action.setShortcut(QKeySequence.Redo)
        redo_action.triggered.connect(self.parent.redo)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        cut_action = QAction("Cut", self)
        cut_action.setShortcut(QKeySequence.Cut)
        cut_action.triggered.connect(self.parent.cut)
        edit_menu.addAction(cut_action)
        
        copy_action = QAction("Copy", self)
        copy_action.setShortcut(QKeySequence.Copy)
        copy_action.triggered.connect(self.parent.copy)
        edit_menu.addAction(copy_action)
        
        paste_action = QAction("Paste", self)
        paste_action.setShortcut(QKeySequence.Paste)
        paste_action.triggered.connect(self.parent.paste)
        edit_menu.addAction(paste_action)
        
        edit_menu.addSeparator()
        
        select_all_action = QAction("Select All", self)
        select_all_action.setShortcut(QKeySequence.SelectAll)
        select_all_action.triggered.connect(self.parent.select_all)
        edit_menu.addAction(select_all_action)
    
    def create_view_menu(self):
        """إنشاء قائمة العرض"""
        view_menu = self.addMenu("View")
        
        # قائمة التيمات
        themes_menu = view_menu.addMenu("Themes")
        
        # الحصول على قائمة التيمات المتاحة
        themes = self.parent.get_available_themes()
        
        # إضافة كل تيم كعنصر في القائمة
        for theme_name in themes:
            theme_action = QAction(theme_name, self)
            theme_action.triggered.connect(lambda checked, name=theme_name: self.parent.apply_theme(name))
            themes_menu.addAction(theme_action)
    
    def create_tools_menu(self):
        """إنشاء قائمة الأدوات"""
        tools_menu = self.addMenu("Tools")
        
        # سيتم إضافة الأدوات لاحقاً
        pass
    
    def create_help_menu(self):
        """إنشاء قائمة المساعدة"""
        help_menu = self.addMenu("Help")
        
        help_action = QAction("Help", self)
        help_action.setShortcut(QKeySequence.HelpContents)
        help_action.triggered.connect(self.parent.show_help)
        help_menu.addAction(help_action)
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.parent.show_about)
        help_menu.addAction(about_action)