import sys

from PySide6.QtWidgets import QApplication, QLabel, QMainWindow


class MainWindow(QMainWindow):
    """The signalfeed desktop app's main window."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("signalfeed")
        self.setCentralWidget(QLabel("signalfeed desktop — coming soon"))


def main() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
