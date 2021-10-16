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
    
    # merge types
    m_types = ["Exhale", "Wheeze", "Inhale"]
    for m in m_types :
        if m in types:
            types.remove(m)
    types.append("|".join(m_types))
    
    return types
    
    
def unpack_wav(audio, anote, filename):
    fs, data = wavfile.read(audio)
    channel_1 = data[:, 0]
    
    anote_frame = get_anote_frames(anote)

    types = get_types(anote_frame)
    
    if not os.path.exists(unpack_folder):
        os.mkdir(unpack_folder)
    
    for t in types :
        type_frame = anote_frame[anote_frame['type']
                                 .str.contains(t, na=False)]
        df.to_csv(file_name, sep='\t')
        
        index = type_frame["index"].to_numpy()
        
        bp = 0
        bp_arr = []
        pos = []
        pos.append((type_frame["start"][index[0]]- pad) * fs)
        for i in range(len(index) - 1):
            if index[i + 1] - index[i] > 1 :
                pos.append((type_frame["end"][index[i]] + pad) * fs)
                pos.append((type_frame["start"][index[i + 1]] - pad) * fs)
                bp = i + 1 - bp
                bp_arr.append(bp)
        bp_arr.append(i + 2 - bp)
        pos.append((type_frame["end"][index[len(index) - 1]] + pad) * fs)
        
        
        
        pos = list(map(int, pos))
        for i in range(int(len(pos) / 2)):
            ptr = i * 2
            chunk = channel_1[pos[ptr] : pos[ptr + 1]]
            filename = ''.join(filename.split("_")[0])
            k = i + 1
            unpack_file = os.path.join(f"{unpack_folder}",
                                       f"{filename}_{t}_{k}_{bp_arr[i]}.wav")
            while os.path.exists(unpack_file):
                k += 1
                unpack_file = os.path.join(f"{unpack_folder}",
                                       f"{filename}_{t}_{k}_{bp_arr[i]}.wav")
                
            
            wavfile.write(unpack_file, fs, chunk)

for file in audio_files:
    audiopath = os.path.join(audio_folder, file)
    anotepath = os.path.join(anote_folder, file.replace("wav", "txt"))
    unpack_wav(audiopath, anotepath, file.replace(".wav", ""))
