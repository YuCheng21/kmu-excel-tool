import sys
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication


class MyWidget():
    def __init__(self):
        super().__init__()

        qfile = QFile('./ui/app.ui')
        qfile.open(QFile.ReadOnly)
        qfile.close()

        self.ui = QUiLoader().load(qfile)

        # self.ui.button.clicked.connect(self.magic)

    def magic(self):
        print('ok')


if __name__ == "__main__":
    app = QApplication([])

    widget = MyWidget()

    sys.exit(app.exec())