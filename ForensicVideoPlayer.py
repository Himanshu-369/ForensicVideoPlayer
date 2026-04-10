import sys
import os
from collections import deque

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QSlider, QLabel, QFileDialog, QFrame, QComboBox,
    QSizePolicy, QDialog, QMenu, QSpinBox, QProgressBar, QScrollArea,
    QCheckBox, QGroupBox, QGridLayout, QListWidget, QListWidgetItem,
    QToolTip, QMessageBox
)
from PyQt6.QtCore import Qt, QUrl, QProcess, QRectF, QPointF, QRect, pyqtSignal, QThread
from PyQt6.QtGui import QImage, QPixmap, QPainter, QColor, QPen, QFont, QWheelEvent, QKeyEvent, QAction

from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput, QVideoSink, QVideoFrame

# ─────────────────────────────────────────────────────────────────────────────
# Optional Dependencies
# ─────────────────────────────────────────────────────────────────────────────
try:
    import cv2
    import numpy as np
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False

try:
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

# ─────────────────────────────────────────────────────────────────────────────
# Theme Stylesheets
# ─────────────────────────────────────────────────────────────────────────────
DARK_QSS = """
QMainWindow, QWidget { background-color: #232326; color: #e0e0e0; font-family: 'Inter', 'Segoe UI', system-ui, sans-serif; }
#controlPanel { background-color: #2a2a2e; border: none; border-radius: 14px; }
QPushButton { background-color: #323237; color: #e0e0e0; border: none; border-radius: 8px; padding: 8px 14px; font-size: 13px; font-weight: 500; }
QPushButton:hover { background-color: #3d3d44; }
QPushButton:pressed, QPushButton[active="true"] { background-color: #5849e2; color: #ffffff; }
QPushButton:checked { background-color: #5849e2; color: #ffffff; }
QPushButton:disabled { background-color: #2a2a2e; color: #66666a; }
QPushButton#forensicsBtn { background-color: #1a3a1a; color: #4caf50; }
QPushButton#forensicsBtn:hover { background-color: #2a4a2a; }
QComboBox { background-color: #323237; color: #e0e0e0; border: none; border-radius: 8px; padding: 6px 10px; min-height: 20px; }
QComboBox::drop-down { border: none; width: 20px; }
QComboBox QAbstractItemView { background-color: #323237; color: #e0e0e0; selection-background-color: #5849e2; }
QSlider::groove:horizontal { background: #3d3d44; height: 6px; border-radius: 3px; }
QSlider::handle:horizontal { background: #5849e2; width: 14px; height: 14px; border-radius: 7px; margin: -4px 0; }
QSlider::sub-page:horizontal { background: #5849e2; border-radius: 3px; }
QLabel { color: #e0e0e0; font-size: 13px; }
QFrame#statusBar { background: transparent; border-top: 1px solid #3d3d44; padding: 6px; }
QDialog { background-color: #232326; color: #e0e0e0; }
QGroupBox { border: 1px solid #3d3d44; border-radius: 8px; margin-top: 10px; padding-top: 14px; font-weight: bold; }
QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; }
QListWidget { background-color: #2a2a2e; border: 1px solid #3d3d44; border-radius: 6px; padding: 4px; }
QListWidget::item { padding: 6px 8px; border-radius: 4px; }
QListWidget::item:hover { background-color: #3d3d44; }
QListWidget::item:selected { background-color: #5849e2; }
QProgressBar { background-color: #3d3d44; border: none; border-radius: 4px; text-align: center; color: #e0e0e0; min-height: 20px; }
QProgressBar::chunk { background-color: #5849e2; border-radius: 4px; }
QSpinBox { background-color: #323237; color: #e0e0e0; border: 1px solid #3d3d44; border-radius: 6px; padding: 4px 8px; }
QScrollArea { border: none; }
QCheckBox { spacing: 8px; }
QCheckBox::indicator { width: 18px; height: 18px; border-radius: 4px; border: 2px solid #3d3d44; background-color: #2a2a2e; }
QCheckBox::indicator:checked { background-color: #5849e2; border-color: #5849e2; }
"""

LIGHT_QSS = """
QMainWindow, QWidget { background-color: #f8f8f9; color: #212121; font-family: 'Inter', 'Segoe UI', system-ui, sans-serif; }
#controlPanel { background-color: #ffffff; border: none; border-radius: 14px; }
QPushButton { background-color: #ececed; color: #212121; border: none; border-radius: 8px; padding: 8px 14px; font-size: 13px; font-weight: 500; }
QPushButton:hover { background-color: #e1e1e3; }
QPushButton:pressed, QPushButton[active="true"] { background-color: #5849e2; color: #ffffff; }
QPushButton:checked { background-color: #5849e2; color: #ffffff; }
QPushButton:disabled { background-color: #eaeaed; color: #88888c; }
QPushButton#forensicsBtn { background-color: #e8f5e9; color: #2e7d32; }
QPushButton#forensicsBtn:hover { background-color: #c8e6c9; }
QComboBox { background-color: #ececed; color: #212121; border: none; border-radius: 8px; padding: 6px 10px; min-height: 20px; }
QComboBox::drop-down { border: none; width: 20px; }
QComboBox QAbstractItemView { background-color: #ececed; color: #212121; selection-background-color: #5849e2; }
QSlider::groove:horizontal { background: #dcdce0; height: 6px; border-radius: 3px; }
QSlider::handle:horizontal { background: #5849e2; width: 14px; height: 14px; border-radius: 7px; margin: -4px 0; }
QSlider::sub-page:horizontal { background: #5849e2; border-radius: 3px; }
QLabel { color: #212121; font-size: 13px; }
QFrame#statusBar { background: transparent; border-top: 1px solid #dcdce0; padding: 6px; }
QDialog { background-color: #f8f8f9; color: #212121; }
QGroupBox { border: 1px solid #dcdce0; border-radius: 8px; margin-top: 10px; padding-top: 14px; font-weight: bold; }
QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; }
QListWidget { background-color: #ffffff; border: 1px solid #dcdce0; border-radius: 6px; padding: 4px; }
QListWidget::item { padding: 6px 8px; border-radius: 4px; }
QListWidget::item:hover { background-color: #e1e1e3; }
QListWidget::item:selected { background-color: #5849e2; color: #fff; }
QProgressBar { background-color: #dcdce0; border: none; border-radius: 4px; text-align: center; color: #212121; min-height: 20px; }
QProgressBar::chunk { background-color: #5849e2; border-radius: 4px; }
QSpinBox { background-color: #ffffff; color: #212121; border: 1px solid #dcdce0; border-radius: 6px; padding: 4px 8px; }
QScrollArea { border: none; }
QCheckBox { spacing: 8px; }
QCheckBox::indicator { width: 18px; height: 18px; border-radius: 4px; border: 2px solid #dcdce0; background-color: #ffffff; }
QCheckBox::indicator:checked { background-color: #5849e2; border-color: #5849e2; }
"""

MENU_DARK_QSS = """
QMenu { background-color: #2a2a2e; border: 1px solid #3d3d44; border-radius: 8px; padding: 6px; }
QMenu::item { padding: 8px 20px; border-radius: 4px; color: #e0e0e0; }
QMenu::item:selected { background-color: #5849e2; }
QMenu::separator { height: 1px; background: #3d3d44; margin: 4px 8px; }
"""

MENU_LIGHT_QSS = """
QMenu { background-color: #ffffff; border: 1px solid #dcdce0; border-radius: 8px; padding: 6px; }
QMenu::item { padding: 8px 20px; border-radius: 4px; color: #212121; }
QMenu::item:selected { background-color: #5849e2; color: #ffffff; }
QMenu::separator { height: 1px; background: #dcdce0; margin: 4px 8px; }
"""


class PreciseSlider(QSlider):
    def wheelEvent(self, event: QWheelEvent):
        d = 500
        if event.angleDelta().y() > 0:
            self.setValue(min(self.maximum(), self.value() + d))
        else:
            self.setValue(max(self.minimum(), self.value() - d))
        self.sliderReleased.emit()


# ─────────────────────────────────────────────────────────────────────────────
# Frame Display with Overlay Support
# ─────────────────────────────────────────────────────────────────────────────
class FrameDisplayWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_image: QImage = None
        self.zoom_enabled = False
        self.zoom_rect = QRectF(0, 0, 0.5, 0.5)
        self.motion_rects = []
        self.roi_rect = None
        self._drawing_roi = False
        self._roi_start = None
        self._roi_current = None
        self.roi_draw_callback = None
        self.setMinimumSize(320, 180)

    def update_frame(self, image: QImage):
        self.current_image = image
        self.update()

    def set_zoom_rect(self, r: QRectF):
        self.zoom_rect = r
        self.update()

    def set_motion_overlay(self, rects):
        self.motion_rects = rects or []
        self.update()

    def set_roi(self, r):
        self.roi_rect = r
        self.update()

    def set_drawing_roi(self, enabled: bool, callback=None):
        self._drawing_roi = enabled
        self._roi_start = None
        self._roi_current = None
        self.roi_draw_callback = callback
        self.setCursor(Qt.CursorShape.CrossCursor if enabled else Qt.CursorShape.ArrowCursor)

    def _display_rect(self) -> QRect:
        if not self.current_image or self.current_image.isNull():
            return self.rect()
        img_w = max(1, self.current_image.width())
        img_h = max(1, self.current_image.height())
        widget_ar = self.width() / max(1, self.height())
        img_ar = img_w / img_h
        if widget_ar > img_ar:
            h = self.height()
            w = int(h * img_ar)
        else:
            w = self.width()
            h = int(w / img_ar)
        return QRect((self.width() - w) // 2, (self.height() - h) // 2, w, h)

    def _norm_to_widget(self, nr: QRectF) -> QRect:
        dr = self._display_rect()
        if dr.width() <= 0 or dr.height() <= 0:
            return QRect()
        x = int(dr.x() + nr.x() * dr.width())
        y = int(dr.y() + nr.y() * dr.height())
        w = int(nr.width() * dr.width())
        h = int(nr.height() * dr.height())
        return QRect(x, y, w, h)

    def _widget_to_norm(self, pos: QPointF) -> QPointF:
        dr = self._display_rect()
        if dr.width() <= 0 or dr.height() <= 0:
            return QPointF(0, 0)
        nx = (pos.x() - dr.x()) / dr.width()
        ny = (pos.y() - dr.y()) / dr.height()
        return QPointF(max(0.0, min(1.0, nx)), max(0.0, min(1.0, ny)))

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        p.fillRect(self.rect(), QColor(17, 17, 19))

        if not self.current_image or self.current_image.isNull():
            p.setPen(QColor(80, 80, 84))
            p.setFont(QFont("Inter", 12))
            p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "No Video Loaded")
            p.end()
            return

        dr = self._display_rect()
        img = self.current_image

        if self.zoom_enabled:
            sx = max(0, int(self.zoom_rect.x() * img.width()))
            sy = max(0, int(self.zoom_rect.y() * img.height()))
            sw = max(1, min(int(self.zoom_rect.width() * img.width()), img.width() - sx))
            sh = max(1, min(int(self.zoom_rect.height() * img.height()), img.height() - sy))
            cropped = QPixmap.fromImage(img).copy(sx, sy, sw, sh)
            p.drawPixmap(dr, cropped, QRect(0, 0, sw, sh))
            p.setPen(QPen(QColor(88, 73, 226, 80), 2))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawRect(dr.adjusted(1, 1, -1, -1))
        else:
            p.drawPixmap(dr, QPixmap.fromImage(img), img.rect())

        # ROI rectangle
        if self.roi_rect:
            wr = self._norm_to_widget(self.roi_rect)
            p.setPen(QPen(QColor(88, 73, 226), 2, Qt.PenStyle.DashLine))
            p.setBrush(QColor(88, 73, 226, 25))
            p.drawRect(wr)
            p.setPen(QColor(88, 73, 226))
            p.setFont(QFont("Inter", 9, QFont.Weight.Bold))
            p.drawText(wr.topLeft() + QPointF(4, 14), "ROI")

        # Drawing ROI in progress
        if self._drawing_roi and self._roi_start and self._roi_current:
            x1, y1 = self._roi_start.x(), self._roi_start.y()
            x2, y2 = self._roi_current.x(), self._roi_current.y()
            draw_rect = QRectF(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
            wr = self._norm_to_widget(draw_rect)
            p.setPen(QPen(QColor(255, 152, 0), 2, Qt.PenStyle.DashLine))
            p.setBrush(QColor(255, 152, 0, 30))
            p.drawRect(wr)

        # Motion detection rectangles
        for rect in self.motion_rects:
            wr = self._norm_to_widget(rect)
            p.setPen(QPen(QColor(0, 230, 118), 2))
            p.setBrush(QColor(0, 230, 118, 35))
            p.drawRect(wr)

        p.end()

    def mousePressEvent(self, event):
        if self._drawing_roi and event.button() == Qt.MouseButton.LeftButton:
            self._roi_start = self._widget_to_norm(event.position())
            self._roi_current = self._roi_start
            self.update()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drawing_roi and self._roi_start:
            self._roi_current = self._widget_to_norm(event.position())
            self.update()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._drawing_roi and self._roi_start and event.button() == Qt.MouseButton.LeftButton:
            self._roi_current = self._widget_to_norm(event.position())
            if self.roi_draw_callback:
                self.roi_draw_callback(self._roi_start, self._roi_current)
            self._roi_start = None
            self._roi_current = None
            self.update()
            return
        super().mouseReleaseEvent(event)


# ─────────────────────────────────────────────────────────────────────────────
# Mini Preview & Zoom Slider
# ─────────────────────────────────────────────────────────────────────────────
class MiniPreviewWidget(QWidget):
    selection_changed = pyqtSignal(QRectF)
    close_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_image: QImage = None
        self.selection_rect = QRectF(0, 0, 0.5, 0.5)
        self.dragging = False
        self.resizing = False
        self.resize_corner = -1
        self.drag_start = QPointF()
        self.drag_orig = QRectF()
        self.setFixedSize(240, 150)
        self.setCursor(Qt.CursorShape.CrossCursor)

    def update_frame(self, image: QImage):
        self.current_image = image
        self.update()

    def set_selection(self, r: QRectF):
        self.selection_rect = r
        self.update()

    def _vrect(self) -> QRect:
        if not self.current_image or self.current_image.isNull():
            return self.rect().adjusted(4, 4, -4, -4)
        img_w = max(1, self.current_image.width())
        img_h = max(1, self.current_image.height())
        widget_ar = self.width() / max(1, self.height())
        img_ar = img_w / img_h
        if widget_ar > img_ar:
            h = self.height()
            w = int(h * img_ar)
        else:
            w = self.width()
            h = int(w / img_ar)
        return QRect((self.width() - w) // 2, (self.height() - h) // 2, w, h)

    def _to_norm(self, pos: QPointF) -> QPointF:
        vr = self._vrect()
        if vr.width() <= 0 or vr.height() <= 0:
            return QPointF(0, 0)
        return QPointF(
            max(0.0, min(1.0, (pos.x() - vr.x()) / vr.width())),
            max(0.0, min(1.0, (pos.y() - vr.y()) / vr.height()))
        )

    def _to_w(self, nr: QRectF) -> QRect:
        vr = self._vrect()
        if vr.width() <= 0 or vr.height() <= 0:
            return QRect()
        return QRect(
            int(vr.x() + nr.x() * vr.width()),
            int(vr.y() + nr.y() * vr.height()),
            int(nr.width() * vr.width()),
            int(nr.height() * vr.height())
        )

    def _corner(self, pos: QPointF) -> int:
        sr = self._to_w(self.selection_rect)
        corners = [sr.topLeft(), sr.topRight(), sr.bottomLeft(), sr.bottomRight()]
        for i, c in enumerate(corners):
            if abs(pos.x() - c.x()) <= 10 and abs(pos.y() - c.y()) <= 10:
                return i
        return -1

    def _inside(self, pos: QPointF) -> bool:
        return self._to_w(self.selection_rect).contains(pos.toPoint())

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        p.setBrush(QColor(25, 25, 28, 230))
        p.setPen(QPen(QColor(60, 60, 64), 1))
        p.drawRoundedRect(self.rect().adjusted(0, 0, -1, -1), 8, 8)

        # Close button
        cbr = QRect(self.width() - 22, 4, 18, 18)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(60, 60, 64))
        p.drawRoundedRect(cbr, 4, 4)
        p.setPen(QColor(180, 180, 184))
        p.setFont(QFont("Inter", 10, QFont.Weight.Bold))
        p.drawText(cbr, Qt.AlignmentFlag.AlignCenter, "×")

        if not self.current_image or self.current_image.isNull():
            p.end()
            return

        vr = self._vrect()
        pm = QPixmap.fromImage(self.current_image).scaled(
            vr.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        )
        p.drawPixmap(vr, pm, pm.rect())

        # Dim areas outside selection
        sr = self._to_w(self.selection_rect)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(0, 0, 0, 130))
        # Top
        p.drawRect(QRect(vr.x(), vr.y(), vr.width(), max(0, sr.y() - vr.y())))
        # Bottom
        p.drawRect(QRect(vr.x(), sr.bottom(), vr.width(), max(0, vr.bottom() - sr.bottom())))
        # Left
        p.drawRect(QRect(vr.x(), sr.y(), max(0, sr.x() - vr.x()), sr.height()))
        # Right
        p.drawRect(QRect(sr.right(), sr.y(), max(0, vr.right() - sr.right()), sr.height()))

        # Selection border
        p.setPen(QPen(QColor(88, 73, 226), 2))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRect(sr)

        # Corner handles
        p.setBrush(QColor(88, 73, 226))
        for c in [sr.topLeft(), sr.topRight(), sr.bottomLeft(), sr.bottomRight()]:
            p.drawRoundedRect(QRect(int(c.x() - 4), int(c.y() - 4), 8, 8), 2, 2)

        # Zoom level text
        zoom = 1.0 / max(0.01, self.selection_rect.width())
        p.setPen(QColor(200, 200, 204))
        p.setFont(QFont("Inter", 8))
        p.drawText(6, 16, f"🔍 {zoom:.1f}x")
        p.end()

    def mousePressEvent(self, e):
        if e.button() != Qt.MouseButton.LeftButton or not self.current_image:
            return
        if QRect(self.width() - 22, 4, 18, 18).contains(e.position().toPoint()):
            self.close_clicked.emit()
            return
        c = self._corner(e.position())
        if c >= 0:
            self.resizing = True
            self.resize_corner = c
        elif self._inside(e.position()):
            self.dragging = True
        self.drag_start = self._to_norm(e.position())
        self.drag_orig = QRectF(self.selection_rect)

    def mouseMoveEvent(self, e):
        if not self.current_image:
            return
        np_ = self._to_norm(e.position())
        if self.dragging:
            dx = np_.x() - self.drag_start.x()
            dy = np_.y() - self.drag_start.y()
            r = QRectF(self.drag_orig)
            r.moveTo(
                max(0, min(r.x() + dx, 1 - r.width())),
                max(0, min(r.y() + dy, 1 - r.height()))
            )
            self.selection_rect = r
            self.selection_changed.emit(r)
            self.update()
        elif self.resizing:
            r = QRectF(self.drag_orig)
            if self.resize_corner in [1, 3]:
                r.setWidth(max(0.05, min(np_.x() - r.x(), 1 - r.x())))
            else:
                nw = max(0.05, r.right() - np_.x())
                r.setX(r.right() - nw)
                r.setWidth(nw)
            if self.resize_corner in [2, 3]:
                r.setHeight(max(0.05, min(np_.y() - r.y(), 1 - r.y())))
            else:
                nh = max(0.05, r.bottom() - np_.y())
                r.setY(r.bottom() - nh)
                r.setHeight(nh)
            self.selection_rect = r
            self.selection_changed.emit(r)
            self.update()

    def mouseReleaseEvent(self, e):
        self.dragging = False
        self.resizing = False
        self.resize_corner = -1


class ZoomSlider(QWidget):
    level_changed = pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(30, 150)
        self.level = 0.5
        self._drag = False

    def set_level(self, l):
        self.level = max(0.0, min(1.0, l))
        self.update()

    def _hy(self):
        m = 22
        return int(m + (self.height() - 2 * m) * (1 - self.level))

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QColor(25, 25, 28, 230))
        p.setPen(QPen(QColor(60, 60, 64), 1))
        p.drawRoundedRect(self.rect().adjusted(0, 0, -1, -1), 6, 6)
        m, cx = 22, self.width() // 2
        th = self.height() - 2 * m
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(50, 50, 54))
        p.drawRoundedRect(cx - 2, m, 4, th, 2, 2)
        hy = self._hy()
        p.setBrush(QColor(88, 73, 226))
        p.drawRoundedRect(cx - 2, hy, 4, m + th - hy, 2, 2)
        hs = 14
        p.setPen(QPen(QColor(88, 73, 226), 2))
        p.setBrush(QColor(40, 40, 44))
        p.drawRoundedRect(cx - hs // 2, hy - hs // 2, hs, hs, 3, 3)
        zoom = 1.0 / max(0.01, 1.0 - self.level * 0.9)
        p.setPen(QColor(160, 160, 164))
        p.setFont(QFont("Inter", 7, QFont.Weight.Bold))
        p.drawText(QRect(0, 2, self.width(), m - 4), Qt.AlignmentFlag.AlignCenter, f"{zoom:.1f}x")
        p.end()

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._drag = True
            self._upd(e.position().y())

    def mouseMoveEvent(self, e):
        if self._drag:
            self._upd(e.position().y())

    def mouseReleaseEvent(self, e):
        self._drag = False

    def wheelEvent(self, e):
        self.level = max(0.0, min(1.0, self.level + (0.05 if e.angleDelta().y() > 0 else -0.05)))
        self.level_changed.emit(self.level)
        self.update()

    def _upd(self, y):
        m = 22
        track_height = self.height() - 2 * m
        if track_height <= 0:
            return
        self.level = max(0.0, min(1.0, 1 - (y - m) / track_height))
        self.level_changed.emit(self.level)
        self.update()


# ─────────────────────────────────────────────────────────────────────────────
# Motion Detector Engine
# ─────────────────────────────────────────────────────────────────────────────
class MotionDetector:
    def __init__(self):
        self.prev_gray = None
        self.sensitivity = 75
        self.min_area = 500
        self.roi = None
        self.active = False
        self.downscale = 4

    def process_frame(self, qimage: QImage):
        if not self.active or not HAS_CV2:
            return [], 0.0
        try:
            gray = qimage.convertToFormat(QImage.Format.Format_Grayscale8)
            w, h = gray.width(), gray.height()
            if w <= 0 or h <= 0:
                return [], 0.0

            # Safely access image bits
            bits = gray.constBits()
            if bits is None:
                return [], 0.0
            bits.setsize(h * w)
            arr = np.frombuffer(bits, np.uint8).reshape((h, w))

            ds = self.downscale
            dw, dh = max(1, w // ds), max(1, h // ds)
            arr = cv2.resize(arr, (dw, dh))
            arr = cv2.GaussianBlur(arr, (21, 21), 0)

            # Apply ROI if set
            if self.roi:
                rx = max(0, int(self.roi.x() * dw))
                ry = max(0, int(self.roi.y() * dh))
                rw = min(int(self.roi.width() * dw), dw - rx)
                rh = min(int(self.roi.height() * dh), dh - ry)
                if rw <= 0 or rh <= 0:
                    return [], 0.0
                roi_arr = arr[ry:ry + rh, rx:rx + rw]
                roi_rx, roi_ry = rx, ry
            else:
                roi_arr = arr
                roi_rx, roi_ry = 0, 0

            if self.prev_gray is None or self.prev_gray.shape != roi_arr.shape:
                self.prev_gray = roi_arr.copy()
                return [], 0.0

            threshold = max(5, 55 - (self.sensitivity / 100.0 * 50))
            diff = cv2.absdiff(self.prev_gray, roi_arr)
            _, thresh = cv2.threshold(diff, threshold, 255, cv2.THRESH_BINARY)
            thresh = cv2.dilate(thresh, None, iterations=2)

            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            rects = []
            min_px = max(10, self.min_area // (ds * ds))
            total_area = 0

            for c in contours:
                if cv2.contourArea(c) < min_px:
                    continue
                x, y, cw, ch = cv2.boundingRect(c)
                # Convert back to normalized coordinates relative to original image
                nx = (roi_rx + x) * ds / w
                ny = (roi_ry + y) * ds / h
                nw = cw * ds / w
                nh = ch * ds / h
                rects.append(QRectF(nx, ny, nw, nh))
                total_area += cv2.contourArea(c)

            self.prev_gray = roi_arr.copy()
            roi_size = roi_arr.shape[0] * roi_arr.shape[1]
            score = min(100.0, (total_area / max(1, roi_size)) * 300)
            return rects, score
        except Exception:
            self.prev_gray = None
            return [], 0.0

    def reset(self):
        self.prev_gray = None


# ─────────────────────────────────────────────────────────────────────────────
# Video Analysis Thread
# ─────────────────────────────────────────────────────────────────────────────
class VideoAnalysisThread(QThread):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, path, mode, params=None):
        super().__init__()
        self.path = path
        self.mode = mode
        self.params = params or {}
        self._cancel = False

    def cancel(self):
        self._cancel = True

    @staticmethod
    def _fmt(ms):
        if ms < 0:
            ms = 0
        s = int(ms / 1000) % 60
        m = int(ms / 60000)
        h = int(ms / 3600000)
        return f"{h:02d}:{m:02d}:{s:02d}" if h > 0 else f"{m:02d}:{s:02d}"

    def run(self):
        if not HAS_CV2:
            self.error.emit("OpenCV not installed. Run: pip install opencv-python numpy")
            return
        try:
            cap = cv2.VideoCapture(self.path)
            if not cap.isOpened():
                self.error.emit("Cannot open video file")
                return
            total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            if fps <= 0:
                fps = 30.0
            if total <= 0:
                total = 1

            result = {}
            if self.mode == 'motion':
                result = self._motion(cap, total, fps)
            elif self.mode == 'scene':
                result = self._scene(cap, total, fps)
            elif self.mode == 'blur':
                result = self._blur(cap, total, fps)
            elif self.mode == 'brightness':
                result = self._brightness(cap, total, fps)

            cap.release()
            if not self._cancel:
                self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

    def _motion(self, cap, total, fps):
        seg_dur = self.params.get('segment_duration', 1.0)
        sens = self.params.get('sensitivity', 75)
        threshold = max(5, 55 - (sens / 100.0 * 50))
        seg_frames = max(1, int(fps * seg_dur))
        skip = max(1, seg_frames // 5)
        prev = None
        segments, scores = [], []
        idx, seg_i = 0, 0

        while not self._cancel:
            ret, frame = cap.read()
            if not ret:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.resize(gray, (gray.shape[1] // 4, gray.shape[0] // 4))
            gray = cv2.GaussianBlur(gray, (21, 21), 0)
            if prev is not None and idx % skip == 0:
                diff = cv2.absdiff(prev, gray)
                _, th = cv2.threshold(diff, threshold, 255, cv2.THRESH_BINARY)
                score = min(100.0, np.count_nonzero(th) / max(1, th.size) * 300)
                scores.append(score)
            prev = gray
            idx += 1
            if idx % seg_frames == 0 and scores:
                avg = sum(scores) / len(scores)
                t = int(seg_i * seg_dur * 1000)
                segments.append({'time_ms': t, 'time_str': self._fmt(t), 'score': avg})
                scores = []
                seg_i += 1
            if idx % max(1, total // 100) == 0:
                p = min(99, int(idx / total * 100))
                self.progress.emit(p, f"Analyzing motion... {p}%")

        if scores and not self._cancel:
            avg = sum(scores) / len(scores)
            t = int(seg_i * seg_dur * 1000)
            segments.append({'time_ms': t, 'time_str': self._fmt(t), 'score': avg})

        if not self._cancel:
            self.progress.emit(100, "Done")
        return {'mode': 'motion', 'segments': segments, 'duration_ms': int(total / fps * 1000), 'fps': fps}

    def _scene(self, cap, total, fps):
        threshold = self.params.get('threshold', 0.4)
        prev_hist = None
        changes = []
        skip = max(1, int(fps / 5))
        idx = 0

        while not self._cancel:
            ret, frame = cap.read()
            if not ret:
                break
            if idx % skip == 0:
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                hist = cv2.calcHist([hsv], [0, 1], None, [50, 60], [0, 180, 0, 256])
                cv2.normalize(hist, hist, 0, 1, cv2.NORM_MINMAX)
                if prev_hist is not None:
                    corr = cv2.compareHist(prev_hist, hist, cv2.HISTCMP_CORREL)
                    if corr < threshold:
                        t = int(idx / fps * 1000)
                        changes.append({'time_ms': t, 'time_str': self._fmt(t), 'correlation': round(float(corr), 3)})
                prev_hist = hist
            idx += 1
            if idx % max(1, total // 100) == 0:
                p = min(99, int(idx / total * 100))
                self.progress.emit(p, f"Detecting scenes... {p}%")

        if not self._cancel:
            self.progress.emit(100, "Done")
        return {'mode': 'scene', 'changes': changes, 'duration_ms': int(total / fps * 1000)}

    def _blur(self, cap, total, fps):
        threshold = self.params.get('threshold', 50)
        results = []
        skip = max(1, int(fps / 10))
        idx = 0

        while not self._cancel:
            ret, frame = cap.read()
            if not ret:
                break
            if idx % skip == 0:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                val = cv2.Laplacian(gray, cv2.CV_64F).var()
                t = int(idx / fps * 1000)
                results.append({
                    'time_ms': t,
                    'time_str': self._fmt(t),
                    'blur_score': round(float(val), 1),
                    'blurry': val < threshold
                })
            idx += 1
            if idx % max(1, total // 100) == 0:
                p = min(99, int(idx / total * 100))
                self.progress.emit(p, f"Analyzing blur... {p}%")

        if not self._cancel:
            self.progress.emit(100, "Done")
        return {'mode': 'blur', 'frames': results, 'threshold': threshold, 'duration_ms': int(total / fps * 1000)}

    def _brightness(self, cap, total, fps):
        results = []
        skip = max(1, int(fps / 5))
        idx = 0

        while not self._cancel:
            ret, frame = cap.read()
            if not ret:
                break
            if idx % skip == 0:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                val = float(np.mean(gray))
                t = int(idx / fps * 1000)
                results.append({
                    'time_ms': t,
                    'time_str': self._fmt(t),
                    'brightness': round(val, 1)
                })
            idx += 1
            if idx % max(1, total // 100) == 0:
                p = min(99, int(idx / total * 100))
                self.progress.emit(p, f"Analyzing brightness... {p}%")

        if not self._cancel:
            self.progress.emit(100, "Done")
        return {'mode': 'brightness', 'frames': results, 'duration_ms': int(total / fps * 1000)}


# ─────────────────────────────────────────────────────────────────────────────
# Clickable Matplotlib Timeline
# ─────────────────────────────────────────────────────────────────────────────
class ClickableTimeline(FigureCanvas):
    time_clicked = pyqtSignal(int)

    def __init__(self, parent=None, height=3):
        self.fig = Figure(figsize=(10, height), dpi=100)
        self.fig.patch.set_facecolor('#232326')
        super().__init__(self.fig)
        self.ax = self.fig.add_subplot(111)
        self._setup_ax()
        self.setParent(parent)
        self.mpl_connect('button_press_event', self._on_click)
        self.mpl_connect('motion_notify_event', self._on_hover)
        self._time_data = []

    def _setup_ax(self):
        self.ax.set_facecolor('#2a2a2e')
        for s in self.ax.spines.values():
            s.set_color('#3d3d44')
        self.ax.tick_params(colors='#a0a0a4', labelsize=8)
        self.ax.xaxis.label.set_color('#e0e0e0')
        self.ax.yaxis.label.set_color('#e0e0e0')
        self.ax.grid(True, color='#3d3d44', alpha=0.5, linewidth=0.5)

    def _on_click(self, event):
        if event.inaxes == self.ax and self._time_data and event.xdata is not None:
            idx = int(round(event.xdata))
            if 0 <= idx < len(self._time_data):
                self.time_clicked.emit(self._time_data[idx]['time_ms'])

    def _on_hover(self, event):
        if event.inaxes == self.ax and self._time_data and event.xdata is not None:
            idx = int(round(event.xdata))
            if 0 <= idx < len(self._time_data):
                d = self._time_data[idx]
                score = d.get('score', d.get('brightness', d.get('blur_score', 'N/A')))
                QToolTip.showText(event.guiEvent.globalPos(), f"{d['time_str']}\nScore: {score}")


# ─────────────────────────────────────────────────────────────────────────────
# Motion Detection Panel (Floating)
# ─────────────────────────────────────────────────────────────────────────────
class MotionDetectionPanel(QFrame):
    def __init__(self, player, parent=None):
        super().__init__(parent)
        self.player = player
        self.detector = MotionDetector()
        self.setFixedSize(280, 340)
        self.setObjectName("controlPanel")
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 10, 14, 10)
        lay.setSpacing(8)

        title = QLabel("🔍 Motion Detection")
        title.setFont(QFont("Inter", 12, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(title)

        self.chk_enable = QCheckBox("Enable Detection")
        self.chk_enable.toggled.connect(self._toggle)
        lay.addWidget(self.chk_enable)

        # Sensitivity
        g1 = QGroupBox("Sensitivity")
        g1l = QHBoxLayout(g1)
        self.sl_sens = QSlider(Qt.Orientation.Horizontal)
        self.sl_sens.setRange(10, 100)
        self.sl_sens.setValue(75)
        self.lbl_sens = QLabel("75%")
        self.lbl_sens.setFixedWidth(40)
        self.sl_sens.valueChanged.connect(self._on_sensitivity_changed)
        g1l.addWidget(self.sl_sens)
        g1l.addWidget(self.lbl_sens)
        lay.addWidget(g1)

        # Min Area
        g2 = QGroupBox("Min Object Area")
        g2l = QHBoxLayout(g2)
        self.sp_area = QSpinBox()
        self.sp_area.setRange(100, 50000)
        self.sp_area.setValue(500)
        self.sp_area.setSingleStep(100)
        self.sp_area.valueChanged.connect(lambda v: setattr(self.detector, 'min_area', v))
        g2l.addWidget(self.sp_area)
        lay.addWidget(g2)

        # ROI
        g3 = QGroupBox("Region of Interest")
        g3l = QVBoxLayout(g3)
        self.chk_roi = QCheckBox("Enable ROI")
        self.chk_roi.toggled.connect(self._toggle_roi)
        row = QHBoxLayout()
        self.btn_draw_roi = QPushButton("Draw ROI")
        self.btn_draw_roi.setEnabled(False)
        self.btn_draw_roi.clicked.connect(self._draw_roi)
        self.btn_clear_roi = QPushButton("Clear")
        self.btn_clear_roi.setEnabled(False)
        self.btn_clear_roi.clicked.connect(self._clear_roi)
        row.addWidget(self.btn_draw_roi)
        row.addWidget(self.btn_clear_roi)
        g3l.addWidget(self.chk_roi)
        g3l.addLayout(row)
        lay.addWidget(g3)

        # Stats
        g4 = QGroupBox("Live Stats")
        g4l = QGridLayout(g4)
        self.lbl_score = QLabel("0.0%")
        self.lbl_score.setFont(QFont("Inter", 14, QFont.Weight.Bold))
        self.lbl_score.setStyleSheet("color: #4caf50;")
        self.lbl_objects = QLabel("0")
        self.lbl_objects.setFont(QFont("Inter", 14, QFont.Weight.Bold))
        g4l.addWidget(QLabel("Motion:"), 0, 0)
        g4l.addWidget(self.lbl_score, 0, 1)
        g4l.addWidget(QLabel("Objects:"), 1, 0)
        g4l.addWidget(self.lbl_objects, 1, 1)
        lay.addWidget(g4)

        self.btn_close = QPushButton("Close Panel")
        self.btn_close.clicked.connect(self.hide)
        lay.addWidget(self.btn_close)

    def _on_sensitivity_changed(self, v):
        self.detector.sensitivity = v
        self.lbl_sens.setText(f"{v}%")

    def _toggle(self, on):
        self.detector.active = on
        if on:
            self.detector.reset()
            self.player.frame_display.set_motion_overlay([])
        else:
            self.player.frame_display.set_motion_overlay([])
            self.lbl_score.setText("0.0%")
            self.lbl_objects.setText("0")
            self.lbl_score.setStyleSheet("color: #4caf50;")

    def _toggle_roi(self, on):
        self.btn_draw_roi.setEnabled(on)
        self.btn_clear_roi.setEnabled(on)
        if not on:
            self._clear_roi()

    def _draw_roi(self):
        self.player.frame_display.set_drawing_roi(True, self._on_roi_drawn)
        self.player.update_status("👆 Click and drag on video to draw ROI region")

    def _on_roi_drawn(self, start, end):
        x1, y1 = start.x(), start.y()
        x2, y2 = end.x(), end.y()
        rx, ry = min(x1, x2), min(y1, y2)
        rw, rh = abs(x2 - x1), abs(y2 - y1)
        if rw > 0.01 and rh > 0.01:
            roi = QRectF(rx, ry, rw, rh)
            self.detector.roi = roi
            self.player.frame_display.set_roi(roi)
            self.player.update_status("ROI set successfully")
        self.player.frame_display.set_drawing_roi(False)

    def _clear_roi(self):
        self.detector.roi = None
        self.player.frame_display.set_roi(None)
        self.player.frame_display.set_drawing_roi(False)

    def process_frame(self, qimage):
        if not self.detector.active:
            return
        rects, score = self.detector.process_frame(qimage)
        self.player.frame_display.set_motion_overlay(rects)
        self.lbl_score.setText(f"{score:.1f}%")
        if score > 30:
            self.lbl_score.setStyleSheet("color: #f44336;")
        elif score > 10:
            self.lbl_score.setStyleSheet("color: #ff9800;")
        else:
            self.lbl_score.setStyleSheet("color: #4caf50;")
        self.lbl_objects.setText(str(len(rects)))

    def hideEvent(self, event):
        self.chk_enable.setChecked(False)
        self._clear_roi()
        super().hideEvent(event)


# ─────────────────────────────────────────────────────────────────────────────
# Base Analysis Dialog
# ─────────────────────────────────────────────────────────────────────────────
class AnalysisDialog(QDialog):
    seek_requested = pyqtSignal(int)

    def __init__(self, player, title, parent=None):
        super().__init__(parent)
        self.player = player
        self.thread = None
        self.setWindowTitle(title)
        self.setMinimumSize(750, 500)
        self.resize(900, 600)
        self._build_base()

    def _build_base(self):
        lay = QVBoxLayout(self)
        lay.setSpacing(10)

        # Progress area
        self.progress_frame = QFrame()
        self.progress_frame.setVisible(False)
        pl = QVBoxLayout(self.progress_frame)
        pl.setContentsMargins(0, 0, 0, 0)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.lbl_progress = QLabel("Preparing...")
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setFixedWidth(80)
        self.btn_cancel.clicked.connect(self._cancel)
        pr = QHBoxLayout()
        pr.addWidget(self.progress_bar)
        pr.addWidget(self.lbl_progress)
        pr.addWidget(self.btn_cancel)
        pl.addLayout(pr)
        lay.addWidget(self.progress_frame)

        # Content area (override in subclass)
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.content_widget, stretch=1)

        # Bottom buttons
        br = QHBoxLayout()
        br.addStretch()
        self.btn_close = QPushButton("Close")
        self.btn_close.clicked.connect(self.close)
        br.addWidget(self.btn_close)
        lay.addLayout(br)

    def _start_analysis(self, mode, params=None):
        if not self.player.current_file:
            self.player.update_status("⚠️ No video loaded")
            self.close()
            return
        if not HAS_CV2:
            QMessageBox.warning(
                self, "Missing Dependency",
                "OpenCV is required.\nInstall with: pip install opencv-python numpy"
            )
            self.close()
            return
        self.progress_frame.setVisible(True)
        self.content_widget.setVisible(False)
        self.thread = VideoAnalysisThread(self.player.current_file, mode, params)
        self.thread.progress.connect(self._on_progress)
        self.thread.finished.connect(self._on_finished)
        self.thread.error.connect(self._on_error)
        self.thread.start()

    def _cancel(self):
        if self.thread:
            self.thread.cancel()

    def _on_progress(self, pct, msg):
        self.progress_bar.setValue(pct)
        self.lbl_progress.setText(msg)

    def _on_error(self, msg):
        self.progress_frame.setVisible(False)
        self.content_widget.setVisible(True)
        self.player.update_status(f"❌ {msg}")

    def _on_finished(self, results):
        self.progress_frame.setVisible(False)
        self.content_widget.setVisible(True)
        self._display_results(results)

    def _display_results(self, results):
        pass  # Override in subclass

    def closeEvent(self, event):
        if self.thread:
            self.thread.cancel()
            self.thread.wait(2000)
            self.thread = None
        super().closeEvent(event)


# ─────────────────────────────────────────────────────────────────────────────
# Clip Analyzer Dialog
# ─────────────────────────────────────────────────────────────────────────────
class ClipAnalyzerDialog(AnalysisDialog):
    def __init__(self, player, parent=None):
        super().__init__(player, "🎬 Clip Analyzer — Motion Frequency", parent)
        self._segments = []
        self._current_idx = -1
        self._build()
        self._start_analysis('motion', {'segment_duration': 1.0, 'sensitivity': 75})

    def _build(self):
        # Settings at top
        sl = QHBoxLayout()
        sl.addWidget(QLabel("Segment Duration:"))
        self.sp_seg = QSpinBox()
        self.sp_seg.setRange(1, 30)
        self.sp_seg.setValue(1)
        self.sp_seg.setSuffix(" sec")
        sl.addWidget(self.sp_seg)
        sl.addWidget(QLabel("Sensitivity:"))
        self.sl_sens = QSlider(Qt.Orientation.Horizontal)
        self.sl_sens.setRange(10, 100)
        self.sl_sens.setValue(75)
        self.sl_sens.setFixedWidth(120)
        self.lbl_sens = QLabel("75%")
        self.lbl_sens.setFixedWidth(40)
        self.sl_sens.valueChanged.connect(lambda v: self.lbl_sens.setText(f"{v}%"))
        sl.addWidget(self.sl_sens)
        sl.addWidget(self.lbl_sens)
        self.btn_reanalyze = QPushButton("🔄 Re-Analyze")
        self.btn_reanalyze.clicked.connect(self._reanalyze)
        sl.addWidget(self.btn_reanalyze)
        sl.addStretch()
        self.content_layout.addLayout(sl)

        # Timeline
        if HAS_MPL:
            self.timeline = ClickableTimeline(self, height=2.5)
            self.timeline.time_clicked.connect(self.seek_requested.emit)
            self.content_layout.addWidget(self.timeline)
        else:
            lbl = QLabel("⚠️ matplotlib required for graph. Install: pip install matplotlib")
            self.content_layout.addWidget(lbl)

        # Stats
        self.stats_frame = QFrame()
        self.stats_layout = QGridLayout(self.stats_frame)
        self.stats_layout.setContentsMargins(8, 8, 8, 8)
        self.content_layout.addWidget(self.stats_frame)

        # Threshold slider
        thr = QHBoxLayout()
        thr.addWidget(QLabel("Highlight Threshold:"))
        self.sl_thresh = QSlider(Qt.Orientation.Horizontal)
        self.sl_thresh.setRange(1, 99)
        self.sl_thresh.setValue(20)
        self.sl_thresh.setFixedWidth(150)
        self.lbl_thresh = QLabel("20%")
        self.lbl_thresh.setFixedWidth(40)
        self.sl_thresh.valueChanged.connect(self._on_threshold_changed)
        thr.addWidget(self.sl_thresh)
        thr.addWidget(self.lbl_thresh)
        self.btn_next = QPushButton("⏭ Next Motion")
        self.btn_next.clicked.connect(self._next_motion)
        thr.addWidget(self.btn_next)
        self.btn_peak = QPushButton("⏮ Peak Motion")
        self.btn_peak.clicked.connect(self._peak_motion)
        thr.addWidget(self.btn_peak)
        thr.addStretch()
        self.content_layout.addLayout(thr)

    def _reanalyze(self):
        self._start_analysis('motion', {
            'segment_duration': self.sp_seg.value(),
            'sensitivity': self.sl_sens.value()
        })

    def _on_threshold_changed(self, v):
        self.lbl_thresh.setText(f"{v}%")
        self._draw_graph()

    def _display_results(self, results):
        # Clear previous stats
        while self.stats_layout.count():
            item = self.stats_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self._segments = results.get('segments', [])
        self._current_idx = -1

        if not self._segments:
            self.stats_layout.addWidget(QLabel("No motion detected"), 0, 0)
            return

        if not HAS_CV2:
            self.stats_layout.addWidget(QLabel("NumPy not available"), 0, 0)
            return

        scores = [s['score'] for s in self._segments]
        high = sum(1 for s in scores if s > 50)
        med = sum(1 for s in scores if 20 < s <= 50)
        low = sum(1 for s in scores if s <= 20)
        total = max(1, len(self._segments))
        peak_idx = int(np.argmax(scores))
        peak = self._segments[peak_idx]

        stats = [
            ("Total Segments", str(len(self._segments))),
            ("🔴 High Motion (>50%)", f"{high} ({high * 100 // total}%)"),
            ("🟡 Medium (20-50%)", f"{med} ({med * 100 // total}%)"),
            ("🟢 Low (<20%)", f"{low} ({low * 100 // total}%)"),
            ("📈 Peak", f"{peak['score']:.1f}% at {peak['time_str']}"),
        ]
        for i, (label, val) in enumerate(stats):
            lbl = QLabel(label)
            self.stats_layout.addWidget(lbl, i, 0)
            val_lbl = QLabel(val)
            val_lbl.setFont(QFont("Inter", 10, QFont.Weight.Bold))
            self.stats_layout.addWidget(val_lbl, i, 1)

        self._draw_graph()

    def _draw_graph(self):
        if not HAS_MPL or not self._segments:
            return
        ax = self.timeline.ax
        ax.clear()
        self.timeline._setup_ax()
        thresh = self.sl_thresh.value()
        xs = list(range(len(self._segments)))
        scores = [s['score'] for s in self._segments]
        colors = ['#f44336' if s > 50 else '#ff9800' if s > thresh else '#4caf50' for s in scores]
        ax.bar(xs, scores, color=colors, width=1.0, edgecolor='none')
        ax.axhline(y=thresh, color='#5849e2', linestyle='--', linewidth=1, alpha=0.8)
        ax.set_ylabel('Motion %', fontsize=9)
        ax.set_xlabel('Time Segment', fontsize=9)

        n = len(self._segments)
        step = max(1, n // 15)
        ticks = list(range(0, n, step))
        labels = [self._segments[i]['time_str'] for i in ticks]
        ax.set_xticks(ticks)
        ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=7)
        ax.set_xlim(-0.5, n - 0.5)
        ax.set_ylim(0, max(100, max(scores) * 1.1))
        self.timeline._time_data = self._segments
        self.timeline.fig.tight_layout()
        self.timeline.draw()

    def _next_motion(self):
        thresh = self.sl_thresh.value()
        start = self._current_idx + 1 if self._current_idx >= 0 else 0
        for i in range(start, len(self._segments)):
            if self._segments[i]['score'] > thresh:
                self._current_idx = i
                self.seek_requested.emit(self._segments[i]['time_ms'])
                self.player.update_status(
                    f"⏭ Jumped to motion at {self._segments[i]['time_str']} "
                    f"({self._segments[i]['score']:.1f}%)"
                )
                return
        self.player.update_status("No more motion segments found")

    def _peak_motion(self):
        if not self._segments or not HAS_CV2:
            return
        idx = int(np.argmax([s['score'] for s in self._segments]))
        self._current_idx = idx
        self.seek_requested.emit(self._segments[idx]['time_ms'])
        self.player.update_status(
            f"⏮ Peak motion at {self._segments[idx]['time_str']} "
            f"({self._segments[idx]['score']:.1f}%)"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Scene Change Detection Dialog
# ─────────────────────────────────────────────────────────────────────────────
class SceneChangeDialog(AnalysisDialog):
    def __init__(self, player, parent=None):
        super().__init__(player, "🔄 Scene Change Detection", parent)
        self._changes = []
        self._list_connected = False
        self._build()
        self._start_analysis('scene', {'threshold': 0.4})

    def _build(self):
        sl = QHBoxLayout()
        sl.addWidget(QLabel("Threshold:"))
        self.sl_thresh = QSlider(Qt.Orientation.Horizontal)
        self.sl_thresh.setRange(10, 90)
        self.sl_thresh.setValue(40)
        self.sl_thresh.setFixedWidth(150)
        self.lbl_thresh = QLabel("0.40")
        self.lbl_thresh.setFixedWidth(40)
        self.sl_thresh.valueChanged.connect(lambda v: self.lbl_thresh.setText(f"{v / 100:.2f}"))
        self.btn_reanalyze = QPushButton("🔄 Re-Analyze")
        self.btn_reanalyze.clicked.connect(
            lambda: self._start_analysis('scene', {'threshold': self.sl_thresh.value() / 100})
        )
        sl.addWidget(self.sl_thresh)
        sl.addWidget(self.lbl_thresh)
        sl.addWidget(self.btn_reanalyze)
        sl.addStretch()
        self.content_layout.addLayout(sl)

        self.info_label = QLabel("")
        self.info_label.setFont(QFont("Inter", 10))
        self.content_layout.addWidget(self.info_label)

        self.list = QListWidget()
        self.list.setMaximumHeight(300)
        self.content_layout.addWidget(self.list)

        # Connect once, not in _display_results
        self.list.itemDoubleClicked.connect(self._on_item_double_clicked)

        if HAS_MPL:
            self.timeline = ClickableTimeline(self, height=1.5)
            self.timeline.time_clicked.connect(self.seek_requested.emit)
            self.content_layout.addWidget(self.timeline)

    def _on_item_double_clicked(self, item):
        data = item.data(Qt.ItemDataRole.UserRole)
        if data is not None:
            self.seek_requested.emit(data)

    def _display_results(self, results):
        self._changes = results.get('changes', [])
        self.info_label.setText(f"Detected {len(self._changes)} scene changes")
        self.list.clear()
        for i, c in enumerate(self._changes):
            item = QListWidgetItem(
                f"  #{i + 1}  │  {c['time_str']}  │  Correlation: {c['correlation']}"
            )
            item.setData(Qt.ItemDataRole.UserRole, c['time_ms'])
            self.list.addItem(item)

        if HAS_MPL and self._changes:
            ax = self.timeline.ax
            ax.clear()
            self.timeline._setup_ax()
            times = [c['time_ms'] / 1000 for c in self._changes]
            corrs = [c['correlation'] for c in self._changes]
            ax.stem(times, corrs, linefmt='-', markerfmt='o', basefmt=' ')
            ax.axhline(y=self.sl_thresh.value() / 100, color='#f44336', linestyle='--', linewidth=1)
            ax.set_ylabel('Correlation', fontsize=8)
            ax.set_xlabel('Time (s)', fontsize=8)
            ax.set_ylim(0, 1)
            self.timeline._time_data = self._changes
            self.timeline.fig.tight_layout()
            self.timeline.draw()


# ─────────────────────────────────────────────────────────────────────────────
# Blur Detection Dialog
# ─────────────────────────────────────────────────────────────────────────────
class BlurDetectionDialog(AnalysisDialog):
    def __init__(self, player, parent=None):
        super().__init__(player, "🌫️ Blur Detection", parent)
        self._frames = []
        self._blur_idx = -1
        self._build()
        self._start_analysis('blur', {'threshold': 50})

    def _build(self):
        sl = QHBoxLayout()
        sl.addWidget(QLabel("Blur Threshold:"))
        self.sl_thresh = QSpinBox()
        self.sl_thresh.setRange(5, 500)
        self.sl_thresh.setValue(50)
        self.btn_reanalyze = QPushButton("🔄 Re-Analyze")
        self.btn_reanalyze.clicked.connect(
            lambda: self._start_analysis('blur', {'threshold': self.sl_thresh.value()})
        )
        sl.addWidget(self.sl_thresh)
        sl.addWidget(self.btn_reanalyze)
        self.btn_next_blur = QPushButton("⏭ Next Blurry")
        self.btn_next_blur.clicked.connect(self._next_blurry)
        sl.addWidget(self.btn_next_blur)
        sl.addStretch()
        self.content_layout.addLayout(sl)

        self.info_label = QLabel("")
        self.content_layout.addWidget(self.info_label)

        if HAS_MPL:
            self.timeline = ClickableTimeline(self, height=2)
            self.timeline.time_clicked.connect(self.seek_requested.emit)
            self.content_layout.addWidget(self.timeline)

        self.list = QListWidget()
        self.list.setMaximumHeight(200)
        self.content_layout.addWidget(self.list)

        # Connect once
        self.list.itemDoubleClicked.connect(self._on_item_double_clicked)

    def _on_item_double_clicked(self, item):
        data = item.data(Qt.ItemDataRole.UserRole)
        if data is not None:
            self.seek_requested.emit(data)

    def _display_results(self, results):
        self._frames = results.get('frames', [])
        self._blur_idx = -1
        blurry = [f for f in self._frames if f['blurry']]
        self.info_label.setText(
            f"Total samples: {len(self._frames)}  │  Blurry: {len(blurry)}  │  "
            f"Sharp: {len(self._frames) - len(blurry)}"
        )
        self.list.clear()
        for f in blurry:
            item = QListWidgetItem(f"  {f['time_str']}  │  Score: {f['blur_score']}")
            item.setData(Qt.ItemDataRole.UserRole, f['time_ms'])
            self.list.addItem(item)

        if HAS_MPL and self._frames:
            ax = self.timeline.ax
            ax.clear()
            self.timeline._setup_ax()
            xs = list(range(len(self._frames)))
            scores = [f['blur_score'] for f in self._frames]
            colors = ['#f44336' if f['blurry'] else '#4caf50' for f in self._frames]
            ax.bar(xs, scores, color=colors, width=1.0, edgecolor='none')
            ax.axhline(y=self.sl_thresh.value(), color='#5849e2', linestyle='--', linewidth=1)
            ax.set_ylabel('Laplacian Var', fontsize=8)
            ax.set_xlabel('Frame Sample', fontsize=8)
            n = len(self._frames)
            step = max(1, n // 15)
            ticks = list(range(0, n, step))
            labels = [self._frames[i]['time_str'] for i in ticks]
            ax.set_xticks(ticks)
            ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=7)
            self.timeline._time_data = self._frames
            self.timeline.fig.tight_layout()
            self.timeline.draw()

    def _next_blurry(self):
        start = self._blur_idx + 1 if self._blur_idx >= 0 else 0
        for i in range(start, len(self._frames)):
            if self._frames[i]['blurry']:
                self._blur_idx = i
                self.seek_requested.emit(self._frames[i]['time_ms'])
                self.player.update_status(
                    f"🌫️ Blurry frame at {self._frames[i]['time_str']} "
                    f"(score: {self._frames[i]['blur_score']})"
                )
                return
        self.player.update_status("No more blurry frames")


# ─────────────────────────────────────────────────────────────────────────────
# Brightness Analysis Dialog
# ─────────────────────────────────────────────────────────────────────────────
class BrightnessAnalysisDialog(AnalysisDialog):
    def __init__(self, player, parent=None):
        super().__init__(player, "💡 Brightness Analysis", parent)
        self._frames = []
        self._build()
        self._start_analysis('brightness')

    def _build(self):
        sl = QHBoxLayout()
        self.btn_reanalyze = QPushButton("🔄 Re-Analyze")
        self.btn_reanalyze.clicked.connect(lambda: self._start_analysis('brightness'))
        sl.addWidget(self.btn_reanalyze)
        sl.addStretch()
        self.content_layout.addLayout(sl)

        self.info_label = QLabel("")
        self.content_layout.addWidget(self.info_label)

        if HAS_MPL:
            self.timeline = ClickableTimeline(self, height=2.5)
            self.timeline.time_clicked.connect(self.seek_requested.emit)
            self.content_layout.addWidget(self.timeline)

    def _display_results(self, results):
        self._frames = results.get('frames', [])
        if not self._frames or not HAS_CV2:
            return

        vals = [f['brightness'] for f in self._frames]
        avg = float(np.mean(vals))
        mn = float(np.min(vals))
        mx = float(np.max(vals))
        dark = sum(1 for v in vals if v < 60)
        bright = sum(1 for v in vals if v > 200)
        self.info_label.setText(
            f"Avg: {avg:.1f}  │  Min: {mn:.1f}  │  Max: {mx:.1f}  │  "
            f"Dark(<60): {dark}  │  Overexposed(>200): {bright}"
        )

        if HAS_MPL:
            ax = self.timeline.ax
            ax.clear()
            self.timeline._setup_ax()
            xs = list(range(len(self._frames)))
            colors = [
                '#1565c0' if v < 60 else '#f44336' if v > 200 else '#ffeb3b' if v > 180 else '#4caf50'
                for v in vals
            ]
            ax.fill_between(xs, vals, alpha=0.3, color='#5849e2')
            ax.plot(xs, vals, color='#5849e2', linewidth=0.8)
            ax.scatter(xs, vals, c=colors, s=8, zorder=5)
            ax.axhline(y=60, color='#1565c0', linestyle=':', linewidth=1, alpha=0.6, label='Dark threshold')
            ax.axhline(y=200, color='#f44336', linestyle=':', linewidth=1, alpha=0.6, label='Overexposed')
            ax.set_ylabel('Brightness (0-255)', fontsize=8)
            ax.set_xlabel('Frame Sample', fontsize=8)
            ax.set_ylim(0, 255)
            n = len(self._frames)
            step = max(1, n // 15)
            ticks = list(range(0, n, step))
            labels = [self._frames[i]['time_str'] for i in ticks]
            ax.set_xticks(ticks)
            ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=7)
            ax.legend(fontsize=7, loc='upper right')
            self.timeline._time_data = self._frames
            self.timeline.fig.tight_layout()
            self.timeline.draw()


# ─────────────────────────────────────────────────────────────────────────────
# Object Counter Dialog (Foreground Analysis)
# ─────────────────────────────────────────────────────────────────────────────
class ObjectCounterDialog(AnalysisDialog):
    def __init__(self, player, parent=None):
        super().__init__(player, "📊 Object Activity Counter", parent)
        self._segments = []
        self._build()
        self._start_analysis('motion', {'segment_duration': 2.0, 'sensitivity': 60})

    def _build(self):
        sl = QHBoxLayout()
        sl.addWidget(QLabel("Segment:"))
        self.sp_seg = QSpinBox()
        self.sp_seg.setRange(1, 60)
        self.sp_seg.setValue(2)
        self.sp_seg.setSuffix(" sec")
        sl.addWidget(self.sp_seg)
        sl.addWidget(QLabel("Sensitivity:"))
        self.sl_sens = QSlider(Qt.Orientation.Horizontal)
        self.sl_sens.setRange(10, 100)
        self.sl_sens.setValue(60)
        self.sl_sens.setFixedWidth(120)
        self.lbl_sens = QLabel("60%")
        self.lbl_sens.setFixedWidth(40)
        self.sl_sens.valueChanged.connect(lambda v: self.lbl_sens.setText(f"{v}%"))
        sl.addWidget(self.sl_sens)
        sl.addWidget(self.lbl_sens)
        self.btn_reanalyze = QPushButton("🔄 Re-Analyze")
        self.btn_reanalyze.clicked.connect(
            lambda: self._start_analysis('motion', {
                'segment_duration': self.sp_seg.value(),
                'sensitivity': self.sl_sens.value()
            })
        )
        sl.addWidget(self.btn_reanalyze)
        sl.addStretch()
        self.content_layout.addLayout(sl)

        self.info_label = QLabel("")
        self.info_label.setFont(QFont("Inter", 11))
        self.content_layout.addWidget(self.info_label)

        if HAS_MPL:
            self.timeline = ClickableTimeline(self, height=2.5)
            self.timeline.time_clicked.connect(self.seek_requested.emit)
            self.content_layout.addWidget(self.timeline)

    def _display_results(self, results):
        self._segments = results.get('segments', [])
        if not self._segments or not HAS_CV2:
            return

        scores = [s['score'] for s in self._segments]
        active = [s for s in self._segments if s['score'] > 15]
        peak_idx = int(np.argmax(scores))
        self.info_label.setText(
            f"Active segments: {len(active)}/{len(self._segments)}  │  "
            f"Peak activity: {self._segments[peak_idx]['score']:.1f}% at "
            f"{self._segments[peak_idx]['time_str']}"
        )

        if HAS_MPL:
            ax = self.timeline.ax
            ax.clear()
            self.timeline._setup_ax()
            xs = list(range(len(self._segments)))
            colors = ['#f44336' if s > 50 else '#ff9800' if s > 15 else '#4caf50' for s in scores]
            ax.bar(xs, scores, color=colors, width=1.0, edgecolor='none')
            ax.axhline(y=15, color='#5849e2', linestyle='--', linewidth=1, alpha=0.8, label='Activity threshold')
            ax.set_ylabel('Activity %', fontsize=9)
            ax.set_xlabel('Time Segment', fontsize=9)
            n = len(self._segments)
            step = max(1, n // 15)
            ticks = list(range(0, n, step))
            labels = [self._segments[i]['time_str'] for i in ticks]
            ax.set_xticks(ticks)
            ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=7)
            ax.set_xlim(-0.5, n - 0.5)
            ax.legend(fontsize=7)
            self.timeline._time_data = self._segments
            self.timeline.fig.tight_layout()
            self.timeline.draw()


# ─────────────────────────────────────────────────────────────────────────────
# Main Video Player
# ─────────────────────────────────────────────────────────────────────────────
class VideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.is_dark_theme = True
        self.is_user_seeking = False
        self.current_file = None
        self.a_point = -1
        self.b_point = -1
        self.ab_loop_active = False
        self.is_recording = False
        self.record_start = -1
        self.record_end = -1
        self.ffmpeg_process = None
        self.zoom_enabled = False
        self._frame_counter = 0
        self._open_dialogs = []

        self.setWindowTitle("🧪 Forensic Video Player")
        self.resize(1100, 720)
        self.setMinimumSize(800, 500)
        self.setup_ui()
        self.setup_media()
        self.apply_theme()

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        ml = QVBoxLayout(central)
        ml.setContentsMargins(10, 10, 10, 10)
        ml.setSpacing(10)

        # Video container
        self.video_container = QWidget()
        self.video_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.video_container.setStyleSheet("background-color: #111113; border-radius: 10px;")
        vl = QVBoxLayout(self.video_container)
        vl.setContentsMargins(0, 0, 0, 0)
        self.frame_display = FrameDisplayWidget()
        vl.addWidget(self.frame_display)
        self.mini_preview = MiniPreviewWidget(self.video_container)
        self.mini_preview.hide()
        self.zoom_slider = ZoomSlider(self.video_container)
        self.zoom_slider.hide()
        ml.addWidget(self.video_container, stretch=1)

        # Motion panel (floating)
        self.motion_panel = MotionDetectionPanel(self, self.video_container)
        self.motion_panel.hide()

        # Control panel
        self.control_panel = QFrame()
        self.control_panel.setObjectName("controlPanel")
        pl = QVBoxLayout(self.control_panel)
        pl.setContentsMargins(16, 12, 16, 12)
        pl.setSpacing(10)

        # Row 1 - Main controls
        r1 = QHBoxLayout()
        r1.setSpacing(8)
        self.btn_open = QPushButton("📂 Open")
        self.btn_play = QPushButton("▶ Play")
        self.btn_stop = QPushButton("⏹ Stop")
        self.speed_combo = QComboBox()
        self.speed_combo.addItems(["0.25x", "0.5x", "0.75x", "1.0x", "1.25x", "1.5x", "2.0x"])
        self.speed_combo.setCurrentText("1.0x")
        self.speed_combo.setFixedWidth(70)
        self.btn_loop = QPushButton("🔁 Loop")
        self.btn_loop.setCheckable(True)
        self.btn_zoom = QPushButton("🔍 Zoom")
        self.btn_zoom.setCheckable(True)
        self.btn_ab = QPushButton("A→B Loop")
        self.btn_ab.setCheckable(True)
        self.btn_set_a = QPushButton("Set A")
        self.btn_set_b = QPushButton("Set B")
        self.btn_clear_ab = QPushButton("Clear AB")
        self.btn_record = QPushButton("⏺ Record")
        self.btn_record.setCheckable(True)
        self.btn_forensics = QPushButton("🧪 Forensics")
        self.btn_forensics.setObjectName("forensicsBtn")

        for b in [self.btn_open, self.btn_play, self.btn_stop, self.btn_record, self.btn_forensics]:
            b.setFixedHeight(36)

        r1.addWidget(self.btn_open)
        r1.addWidget(self.btn_play)
        r1.addWidget(self.btn_stop)
        r1.addStretch(1)
        r1.addWidget(QLabel("Speed:"))
        r1.addWidget(self.speed_combo)
        r1.addWidget(self.btn_loop)
        r1.addWidget(self.btn_zoom)
        r1.addWidget(self.btn_set_a)
        r1.addWidget(self.btn_set_b)
        r1.addWidget(self.btn_clear_ab)
        r1.addWidget(self.btn_ab)
        r1.addSpacing(8)
        r1.addWidget(self.btn_record)
        r1.addWidget(self.btn_forensics)

        # Row 2 - Progress and volume
        r2 = QHBoxLayout()
        r2.setSpacing(10)
        self.progress_slider = PreciseSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setRange(0, 0)
        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setFixedWidth(120)
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_slider.setFixedWidth(90)
        self.vol_label = QLabel("🔊")
        self.vol_label.setFixedWidth(24)
        self.btn_theme = QPushButton("🌙 Dark")
        self.btn_theme.setFixedHeight(36)
        r2.addWidget(self.progress_slider, stretch=1)
        r2.addWidget(self.time_label)
        r2.addWidget(self.vol_label)
        r2.addWidget(self.volume_slider)
        r2.addWidget(self.btn_theme)

        pl.addLayout(r1)
        pl.addLayout(r2)
        ml.addWidget(self.control_panel)

        # Status bar
        self.status_bar = QFrame()
        self.status_bar.setObjectName("statusBar")
        self.status_layout = QHBoxLayout(self.status_bar)
        self.status_label = QLabel("Ready — Load a video to begin forensic analysis")
        self.status_layout.addWidget(self.status_label)
        self.status_layout.setContentsMargins(16, 6, 16, 6)
        ml.addWidget(self.status_bar)

        # Connections
        self.btn_open.clicked.connect(self.open_file)
        self.btn_play.clicked.connect(self.toggle_playback)
        self.btn_stop.clicked.connect(self.stop_playback)
        self.progress_slider.sliderPressed.connect(lambda: setattr(self, 'is_user_seeking', True))
        self.progress_slider.sliderReleased.connect(self.end_seeking)
        self.volume_slider.valueChanged.connect(self.set_volume)
        self.btn_theme.clicked.connect(self.toggle_theme)
        self.speed_combo.currentTextChanged.connect(self.set_speed)
        self.btn_loop.toggled.connect(self.toggle_normal_loop)
        self.btn_ab.toggled.connect(self.toggle_ab_loop)
        self.btn_set_a.clicked.connect(self.set_a_point)
        self.btn_set_b.clicked.connect(self.set_b_point)
        self.btn_clear_ab.clicked.connect(self.clear_ab_points)
        self.btn_record.clicked.connect(self.toggle_recording)
        self.btn_zoom.toggled.connect(self.toggle_zoom)
        self.zoom_slider.level_changed.connect(self._on_zoom_level)
        self.mini_preview.selection_changed.connect(self._on_sel_changed)
        self.mini_preview.close_clicked.connect(lambda: self.btn_zoom.setChecked(False))
        self.btn_forensics.clicked.connect(self._show_forensics_menu)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def setup_media(self):
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.video_sink = QVideoSink(self)
        self.player.setVideoSink(self.video_sink)
        self.video_sink.videoFrameChanged.connect(self._on_frame)
        self.audio_output.setVolume(0.7)
        self.player.positionChanged.connect(self.update_position)
        self.player.durationChanged.connect(self.update_duration)
        self.player.playbackStateChanged.connect(self.update_play_button)

    def _on_frame(self, frame):
        if not frame.isValid():
            return
        self._frame_counter += 1
        # Reset counter to prevent overflow
        if self._frame_counter > 1000000:
            self._frame_counter = 0
        try:
            img = frame.toImage()
            if img.isNull():
                return
            self.frame_display.update_frame(img)
            if self.zoom_enabled and self._frame_counter % 2 == 0:
                self.mini_preview.update_frame(img)
            if self.motion_panel.isVisible() and self.motion_panel.detector.active:
                self.motion_panel.process_frame(img)
        except Exception:
            pass

    # ─── Forensics Menu ───
    def _show_forensics_menu(self):
        if not self.current_file:
            self.update_status("⚠️ Load a video first")
            return

        menu = QMenu(self)
        menu.setStyleSheet(MENU_DARK_QSS if self.is_dark_theme else MENU_LIGHT_QSS)

        actions = [
            ("🔍 Motion Detection (Real-time)", self._open_motion_panel),
            None,
            ("🎬 Clip Analyzer (Motion Frequency)", self._open_clip_analyzer),
            ("🔄 Scene Change Detection", self._open_scene_change),
            None,
            ("🌫️ Blur Detection", self._open_blur_detect),
            ("💡 Brightness Analysis", self._open_brightness),
            ("📊 Object Activity Counter", self._open_object_counter),
        ]

        for item in actions:
            if item is None:
                menu.addSeparator()
            else:
                act = QAction(item[0], self)
                act.triggered.connect(item[1])
                menu.addAction(act)

        menu.exec(self.btn_forensics.mapToGlobal(self.btn_forensics.rect().bottomLeft()))

    def _open_motion_panel(self):
        if not HAS_CV2:
            self.update_status("⚠️ Install OpenCV: pip install opencv-python numpy")
            return
        self.motion_panel.move(15, 15)
        self.motion_panel.show()
        self.update_status("Motion detection panel opened")

    def _open_dialog(self, dialog_class):
        d = dialog_class(self)
        d.seek_requested.connect(self._seek_to)
        d.destroyed.connect(lambda obj=d: self._remove_dialog(d))
        self._open_dialogs.append(d)
        d.show()
        return d

    def _remove_dialog(self, dialog):
        if dialog in self._open_dialogs:
            self._open_dialogs.remove(dialog)

    def _seek_to(self, ms):
        self.player.setPosition(ms)

    def _open_clip_analyzer(self):
        d = self._open_dialog(ClipAnalyzerDialog)
        self.update_status("Clip analyzer started...")

    def _open_scene_change(self):
        self._open_dialog(SceneChangeDialog)

    def _open_blur_detect(self):
        self._open_dialog(BlurDetectionDialog)

    def _open_brightness(self):
        self._open_dialog(BrightnessAnalysisDialog)

    def _open_object_counter(self):
        self._open_dialog(ObjectCounterDialog)

    # ─── Zoom ───
    def toggle_zoom(self, checked):
        self.zoom_enabled = checked
        self.frame_display.zoom_enabled = checked
        self.mini_preview.setVisible(checked)
        self.zoom_slider.setVisible(checked)
        if checked:
            self._pos_zoom()
            self._update_zoom_from_slider(self.zoom_slider.level)
        else:
            self.frame_display.set_zoom_rect(QRectF(0, 0, 1, 1))
        self.update_status("Zoom: " + ("ON" if checked else "OFF"))

    def _pos_zoom(self):
        m, g = 15, 8
        self.mini_preview.move(
            self.video_container.width() - self.mini_preview.width() - m, m
        )
        self.zoom_slider.move(
            self.mini_preview.x() - self.zoom_slider.width() - g,
            m + (self.mini_preview.height() - self.zoom_slider.height()) // 2
        )

    def _on_zoom_level(self, level):
        if self.zoom_enabled:
            self._update_zoom_from_slider(level)

    def _update_zoom_from_slider(self, level):
        rs = 1.0 - level * 0.9
        c = self.mini_preview.selection_rect
        cx = c.x() + c.width() / 2
        cy = c.y() + c.height() / 2
        nr = QRectF(
            max(0, min(1 - rs, cx - rs / 2)),
            max(0, min(1 - rs, cy - rs / 2)),
            rs, rs
        )
        self.mini_preview.set_selection(nr)
        self.frame_display.set_zoom_rect(nr)

    def _on_sel_changed(self, r):
        if self.zoom_enabled:
            self.frame_display.set_zoom_rect(r)
            lv = (1.0 - r.width()) / 0.9
            self.zoom_slider.blockSignals(True)
            self.zoom_slider.set_level(lv)
            self.zoom_slider.blockSignals(False)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if self.zoom_enabled:
            self._pos_zoom()

    # ─── Theme ───
    def apply_theme(self):
        self.setStyleSheet(DARK_QSS if self.is_dark_theme else LIGHT_QSS)
        self.video_container.setStyleSheet("background-color: #111113; border-radius: 10px;")

    def toggle_theme(self):
        self.is_dark_theme = not self.is_dark_theme
        self.btn_theme.setText("🌙 Dark" if self.is_dark_theme else "☀️ Light")
        self.apply_theme()

    # ─── Playback ───
    @staticmethod
    def format_time(ms):
        if ms < 0:
            ms = 0
        s = int(ms / 1000) % 60
        m = int(ms / 60000)
        h = int(ms / 3600000)
        return f"{h:02d}:{m:02d}:{s:02d}" if h > 0 else f"{m:02d}:{s:02d}"

    def update_position(self, pos):
        if not self.is_user_seeking:
            self.progress_slider.setValue(pos)
        if self.ab_loop_active and self.a_point != -1 and self.b_point != -1 and pos >= self.b_point:
            self.player.setPosition(self.a_point)
            return
        duration = self.player.duration()
        self.time_label.setText(f"{self.format_time(pos)} / {self.format_time(duration)}")

    def update_duration(self, d):
        self.progress_slider.setRange(0, d)
        self.time_label.setText(f"00:00 / {self.format_time(d)}")

    def toggle_playback(self):
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
        else:
            self.player.play()

    def update_play_button(self, s):
        is_playing = s == QMediaPlayer.PlaybackState.PlayingState
        self.btn_play.setText("⏸ Pause" if is_playing else "▶ Play")
        self.btn_play.setProperty("active", is_playing)
        self.btn_play.style().unpolish(self.btn_play)
        self.btn_play.style().polish(self.btn_play)

    def stop_playback(self):
        self.player.stop()
        self.progress_slider.setValue(0)

    def set_speed(self, text):
        try:
            rate = float(text.replace("x", ""))
            self.player.setPlaybackRate(rate)
        except ValueError:
            pass

    def set_volume(self, v):
        self.audio_output.setVolume(v / 100.0)
        self.vol_label.setText("🔊" if v > 0 else "🔇")

    def open_file(self):
        fp, _ = QFileDialog.getOpenFileName(
            self, "Open Video", "",
            "Video Files (*.mp4 *.avi *.mkv *.mov *.webm *.flv *.wmv)"
        )
        if fp:
            self.current_file = fp
            self.player.setSource(QUrl.fromLocalFile(fp))
            self.player.play()
            self.clear_ab_points()
            self.btn_loop.setChecked(False)
            self.update_status(f"Loaded: {os.path.basename(fp)}")

    def end_seeking(self):
        self.is_user_seeking = False
        self.player.setPosition(self.progress_slider.value())

    # ─── Loops ───
    def toggle_normal_loop(self, checked):
        self.player.setLoops(QMediaPlayer.Loops.Infinite if checked else 1)
        self.update_status("Loop: " + ("ON" if checked else "OFF"))

    def toggle_ab_loop(self, checked):
        if checked:
            if self.a_point == -1 or self.b_point == -1:
                self.btn_ab.blockSignals(True)
                self.btn_ab.setChecked(False)
                self.btn_ab.blockSignals(False)
                self.update_status("⚠️ Set A & B points first")
                return
            if self.b_point <= self.a_point:
                self.btn_ab.blockSignals(True)
                self.btn_ab.setChecked(False)
                self.btn_ab.blockSignals(False)
                self.update_status("⚠️ B must be after A")
                return
            self.ab_loop_active = True
            self.update_status(
                f"A→B Loop ON ({self.format_time(self.a_point)} → {self.format_time(self.b_point)})"
            )
            pos = self.player.position()
            if pos < self.a_point or pos >= self.b_point:
                self.player.setPosition(self.a_point)
        else:
            self.ab_loop_active = False
            self.update_status("A→B Loop: OFF")

    def set_a_point(self):
        pos = self.player.position()
        if pos > 0:
            self.a_point = pos
            if self.ab_loop_active:
                self.btn_ab.blockSignals(True)
                self.btn_ab.setChecked(False)
                self.btn_ab.blockSignals(False)
                self.ab_loop_active = False
            self.update_status(f"Point A: {self.format_time(self.a_point)}")

    def set_b_point(self):
        if self.a_point == -1:
            self.update_status("⚠️ Set A first")
            return
        pos = self.player.position()
        if pos > self.a_point:
            self.b_point = pos
            if self.ab_loop_active:
                self.btn_ab.blockSignals(True)
                self.btn_ab.setChecked(False)
                self.btn_ab.blockSignals(False)
                self.ab_loop_active = False
            self.update_status(f"Point B: {self.format_time(self.b_point)}")
        else:
            self.update_status("⚠️ B must be after A")

    def clear_ab_points(self):
        self.a_point = -1
        self.b_point = -1
        self.ab_loop_active = False
        self.btn_ab.blockSignals(True)
        self.btn_ab.setChecked(False)
        self.btn_ab.blockSignals(False)
        self.update_status("A/B cleared")

    # ─── Recording ───
    def toggle_recording(self):
        if not self.btn_record.isChecked():
            self.is_recording = False
            self.record_start = -1
            self.record_end = -1
            self.btn_record.setText("⏺ Record")
            self.update_status("Recording cancelled")
            return

        if self.record_start == -1:
            self.record_start = self.player.position()
            self.btn_record.setText("⏹ Stop & Save")
            self.update_status(f"🔴 Recording from {self.format_time(self.record_start)}")
            return

        self.record_end = self.player.position()
        self.btn_record.setChecked(False)
        self.btn_record.setText("⏺ Record")
        self.is_recording = False
        self._record_segment()

    def _record_segment(self):
        if not self.current_file or self.record_end <= self.record_start:
            self.update_status("⚠️ Invalid segment")
            return
        out, _ = QFileDialog.getSaveFileName(self, "Save", "", "MP4 (*.mp4)")
        if not out:
            return
        self.update_status("⏳ Exporting with FFmpeg...")
        cmd = [
            "ffmpeg", "-y", "-i", self.current_file,
            "-ss", self.format_time(self.record_start),
            "-to", self.format_time(self.record_end),
            "-c", "copy", out
        ]
        self.ffmpeg_process = QProcess()
        self.ffmpeg_process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.ffmpeg_process.finished.connect(self._on_ffmpeg_finished)
        self.ffmpeg_process.start(cmd[0], cmd[1:])

    def _on_ffmpeg_finished(self, exit_code, exit_status):
        if exit_code == 0:
            self.update_status("✅ Saved!")
        else:
            self.update_status("❌ Export failed. Ensure FFmpeg is installed.")
        self.ffmpeg_process = None

    def update_status(self, msg):
        self.status_label.setText(msg)

    def keyPressEvent(self, e):
        k = e.key()
        if k == Qt.Key.Key_Space:
            self.toggle_playback()
        elif k == Qt.Key.Key_Left:
            s = 1000 if e.modifiers() & Qt.KeyboardModifier.ShiftModifier else 5000
            self.player.setPosition(max(0, self.player.position() - s))
        elif k == Qt.Key.Key_Right:
            s = 1000 if e.modifiers() & Qt.KeyboardModifier.ShiftModifier else 5000
            self.player.setPosition(min(self.player.duration(), self.player.position() + s))
        elif k == Qt.Key.Key_Up:
            self.volume_slider.setValue(min(100, self.volume_slider.value() + 5))
        elif k == Qt.Key.Key_Down:
            self.volume_slider.setValue(max(0, self.volume_slider.value() - 5))
        elif k == Qt.Key.Key_Z:
            self.btn_zoom.toggle()
        elif k == Qt.Key.Key_F:
            self._open_motion_panel()
        else:
            super().keyPressEvent(e)

    def closeEvent(self, event):
        # Clean up FFmpeg process
        if self.ffmpeg_process:
            self.ffmpeg_process.terminate()
            self.ffmpeg_process.waitForFinished(3000)
            self.ffmpeg_process = None

        # Clean up dialogs
        for d in list(self._open_dialogs):
            d.close()
        self._open_dialogs.clear()

        # Stop media player
        self.player.stop()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec())