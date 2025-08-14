from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QMessageBox, QGraphicsView, QGraphicsScene, 
                             QGraphicsItem, QGraphicsRectItem, QMenu, QAction, 
                             QLabel, QFileDialog, QApplication)
from PyQt5.QtCore import Qt, QRectF, QPointF, QSize, pyqtSignal, QLineF
from PyQt5.QtGui import QPixmap, QPainter, QColor, QPen, QBrush, QDragEnterEvent, QDropEvent, QImage
import os
import cv2
import librosa
import numpy as np

class TimelineItem(QGraphicsItem):
    def __init__(self, file_path, video_thumbnail=None, audio_waveform=None, duration_seconds=0, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.video_thumbnail = video_thumbnail
        self.audio_waveform = audio_waveform
        self.duration = duration_seconds
        self.video_height = 60
        self.audio_height = 40
        self.total_height = self.video_height + self.audio_height
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemSendsGeometryChanges | QGraphicsItem.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        
    def boundingRect(self) -> QRectF:
        width = self.duration * 100  # يمكن تعديل نسبة البكسل لكل ثانية حسب zoom بالـ TimelinePanel
        return QRectF(0, 0, width, self.total_height)
    
    def paint(self, painter: QPainter, option, widget=None):
        rect = self.boundingRect()
        # خلفية العنصر
        painter.setBrush(QBrush(QColor(40, 40, 40)))
        painter.setPen(Qt.NoPen)
        painter.drawRect(rect)
        
        # رسم الفيديو (صورة مصغرة)
        if self.video_thumbnail:
            scaled_video = self.video_thumbnail.scaled(int(rect.width()), self.video_height, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            painter.drawPixmap(0, 0, scaled_video)
        
        # رسم شريط الصوت
        audio_rect = QRectF(0, self.video_height, rect.width(), self.audio_height)
        painter.setBrush(QBrush(QColor(25, 25, 25)))
        painter.drawRect(audio_rect)
        
        if self.audio_waveform:
            pen_wave = QPen(QColor(0, 180, 255))
            pen_wave.setWidth(1)
            painter.setPen(pen_wave)
            total_points = len(self.audio_waveform)
            if total_points > 1:
                step_x = audio_rect.width() / (total_points - 1)
                for i in range(total_points - 1):
                    x1 = i * step_x
                    x2 = (i + 1) * step_x
                    y1 = audio_rect.bottom() - (self.audio_waveform[i] * audio_rect.height())
                    y2 = audio_rect.bottom() - (self.audio_waveform[i + 1] * audio_rect.height())
                    painter.drawLine(QLineF(x1, y1, x2, y2))
            
            # تمييز مناطق الصمت (أقل من 0.05) برسم مستطيل شفاف أبيض
            silence_threshold = 0.05
            brush_silence = QBrush(QColor(255, 255, 255, 80))
            painter.setBrush(brush_silence)
            painter.setPen(Qt.NoPen)
            in_silence = False
            silence_start_x = 0
            for i, amplitude in enumerate(self.audio_waveform):
                x = i * step_x
                if amplitude < silence_threshold:
                    if not in_silence:
                        in_silence = True
                        silence_start_x = x
                else:
                    if in_silence:
                        in_silence = False
                        silence_width = x - silence_start_x
                        painter.drawRect(silence_start_x, audio_rect.top(), silence_width, audio_rect.height())
            if in_silence:
                painter.drawRect(silence_start_x, audio_rect.top(), audio_rect.right() - silence_start_x, audio_rect.height())
    
    def itemChange(self, change, value):
        # تقييد الحركة أفقياً فقط حسب الحاجة (y يبقى ثابت)
        if change == QGraphicsItem.ItemPositionChange:
            new_pos = value
            if new_pos.x() < 0:
                new_pos.setX(0)
            return new_pos
        return super().itemChange(change, value)
    
    def cleanup(self):
        """تنظيف الموارد"""
        pass

class TimelineHeader(QWidget):
    def __init__(self, theme_manager=None):
        super().__init__()
        self.theme_manager = theme_manager
        self.width_pixels = 1000
        self.zoom_factor = 1.0
        self.setMinimumHeight(30)
        
        # تطبيق الثيم الأولي
        if theme_manager:
            theme_manager.apply_theme(self)
    
    def set_width(self, width_pixels, zoom_factor):
        self.width_pixels = width_pixels
        self.zoom_factor = zoom_factor
        self.setFixedWidth(int(width_pixels))  # التحويل إلى int لتفادي الخطأ
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(50, 50, 50))
        painter.setPen(QColor(200, 200, 200))
        pixels_per_second = 100 * self.zoom_factor
        total_seconds = int(self.width_pixels / pixels_per_second) + 1
        for sec in range(total_seconds):
            x = sec * pixels_per_second
            painter.drawLine(QLineF(x, 20, x, 30))
            painter.drawText(int(x) + 2, 15, f"{sec}s")
        painter.end()

class TimelinePanel(QWidget):  # تغيير من QGraphicsView إلى QWidget
    itemSelected = pyqtSignal(object)
    
    def __init__(self, theme_manager=None):
        super().__init__()
        self.theme_manager = theme_manager
        
        # إعدادات التكبير/التصغير
        self.zoom_factor = 1.0
        
        self.tracks = []
        self.track_height = 100
        self.track_spacing = 10
        
        # شريط زمني علوي - تهيئته أولاً
        self.timeline_header = TimelineHeader(theme_manager)
        
        # إنشاء QGraphicsView و QGraphicsScene
        self.view = QGraphicsView()
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
        
        self.view.setMinimumHeight(180)
        self.view.setMaximumHeight(300)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        
        self.scene.setBackgroundBrush(QColor(30, 30, 30))
        self.view.setRenderHint(QPainter.Antialiasing)
        
        self.view.setAcceptDrops(True)
        self.view.setDragMode(QGraphicsView.RubberBandDrag)
        
        # الآن يمكننا استدعاء add_track بأمان
        self.add_track()
        
        self.setup_ui()
        
        # تطبيق الثيم الأولي
        if theme_manager:
            theme_manager.apply_theme(self)
    
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(2)
        
        # إضافة شريط الوقت العلوي
        main_layout.addWidget(self.timeline_header)
        
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(2)
        
        add_track_btn = QPushButton("Add Track")
        add_track_btn.clicked.connect(self.add_track)
        toolbar_layout.addWidget(add_track_btn)
        
        remove_track_btn = QPushButton("Remove Track")
        remove_track_btn.clicked.connect(self.remove_track)
        toolbar_layout.addWidget(remove_track_btn)
        
        add_media_btn = QPushButton("Add Media")
        add_media_btn.clicked.connect(self.add_media_file_dialog)
        toolbar_layout.addWidget(add_media_btn)
        
        toolbar_layout.addStretch()
        
        zoom_in_btn = QPushButton("Zoom In")
        zoom_in_btn.clicked.connect(self.zoom_in)
        toolbar_layout.addWidget(zoom_in_btn)
        
        zoom_out_btn = QPushButton("Zoom Out")
        zoom_out_btn.clicked.connect(self.zoom_out)
        toolbar_layout.addWidget(zoom_out_btn)
        
        main_layout.addLayout(toolbar_layout)
        
        # إضافة QGraphicsView
        main_layout.addWidget(self.view, 1)
        
        self.setLayout(main_layout)
    
    def add_track(self):
        track_id = len(self.tracks)
        self.tracks.append({
            'id': track_id,
            'items': []
        })
        
        y_pos = track_id * (self.track_height + self.track_spacing)
        self.scene.addLine(0, y_pos, 2000, y_pos, QPen(QColor(100, 100, 100)))
        
        self.update_scene_size()
        
        # التحقق من وجود شريط الحالة قبل استخدامه
        if hasattr(self.parent(), 'status_bar'):
            self.parent().status_bar().showMessage(f"Track {track_id+1} added", 2000)
    
    def remove_track(self):
        if not self.tracks:
            return
            
        reply = QMessageBox.question(
            self, 'Remove Track',
            f'Are you sure you want to remove track {len(self.tracks)}?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            removed_track = self.tracks.pop()
            
            for item in removed_track['items']:
                self.scene.removeItem(item)
            
            self.update_scene_size()
            
            # التحقق من وجود شريط الحالة قبل استخدامه
            if hasattr(self.parent(), 'status_bar'):
                self.parent().statusBar().showMessage("Track removed", 2000)
    
    def update_scene_size(self):
        max_width = 0
        max_tracks = len(self.tracks)
        for track in self.tracks:
            for item in track['items']:
                item_width = item.duration * 100 * self.zoom_factor
                if item_width > max_width:
                    max_width = item_width
        
        height = max_tracks * (self.track_height + self.track_spacing)
        self.scene.setSceneRect(0, 0, int(max_width) + 200, height + 50)
        self.timeline_header.set_width(int(max_width) + 200, self.zoom_factor)
    
    def zoom_in(self):
        if self.zoom_factor < 5.0:
            self.zoom_factor += 0.25
            self.apply_zoom()
            # التحقق من وجود شريط الحالة قبل استخدامه
            if hasattr(self.parent(), 'status_bar'):
                self.parent().status_bar().showMessage("Zoomed in", 2000)
    
    def zoom_out(self):
        if self.zoom_factor > 0.25:
            self.zoom_factor -= 0.25
            self.apply_zoom()
            # التحقق من وجود شريط الحالة قبل استخدامه
            if hasattr(self.parent(), 'status_bar'):
                self.parent().statusBar().showMessage("Zoomed out", 2000)
    
    def apply_zoom(self):
        for track in self.tracks:
            for item in track['items']:
                # prepareGeometryChange لتنبيه Qt بتغيير الحجم
                item.prepareGeometryChange()
                # boundingRect تعتمد على self.duration فقط لذلك لا نحتاج تعديل عرض يدوي
                pass
        self.update_scene_size()
        self.timeline_header.set_width(self.scene.width(), self.zoom_factor)
    
    def add_media_file_dialog(self):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "اختر ملفات فيديو أو صوت أو صورة",
            "",
            "Media Files (*.mp4 *.avi *.mov *.wav *.mp3 *.png *.jpg *.jpeg);;All Files (*)",
            options=options,
        )
        for file_path in files:
            self.add_media_item(file_path)
    
    def add_media_item(self, file_path, track_id=None):
        # تحضير الصورة المصغرة للفيديو
        thumbnail = get_video_thumbnail(file_path)
        
        # الحصول على مدة الفيديو
        duration = get_video_duration_seconds(file_path)
        if duration == 0:
            duration = 5  # مدة افتراضية
        
        # تحضير موجة الصوت
        waveform = get_audio_waveform(file_path, max_duration=duration)
        
        # إنشاء عنصر التايم لاين
        timeline_item = TimelineItem(
            file_path=file_path,
            video_thumbnail=thumbnail,
            audio_waveform=waveform,
            duration_seconds=duration
        )
        
        # تحديد المسار المناسب
        if track_id is None or track_id >= len(self.tracks):
            # ضع العنصر في أول مسار فيه مكان (عدم التداخل)
            track_index = 0
            while True:
                can_place = True
                if track_index >= len(self.tracks):
                    self.add_track()
                
                # حساب الموضع الأفقي المناسب
                position = 0
                for existing_item in self.tracks[track_index]['items']:
                    # التحقق من عدم التداخل
                    item_rect = QRectF(position, 0, timeline_item.duration * 100, timeline_item.total_height)
                    existing_rect = QRectF(existing_item.pos().x(), 0, existing_item.duration * 100, existing_item.total_height)
                    
                    if item_rect.intersects(existing_rect):
                        can_place = False
                        # تحديث الموضع المحتمل
                        position = existing_item.pos().x() + existing_item.duration * 100
                
                if can_place:
                    break
                track_index += 1
            
            track_id = track_index
        
        # إضافة العنصر إلى المسار المحدد
        y_pos = track_id * (self.track_height + self.track_spacing) + 5
        
        # حساب الموضع الأفقي
        position = 0
        for item in self.tracks[track_id]['items']:
            position += item.duration * 100
        
        timeline_item.setPos(position, y_pos)
        
        self.scene.addItem(timeline_item)
        self.tracks[track_id]['items'].append(timeline_item)
        
        self.scene.update()
        self.view.update()
        
        self.update_scene_size()
        
        # التحقق من وجود شريط الحالة قبل استخدامه
        if hasattr(self.parent(), 'status_bar'):
            self.parent().statusBar().showMessage(f"Added {os.path.basename(file_path)} to timeline", 2000)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        # توجيه الحدث إلى QGraphicsView
        self.view.dragEnterEvent(event)
    
    def dropEvent(self, event: QDropEvent):
        # توجيه الحدث إلى QGraphicsView
        self.view.dropEvent(event)
    
    def mousePressEvent(self, event):
        # توجيه الحدث إلى QGraphicsView
        self.view.mousePressEvent(event)
        
        if self.scene.selectedItems():
            self.itemSelected.emit(self.scene.selectedItems()[0])
    
    def select_all(self):
        for track in self.tracks:
            for item in track['items']:
                item.setSelected(True)
        
        # التحقق من وجود شريط الحالة قبل استخدامه
        if hasattr(self.parent(), 'status_bar'):
            self.parent().statusBar().showMessage("All timeline items selected", 2000)
    
    def clear_selection(self):
        for track in self.tracks:
            for item in track['items']:
                item.setSelected(False)
        
        # التحقق من وجود شريط الحالة قبل استخدامه
        if hasattr(self.parent(), 'status_bar'):
            self.parent().statusBar().showMessage("Timeline selection cleared", 2000)
    
    def cleanup(self):
        """تنظيف الموارد"""
        for track in self.tracks:
            for item in track['items']:
                item.cleanup()

# دوال مساعدة لتحضير الصورة المصغرة وموجات الصوت
def get_video_thumbnail(video_path, width=320, height=180):
    cap = cv2.VideoCapture(video_path)
    success, frame = cap.read()
    cap.release()
    if not success:
        return QPixmap(width, height)  # صورة فارغة في حالة الفشل
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = cv2.resize(frame, (width, height))
    h, w, ch = frame.shape
    bytes_per_line = ch * w
    qImg = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
    return QPixmap.fromImage(qImg)

def get_audio_waveform(video_path, sr=22050, max_duration=5):
    try:
        y, _ = librosa.load(video_path, sr=sr, duration=max_duration)
    except Exception as e:
        print(f"خطأ في تحميل الصوت: {e}")
        return []
    y_abs = np.abs(y)
    frames = 100  # عدد نقاط في waveform يمكن تعديلها حسب عرض التايم لاين
    hop_length = max(1, int(len(y_abs) / frames)) 
    waveform = [np.mean(y_abs[i * hop_length:(i + 1) * hop_length]) for i in range(frames)]
    max_val = max(waveform) if max(waveform) > 0 else 1
    waveform_normalized = [val / max_val for val in waveform]
    return waveform_normalized

def get_video_duration_seconds(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return 0
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    cap.release()
    if fps > 0:
        return frame_count / fps
    return 0

# لتجربة الملف مباشرة
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TimelinePanel()
    window.setWindowTitle("Timeline Panel مع عرض الفيديو والصوت")
    window.resize(1200, 400)
    window.show()
    sys.exit(app.exec_())