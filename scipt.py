from scipy.io import wavfile
import numpy as np
import pandas as pd
import os

audio_folder = "data/audio"
anote_folder = "data/anote"
anote_folder = "data/anote"
unpack_folder = "data/unpackd_audio"

audio_files = os.listdir(audio_folder)
pad = 0.7;

def rmNums(t) :
    return ''.join([c for c in t if not c.isdigit()]).strip()

def unpackWav(audio, anote, filename):
    fs, data = wavfile.read(audio)
    channel1 = data[:, 0]
    
    print(filename, "pd read")
    
    anote_frame = pd.read_csv(
        anote, sep='\t', 
        header=None, 
        usecols=[0, 1, 2], 
        names=['start', 'end', 'type'])
    
    anote_frame.insert(0, 'index', range(0, len(anote_frame)))
    
    # print(filename, anote_frame['type'].unique())
    
    cleanTypesDigits = [rmNums(t) for t in anote_frame['type'].unique() if isinstance(t, str)]
    types = list(pd.DataFrame({'type': cleanTypesDigits})['type'].unique())
    
    # print(filename, "types", types)
    
    # merge types
    m_types = ["Exhale", "Wheeze", "Inhale"]
    for m in m_types :
        try :
            types.remove(m) 
        except :
            continue
    types.append("|".join(m_types))
    
    unpack_info = {}
    for t in types :
       
        type_frame = anote_frame[anote_frame['type'].str.contains(t, na=False)]
        index = type_frame["index"].to_numpy()
        
        pos = []
        bp_arr = []
        bp = 0
        pos.append((type_frame["start"][index[0]]- pad) * fs)
        for i in range(len(index) - 1):
            if index[i + 1] - index[i] > 1 :
                pos.append((type_frame["end"][index[i]] + pad) * fs)
                pos.append((type_frame["start"][index[i+1]] - pad) * fs)
                bp = i + 1 - bp
                bp_arr.append(bp);
        bp_arr.append(i + 2 - bp)
        pos.append((type_frame["end"][index[len(index) - 1]] + pad) * fs)
        
        pos = list(map(int, pos))

        for i in range(int(len(pos) / 2)):
            ptr = i * 2
            chunk = channel1[pos[ptr] : pos[ptr + 1]]
            filename = ''.join(filename.split("_")[0])
            unpack_file = os.path.join(f"{unpack_folder}", 
                                       f"{filename}_{t}_{i+1}_{bp_arr[i]}.wav")
            wavfile.write(unpack_file, fs, chunk)
        



for file in audio_files:
    audiopath = os.path.join(audio_folder, file)
    anotepath = os.path.join(anote_folder, file.replace("wav", "txt"))
    unpackWav(audiopath, anotepath, file.replace(".wav", ""))

    


    
    
    
