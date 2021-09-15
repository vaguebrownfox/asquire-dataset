from scipy.io import wavfile
import numpy as np
import pandas as pd
import os

audio_folder = "data/audio"
anote_folder = "data/anote"

audio_files = os.listdir(audio_folder)
pad = 0.3;

def rmNums(t) :
    return ''.join([c for c in t if not c.isdigit()])

def unpackWav(audio, anote):
    fs, data = wavfile.read(audio)
    channel1 = data[:, 0]
    
    anote_frame = pd.read_csv(
        anote, sep='\t', 
        header=None, 
        usecols=[0, 1, 2], 
        names=['start', 'end', 'type']
        )
    
    anote_frame.insert(0, 'index', range(0, len(anote_frame)))
    
    cleanTypesDigits = [rmNums(t) for t in anote_frame['type'].unique()]
    types = pd.DataFrame({'type': cleanTypesDigits})['type'].unique()
    
    print("filename", audio)
    
    unpack_info = {}
    for t in types :
        print("type", t)
        type_frame = anote_frame[anote_frame['type'].str.contains(t)]
        index = type_frame["index"].to_numpy()
        samples = []
        print("start",type_frame["start"][index[0]])
        samples.append((type_frame["start"][index[0]]- pad) * fs // 1)
        for i in range(len(index) - 1):
            if index[i + 1] - index[i] > 1 :
                print("end",type_frame["end"][index[i]])
                samples.append((type_frame["end"][index[i]] + pad) * fs // 1)
                
                print("start",type_frame["start"][index[i+1]])
                samples.append((type_frame["start"][index[i+1]] - pad) * fs // 1)
        print("end",type_frame["end"][index[len(index) - 1]])
        samples.append((type_frame["end"][index[len(index) - 1]] + pad) * fs // 1) 
        
        unpack_info[t] = samples; 
    
    
    return [unpack_info, channel1]
    
    


for file in audio_files[:1]:
    audiopath = os.path.join(audio_folder, file)
    anotepath = os.path.join(anote_folder, file.replace("wav", "txt"))
    info, data = unpackWav(audiopath, anotepath)
    print(info)
    


    
    
    
