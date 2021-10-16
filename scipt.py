from scipy.io import wavfile
import numpy as np
import pandas as pd
import os

audio_folder = "data/audio"
anote_folder = "data/anote"
unpack_folder = "data/unpackd_audio2"

audio_files = os.listdir(audio_folder)
pad = 0.7;

def rm_nums(t) :
    return ''.join([c for c in t if not c.isdigit()]).strip()

def get_anote_frames(anoteFile) :
    anote_frame = pd.read_csv(
        anoteFile, sep='\t', 
        header=None, 
        usecols=[0, 1, 2], 
        names=['start', 'end', 'type'])
    anote_frame.insert(0, 'index', range(0, len(anote_frame)))
    
    return anote_frame

def get_types(anote_frame) :
    clean_types_digits = [rm_nums(t) for t in anote_frame['type']
                        .unique() if isinstance(t, str)]
    types = list(pd.DataFrame({'type': clean_types_digits})['type'].unique())
    
    m_types = ["Exhale", "Wheeze", "Inhale"] # merge types
    for m in m_types :
        if m in types:
            types.remove(m)
    types.append("|".join(m_types))
    
    return types

def get_type_sections(type_frame) :
    tf_idx = type_frame["index"].to_numpy()
    sp = 0
    tfs = []
    for i in range(len(tf_idx) - 1):
        if tf_idx[i + 1] - tf_idx[i] > 1 :
            sec = type_frame.iloc[sp:i + 1, :]
            tfs.append(sec)
            sp = i + 1
    sec = type_frame.iloc[sp:, :]
    tfs.append(sec)
    return tfs
    
    
def unpack_wav(audio, anote, filename): # for each file
    if not os.path.exists(unpack_folder):
        os.mkdir(unpack_folder)
    fs, data = wavfile.read(audio)
    channel_1 = data[:, 0]
    
    anote_frame = get_anote_frames(anote)
    types = get_types(anote_frame)
        
    for t in types :
        type_frame = anote_frame[anote_frame['type']
                                 .str.contains(t, na=False)]
    
        tf_sections = get_type_sections(type_frame)
        
        for si, sec in enumerate(tf_sections):
            
            ts = sec["start"][:1].to_numpy()[0]
            te = sec["end"][-1:].to_numpy()[0]
            
            start = int((ts - pad) * fs)
            end   = int((te + pad) * fs)
            
            fn = f"{filename}_{t}_{si+1}_{len(sec)}"
            f_csv = os.path.join(unpack_folder, f"{fn}.txt")
            sec = pd.merge(sec.iloc[:, 1:-1] - ts + pad, sec.iloc[:, -1:], 
                           on=sec.index, how='outer')
            sec.iloc[:, 1:].to_csv(f_csv, sep='\t', header=False, index=False)
            
            aud_chunk = channel_1[start : end]
            f_wav = os.path.join(unpack_folder, f"{fn}.wav")
            wavfile.write(f_wav, fs, aud_chunk)


for file in audio_files:
    audiopath = os.path.join(audio_folder, file)
    anotepath = os.path.join(anote_folder, file.replace("wav", "txt"))
    unpack_wav(audiopath, anotepath, file.replace(".wav", ""))
