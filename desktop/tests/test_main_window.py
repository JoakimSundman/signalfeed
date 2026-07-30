from app.main import MainWindow
from PySide6.QtWidgets import QApplication


def test_main_window_has_correct_title(qapp: QApplication) -> None:
    window = MainWindow()
    assert window.windowTitle() == "signalfeed"
