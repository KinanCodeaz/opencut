from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSlider, QLabel, QFileDialog
from PyQt5.QtCore import Qt
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl

class PlayerPanel(QWidget):
    def __init__(self):
        super().__init__()
        
        # إعدادات اللوحة - زيادة الارتفاع
        self.setMinimumHeight(400)
        
        # إنشاء مشغل الوسائط
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        
        # إنشاء التخطيط
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)  # تقليل الهوامش
        layout.setSpacing(2)  # تقليل المسافات بين المكونات
        
        # منطقة عرض الفيديو - زيادة المساحة
        self.video_widget = QVideoWidget()
        self.video_widget.setStyleSheet("background-color: #2d2d2d;")
        layout.addWidget(self.video_widget, 1)  # إضافة عامل تمدد لزيادة المساحة
        
        # ربط مشغل الوسائط بعرض الفيديو
        self.media_player.setVideoOutput(self.video_widget)
        
        # أزرار التحكم في المشغل
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(2)  # تقليل المسافات بين الأزرار
        
        self.play_btn = QPushButton("Play")
        self.play_btn.clicked.connect(self.toggle_play)
        controls_layout.addWidget(self.play_btn)
        
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self.stop)
        controls_layout.addWidget(self.stop_btn)
        
        self.open_btn = QPushButton("Open")
        self.open_btn.clicked.connect(self.open_media)
        controls_layout.addWidget(self.open_btn)
        
        controls_layout.addStretch()
        
        # شريط التقدم
        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.setRange(0, 100)
        self.progress_slider.sliderMoved.connect(self.set_position)
        controls_layout.addWidget(self.progress_slider)
        
        # زر ملء الشاشة
        self.fullscreen_btn = QPushButton("Fullscreen")
        self.fullscreen_btn.clicked.connect(self.toggle_fullscreen)
        controls_layout.addWidget(self.fullscreen_btn)
        
        layout.addLayout(controls_layout)
        
        # شريط معلومات الوقت
        time_layout = QHBoxLayout()
        time_layout.setSpacing(2)  # تقليل المسافات بين العناصر
        
        self.current_time_label = QLabel("00:00:00")
        time_layout.addWidget(self.current_time_label)
        
        time_layout.addStretch()
        
        self.total_time_label = QLabel("00:00:00")
        time_layout.addWidget(self.total_time_label)
        
        layout.addLayout(time_layout)
        
        # ربط إشارات مشغل الوسائط
        self.media_player.stateChanged.connect(self.media_state_changed)
        self.media_player.positionChanged.connect(self.position_changed)
        self.media_player.durationChanged.connect(self.duration_changed)
    
    def open_media(self):
        """فتح ملف وسائط"""
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("Media Files (*.mp4 *.avi *.mov *.mkv *.mp3 *.wav)")
        
        if file_dialog.exec_():
            file_path = file_dialog.selectedFiles()[0]
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(file_path)))
            self.play_btn.setEnabled(True)
            self.parent().statusBar().showMessage(f"Opened: {file_path.split('/')[-1].split('\\')[-1]}", 2000)
    
    def toggle_play(self):
        """تبديل حالة التشغيل"""
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()
    
    def stop(self):
        """إيقاف التشغيل"""
        self.media_player.stop()
    
    def toggle_fullscreen(self):
        """تبديل وضع ملء الشاشة"""
        if self.isFullScreen():
            self.showNormal()
            self.fullscreen_btn.setText("Fullscreen")
        else:
            self.showFullScreen()
            self.fullscreen_btn.setText("Exit Fullscreen")
    
    def media_state_changed(self, state):
        """تحديث حالة زر التشغيل"""
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.play_btn.setText("Pause")
        else:
            self.play_btn.setText("Play")
    
    def position_changed(self, position):
        """تحديث شريط التقدم"""
        self.progress_slider.setValue(position)
        
        # تحديث وقت التشغيل الحالي
        seconds = position // 1000
        minutes = seconds // 60
        hours = minutes // 60
        seconds = seconds % 60
        minutes = minutes % 60
        self.current_time_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
    
    def duration_changed(self, duration):
        """تحديث المدة الإجمالية"""
        self.progress_slider.setRange(0, duration)
        
        # تحديث الوقت الإجمالي
        seconds = duration // 1000
        minutes = seconds // 60
        hours = minutes // 60
        seconds = seconds % 60
        minutes = minutes % 60
        self.total_time_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
    
    def set_position(self, position):
        """تعيين موضع التشغيل"""
        self.media_player.setPosition(position)
    
    def select_all(self):
        """تحديد كل العناصر في لوحة المشغل"""
        # في لوحة المشغل، لا يوجد عناصر لتحديدها حالياً
        pass
    
    def clear_selection(self):
        """إلغاء تحديد كل العناصر في لوحة المشغل"""
        # في لوحة المشغل، لا يوجد عناصر لإلغاء تحديدها حالياً
        pass