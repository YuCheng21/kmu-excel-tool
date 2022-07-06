from datetime import datetime
from pathlib import Path
import pandas as pd
import codebook


def read_file(input_file):
    input_path = Path(input_file)
    if not input_path.exists():
        raise Exception('00', 'input path not exists')
    return pd.read_excel(input_path, sheet_name=None)


class AppHelper:
    def __init__(self) -> None:
        super().__init__()
        self.case_name = None
        self.case_id = None
        self.result = None
        self.df_normalization = None
        self.input_excel = None

    def normalize(self, key, value):
        sheet_name = key.split('_')
        sheet_content = pd.DataFrame(value)

        self.case_id = sheet_name[1]
        self.case_name = sheet_name[2]

        normal = []
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
                normal.append([drug_type, drug, row.loc['副作用'], row.loc['新增日期'], start_date])
                flag = False
        if flag is True:
            normal.append([drug_type, drug, None, None, start_date])
        return pd.DataFrame(normal)

    def flatten(self):
        result_difficulty = []
        result_severity = []
        for index, date in enumerate(self.df_normalization.loc[:, 3].unique()):
            CT_DRUG = {v: None for k, v in codebook.CT_DRUG.items()}
            TT_DRUG = {v: None for k, v in codebook.TT_DRUG.items()}
            HT_DRUG = {v: None for k, v in codebook.HT_DRUG.items()}
            effect_difficulty = {v: None for k, v in codebook.effect.items()}
            effect_severity = {v: None for k, v in codebook.effect.items()}

            mask = self.df_normalization[self.df_normalization.loc[:, 3] == date]
            if date is None:
                mask = self.df_normalization[self.df_normalization.loc[:, 3].isnull()]

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
            CT_DRUG_str = ','.join(list(filter(None, CT_DRUG.values())))
            TT_DRUG_str = ','.join(list(filter(None, TT_DRUG.values())))
            HT_DRUG_str = ','.join(list(filter(None, HT_DRUG.values())))
            info = [self.case_id, start_date, date, CT_DRUG_str, TT_DRUG_str, HT_DRUG_str, ]
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
        return df_result_difficulty, df_result_severity

    def export(self, output_file):
        output_path = Path(output_file)
        if output_path.is_dir():
            filename = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"
            output_path = output_path.joinpath(filename)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        writer = pd.ExcelWriter(output_path)
        for key, value in self.result.items():
            for i in range(6, 22):
                value.iloc[:, i] = pd.to_numeric(value.iloc[:, i])
            value.to_excel(writer, key, index=False)
        writer.save()

    def auto_run(self, input_file, output_file):
        self.input_excel = read_file(input_file)
        self.result = {}
        for key, value in self.input_excel.items():
            self.df_normalization = self.normalize(key, value)
            difficulty, severity = self.flatten()
            self.result[f'{self.case_name}-{self.case_id}-困擾度'] = difficulty
            self.result[f'{self.case_name}-{self.case_id}-嚴重度'] = severity
        self.export(output_file)


if __name__ == '__main__':
    app_helper = AppHelper()
    app_helper.auto_run('./input/2.xls', './output/result.xlsx')
