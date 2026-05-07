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

    # Set activation policy - must be done before any windows are shown
    if sys.platform == "darwin":
        try:
            import AppKit
            ns_app = AppKit.NSApplication.sharedApplication()
            # Accessory policy - no dock icon, shouldn't activate
            ns_app.setActivationPolicy_(AppKit.NSApplicationActivationPolicyAccessory)
        except Exception as e:
            print(f"Failed to set activation policy: {e}")

    assets_dir = os.path.join(os.path.dirname(__file__), "assets")

    # Create pet overlay
    overlay = PetOverlay(assets_dir)

    # On macOS, show window with a delay to avoid activation
    if sys.platform == "darwin":
        from PyQt6.QtCore import QTimer
        def delayed_show():
            overlay.show()
            # Re-activate the previously active app
            try:
                import AppKit
                front_app = AppKit.NSWorkspace.sharedWorkspace().frontmostApplication()
                if front_app:
                    front_app.activateWithOptions_(AppKit.NSApplicationActivateIgnoringOtherApps)
            except Exception:
                pass
        QTimer.singleShot(100, delayed_show)
    else:
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

    reset_action = QAction("Reset to Default Cat", menu)
    reset_action.triggered.connect(lambda: overlay.reload_sprites())
    menu.addAction(reset_action)

    menu.addSeparator()

    quit_action = QAction("Exit", menu)
    quit_action.triggered.connect(app.quit)
    menu.addAction(quit_action)

    tray.setContextMenu(menu)
    tray.setToolTip("Desktop Pet Cat")
    tray.show()

    sys.exit(app.exec())


def _upload_photo(overlay):
    """Open file dialog, extract colors, recolor templates, reload sprites."""
    from PyQt6.QtWidgets import QFileDialog
    path, _ = QFileDialog.getOpenFileName(
        None, "Select Cat Photo", "", "Images (*.png *.jpg *.jpeg *.bmp)"
    )
    if path:
        from customization.importer import process_cat_photo
        assets_dir = os.path.join(os.path.dirname(__file__), "assets")
        cache_dir = process_cat_photo(path, assets_dir)
        overlay.reload_sprites(cache_dir)


if __name__ == "__main__":
    main()
