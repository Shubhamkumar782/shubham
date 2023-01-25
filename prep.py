class region_data:
    def __init__(self, tsvdir, txttyp):
        self.txttyp = txttyp
        self.gatherdir = 'rgn-data'         self.mergedir = 'rgn-mrgd-data'         self.mrgd = 'rgn-master.tsv'         self.tsvdir = tsvdir
        with open('countr_region_mappings.json', 'r', encoding='utf-8') as f:
            self.crj = json.load(f)



    def _gather(self):
        fpaths = list(Path(self.tsvdir).glob(f'**/{self.txttyp}/*.tsv'))
        print(fpaths)
        for fpath in fpaths:
            fstem = fpath.stem
            typ, subtyp, nlabels, ctr = fstem.split('_')
            rgn = self.crj[ctr]
            pth = Path(self.gatherdir) / f'{typ}' / f'{subtyp}' / f'{rgn}' / f'{fpath.name}'             # pth = Path(self.gatherdir) / f'{typ}' / f'{subtyp}' / f'{rgn}' / f'{self.txttyp}'/f'{fpath.name}'             pth.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(fpath, pth)



    def _merge(self):
            fpaths = list(Path(self.gatherdir).glob('**/*.tsv'))
            print('merge fpaths:', fpaths)
            config_label = {}
            if os.path.exists("config.json"):
                f = open('config.json')
                config_label = json.load(f)
            di = {}
            for fpath in fpaths:
                # if str(fpath).endswith('master.tsv'):
                # continue
                fstem = fpath.stem
                prnt = fpath.parent
                typ, subtyp, nlabels, ctr = fstem.split('_')
                prfx = '_'.join([typ, subtyp, nlabels])
                if (prnt, prfx) not in di:
                    di[(prnt, prfx)] = []
                di[(prnt, prfx)].append(fpath)
            for tup, fpaths in di.items():
                print('***tup', tup)
                print('***fpaths', fpaths)
                prnt, prfx = tup
                print('**prfx:', prfx)
                print(Path(prnt).parts)
                _, typ, subtyp, rgn = Path(prnt).parts
                lst_byts = []
                for fpath in fpaths:
                    with open(fpath, 'rb') as fp:
                        lst_byts.append(fp.read())
                mrgd_path = Path(f'{self.mergedir}/{typ}/{subtyp}/{rgn}/{self.txttyp}/{prfx}_{rgn}.tsv')
                mrgd_path.parent.mkdir(parents=True, exist_ok=True)
                with open(mrgd_path, 'wb') as fp:
                    fp.write(b''.join(lst_byts))
                # for file in files:
                #     if str(file).endswith(".tsv"):
                # tsv_path = os.path.join(input_path, file)
                # fname, ext = os.path.splitext(os.path.basename(tsv_path))
                docType, subType, cls_num = prfx.split('_')
                config_label[docType + "_" + subType + "_" + rgn] = cls_num
                # obj = train_test_dev(tsv_path, fname)
                # df = obj._read_tsv_to_df()
                # obj.df_to_trainTestDev(df)
                # print(" output is saved at path -->", os.getcwd())
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(config_label, f)
    
    def _split(self):
        fpaths = list(Path(self.mergedir).glob('**/*.tsv'))
        for fpath in fpaths:
            obj = train_test_dev(fpath, fpath.stem, self.txttyp)
            df = obj._read_tsv_to_df()
            list_unique_df = obj.unique_data_gen(df, data_percent=100)  # 100 means
            obj.df_to_tr