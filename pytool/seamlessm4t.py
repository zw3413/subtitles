import io
import json
import matplotlib as mpl
import matplotlib.pyplot as plt
import mmap
import numpy
import soundfile
import torchaudio
import torch
import re

from collections import defaultdict
from IPython.display import Audio, display
from pathlib import Path
from pydub import AudioSegment

from seamless_communication.inference import Translator
from seamless_communication.streaming.dataloaders.s2tt import SileroVADSilenceRemover


# Initialize a Translator object with a multitask model, vocoder on the GPU.

#model_name = "seamlessM4T_v2_large"
model_name = "seamlessM4T_medium"
vocoder_name = "vocoder_v2" #if model_name == "seamlessM4T_v2_large" else "vocoder_36langs"

translator = Translator(
    model_name,
    vocoder_name,
    device=torch.device("cuda:0"),
    dtype=torch.float16,
)

#tgt_langs = ("arb", "rus", "ind", "tam", "kor","cmn")

tgt_langs = ("eng","cmn")

file_path = "../file/subtitle/abc/jpn1.srt"
file = open(file_path, "r")
#content = file.read()
#print(len(content))


#for tgt_lang in tgt_langs:

    # text_output, speech_output = translator.predict(
    #     input="Hey everyone! I hope you're all doing well. Thank you for attending our workshop.",
    #     task_str="t2tt",
    #     tgt_lang=tgt_lang,
    #     src_lang="eng",
    # )
    
try:
    for l in file:
        line = l.strip()
        print(line)
        pattern_num = r'^-?\d+$'
        pattern_timestamp = re.compile(r'^\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}$')
        if re.match(pattern_num, line) or re.match(pattern_timestamp, line):
            print(line)
        else:        
            tgt_lang ="eng"
            text_output_en, speech_output = translator.predict(
                #input="Hey everyone! I hope you're all doing well. Thank you for attending our workshop.",
                input = line,
                task_str="t2tt",
                tgt_lang=tgt_lang,
                src_lang="jpn",
            )
            print(f"Translated text in {tgt_lang}: {text_output_en[0]}")
         
finally:
    file.close()
        

#    print()
