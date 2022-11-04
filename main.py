# ======================================================================================================================
# Standard library imports =============================================================================================
# ======================================================================================================================
import sys
import re
import os

# ======================================================================================================================
# Related third party imports ==========================================================================================
# ======================================================================================================================
from PySide2 import QtGui, QtWidgets

# ======================================================================================================================
# Local application/library specific imports ===========================================================================
# ======================================================================================================================
from mainwindow import UiMainWindow

# ======================================================================================================================
# Constants ============================================================================================================
# ======================================================================================================================
RENDER_TIME_REGEX = r'render done in (.*)$'
MEMORY_USAGE_REGEX = r'\d{2}\:\d{2}\:\d{2}\ +\d+MB\ +\|'
TIME_ELAPSED_REGEX = r'(\d{2}\:\d{2}\:\d{2})\ +\d+MB'
MEMORY_USAGE_TIME_REGEX = r'\d{2}\:\d{2}\:\d{2}\ +(\d+MB)'
WARNING_REGEX = r'WARNING(.*)'
ERROR_REGEX = r'ERROR(.*)'


class LogBrowserModel(QtGui.QStandardItemModel):
    """ Define the model for data manipulation. """

    def __init__(self):
        super().__init__()
        self._raw_log = []
        self._render_time = None
        self._memory_usage = {}
        self._warnings = []
        self._errors = []

    @property
    def render_time(self):
        return self._render_time

    @render_time.setter
    def render_time(self, render_time):
        self._render_time = render_time

    @property
    def memory_usage(self):
        return self._memory_usage

    @memory_usage.setter
    def memory_usage(self, memory_usage):
        self._memory_usage = memory_usage

    @property
    def raw_log(self):
        return self._raw_log

    @raw_log.setter
    def raw_log(self, raw_log):
        self._raw_log = raw_log

    @property
    def warnings(self):
        return self._warnings

    @warnings.setter
    def warnings(self, warnings):
        self._warnings = warnings

    @property
    def errors(self):
        return self._errors

    @errors.setter
    def errors(self, errors):
        self._errors = errors

    def reset_data(self):
        """ Reset stored data. """

        self.raw_log = []
        self.render_time = None
        self.memory_usage = {}
        self.warnings = []
        self.errors = []

    def store_raw_log(self, file_path):
        """
        Extract and store raw render log from a given file path.

        :param file_path: File path to extract log from
        :type file_path: str
        """
        with open(file_path, 'r') as openFile:
            self.raw_log = openFile.readlines()

    @staticmethod
    def extract_regex_match(regex, string, group_index):
        """
        Extract regex match from a given string

        :param regex: Specific regex to look for
        :type regex: re.Match object
        :param string: String where to search for a match
        :type string: str
        :param group_index: Index of the match group to be returned
        :type group_index: int
        :return: str
        """

        match = re.search(regex, string)
        if match:
            return match.group(group_index)

    def parse_log(self):
        """ Parse the raw render log. """

        # Analyze every line of the extracted information
        for line in self.raw_log:
            # Look for render time
            render_time = self.extract_regex_match(regex=RENDER_TIME_REGEX, string=line, group_index=1)
            if render_time:
                self.render_time = render_time

            # Gather memory usage
            memory_usage = self.extract_regex_match(regex=MEMORY_USAGE_REGEX, string=line, group_index=0)
            if memory_usage:
                time_elapsed = self.extract_regex_match(regex=TIME_ELAPSED_REGEX,
                                                        string=memory_usage,
                                                        group_index=1)
                if not self.memory_usage.get(time_elapsed):
                    memory_usage_time = self.extract_regex_match(MEMORY_USAGE_TIME_REGEX,
                                                                 string=memory_usage,
                                                                 group_index=1)
                    if memory_usage_time:
                        self.memory_usage[time_elapsed] = memory_usage_time

            # Look for warnings
            warning = self.extract_regex_match(regex=WARNING_REGEX, string=line, group_index=0)
            if warning:
                self.warnings.append(warning)

            # Look for errors
            error = self.extract_regex_match(regex=ERROR_REGEX, string=line, group_index=0)
            if error:
                self.errors.append(error)


class MainWindow(QtWidgets.QMainWindow, UiMainWindow):
    """ Define the main window object. """
    def __init__(self):
        super().__init__()

        self.set_up_ui(self)
        self.model = LogBrowserModel()
        self.table_view.setModel(self.model)
        self.browse_button.pressed.connect(self.browse_on_click)
        self.file_path_edit.returnPressed.connect(self.browse_on_key_pressed)

    def clean_window_and_stored_data(self):
        """ Clean previously loaded data. """

        # Clean UI
        tabs_count = self.tab_widget.count()
        for index in range(tabs_count):
            self.tab_widget.removeTab(0)
        self.file_path_edit.setStyleSheet('QLineEdit'
                                          '{'
                                          'background : white;'
                                          '}')

        # Clean stored information
        self.model.reset_data()

    def wrong_file_path(self):
        """ Warn user about a wrong file path. """

        # Init tab
        error_tab = self.new_tab(tab_name='ERROR', tab_title_color='red')
        self.add_text_to_widget(widget=error_tab, text='Please select an existing .log file', text_color='red')
        self.file_path_edit.setStyleSheet('QLineEdit'
                                          '{'
                                          'background : red;'
                                          '}')

    def set_tabs(self, file_path):
        """
        Set all tabs.

        :param file_path: The file path to retrieve information from
        :type file_path: str
        """
        # Display the selected file path inside the search bar
        self.file_path_edit.setText(file_path)

        # Load and store raw information
        self.model.store_raw_log(file_path)

        # Grab information from selected file
        self.model.parse_log()

        # Create tabs dynamically depending on parsing results
        self.set_render_time_tab()
        self.set_memory_usage_tab()
        self.set_warnings_tab()
        self.set_errors_tab()

    def browse_on_key_pressed(self):
        """ Browse log file in order to display their information when pressing enter key. """

        # Clean window and stored data from previously browsed file
        self.clean_window_and_stored_data()

        # Select file (restrict to .log files)
        file_path = self.file_path_edit.text()
        if not (os.path.exists(file_path) and os.path.splitext(file_path)[1] == '.log'):
            self.wrong_file_path()
            return

        # Generate tabs
        self.set_tabs(file_path)

    def browse_on_click(self):
        """ Browse log file in order to display their information when selecting a file from the file browser. """

        # Clean window and stored data from previously browsed file
        self.clean_window_and_stored_data()

        # Select file (restrict to .log files)
        file_paths = QtWidgets.QFileDialog.getOpenFileName(self, 'Select File', os.sep, 'Logs (*.log)')
        if not file_paths[0]:
            return

        # Generate tabs
        self.set_tabs(file_paths[0])

    def new_table(self, tab_name, hide_vertical_header=False, hide_horizontal_header=False, show_grid=False,
                  tab_title_color=None):
        """
        Generate a new QTableWidget element.

        :param tab_name: The tab name
        :type tab_name: str
        :param hide_vertical_header: Hide the vertical header information
        :type hide_vertical_header: bool
        :param hide_horizontal_header: Hide the horizontal header information
        :type hide_horizontal_header: bool
        :param show_grid: Show the table grid
        :type show_grid: bool
        :param tab_title_color: Set a specific color to the tab title
        :type tab_title_color: str
        :return: QtWidgets.QTableWidget, QtWidgets.QTableView, QtGui.QStandardItemModel
        """

        # Init new table
        new_table = QtWidgets.QTableWidget()

        # Create a table view for dynamic information display
        table_view = QtWidgets.QTableView(new_table)
        if hide_vertical_header:
            table_view.verticalHeader().hide()
        if hide_horizontal_header:
            table_view.horizontalHeader().hide()
        if show_grid:
            table_view.setShowGrid(True)

        # Insert inside a layout for display
        vertical_layout = QtWidgets.QVBoxLayout(new_table)
        vertical_layout.addWidget(table_view)

        # Set table view model for dynamic information
        model = QtGui.QStandardItemModel()
        table_view.setModel(model)

        # Add tab to widget
        self.tab_widget.addTab(new_table, "")
        self.tab_widget.setTabText(self.tab_widget.indexOf(new_table), tab_name)
        if tab_title_color:
            self.tab_widget.tabBar().setTabTextColor(self.tab_widget.indexOf(new_table), QtGui.QColor(tab_title_color))

        return new_table, table_view, model

    def new_tab(self, tab_name, tab_title_color=None):
        """
        Generate a new QTabWidget element.
        
        :param tab_name: Name of the tab
        :type tab_name: str
        :param tab_title_color: Set a specific color to the tab title
        :type tab_title_color: str
        :return: QtWidgets.QTabWidget object
        """

        # Init tab
        new_tab = QtWidgets.QTabWidget()

        # Add tab to main widget
        self.tab_widget.addTab(new_tab, "")

        # Name tab
        self.tab_widget.setTabText(self.tab_widget.indexOf(new_tab), tab_name)
        if tab_title_color:
            self.tab_widget.tabBar().setTabTextColor(self.tab_widget.indexOf(new_tab), QtGui.QColor(tab_title_color))

        return new_tab

    @staticmethod
    def add_text_to_widget(widget, text, text_color=None):
        """Add text to a specific widget.

        :param widget: widget where to add the text
        :type widget: QtWidgets.QTabWidget, QtWidgets.QTableWidget
        :param text: Text to be added
        :type text: str
        :param text_color: Color of the text
        :type text_color: str
        """
        # Init a layout from the new tab for display purpose
        vertical_layout = QtWidgets.QVBoxLayout(widget)

        # Init a text edit widget for information display
        text_edit = QtWidgets.QTextEdit(widget)
        if text_color:
            text_edit.setTextColor(QtGui.QColor(text_color))
        text_edit.setText(text)

        # Add text widget to layout
        vertical_layout.addWidget(text_edit)

    def set_render_time_tab(self):
        """ Create the render time sub-widget tab. """

        if not self.model.render_time:
            return

        # Init render tab
        render_tab = self.new_tab(tab_name='Render Time')

        # Add information
        self.add_text_to_widget(widget=render_tab, text='Render done in: {}'.format(self.model.render_time))

    def set_memory_usage_tab(self):
        """ Add the memory usage sub-widget tab. """

        if not self.model.memory_usage:
            return

        # Init memory usage table
        memory_usage_tab, memory_usage_table_view, model = self.new_table(tab_name='Memory Usage',
                                                                          hide_vertical_header=True)

        # Sort time tags to display them chronologically
        time_elapsed_list = sorted(self.model.memory_usage.keys())
        model.setHorizontalHeaderLabels(['Time Elapsed', 'Memory usage at that stage'])
        for time_elapsed in time_elapsed_list:
            memory_usage = self.model.memory_usage.get(time_elapsed)
            model.appendRow([QtGui.QStandardItem(time_elapsed), QtGui.QStandardItem(memory_usage)])
        memory_usage_table_view.resizeColumnsToContents()

    def set_warnings_tab(self):
        """ Add the warnings sub-widget tab. """

        if not self.model.warnings:
            return

        # Create tab
        warning_tab, table_view, model = self.new_table(tab_name='Warnings ({})'.format(len(self.model.warnings)),
                                                        hide_vertical_header=True,
                                                        hide_horizontal_header=True,
                                                        tab_title_color='orange')
        # Add information
        for warning in self.model.warnings:
            model.appendRow([QtGui.QStandardItem(warning)])
        table_view.resizeColumnsToContents()

        # Set warning icon
        self.set_icon('SP_MessageBoxWarning', self.tab_widget.indexOf(warning_tab))

    def set_errors_tab(self):
        """ Add the errors sub-widget tab. """

        if not self.model.errors:
            return

        # Create tab
        errors_tab, table_view, model = self.new_table(tab_name='Errors ({})'.format(len(self.model.errors)),
                                                       hide_vertical_header=True,
                                                       hide_horizontal_header=True,
                                                       tab_title_color='red')
        # Add information
        for error in self.model.errors:
            model.appendRow([QtGui.QStandardItem(error)])
        table_view.resizeColumnsToContents()

        # Set error icon
        self.set_icon('SP_MessageBoxCritical', self.tab_widget.indexOf(errors_tab))

    def set_icon(self, icon_name, tab_index):
        """
        Add an icon to a specific tab.

        :param icon_name: name of the icon (from Qts Built-in Icons)
        :type icon_name: str
        :param tab_index: Target tab index
        :type tab_index: int
        """
        icon_style = getattr(QtWidgets.QStyle, icon_name)
        icon = self.tab_widget.style().standardIcon(icon_style)
        self.tab_widget.setTabIcon(tab_index, icon)


app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()
