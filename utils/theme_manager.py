import os
from PyQt5.QtCore import QObject, pyqtSignal

class ThemeManager(QObject):
    theme_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.current_theme = "midnight_pro"
        self.themes_file = "resources/themes/all_themes.css"
        self.available_themes = self._load_available_themes()
    
    def _load_available_themes(self):
        """تحميل الثيمات من الملف الموحد"""
        themes = {}
        
        if os.path.exists(self.themes_file):
            try:
                with open(self.themes_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # تقسيم المحتوى إلى ثيمات منفصلة
                theme_blocks = content.split('/* THEME:')
                    
                for block in theme_blocks[1:]:  # تجاهل الأول الفارغ
                    lines = block.strip().split('\n')
                    if lines:
                        # استخراج اسم الثيم من السطر الأول
                        theme_name = lines[0].strip()
                        theme_id = theme_name.lower().replace(' ', '_')
                        themes[theme_id] = {
                            'name': theme_name,
                            'content': block
                        }
            except Exception as e:
                print(f"Error loading themes: {e}")
        
        return themes
    
    def get_available_themes(self):
        """الحصول على قائمة الثيمات المتاحة"""
        return list(self.available_themes.keys())
    
    def get_theme_names(self):
        """الحصول على أسماء الثيمات المعروضة"""
        names = {}
        for theme_id, theme_info in self.available_themes.items():
            names[theme_id] = theme_info['name']
        return names
    
    def get_theme_stylesheet(self, theme_name):
        """الحصول على stylesheet لثيم معين"""
        if theme_name in self.available_themes:
            theme_info = self.available_themes[theme_name]
            
            try:
                # استخراج الجزء الخاص بالثيم المطلوب
                content = theme_info['content']
                theme_start = f"/* THEME: {theme_info['name']} */"
                theme_end = content.find('/* THEME:', content.find(theme_start) + 1)
                
                if theme_end == -1:
                    # إذا كان هذا هو الثيم الأخير
                    theme_css = content[content.find(theme_start):]
                else:
                    theme_css = content[content.find(theme_start):theme_end]
                
                return theme_css
            except Exception as e:
                print(f"Error loading theme {theme_name}: {e}")
        
        # العودة إلى الثيم الافتراضي في حالة الخطأ
        try:
            default_theme = self.available_themes.get("midnight_pro")
            if default_theme:
                return default_theme['content']
        except:
            return ""
    
    def apply_theme(self, widget, theme_name=None):
        """تطبيق ثيم على ويدجت معين"""
        if theme_name is None:
            theme_name = self.current_theme
        
        stylesheet = self.get_theme_stylesheet(theme_name)
        widget.setStyleSheet(stylesheet)
        
        if theme_name != self.current_theme:
            self.current_theme = theme_name
            self.theme_changed.emit(theme_name)
    
    def get_current_theme(self):
        """الحصول على الثيم الحالي"""
        return self.current_theme