from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QPlainTextEdit, QComboBox, QCheckBox, QSplitter, QListWidget, QListWidgetItem, QLabel
from PySide6.QtCore import Qt
from core import http_client, request_builder,history_data
from urllib.parse import urlsplit
from PySide6.QtGui import QColor, QBrush

class MainWindow(QMainWindow): # another calss that inherits QMainWindow (for more customization)
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Burp-lite Request Lab") # title
        self.resize(1300, 700) # window size

        self.setStyleSheet("""
            QMainWindow {
                background-color: #14161a;
            }
            QWidget {
                background-color: #14161a;
                color: #e8d986;
                font-size: 13px;
            }
            QPlainTextEdit, QLineEdit, QListWidget, QComboBox {
                background-color: #24262b;
                color: #e8d986;
                border: 1px solid #34363c;
                border-radius: 6px;
                padding: 6px;
                selection-background-color: #4a4530;
                selection-color: #fff3b0;
            }
            QPlainTextEdit:focus, QLineEdit:focus, QComboBox:focus {
                border: 1px solid #6b6440;
            }
            QPushButton {
                background-color: #2c2f36;
                color: #e8d986;
                border: 1px solid #3a3d44;
                border-radius: 6px;
                padding: 6px 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #3a3d44;
                border: 1px solid #6b6440;
            }
            QPushButton:pressed {
                background-color: #22242a;
            }
            QCheckBox {
                color: #cfc8a0;
                spacing: 6px;
            }
            QListWidget::item:selected {
                background-color: #3a3620;
                color: #fff3b0;
            }
            QComboBox QAbstractItemView {
                background-color: #24262b;
                color: #e8d986;
                selection-background-color: #3a3620;
            }
            QListWidget::item {
                padding: 5px;
                margin-top: 2px;
            }
            QLabel {
                color: #8a8468;
                font-size: 11px;
            }
            QToolTip {
                background-color: #1e2028;
                color: #e8d986;
                border: 1px solid #3a3d44;
                border-radius: 4px;
                padding: 6px;
                font-size: 11px;
            }
        """)

        # central widget & main layout
        self.central = QWidget() # central widget
        self.mainLayout = QVBoxLayout()
        self.mainLayout.setContentsMargins(10, 10, 10, 10)
        self.mainLayout.setSpacing(8)
        self.central.setLayout(self.mainLayout)
        self.setCentralWidget(self.central)

        # splitter (history list | right panel)
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setSizes([260, 1080])

        # history header and reset
        self.historyContainer = QWidget()
        self.historyLayout = QVBoxLayout()
        self.historyContainer.setLayout(self.historyLayout)

        self.historyContainer.setMinimumWidth(180)
        self.historyContainer.setMaximumWidth(300)

        self.historyHeader = QHBoxLayout()
        self.historyLabel = QLabel("History")
        self.clearButton = QPushButton("Clear")

        self.historyLayout.setContentsMargins(0, 0, 0, 0)
        self.historyLayout.setSpacing(6)

        self.historyHeader.addWidget(self.historyLabel)
        self.historyHeader.addStretch()
        self.historyHeader.addWidget(self.clearButton)

        self.historyList = QListWidget()
        self.historyList.setSpacing(1)
        self.historyList.setUniformItemSizes(True)
        self.historyList.setMinimumWidth(180)
        self.historyList.setMaximumWidth(300)

        self.historyLayout.addLayout(self.historyHeader)
        self.historyLayout.addWidget(self.historyList)
        self.splitter.addWidget(self.historyContainer)

        self.rightPanel = QWidget()
        self.rightLayout = QVBoxLayout()
        self.rightLayout.setContentsMargins(8, 8, 8, 8)
        self.rightLayout.setSpacing(6)
        self.rightPanel.setLayout(self.rightLayout)
        self.splitter.addWidget(self.rightPanel)

        # top bar (method, url, send button)
        self.urlMethod = QComboBox()
        self.urlMethod.addItem('GET')
        self.urlMethod.addItem('POST')
        self.urlMethod.addItem('PUT')
        self.urlMethod.addItem('PATCH')
        self.urlMethod.addItem('HEAD')
        self.urlMethod.addItem('DELETE')

        self.urlInput = QLineEdit()
        self.urlInput.setPlaceholderText("https://example.com")

        self.sendButton = QPushButton()
        self.sendButton.setText("Send")

        topBar = QHBoxLayout()
        topBar.setSpacing(8)
        topBar.addWidget(self.urlMethod)
        topBar.addWidget(self.urlInput)
        topBar.addWidget(self.sendButton)

        # quick bar (checkboxes)
        self.autoHostSync = QCheckBox("Auto Host Sync")
        self.autoHostSync.setChecked(True)
        self.followRedirects = QCheckBox("Follow Redirects")
        self.followRedirects.setChecked(False)

        quickBar = QHBoxLayout()
        quickBar.setSpacing(8)
        quickBar.addWidget(self.autoHostSync)
        quickBar.addWidget(self.followRedirects)
        quickBar.addStretch()

        # request/response editors
        self.reqLabel = QLabel("Request")
        self.reqEditor = QPlainTextEdit()
        self.respLabel = QLabel("Response")
        self.respEditor = QPlainTextEdit()
        self.respEditor.setReadOnly(True)
        self.first_render = True

        # assemble layouts
        self.mainLayout.addLayout(topBar)
        self.mainLayout.addLayout(quickBar)
        self.mainLayout.addWidget(self.splitter)
        self.rightLayout.addWidget(self.reqEditor)
        self.rightLayout.addWidget(self.respEditor)
        self.rightLayout.addWidget(self.reqLabel)
        self.rightLayout.addWidget(self.reqEditor)
        self.rightLayout.addWidget(self.respLabel)
        self.rightLayout.addWidget(self.respEditor)

        # signal/slot connections
        self.urlInput.editingFinished.connect(self.update_host_header)
        self.sendButton.clicked.connect(self.send_request)
        self.urlMethod.currentTextChanged.connect(self.update_method)
        self.historyList.itemClicked.connect(self.load_history)
        self.clearButton.clicked.connect(self.clear_history)

    def send_request(self):
        url = self.urlInput.text()
        if not url.strip():
            return
        if not url.startswith("http://") and not url.startswith("https://"):
            url = f'https://{url}'
        method = self.urlMethod.currentText()
        self.display_request(method, url)
        print("[i]sending request:", method , "-->", url)

        self.update_host_header()
        currentReqeditorText = self.reqEditor.toPlainText()
        print(currentReqeditorText)
        result = http_client.send_request(method, url, currentReqeditorText, self.followRedirects.isChecked())
        self.display_results(result)
        self.refresh_history()
        
    def display_results(self, result):
        if not result["success"]:
            self.respEditor.setPlainText("Request was NOT Successful.\n")
            self.respEditor.appendPlainText(f'Error/Reason: {result["error"]}')
        else:
            self.respEditor.setPlainText(f'{result["url"]} {result["status"]} {result["reason"]} \n')
            for key, val in result["headers"].items():
                self.respEditor.appendPlainText(f'{key} : {val}')
            self.respEditor.appendPlainText("\n")
            self.respEditor.appendPlainText(f'{result["body"]}')

            self.respEditor.appendPlainText("\n")
            self.respEditor.appendPlainText(f'total elapsed time: {result["timeElapsed"]}')
    
    def display_request(self, method, url):
        if self.first_render:
            req = request_builder.build_request(method, url)
            self.reqEditor.setPlainText(req)
            self.first_render = False
        
    def update_method(self, method):
        text = self.reqEditor.toPlainText()

        if not text.strip():
            return

        lines = text.split("\n")

        parts = lines[0].split(" ", 2)

        if len(parts) == 3:
            parts[0] = method
            lines[0] = " ".join(parts)

        self.reqEditor.setPlainText("\n".join(lines))

    def update_host_header(self):
        if not self.autoHostSync.isChecked():
            return
        text = self.reqEditor.toPlainText()

        if not text.strip():
            return

        url = self.urlInput.text().strip()

        if not url:
            return

        if not url.startswith(("http://", "https://")):
            url = f'https://{url}'

        host = urlsplit(url).netloc

        lines = text.split("\n")

        for i, line in enumerate(lines):
            if line.startswith("Host:"):
                lines[i] = f"Host: {host}"
                break

        self.reqEditor.setPlainText("\n".join(lines))

    def refresh_history(self):
        self.historyList.clear()

        for index, item in enumerate(history_data.HISTORY):
            data = f'{item["method"]}  {item["url"]}  {item["status"]}'
            listItem = QListWidgetItem(data)
            listItem.setData(Qt.UserRole, index)  # Qt.UserRole is a special place to store arbitrary data for each item.

            # set color
            color = self.get_hist_color(item["status"])
            listItem.setBackground(QBrush(QColor(color)))

            # tooltip
            path = urlsplit(item["url"]).path
            if not path:
                path = "/"

            time_ms = round(item["timeElapsed"] * 1000)

            tooltip = (
                f'{item["method"]} {path}\n\n'
                f'Status : {item["status"]}\n'
                f'Size   : {item["size"]} B\n'
                f'Time   : {time_ms} ms'
            )

            listItem.setToolTip(tooltip)

            self.historyList.addItem(listItem)

    def load_history(self, item):
        index = item.data(Qt.UserRole)
        data = history_data.HISTORY[index]

        self.urlInput.setText(data["url"])
        self.urlMethod.setCurrentText(data["method"])
        self.reqEditor.setPlainText(data["raw_request"])

    def clear_history(self):
        history_data.HISTORY.clear()
        self.refresh_history()

    def get_hist_color(self, stc):
        try:
            status = int(stc)
        except Exception:
            return "#2a2c31"

        if 200 <= status < 300:
            return "#1a3a2a"   # muted green
        elif 300 <= status < 400:
            return "#1a2a3a"   # muted blue
        elif 400 <= status < 500:
            return "#3a2a1a"   # muted orange
        elif 500 <= status < 600:
            return "#3a1a1a"   # muted red
        else:
            return "#2a2c31"   # default dark