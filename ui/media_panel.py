import os
import cv2
from PIL import Image, ImageDraw, ImageFont
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QListWidget, 
                            QAbstractItemView, QFileDialog, QMessageBox, 
                            QListWidgetItem, QMenu, QAction, QInputDialog)
from PyQt5.QtCore import Qt, QSize, QPoint, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap, QFont, QImage, QPainter
import time

class ThumbnailThread(QThread):
    """خيط منفصل لإنشاء الصور المصغرة"""
    thumbnail_ready = pyqtSignal(str, object)  # إشارة عند اكتمال الصورة المصغرة
    
    def __init__(self, file_path, file_ext, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.file_ext = file_ext
    
    def run(self):
        """إنشاء الصورة المصغرة في خيط منفصل"""
        thumbnail = self.create_thumbnail(self.file_path, self.file_ext)
        self.thumbnail_ready.emit(self.file_path, thumbnail)
    
    def create_thumbnail(self, file_path, file_ext):
        """إنشاء صورة مصغرة للملف"""
        try:
            # إنشاء مسار للصورة المصغرة
            file_hash = str(hash(file_path))
            thumbnail_path = f"resources/thumbnails/{file_hash}.jpg"
            
            # إذا كانت الصورة المصغرة موجودة بالفعل، أرجعها
            if os.path.exists(thumbnail_path) and os.path.getsize(thumbnail_path) > 0:
                return thumbnail_path
            
            # إنشاء صورة مصغرة حسب نوع الملف
            if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']:
                # للصور، قم بتغيير الحجم مباشرة
                with Image.open(file_path) as img:
                    img.thumbnail((100, 100))
                    img.save(thumbnail_path, quality=95)
                return thumbnail_path
            
            elif file_ext in ['.mp4', '.avi', '.mov', '.mkv']:
                # للفيديو، استخدم إطارًا أول
                cap = cv2.VideoCapture(file_path)
                success, frame = cap.read()
                if success:
                    # تحويل من BGR إلى RGB
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(frame)
                    img.thumbnail((100, 100))
                    img.save(thumbnail_path, quality=95)
                    cap.release()
                    return thumbnail_path
                cap.release()
            
            elif file_ext in ['.mp3', '.wav']:
                # للصوت، أنشئ صورة مع اسم الملف
                img = Image.new('RGB', (100, 100), color=(73, 109, 137))
                d = ImageDraw.Draw(img)
                try:
                    font = ImageFont.truetype("arial.ttf", 12)
                except:
                    font = ImageFont.load_default()
                d.text((10, 10), "AUDIO", fill=(255, 255, 255), font=font)
                img.save(thumbnail_path, quality=95)
                return thumbnail_path
            
            return None
        except Exception as e:
            print(f"Error creating thumbnail: {e}")
            return None

class MediaPanel(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.thumbnail_threads = {}  # لتتبع خيوط الصور المصغرة
        
        # إعدادات اللوحة
        self.setMinimumWidth(200)
        self.setMaximumWidth(300)
        
        # إنشاء التخطيط
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)  # تقليل الهوامش
        layout.setSpacing(2)  # تقليل المسافات بين المكونات
        
        # زر إضافة الملفات
        add_files_btn = QPushButton("Add Files")
        add_files_btn.clicked.connect(self.add_files)
        layout.addWidget(add_files_btn)
        
        # قائمة الملفات - تقليل المسافات بين العناصر
        self.media_list = QListWidget()
        self.media_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.media_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.media_list.customContextMenuRequested.connect(self.show_context_menu)
        self.media_list.setViewMode(QListWidget.IconMode)
        self.media_list.setIconSize(QSize(80, 80))  # تقليل حجم الأيقونات
        self.media_list.setResizeMode(QListWidget.Adjust)
        self.media_list.setGridSize(QSize(90, 90))  # تقليل حجم الشبكة لتقليل المسافات
        self.media_list.setSpacing(2)  # تقليل المسافة بين العناصر
        layout.addWidget(self.media_list)
        
        # أزرار التحكم
        controls_layout = QVBoxLayout()
        controls_layout.setSpacing(2)  # تقليل المسافات بين الأزرار
        
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self.remove_selected)
        controls_layout.addWidget(remove_btn)
        
        properties_btn = QPushButton("Properties")
        properties_btn.clicked.connect(self.show_properties)
        controls_layout.addWidget(properties_btn)
        
        layout.addLayout(controls_layout)
        
        # إنشاء مجلد الصور المصغرة إذا لم يكن موجوداً
        os.makedirs("resources/thumbnails", exist_ok=True)
    
    def add_files(self):
        """إضافة ملفات جديدة إلى القائمة"""
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("Media Files (*.mp4 *.avi *.mov *.mkv *.mp3 *.wav *.jpg *.png *.gif *.bmp *.tiff)")
        
        if file_dialog.exec_():
            selected_files = file_dialog.selectedFiles()
            for file_path in selected_files:
                # إضافة الملف إلى القائمة مع صورة مصغرة
                self.add_media_item(file_path)
            
            self.main_window.statusBar().showMessage(f"Added {len(selected_files)} file(s)", 2000)
    
    def add_media_item(self, file_path):
        """إضافة عنصر ميديا إلى القائمة مع صورة مصغرة"""
        file_name = os.path.basename(file_path)
        file_ext = os.path.splitext(file_name)[1].lower()
        
        # اختصار الاسم الطويل
        if len(file_name) > 20:
            name, ext = os.path.splitext(file_name)
            file_name = name[:17] + "..." + ext
        
        # إنشاء عنصر القائمة
        item = QListWidgetItem(self.media_list)
        item.setText(file_name)
        item.setData(Qt.UserRole, file_path)  # حفظ المسار الكامل
        
        # تعيين أيقونة مؤقتة
        if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']:
            item.setIcon(QIcon("resources/icons/image.png"))
        elif file_ext in ['.mp3', '.wav']:
            item.setIcon(QIcon("resources/icons/audio.png"))
        elif file_ext in ['.mp4', '.avi', '.mov', '.mkv']:
            item.setIcon(QIcon("resources/icons/video.png"))
        
        # إنشاء الصورة المصغرة في خيط منفصل
        thread = ThumbnailThread(file_path, file_ext)
        thread.thumbnail_ready.connect(self.set_thumbnail)
        self.thumbnail_threads[file_path] = thread
        thread.start()
    
    def set_thumbnail(self, file_path, thumbnail_path):
        """تعيين الصورة المصغرة للعنصر"""
        # البحث عن العنصر المطابق للمسار
        for i in range(self.media_list.count()):
            item = self.media_list.item(i)
            if item.data(Qt.UserRole) == file_path:
                if thumbnail_path and os.path.exists(thumbnail_path):
                    item.setIcon(QIcon(thumbnail_path))
                break
        
        # حذف الخيط من القائمة
        if file_path in self.thumbnail_threads:
            del self.thumbnail_threads[file_path]
    
    def remove_selected(self):
        """إزالة العناصر المحددة من القائمة"""
        selected_items = self.media_list.selectedItems()
        if selected_items:
            reply = QMessageBox.question(
                self, 'Remove Items',
                f'Are you sure you want to remove {len(selected_items)} item(s)?',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                for item in selected_items:
                    file_path = item.data(Qt.UserRole)
                    # إيقاف خيط الصورة المصغرة إذا كان يعمل
                    if file_path in self.thumbnail_threads:
                        self.thumbnail_threads[file_path].terminate()
                        self.thumbnail_threads[file_path].wait()
                        del self.thumbnail_threads[file_path]
                    
                    self.media_list.takeItem(self.media_list.row(item))
                
                self.main_window.statusBar().showMessage(f"Removed {len(selected_items)} item(s)", 2000)
    
    def show_properties(self):
        """عرض خصائص العنصر المحدد"""
        selected_items = self.media_list.selectedItems()
        if selected_items:
            # عرض خصائص العنصر الأول المحدد
            item = selected_items[0]
            file_path = item.data(Qt.UserRole)
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # بالـ MB
            
            QMessageBox.information(
                self, "File Properties",
                f"File: {item.text()}\n\n"
                f"Path: {file_path}\n"
                f"Size: {file_size:.2f} MB\n"
                f"Type: {os.path.splitext(file_path)[1]}"
            )
        else:
            QMessageBox.information(self, "No Selection", "Please select a file to view its properties.")
    
    def show_context_menu(self, position):
        """عرض قائمة السياق عند النقر بالزر الأيمن"""
        menu = QMenu()
        
        # إضافة خيارات القائمة
        rename_action = QAction("Rename", self)
        rename_action.triggered.connect(self.rename_selected)
        menu.addAction(rename_action)
        
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(self.remove_selected)
        menu.addAction(delete_action)
        
        menu.addSeparator()
        
        send_to_timeline_action = QAction("Send to Timeline", self)
        send_to_timeline_action.triggered.connect(self.send_to_timeline)
        menu.addAction(send_to_timeline_action)
        
        menu.addSeparator()
        
        add_file_action = QAction("Add File", self)
        add_file_action.triggered.connect(self.add_files)
        menu.addAction(add_file_action)
        
        menu.addSeparator()
        
        select_all_action = QAction("Select All", self)
        select_all_action.triggered.connect(self.select_all)
        menu.addAction(select_all_action)
        
        # عرض القائمة في موقع المؤشر
        menu.exec_(self.media_list.mapToGlobal(position))
    
    def rename_selected(self):
        """إعادة تسمية العنصر المحدد"""
        selected_items = self.media_list.selectedItems()
        if selected_items:
            item = selected_items[0]
            current_name = item.text()
            
            # إنشاء مربع حوار لإدخال الاسم الجديد
            new_name, ok = QInputDialog.getText(
                self, "Rename File",
                f"Enter new name for {current_name}:",
                text=current_name
            )
            
            if ok and new_name:
                item.setText(new_name)
                self.main_window.statusBar().showMessage(f"Renamed to {new_name}", 2000)
    
    def send_to_timeline(self):
        """إرسال الملف المحدد إلى التايم لاين"""
        selected_items = self.media_list.selectedItems()
        if selected_items:
            # سيتم تنفيذ هذا لاحقاً
            self.main_window.statusBar().showMessage(f"Sent {len(selected_items)} item(s) to timeline", 2000)
    
    def select_all(self):
        """تحديد كل العناصر في القائمة"""
        self.media_list.selectAll()
        self.main_window.statusBar().showMessage("All items selected", 2000)
    
    def keyPressEvent(self, event):
        """معالجة ضغطات المفاتيح"""
        # Ctrl+A لتحديد الكل
        if event.key() == Qt.Key_A and event.modifiers() & Qt.ControlModifier:
            self.select_all()
        # Delete key لحذف العناصر المحددة
        elif event.key() == Qt.Key_Delete:
            self.remove_selected()
        
        super().keyPressEvent(event)