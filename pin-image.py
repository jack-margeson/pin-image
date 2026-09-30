#!/usr/bin/env python3
"""Pin an image to the desktop as a borderless, always-on-top window.

Usage: pin-image.py IMAGE [IMAGE ...]

  Mouse wheel         zoom in / out (anchored at the cursor)
  Left-drag           move the image
  Double-click / Esc  close
  Right-click         menu (reset zoom, copy, close)
  Ctrl+C              copy image to clipboard
  0                   reset zoom to 100%
"""
import sys

try:
    from PyQt6.QtCore import Qt, QPoint, QRect
    from PyQt6.QtGui import QPixmap, QPainter, QGuiApplication, QAction
    from PyQt6.QtWidgets import QApplication, QWidget, QMenu
except ImportError:
    from PySide6.QtCore import Qt, QPoint, QRect
    from PySide6.QtGui import QPixmap, QPainter, QGuiApplication, QAction
    from PySide6.QtWidgets import QApplication, QWidget, QMenu

MIN_SIZE = 16
ZOOM_STEP = 1.1


class PinWindow(QWidget):
    def __init__(self, path, offset=0):
        super().__init__()
        self.pixmap = QPixmap(path)
        if self.pixmap.isNull():
            raise ValueError(f"cannot load image: {path}")
        self.setWindowTitle(f"Pin - {path}")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.drag_offset = None

        # Device pixel ratio: show the screenshot at its native pixel size.
        dpr = self.devicePixelRatioF()
        self.base_w = self.pixmap.width() / dpr
        self.base_h = self.pixmap.height() / dpr

        # Start no bigger than 90% of the screen.
        avail = QGuiApplication.primaryScreen().availableGeometry()
        fit = min(1.0, avail.width() * 0.9 / self.base_w, avail.height() * 0.9 / self.base_h)
        self.scale = fit
        w, h = self.scaled_size()
        self.setGeometry(
            avail.x() + (avail.width() - w) // 2 + offset,
            avail.y() + (avail.height() - h) // 2 + offset,
            w, h,
        )

    def scaled_size(self):
        return max(MIN_SIZE, round(self.base_w * self.scale)), max(MIN_SIZE, round(self.base_h * self.scale))

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, self.scale < 1.0)
        p.drawPixmap(self.rect(), self.pixmap)
        # Thin border so the pinned image stands out from what's underneath.
        p.setPen(Qt.GlobalColor.darkGray)
        p.drawRect(self.rect().adjusted(0, 0, -1, -1))

    def set_scale(self, new_scale, anchor=None):
        """Resize, keeping the image point under `anchor` (local coords) fixed on screen."""
        old_w, old_h = self.width(), self.height()
        self.scale = max(new_scale, MIN_SIZE / min(self.base_w, self.base_h))
        w, h = self.scaled_size()
        if anchor is None:
            anchor = QPoint(old_w // 2, old_h // 2)
        fx, fy = anchor.x() / old_w, anchor.y() / old_h
        g = self.geometry()
        x = round(g.x() + anchor.x() - fx * w)
        y = round(g.y() + anchor.y() - fy * h)
        self.setGeometry(QRect(x, y, w, h))
        self.update()

    def wheelEvent(self, event):
        steps = event.angleDelta().y() / 120
        if steps:
            self.set_scale(self.scale * ZOOM_STEP ** steps, event.position().toPoint())

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            handle = self.windowHandle()
            # On Wayland, clients can't position themselves; let the compositor move us.
            if QGuiApplication.platformName() == "wayland" and handle and handle.startSystemMove():
                return
            self.drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self.drag_offset is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_offset)

    def mouseReleaseEvent(self, event):
        self.drag_offset = None

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.close()

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key.Key_Escape:
            self.close()
        elif key == Qt.Key.Key_0:
            self.set_scale(1.0)
        elif key in (Qt.Key.Key_Plus, Qt.Key.Key_Equal):
            self.set_scale(self.scale * ZOOM_STEP)
        elif key == Qt.Key.Key_Minus:
            self.set_scale(self.scale / ZOOM_STEP)
        elif key == Qt.Key.Key_C and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.copy()

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        for label, fn in (
            (f"Zoom: {self.scale * 100:.0f}% — reset to 100%", lambda: self.set_scale(1.0)),
            ("Copy image", self.copy),
            ("Close", self.close),
        ):
            action = QAction(label, menu)
            action.triggered.connect(fn)
            menu.addAction(action)
        menu.exec(event.globalPos())

    def copy(self):
        QGuiApplication.clipboard().setPixmap(self.pixmap)


def main():
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        return 1
    app = QApplication(sys.argv)
    app.setApplicationName("pin-image")
    app.setDesktopFileName("pin-image")
    windows = []
    for i, path in enumerate(sys.argv[1:]):
        try:
            win = PinWindow(path, offset=i * 30)
        except ValueError as e:
            print(e, file=sys.stderr)
            continue
        win.show()
        windows.append(win)
    if not windows:
        return 1
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
