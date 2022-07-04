import sys

from PySide6.QtGui import QIcon
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox
from PySide6.QtCore import QFile, QIODevice

from pathlib import Path
import pandas as pd
import codebook


def run():
    input_path = window.textEdit.toPlainText()
    output_path = window.textEdit_2.toPlainText()
    file_path = Path(input_path)
    excel = pd.read_excel(file_path, sheet_name=None)
    result = {}
    for key, value in excel.items():
        sheet_name = key.split('_')
        sheet_content = pd.DataFrame(value)

        case_id = sheet_name[1]
        case_name = sheet_name[2]

        normalization = []
        drug = None
        drug_type = None
        start_date = None
        flag = None
        for index, row in sheet_content.iterrows():
            if not pd.isna(row.loc['施打藥物']) and not pd.isna(row.loc['藥物種類']) and pd.isna(row.loc['副作用']):
                drug = row.loc['藥物種類']
                drug_type = row.loc['施打藥物']
                start_date = row.loc['新增日期']
                flag = True
            elif pd.isna(row.loc['施打藥物']) and pd.isna(row.loc['藥物種類']) and not pd.isna(row.loc['副作用']):
                normalization.append([drug_type, drug, row.loc['副作用'], row.loc['新增日期'], start_date])
                flag = False
        if flag is True:
            normalization.append([drug_type, drug, None, None, start_date])
        df_norm = pd.DataFrame(normalization)

        result_difficulty = []
        result_severity = []
        for index, date in enumerate(df_norm.loc[:, 3].unique()):
            CT_DRUG = {v: None for k, v in codebook.CT_DRUG.items()}
            TT_DRUG = {v: None for k, v in codebook.TT_DRUG.items()}
            HT_DRUG = {v: None for k, v in codebook.HT_DRUG.items()}
            effect_difficulty = {v: None for k, v in codebook.effect.items()}
            effect_severity = {v: None for k, v in codebook.effect.items()}
            mask = df_norm[df_norm.loc[:, 3] == date]
            if date is None: mask = df_norm[df_norm.loc[:, 3].isnull()]
            start_date = None
            for _, row in mask.iterrows():
                start_date = row.loc[4]
                buffer_drug = row.loc[1].split('、')
                for _, item in enumerate(buffer_drug):
                    if item in codebook.CT_DRUG.values():
                        CT_DRUG[item] = {v: k for k, v in codebook.CT_DRUG.items()}[item]
                    if item in codebook.TT_DRUG.values():
                        TT_DRUG[item] = {v: k for k, v in codebook.TT_DRUG.items()}[item]
                    if item in codebook.HT_DRUG.values():
                        HT_DRUG[item] = {v: k for k, v in codebook.HT_DRUG.items()}[item]

                if type(row.loc[2]) is str:
                    buffer_effect = row.loc[2].split('、')
                    for _, item in enumerate(buffer_effect):
                        key = item.split('(')[0]
                        difficulty = item.split('(')[1].split(':')[0].split('A')[1]
                        severity = item.split('(')[1].split(':')[1].split(')')[0].split('B')[1]
                        # if key not in codebook.effect.values(): continue
                        if key not in codebook.effect.values():
                            effect_difficulty['其他'] = difficulty
                            effect_severity['其他'] = severity
                            continue
                        effect_difficulty[key] = difficulty
                        effect_severity[key] = severity
            CT_DRUG_str = ''.join(list(filter(None, CT_DRUG.values())))
            TT_DRUG_str = ''.join(list(filter(None, TT_DRUG.values())))
            HT_DRUG_str = ''.join(list(filter(None, HT_DRUG.values())))
            info = [case_id, start_date, date, CT_DRUG_str, TT_DRUG_str, HT_DRUG_str, ]
            result_difficulty.append(info + list({k: v or '0' for (k, v) in effect_difficulty.items()}.values()))
            result_severity.append(info + list({k: v or '0' for (k, v) in effect_severity.items()}.values()))

        label_base = ['ID', 'CTSDAY', 'DATE', 'CT_DRUG', 'TT_DRUG', 'HT_DRUG']
        label_1 = [
            'DS1(皮疹)', 'DS2(掉髮)', 'DS3(熱潮紅)', 'DS4(噁心嘔吐)', 'DS5(皮膚反應)', 'DS6(白血球下降)',
            'DS7(腹瀉)', 'DS8(關節痠痛)', 'DS9(疲倦)', 'DS10(周邊神經病變)', 'DS11(口腔黏膜炎)', 'DS12(手足症候群)',
            'DS13(陰道乾燥異常分泌)', 'DS14(皮膚/頭髮乾燥)', 'DS15(骨質疏鬆)', 'DS16(其他)',
        ]
        label_2 = [
            'SS1(皮疹)', 'SS2(掉髮)', 'SS3(熱潮紅)', 'SS4(噁心嘔吐)', 'SS5(皮膚反應)', 'SS6(白血球下降)',
            'SS7(腹瀉)', 'SS8(關節痠痛)', 'SS9(疲倦)', 'SS10(周邊神經病變)', 'SS11(口腔黏膜炎)', 'SS12(手足症候群)',
            'SS13(陰道乾燥異常分泌)', 'SS14(皮膚/頭髮乾燥)', 'SS15(骨質疏鬆)', 'SS16(其他)',
        ]
        df_result_difficulty = pd.DataFrame(result_difficulty)
        df_result_difficulty.columns = label_base + label_1
        df_result_severity = pd.DataFrame(result_severity)
        df_result_severity.columns = label_base + label_2
        result[f'{case_name}-{case_id}-困擾度'] = df_result_difficulty
        result[f'{case_name}-{case_id}-嚴重度'] = df_result_severity
    writer = pd.ExcelWriter(Path(output_path))
    for key, value in result.items():
        for i in range(3, 22):
            value.iloc[:, i] = pd.to_numeric(value.iloc[:, i])
        value.to_excel(writer, key, index=False)
    writer.save()
    QMessageBox.information(window, '完成', '轉換完成', QMessageBox.Ok)


def open_file():
    filename, filetype = QFileDialog.getOpenFileName(window, "輸入檔案路徑", "./input")
    window.textEdit.setText(str(Path(filename).absolute()))


def save_folder():
    # folder_path = QFileDialog.getExistingDirectory(window, "輸出檔案資料夾", "./")
    filename, filetype = QFileDialog.getSaveFileName(window, "輸出檔案路徑", './output/result.xlsx', "All Files (*)")
    window.textEdit_2.setText(str(Path(filename).absolute()))


app = QApplication(sys.argv)
app.setWindowIcon(QIcon('./ui/logo.png'))

ui_file_name = "./ui/app.ui"
ui_file = QFile(ui_file_name)
if not ui_file.open(QIODevice.ReadOnly):
    print(f"Cannot open {ui_file_name}: {ui_file.errorString()}")
    sys.exit(-1)
loader = QUiLoader()
window = loader.load(ui_file)
ui_file.close()
if not window:
    print(loader.errorString())
    sys.exit(-1)
window.pushButton.clicked.connect(open_file)
window.pushButton_2.clicked.connect(save_folder)
window.pushButton_3.clicked.connect(run)

window.textEdit.setText(str(Path('./input/2.xls').absolute()))
window.textEdit_2.setText(str(Path('./output/result.xlsx').absolute()))

window.show()

sys.exit(app.exec())
