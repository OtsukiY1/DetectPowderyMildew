import os
import glob

path = r"C:\Users\abeke\DetectPowderyMildewSpore\dataset_25-1001-v3\test"
files = glob.glob(path + '\\*') #名前順でファイル名を取得できる

#print("files =",files)

i = 0
for f in files:
    i += 1
    os.rename(f, path + f"\\{i:02d}.jpg") #02d->二桁で０埋め。03d->3桁でゼロ埋め。f文字列でググれ
    
print("complete")