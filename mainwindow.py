# ======================================================================================================================
# Standard library imports =============================================================================================
# ======================================================================================================================

# ======================================================================================================================
# Related third party imports ==========================================================================================
# ======================================================================================================================
from PySide2.QtCore import QMetaObject
from PySide2.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QTabWidget, QTableView

# ======================================================================================================================
# Local application/library specific imports ===========================================================================
# ======================================================================================================================

# ======================================================================================================================
# Constants ============================================================================================================
# ======================================================================================================================


class UiMainWindow(object):
    def __init__(self):
        super().__init__()
        self.central_widget = None
        self.vertical_layout = None
        self.widget = None
        self.horizontal_layout = None
        self.browse_button = None
        self.file_path_edit = None
        self.tab_widget = None
        self.tab = None
        self.table_view = None

    def set_up_ui(self, main_window):
        # Set main window size
        main_window.resize(1050, 400)

        # Set window title
        main_window.setWindowTitle('Render Log Analysis')

        # Create central widget
        self.central_widget = QWidget(main_window)
        main_window.setCentralWidget(self.central_widget)

        # Create vertical layout inside central widget
        self.vertical_layout = QVBoxLayout(self.central_widget)
        # Create a widget where to display the browse section and add it to vertical layout
        self.widget = QWidget(self.central_widget)
        self.vertical_layout.addWidget(self.widget)

        # Create a horizontal layout to display the browse button and the select file on the same line
        self.horizontal_layout = QHBoxLayout(self.widget)
        # Create a browse button
        self.browse_button = QPushButton(self.central_widget)
        self.browse_button.setText('Browse File')
        # Set the browse button inside the horizontal layout
        self.horizontal_layout.addWidget(self.browse_button)

        # Create a line edit to display the browsed file
        self.file_path_edit = QLineEdit(self.central_widget)
        self.vertical_layout.addWidget(self.file_path_edit)
        self.horizontal_layout.addWidget(self.file_path_edit)

        # Create the main tab widget to dynamically add tabs later
        self.tab_widget = QTabWidget(self.central_widget)
        self.tab = QWidget()
        self.table_view = QTableView(self.tab)
        self.vertical_layout.addWidget(self.tab_widget)

        QMetaObject.connectSlotsByName(main_window)
