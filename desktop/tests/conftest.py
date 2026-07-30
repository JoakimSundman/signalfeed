from typing import cast

import pytest
from PySide6.QtWidgets import QApplication


@pytest.fixture(scope="session")
def qapp() -> QApplication:
    """Provide a single shared QApplication instance for all Qt-based tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return cast(QApplication, app)
