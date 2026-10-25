import os
import sys
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

print("=== Indian Languages Datasets ===")
langs = ['hindi', 'kannada', 'malyalam', 'tamil', 'telugu']
for lang in langs:
    train_path = f"{lang}_train.csv"
    val_path = f"{lang}_val.csv"
    test_path = f"{lang}_test.csv"
    if os.path.exists(train_path):
        df = pd.read_csv(train_path)
        print(f"[{lang.upper()}] train: {df.shape}, cols: {df.columns.tolist()}")
        print(f"  labels: {df['label'].value_counts().to_dict()}")
        sample_0 = df[df['label'] == 0]['text'].iloc[0] if len(df[df['label'] == 0]) > 0 else ""
        sample_1 = df[df['label'] == 1]['text'].iloc[0] if len(df[df['label'] == 1]) > 0 else ""
        print(f"  sample label=0: {sample_0[:60]}")
        print(f"  sample label=1: {sample_1[:60]}")

print("\n=== Indo-HateSpeech_Dataset.xlsx ===")
indo_path = os.path.join("dataset", "Indo-HateSpeech_Dataset.xlsx")
if os.path.exists(indo_path):
    xl = pd.ExcelFile(indo_path)
    print("Sheets:", xl.sheet_names)
    for sheet in xl.sheet_names:
        df_sheet = pd.read_excel(indo_path, sheet_name=sheet, nrows=5)
        print(f"Sheet '{sheet}': cols = {df_sheet.columns.tolist()}")
        print(df_sheet.head(2))

print("\n=== Jigsaw Dataset ===")
jigsaw_path = os.path.join("dataset", "jigsaw-toxic-comment-train-processed-seqlen128.csv")
if os.path.exists(jigsaw_path):
    df_jig = pd.read_csv(jigsaw_path, nrows=5)
    print(f"Jigsaw cols: {df_jig.columns.tolist()}")
    print(df_jig.head(2))
