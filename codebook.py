"""
- 可以【動態新增】，只是手動合併會比教多工作，因為每個人動態新增的欄位不一樣，會需要一直手動往後合併，然後補 0。
    - 採用【動態新增】，程式碼需要改寫的地方也比較多，需要在一開始就先判斷哪寫不重複的項目，然後把沒出現過的加在 codebook 後面。
- 採用【其他】方法手動合併只需要複製貼上就好，因為大家的欄位都一致。缺點是一天如果有兩筆其他會被後者覆蓋。
"""

# ID:個案編號
# CTSDAY:藥物施打開始日期
# DATE:症狀日期

# 化療施打藥物
CT_DRUG = {
    '1': '癌德星',
    '2': '微脂體小紅莓',
    '3': '小紅莓',
    '4': '歐洲紫杉醇',
}

# 標靶施打藥物
TT_DRUG = {
    '1': '癌思婷',
    '2': '賀癌平',
    '3': '賀疾妥',
    '4': '賀癌寧',
    '5': '癌伏妥',
    '6': '泰嘉錠',
    '7': '愛乳適',
    '8': '擊癌利',
}

# 賀爾蒙施打藥物
HT_DRUG = {
     '1': '復乳納',
     '2': '達芬錠',
     '3': '諾曼癌素',
     '4': '法洛德',
     '5': '諾雷德',
     '6': '柳菩林',
}

# 症狀
effect = {
    '1': '皮疹',
    '2': '掉髮',
    '3': '熱潮紅',
    '4': '噁心嘔吐',
    '5': '皮膚反應',
    '6': '白血球下降',
    '7': '腹瀉',
    '8': '關節痠痛',
    '9': '疲倦',
    '10': '周邊神經病變',
    '11': '口腔黏膜炎',
    '12': '手足症候群',
    '13': '陰道乾燥異常分泌',
    '14': '皮膚/頭髮乾燥',
    '15': '骨質疏鬆',
    '16': '其他',
}