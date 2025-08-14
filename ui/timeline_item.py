from PyQt5.QtWidgets import QGraphicsRectItem
from PyQt5.QtCore import Qt, QRectF, QPointF
from PyQt5.QtGui import QPixmap, QPainter, QColor, QPen
import av
import numpy as np
from PIL import Image
import os
import tempfile

class TimelineItem(QGraphicsRectItem):
    def __init__(self, file_path, track_id=0, position=0, duration=10):
        super().__init__(0, 0, duration * 50, 100)
        self.file_path = file_path
        self.track_id = track_id
        self.position = position
        self.duration = duration
        self.thumbnails = []
        self.waveform = []
        self.volume = 1.0
        self.effects = []
        
        # إعدادات العنصر
        self.setFlag(QGraphicsRectItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsRectItem.ItemIsMovable, True)
        self.setFlag(QGraphicsRectItem.ItemSendsGeometryChanges, True)
        
        # تحضير العنصر
        self.prepare_item()
    
    def prepare_item(self):
        """تحضير الصور المصغرة وموجات الصوت"""
        self.temp_dir = tempfile.mkdtemp()
        self.extract_thumbnails()
        self.analyze_audio()
        self.update()
    
    def extract_thumbnails(self):
        """استخراج 5 صور مصغرة من الفيديو"""
        try:
            with av.open(self.file_path) as container:
                video_stream = None
                for s in container.streams:
                    if s.type == 'video':
                        video_stream = s
                        break
                
                if not video_stream:
                    default_thumb = QPixmap(80, 60)
                    default_thumb.fill(QColor(70, 130, 180))
                    self.thumbnails = [default_thumb] * 5
                    return
                
                duration = container.duration / av.time_base
                thumb_times = np.linspace(0, duration, 5)
                
                for i, time in enumerate(thumb_times):
                    container.seek(int(time * av.time_base))
                    for frame in container.decode(video_stream):
                        img = frame.to_ndarray(format='rgb24')
                        pil_img = Image.fromarray(img)
                        pil_img = pil_img.resize((80, 60), Image.LANCZOS)
                        thumb_path = os.path.join(self.temp_dir, f"thumb_{i}.png")
                        pil_img.save(thumb_path)
                        self.thumbnails.append(QPixmap(thumb_path))
                        break
        except Exception:
            default_thumb = QPixmap(80, 60)
            default_thumb.fill(QColor(180, 70, 70))
            self.thumbnails = [default_thumb] * 5
    
    def analyze_audio(self):
        """تحليل الصوت لإنشاء موجات صوتية"""
        try:
            with av.open(self.file_path) as container:
                audio_stream = next((s for s in container.streams if s.type == 'audio'), None)
                if not audio_stream:
                    return
                
                audio_data = []
                for frame in container.decode(audio_stream):
                    audio_data.extend(frame.to_ndarray().flatten())
                
                chunk_size = max(len(audio_data) // 100, 1)
                waveform = []
                for i in range(0, len(audio_data), chunk_size):
                    chunk = audio_data[i:i+chunk_size]
                    level = np.abs(chunk).mean() if chunk else 0
                    waveform.append(level * self.volume)
                
                self.waveform = waveform
        except Exception:
            pass
    
    def paint(self, painter, option, widget):
        """رسم العنصر في التايم لاين"""
        painter.fillRect(self.rect(), QColor(50, 50, 50))
        
        if self.thumbnails:
            thumb_width = self.rect().width() / len(self.thumbnails)
            for i, thumb in enumerate(self.thumbnails):
                painter.drawPixmap(
                    int(self.rect().x() + i * thumb_width),
                    int(self.rect().y()),
                    int(thumb_width),
                    60,
                    thumb
                )
        
        if self.waveform:
            painter.setPen(QPen(QColor(100, 200, 255), 1))
            wave_height = self.rect().height() - 70
            wave_y = self.rect().y() + 65
            
            for i, level in enumerate(self.waveform):
                x = self.rect().x() + i * (self.rect().width() / len(self.waveform))
                height = level * wave_height
                painter.drawLine(
                    QPointF(x, wave_y),
                    QPointF(x, wave_y - height)
                )
        
        if self.isSelected():
            painter.setPen(QPen(QColor(255, 200, 0), 2))
            painter.drawRect(self.rect())
    
    def itemChange(self, change, value):
        """معالجة تغييرات العنصر"""
        if change == QGraphicsRectItem.ItemPositionHasChanged:
            self.position = value.x() / 50
        return super().itemChange(change, value)
    
    def cleanup(self):
        """تنظيف الموارد"""
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)