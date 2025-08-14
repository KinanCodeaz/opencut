from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QMessageBox, QGraphicsView, QGraphicsScene, 
                             QGraphicsItem, QGraphicsRectItem, QMenu, QAction, QLabel)
from PyQt5.QtCore import Qt, QRectF, QPointF, QSize, pyqtSignal
from PyQt5.QtGui import QPixmap, QPainter, QColor, QPen, QBrush, QDragEnterEvent, QDropEvent
import os
from ui.timeline_item import TimelineItem
from utils.thread_manager import thread_manager

class TimelinePanel(QGraphicsView):
    itemSelected = pyqtSignal(object)
    
    def __init__(self, theme_manager=None):
        super().__init__()
        self.theme_manager = theme_manager
        
        self.setMinimumHeight(180)
        self.setMaximumHeight(300)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        
        self.scene.setBackgroundBrush(QColor(30, 30, 30))
        self.setRenderHint(QPainter.Antialiasing)
        
        self.setAcceptDrops(True)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        
        self.tracks = []
        self.track_height = 100
        self.add_track()
        
        self.setup_ui()
        
        # تطبيق الثيم الأولي
        if theme_manager:
            theme_manager.apply_theme(self)
    
    def setup_ui(self):
        self.parent_widget = QWidget()
        container_layout = QVBoxLayout(self.parent_widget)
        container_layout.setContentsMargins(2, 2, 2, 2)
        container_layout.setSpacing(2)
        
        title_label = QLabel("OpenCut Timeline")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; color: white; margin: 5px;")
        container_layout.addWidget(title_label)
        
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(2)
        
        add_track_btn = QPushButton("Add Track")
        add_track_btn.clicked.connect(self.add_track)
        toolbar_layout.addWidget(add_track_btn)
        
        remove_track_btn = QPushButton("Remove Track")
        remove_track_btn.clicked.connect(self.remove_track)
        toolbar_layout.addWidget(remove_track_btn)
        
        toolbar_layout.addStretch()
        
        zoom_in_btn = QPushButton("Zoom In")
        zoom_in_btn.clicked.connect(self.zoom_in)
        toolbar_layout.addWidget(zoom_in_btn)
        
        zoom_out_btn = QPushButton("Zoom Out")
        zoom_out_btn.clicked.connect(self.zoom_out)
        toolbar_layout.addWidget(zoom_out_btn)
        
        container_layout.addLayout(toolbar_layout)
        
        # التعديل البسيط: إضافة العرض الرسومي مع عامل تمدد
        container_layout.addWidget(self, 1)  # هذا هو التغيير الرئيسي
        
        self.parent_widget.setLayout(container_layout)
    
    def add_track(self):
        track_id = len(self.tracks)
        self.tracks.append({
            'id': track_id,
            'items': []
        })
        
        y_pos = track_id * (self.track_height + 10)
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
        height = len(self.tracks) * (self.track_height + 10) + 20
        self.scene.setSceneRect(0, 0, 2000, height)
    
    def zoom_in(self):
        self.scale(1.2, 1.0)
        # التحقق من وجود شريط الحالة قبل استخدامه
        if hasattr(self.parent(), 'status_bar'):
            self.parent().status_bar().showMessage("Zoomed in", 2000)
    
    def zoom_out(self):
        self.scale(1/1.2, 1.0)
        # التحقق من وجود شريط الحالة قبل استخدامه
        if hasattr(self.parent(), 'status_bar'):
            self.parent().statusBar().showMessage("Zoomed out", 2000)
    
    def add_media_item(self, file_path, track_id=0):
        if track_id >= len(self.tracks):
            track_id = 0
        
        position = 0
        for item in self.tracks[track_id]['items']:
            position += item.duration
        
        timeline_item = TimelineItem(
            file_path=file_path,
            track_id=track_id,
            position=position
        )
        
        y_pos = track_id * (self.track_height + 10) + 5
        timeline_item.setPos(position * 50, y_pos)
        
        self.scene.addItem(timeline_item)
        self.tracks[track_id]['items'].append(timeline_item)
        
        self.scene.update()
        self.update()
        
        self.update_scene_size()
        
        # التحقق من وجود شريط الحالة قبل استخدامه
        if hasattr(self.parent(), 'status_bar'):
            self.parent().statusBar().showMessage(f"Added {os.path.basename(file_path)} to timeline", 2000)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if os.path.isfile(file_path):
                self.add_media_item(file_path)
    
    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        
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