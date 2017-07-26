import pandas as pd
import re


df = pd.read_csv("./ALL_tracklists.csv")
df.columns = ['track_info','artist']
df['track'] = df['track_info'].apply(lambda x: x.split(' - ')[1])
df['track_artist'] = df['track_info'].apply(lambda x: x.split(' - ')[0])
df['track_basic'] = df['track'].apply(lambda x: x.split(' (')[0])
df['artist_basic'] = df['track_artist'].apply(lambda x: re.split('( feat. | ft. )', x)[0])
df['track_remix'] = df['track'].apply(lambda x: [re.search('\((.*)\)', x).group(1)] if re.search('\((.*)\)', x) else [])