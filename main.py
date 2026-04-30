"""Desktop Pet Cat — Entry point."""

import sys
import os

from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QAction
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPolygon

from pet.overlay import PetOverlay


def make_tray_icon():
    """Create a simple cat-face icon for the system tray."""
    px = QPixmap(32, 32)
    px.fill(Qt.GlobalColor.transparent)
    p = QPainter(px)
    p.setBrush(QColor("#666666"))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawEllipse(4, 8, 24, 20)
    # Ears
    p.drawPolygon(QPolygon([QPoint(6, 10), QPoint(2, 0), QPoint(14, 8)]))
    p.drawPolygon(QPolygon([QPoint(26, 10), QPoint(30, 0), QPoint(18, 8)]))
    # Eyes
    p.setBrush(QColor("white"))
    p.drawEllipse(9, 13, 6, 5)
    p.drawEllipse(19, 13, 6, 5)
    p.setBrush(QColor("black"))
    p.drawEllipse(11, 14, 3, 3)
    p.drawEllipse(21, 14, 3, 3)
    p.end()
    return QIcon(px)


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    assets_dir = os.path.join(os.path.dirname(__file__), "assets")

    # Create pet overlay
    overlay = PetOverlay(assets_dir)
    overlay.show()

    # System tray
    tray = QSystemTrayIcon(make_tray_icon(), app)

    menu = QMenu()

    toggle_action = QAction("Hide Pet", menu)
    def toggle_pet():
        if overlay._user_hidden:
            overlay.set_user_hidden(False)
            toggle_action.setText("Hide Pet")
        else:
            overlay.set_user_hidden(True)
            toggle_action.setText("Show Pet")
    toggle_action.triggered.connect(toggle_pet)
    menu.addAction(toggle_action)

    upload_action = QAction("Upload Cat Photo...", menu)
    upload_action.triggered.connect(lambda: _upload_photo(overlay))
    menu.addAction(upload_action)

    menu.addSeparator()

    quit_action = QAction("Exit", menu)
    quit_action.triggered.connect(app.quit)
    menu.addAction(quit_action)

    tray.setContextMenu(menu)
    tray.setToolTip("Desktop Pet Cat")
    tray.show()

    sys.exit(app.exec())


def _upload_photo(overlay):
    """Open file dialog to upload a cat photo (stub for Phase 3)."""
    from PyQt6.QtWidgets import QFileDialog
    path, _ = QFileDialog.getOpenFileName(
        None, "Select Cat Photo", "", "Images (*.png *.jpg *.jpeg *.bmp)"
    )
    if path:
        print(f"[TODO] Process cat photo: {path}")
        # Phase 3: will call customization pipeline here


if __name__ == "__main__":
    main()
