import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget,
    QTreeWidget, QTreeWidgetItem, QLabel, QProgressBar, QFileDialog, QMessageBox, QHeaderView
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

from zip_analyzer import ZipAnalyzer

class IndexingThread(QThread):
    progress = pyqtSignal(int, str)
    finished_signal = pyqtSignal()

    def __init__(self, root_path, analyzer):
        super().__init__()
        self.root_path = root_path
        self.analyzer = analyzer

    def run(self):
        self.analyzer.index_drive(self.root_path)
        self.analyzer.analyze_zip_files()
        self.analyzer.find_potential_extractions()
        self.finished_signal.emit()

class ZipManagerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.analyzer = ZipAnalyzer()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('ZIP Analyzer')
        self.setGeometry(100, 100, 800, 600)
        main_layout = QVBoxLayout()

        drive_layout = QHBoxLayout()
        self.path_label = QLabel("Select drive to analyze:")
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.browse_directory)
        drive_layout.addWidget(self.path_label)
        drive_layout.addWidget(self.browse_button)
        main_layout.addLayout(drive_layout)

        self.progress_bar = QProgressBar()
        self.progress_status = QLabel("Ready")
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.progress_status)

        self.scan_button = QPushButton("Start Scan")
        self.scan_button.clicked.connect(self.start_scan)
        main_layout.addWidget(self.scan_button)

        self.results_tree = QTreeWidget()
        self.results_tree.setHeaderLabels(["ZIP File", "Extracted Location", "Confidence"])
        self.results_tree.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        main_layout.addWidget(self.results_tree)

        self.delete_button = QPushButton("Delete Selected ZIP Files")
        self.delete_button.clicked.connect(self.delete_selected)
        self.delete_button.setEnabled(False)
        main_layout.addWidget(self.delete_button)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory to Scan")
        if directory:
            self.path_label.setText(f"Selected: {directory}")
            self.selected_directory = directory

    def start_scan(self):
        if not hasattr(self, 'selected_directory'):
            QMessageBox.warning(self, "Warning", "Please select a directory first")
            return
        self.progress_bar.setValue(0)
        self.scan_button.setEnabled(False)
        self.results_tree.clear()
        self.index_thread = IndexingThread(self.selected_directory, self.analyzer)
        self.index_thread.finished_signal.connect(self.scan_finished)
        self.index_thread.start()

    def scan_finished(self):
        redundant_zips = self.analyzer.get_redundant_zips()
        for zip_path, extracted_dir, confidence in redundant_zips:
            item = QTreeWidgetItem([
                zip_path,
                extracted_dir,
                f"{confidence:.2f}",
            ])
            item.setCheckState(0, Qt.Unchecked)
            self.results_tree.addTopLevelItem(item)
        self.scan_button.setEnabled(True)
        self.delete_button.setEnabled(True)
        self.progress_status.setText(f"Found {len(redundant_zips)} redundant ZIP files")

    def delete_selected(self):
        selected_paths = []
        root = self.results_tree.invisibleRootItem()
        for i in range(root.childCount()):
            item = root.child(i)
            if item.checkState(0) == Qt.Checked:
                selected_paths.append(item.text(0))
        if not selected_paths:
            QMessageBox.information(self, "Information", "No ZIP files selected")
            return
        confirm = QMessageBox.question(self, "Confirm Deletion",
                                     f"Delete {len(selected_paths)} ZIP files?",
                                     QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            self.analyzer.delete_redundant_zips(selected_paths)
            QMessageBox.information(self, "Success", f"Deleted {len(selected_paths)} ZIP files")
            self.update_tree_after_deletion(selected_paths)

    def update_tree_after_deletion(self, deleted_paths):
        root = self.results_tree.invisibleRootItem()
        for i in range(root.childCount()-1, -1, -1):
            item = root.child(i)
            if item.text(0) in deleted_paths:
                root.removeChild(item)

def main():
    app = QApplication(sys.argv)
    window = ZipManagerApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()