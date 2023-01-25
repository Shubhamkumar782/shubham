import shutil
from pathlib import Path
import json
import pandas as pd
import csv
import sys, math
import os
from Data_Cleansing import Data_Cleaning

class train_test_dev:
    def __init__(self, main_tsv_path, fstem, txtType) -> None:
        self.splitdir = 'datasets/data/'
        self.main_tsv_path = main_tsv_path
        self.typ, self.subtyp, self.nlabels, self.rgn = fstem.split('_')
        self.txt_type = txtType

    def _read_tsv_to_df(self, quotechar=None):
        """
        Reads a Tab Separated Values (TSV) file
        :param input_file:
        :param quotechar:
        :return:
        """
        with open(self.main_tsv_path, "r", encoding='utf-8') as f:
            reader = csv.reader(f, delimiter="\t", quotechar=quotechar)
            lines = []
            for line in reader:
                if sys.version_info[0] == 2:
                    line = list(str(cell, 'utf-8') for cell in line)
                lines.append(line)  ###  changes done from below  ###################
            f_data = pd.DataFrame(lines)
            return f_data

        def unique_data_gen(self, f_data, data_percent):
            cat_data_list = list()
            unique_cat = f_data[0].unique()
            for cat in unique_cat:
                _cat_data = f_data.loc[f_data[0] == cat]
                cat_data = pd.DataFrame(f_data.loc[f_data[0] == cat])
                cat_data = cat_data[:math.floor((len(_cat_data) / 100) * data_percent)]
                cat_data_list.append(pd.DataFrame(cat_data))
            return cat_data_list

    def df_to_trainTestDev(self, df_list):
        train_list = list()
        test_list = list()
        dev_list = list()
        for df in df_list:
            train_size = 0.6
            valid_size = 0.2
            train_index = int(
                len(df) * train_size)  # First we need to sort the dataset by the desired column
            _df_train = df[0:train_index]
            df_rem = df[train_index:]
            valid_index = int(len(df) * valid_size)
            _df_dev = df[train_index:train_index + valid_index]
            _df_test = df[train_index + valid_index:]
            train_list.append(_df_train)
            test_list.append(_df_test)
            dev_list.append(_df_dev)
        df_train = pd.concat(train_list)
        df_test = pd.concat(test_list)
        df_dev = pd.concat(dev_list)
        print(len(df_train), len(df_dev), len(df_test))

    save_dir = Path(f'datasets/data/{self.typ}/{self.subtyp}/{self.rgn}/{self.txt_type}')
    save_dir.mkdir(parents=True, exist_ok=True)

    # data cleansing
    # - Its a time  consuming process lets run on just first 100 chars of dev.tsv to check
    train_text = df_train.iloc[:, 1].tolist()
    test_text = df_test.iloc[:, 1].tolist()
    dev_text = df_dev.iloc[:, 1].tolist()
    dc = Data_Cleaning()
    all_dfs_ls = [train_text, test_text, dev_text]
    all_dfs = [df_train, df_test, df_dev]
    df_nms = ['train.tsv', "test.tsv", "dev.tsv"]
    for df_text_ls, df_, df_nm in zip(all_dfs_ls, all_dfs, df_nms):
        cleaned_df_txt = []
        cleaned_df_txt_256 = []
        for t_t in df_text_ls:
            cleaned_text_, cleaned_text_256_ = dc.main_preprocessor(t_t)
            # cleaned_text_, cleaned_text_256_ = t_t,t_t                 cleaned_df_txt.append(cleaned_text_)
            cleaned_df_txt_256.append(cleaned_text_256_)
        # save all clean data             df_.iloc[:, 1] = cleaned_df_txt
        df_.to_csv(os.path.join(save_dir, df_nm), encoding='utf-8', sep='\t', index=False, header=False)
        print(f' data {df_nm} saved at-->', save_dir)

    print(f'list of langs detected but no stop words found for them are --> {dc.no_stopw_langs} ')
    print('Lang and its count is - ', {i: dc.no_stopw_langs.count(i) for i in dc.no_stopw_langs})

    country, type, cls_num = self.country, self.typ, self.nlabels
    config_label = {}
    if os.path.exists("config.json"):
        f = open('config.json')
        config_label = json.load(f)
    config_label[country + "_" + type] = cls_num
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config_label, f)


    def _split(fpath, text_type):
        obj = train_test_dev(fpath, fpath.stem, text_type)
        df = obj._read_tsv_to_df()
        list_unique_df = obj.unique_data_gen(df, data_percent=100)  # 100 means
        obj.df_to_trainTestDev(list_unique_df)


    def delete_existing_dir(dir):
        if Path(dir).is_dir():
            shutil.rmtree(Path(dir))
            print("removed dir")
        elif Path(dir).is_file():
            Path(dir).unlink()
            print("removed file")
        else:
            pass


if __name__ == '__main__':
    dirs = ['config.json']
    [delete_existing_dir(dir) for dir in dirs]

    comb = ["cons_250w", "cons_5p", "uncons"]
    length = len(comb)

    fpaths = list(Path("data").glob('**/*.tsv'))
    for f in fpaths:
        temp = [f for i in range(length)]
        for fpath, t_type in zip(temp, comb):
            _split(fpath, t_type)