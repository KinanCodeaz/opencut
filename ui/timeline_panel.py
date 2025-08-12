from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QScrollArea, QMessageBox
from PyQt5.QtCore import Qt

class TimelinePanel(QWidget):
    def __init__(self):
        super().__init__()
        
        # إعدادات اللوحة - زيادة الارتفاع
        self.setMinimumHeight(180)  # زيادة الحد الأدنى للارتفاع
        self.setMaximumHeight(300)  # زيادة الحد الأقصى للارتفاع
        
        # إنشاء التخطيط
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)  # تقليل الهوامش
        layout.setSpacing(2)  # تقليل المسافات بين المكونات
        
        # شريط الأدوات
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(2)  # تقليل المسافات بين الأزرار
        
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
        
        layout.addLayout(toolbar_layout)
        
        # منطقة التايم لاين (قابلة للتمرير)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        
        # محتوى التايم لاين (سيتم تطويره لاحقاً)
        self.timeline_content = QWidget()
        self.timeline_content.setMinimumSize(1000, 300)
        self.timeline_content.setStyleSheet("background-color: #3d3d3d;")
        
        scroll_area.setWidget(self.timeline_content)
        layout.addWidget(scroll_area, 1)  # إضافة عامل تمدد لزيادة المساحة
    
    # ... باقي الكود كما هو ...
    
    def add_track(self):
        """إضافة مسار جديد للتايم لاين"""
        QMessageBox.information(self, "Add Track", "Track will be added to the timeline.")
        self.parent().statusBar().showMessage("New track added", 2000)
    
    def remove_track(self):
        """إزالة مسار من التايم لاين"""
        reply = QMessageBox.question(
            self, 'Remove Track',
            'Are you sure you want to remove the selected track?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.parent().statusBar().showMessage("Track removed", 2000)
    
    def zoom_in(self):
        """تكبير عرض التايم لاين"""
        current_size = self.timeline_content.width()
        new_size = int(current_size * 1.2)
        self.timeline_content.setMinimumSize(new_size, self.timeline_content.height())
        self.parent().statusBar().showMessage("Zoomed in", 2000)
    
    def zoom_out(self):
        """تصغير عرض التايم لاين"""
        current_size = self.timeline_content.width()
        new_size = int(current_size / 1.2)
        if new_size < 500:
            new_size = 500
        self.timeline_content.setMinimumSize(new_size, self.timeline_content.height())
        self.parent().statusBar().showMessage("Zoomed out", 2000)
    
    def select_all(self):
        """تحديد كل العناصر في التايم لاين"""
        QMessageBox.information(self, "Select All", "All timeline items will be selected.")
        self.parent().statusBar().showMessage("All timeline items selected", 2000)
    
    def clear_selection(self):
        """إلغاء تحديد كل العناصر في التايم لاين"""
        QMessageBox.information(self, "Clear Selection", "Timeline selection will be cleared.")
        self.parent().statusBar().showMessage("Timeline selection cleared", 2000)