import sys
import logging
from datetime import datetime
from pathlib import Path

from PySide6.QtGui import QIcon, QTextCursor
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox
from PySide6.QtCore import QFile, QIODevice

from app_helper import AppHelper

logging.basicConfig(
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    stream=sys.stderr,
    level=logging.INFO,
)


class GuiLogger(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        self.edit.textCursor().insertText(self.format(record) + '\n')
        self.edit.moveCursor(QTextCursor.End)


class Home:
    def __init__(self) -> None:
        super().__init__()

        ui_file_name = "./ui/app.ui"
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

    def gui_logger(self):
        handler = GuiLogger()
        formatter = logging.Formatter(
            fmt='%(asctime)s %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
        )
        handler.setFormatter(formatter)
        handler.edit = self.window.edit_logging
        logging.getLogger().addHandler(handler)

    def connect(self):
        self.window.btn_input.clicked.connect(self.open_file)
        self.window.btn_output.clicked.connect(self.save_folder)
        self.window.btn_convert.clicked.connect(self.convert)

    def initialize(self):
        input_str = Path('./input/testing2.xls')
        # if input_str.exists():
        #     self.window.edit_input.setText(str(input_str.absolute()))
        self.window.edit_input.setText(str(input_str.absolute()))
        output_str = Path(f"./output/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx")
        self.window.edit_output.setText(str(output_str.absolute()))

    def open_file(self):
        filename, filetype = QFileDialog.getOpenFileName(
            self.window,
            "輸入檔案路徑",
            "./input",
            "XML Spreadsheet file (*.xls)"
        )
        self.window.edit_input.setText(str(Path(filename).absolute()))

    def save_folder(self):
        # folder_path = QFileDialog.getExistingDirectory(self.window, "輸出檔案資料夾", "./")
        filename, filetype = QFileDialog.getSaveFileName(
            self.window,
            "輸出檔案路徑",
            './output/result.xlsx',
            "XML Spreadsheet file (*.xlsx)"
        )
        self.window.edit_output.setText(str(Path(filename).absolute()))

    def convert(self):
        input_file = self.window.edit_input.toPlainText()
        output_file = self.window.edit_output.toPlainText()

        app_helper = AppHelper()
        logging.info('開始轉換')
        try:
            output_path = app_helper.auto_run(input_file, output_file)
        except Exception as e:
            logging.error(e)
            QMessageBox.critical(self.window, '錯誤', '轉換失敗', QMessageBox.Ok)
        else:
            logging.info('轉換完成')
            logging.info(f'輸出路徑: {output_path}')
            QMessageBox.information(self.window, '完成', '轉換完成', QMessageBox.Ok)

    def test(self):
        self.window.edit_logging.setText('ok')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('./ui/logo.png'))
    home = Home()
    home.connect()
    home.initialize()
    home.gui_logger()
    home.window.show()
    sys.exit(app.exec())
