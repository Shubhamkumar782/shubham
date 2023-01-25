import os, re, string, sys, csv
from pathlib import Path
import json
import spacy
from spacy.language import Language
import random
random.seed(42)
from spacy_langdetect  import LanguageDetector
import advertools as adv # for getting list of stopwords
# from transformers import AutoTokenizer, AutoModelForSequenceClassification
class Data_Cleaning:
    def __init__(self):
        self.no_stopw_langs = []
        self.raw_text = ""
        with open('spacy_lan_codes.json','r', encoding='utf-8') as f:
            lang_codes = json.load(f)
        self.lang_codes = lang_codes

        self.nlp_model = spacy.load("en_core_web_sm")
        Language.factory("language_detector", func=self.get_lang_detector)
        self.nlp_model.add_pipe('language_detector', last=True)

    def get_lang_detector(self, nlp, name):
        return LanguageDetector()  # We use the seed 42 seed=42
    def primary_cleaning(self,text):
        text = text.lower()
        text = text.strip()
        text = text.replace('\n', ' ')  # remove newline chars
        text = ' '.join([i for i in text.split() if len(i)>1]) # remove extra whitespaces and single alphabets
        pcleaned_text = re.compile('[%s]' % re.escape(string.punctuation)).sub(' ', text)
        return pcleaned_text

    def lang_detect_prim_clean(self,raw_text):
        #move
        #pcleaned_text = self.primary_cleaning(raw_text)
        doc = self.nlp_model(raw_text)
        lang = doc._.language
        detected_lang = lang['language']
        if detected_lang =='id':
            print('detected lang is Indonesian (Malay)') # Malay and Indonesian are 80% same
        elif detected_lang=='UNKNOWN':
            detected_lang = 'en'
            self.no_stopw_langs.append(detected_lang)
        elif detected_lang =='zh-cn':
            detected_lang=str('zh')
        print(f'Detected language is --> {lang}')
        return detected_lang

    def stopw_removal(self,detected_lang, pcleaned_text):  # detected_lang, pcleaned_text
        if detected_lang in self.lang_codes.keys():
            detect_lang_stopw = self.lang_codes[detected_lang]
            stopw_free_words = [i for i in pcleaned_text.split(' ') if i not in detect_lang_stopw and len(i)>1]
            stop_free_text =  ' '.join(stopw_free_words)
            # stop_free_text = ' '.join([i for i in stop_free_text.split() if len(i) > 1])
            return stop_free_text
        else:
            print(f' No stopwords found for Spacy_lang_code --> {detected_lang}')
            self.no_stopw_langs.append(detected_lang)

            return pcleaned_text

    def text_filtering(self,text):
        filtered_text = text.split(".")
        f_text = ""
        for f_t in filtered_text:
            if len(f_t.split())>=5:
                f_text=f_t
                break
        return f_text

    def main_preprocessor(self,raw_text):
        self.raw_text = raw_text
        textr = self.raw_text
        pcleaned_text = self.primary_cleaning(textr)
        f_text = self.text_filtering(textr)
        detected_lang = self.lang_detect_prim_clean(f_text)
        cleaned_text = self.stopw_removal(detected_lang,pcleaned_text)

        # take only first 256 words/doc
        cleaned_text_256 = ' '.join(cleaned_text.split()[:256]).strip()  # to save new data of word_limit 256 at new dir
        return cleaned_text, cleaned_text_256


if __name__ == '__main__':

    english = 'Pre-employment fofmwomafofwon Health Assessment NAME _ANrA uzh .BEChA-PEKh ? ? Please find below an outline of the physical activities associated with the position of | This information is supplied to assist medical practitioners in completing the pre-employment health assessment? If there are an Questions? please do not hesitate to contact the Human Resources Department ? ,c ? ? M ? BSG ? 000 Company Location | ? L R ? 7 L NEffewhnager QCKiAruD 164 oxes ticked indicate those activities which will be routinely performed within this position?Where necessary? additional comments are supplied? ??????Job Reduirements ? Tick | AddiionalComments ? 5. . =. ~. . . | Heavy Lifting /'
    arebic = 'قَدّ خَرَجَتْ سَالِي.'
    japanese = 'あなたは明日どこに行きますか。私は映画に行く予定です。いっしょに来てください.  قَدّ خَرَجَتْ سَالِي.  '    # jpns = nospwrd for jpns
    korian = '헤이 샘, 내일 어디 가니? 영화보러 갈 계획이 있어요. 나랑 함께 가겠 니. 훌륭한 영화입니다.'  # adv lib dosent supports korian lang, its hardcoded in json mannually.
    malay = 'hai gaurav. Apa khabar. apa yang sedang anda lakukan. boleh saya hubungi awak sebentar?'
    indonesian = 'hai gaurav. Apa kabarmu. apa yang kamu lakukan. bolehkah aku meneleponmu sebentar?'
    obj = Data_Cleaning()
    cleaned_text, cleaned_text_256 = obj.main_preprocessor(korian)
    print(cleaned_text)
    print(cleaned_text_256)


