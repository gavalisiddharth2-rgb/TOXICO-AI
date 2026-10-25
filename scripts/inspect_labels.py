import os
import sys
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

indo_path = os.path.join("dataset", "Indo-HateSpeech_Dataset.xlsx")
if os.path.exists(indo_path):
    df_indo = pd.read_excel(indo_path)
    print("Indo-HateSpeech labels:", df_indo['Label'].value_counts().to_dict())
    print("Indo-HateSpeech shape:", df_indo.shape)
    print("\nIndo samples with HS1:")
    print(df_indo[df_indo['Label'].astype(str).str.contains('1')][['Comment', 'Label']].head(3))
    print("\nIndo samples with HS0:")
    print(df_indo[df_indo['Label'].astype(str).str.contains('0')][['Comment', 'Label']].head(3))

print("\n--- Inspecting Indian Languages train label meaning ---")
for lang in ['hindi', 'kannada', 'malyalam', 'tamil', 'telugu']:
    df = pd.read_csv(f"{lang}_train.csv")
    print(f"\n[{lang.upper()}]")
    print("Label 0 (first 2):", df[df['label']==0]['text'].head(2).tolist())
    print("Label 1 (first 2):", df[df['label']==1]['text'].head(2).tolist())
