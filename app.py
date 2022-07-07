import logging
import sys
import webbrowser
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QFile, QIODevice
from PySide6.QtGui import QIcon, QTextCursor
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox, QTextEdit, QPushButton
import qdarkstyle

from helper import Helper

logging.basicConfig(
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    stream=sys.stderr,
    level=logging.INFO,
)


class LoggerHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        self.edit.textCursor().insertText(self.format(record) + '\n')
        self.edit.moveCursor(QTextCursor.End)


class Home:
    def __init__(self) -> None:
        super().__init__()

        ui_file_name = "app.ui"
        ui_file = QFile(ui_file_name)
        if not ui_file.open(QIODevice.ReadOnly):
            print(f"Cannot open {ui_file_name}: {ui_file.errorString()}")
            sys.exit(-1)

        loader = QUiLoader()
        self.window = loader.load(ui_file)
        ui_file.close()
        if not self.window:
            print(loader.errorString())
            sys.exit(-1)

        self.btn_input = self.window.findChild(QPushButton, 'btn_input')
        self.btn_output = self.window.findChild(QPushButton, 'btn_output')
        self.btn_convert = self.window.findChild(QPushButton, 'btn_convert')
        self.btn_open_dir = self.window.findChild(QPushButton, 'btn_open_dir')

        self.edit_input = self.window.findChild(QTextEdit, 'edit_input')
        self.edit_output = self.window.findChild(QTextEdit, 'edit_output')
        self.edit_logging = self.window.findChild(QTextEdit, 'edit_logging')

    def gui_logger(self):
        handler = LoggerHandler()
        formatter = logging.Formatter(
            fmt='%(asctime)s %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
        )
        handler.setFormatter(formatter)
        handler.edit = self.edit_logging
        logging.getLogger().addHandler(handler)

    def connect(self):
        # self.window.btn_input.clicked.connect(self.open_file)
        # self.window.btn_output.clicked.connect(self.save_folder)
        # self.window.btn_convert.clicked.connect(self.convert)
        self.btn_input.clicked.connect(self.open_file)
        self.btn_output.clicked.connect(self.save_folder)
        self.btn_convert.clicked.connect(self.convert)
        self.btn_open_dir.clicked.connect(self.open_dir)

    def initialize(self):
        input_str = Path('./input/testing2.xls')
        # if input_str.exists():
        #     self.window.edit_input.setPlainText(str(input_str.absolute()))
        self.edit_input.setPlainText(str(input_str.absolute()))
        output_str = Path(f"./output/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx")
        self.edit_output.setPlainText(str(output_str.absolute()))

    def open_file(self):
        filename, filetype = QFileDialog.getOpenFileName(
            self.window,
            "輸入檔案路徑",
            "./input",
            "XML Spreadsheet file (*.xls)"
        )
        self.edit_input.setPlainText(str(Path(filename).absolute()))

    def save_folder(self):
        # folder_path = QFileDialog.getExistingDirectory(self.window, "輸出檔案資料夾", "./")
        filename, filetype = QFileDialog.getSaveFileName(
            self.window,
            "輸出檔案路徑",
            './output/result.xlsx',
            "XML Spreadsheet file (*.xlsx)"
        )
        self.edit_output.setPlainText(str(Path(filename).absolute()))

    def open_dir(self):
        output_file = self.edit_output.toPlainText()
        output_path = Path(output_file)
        while not output_path.exists():
            output_path = output_path.parent
        if output_path.is_file():
            output_path = output_path.parent
        if output_path.is_dir():
            webbrowser.open(output_path)
            return
        raise Exception('03', 'open directory error')

    def convert(self):
        input_file = self.edit_input.toPlainText()
        output_file = self.edit_output.toPlainText()

        helper = Helper()
        logging.info('開始轉換')
        try:
            output_path = helper.auto_run(input_file, output_file)
        except Exception as e:
            logging.error(e)
            QMessageBox.critical(self.window, '錯誤', '轉換失敗', QMessageBox.Ok)
        else:
            logging.info('轉換完成')
            logging.info(f'輸出路徑: {output_path}')
            QMessageBox.information(self.window, '完成', '轉換完成', QMessageBox.Ok)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('./static/logo.png'))

    # setup stylesheet
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyside6', palette=qdarkstyle.LightPalette))

    home = Home()
    home.connect()
    home.initialize()
    home.gui_logger()
    home.window.show()
    sys.exit(app.exec())
