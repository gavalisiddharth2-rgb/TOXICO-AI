import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.stdout.reconfigure(encoding='utf-8')
from backend.app.ml.pipeline import pipeline

async def run_tests():
    samples = [
        ('नमस्ते, आपका दिन शुभ हो! आशा है आप अच्छे होंगे।', 'Hindi Safe'),
        ('भीड़ में बहुत हब्सी मिलेंगे साले बेवकूफ', 'Hindi Toxic/Abusive'),
        ('Bhai video was awesome! Thanks for sharing this.', 'English Safe'),
        ('You are a filthy idiot and I will kill you asshole', 'English Violent Threat'),
        ('teri maa ki chut tu kutta hai saale kamine', 'Hinglish Vulgar/Abuse'),
        ('superb bro keep it up good job yaar', 'Hinglish Safe'),
        ('ಸೂಳೆ ಮೂಡೆ ಅವ್ಳು ಕಾಂಗ್ರೆಸ್', 'Kannada Abuse'),
        ('ഇത് വളരെ മനോഹരമായ കാഴ്ചയാണ്', 'Malayalam Safe'),
        ('இப் புண்டா மவனே வீடியோ அளி டி', 'Tamil Vulgar'),
        ('విడు ఈపాటికి ఎంత మంది అమ్మయిలని దేగిండో', 'Telugu Abuse'),
    ]

    for text, desc in samples:
        res = await pipeline.analyze_text(text)
        print(f"\n=== [{desc}] ===")
        print(f"  Input: {text[:50]}")
        print(f"  Language: {res['language']['language_name']} ({res['language']['confidence']})")
        print(f"  Toxicity: {res['toxicity']['percentage']}% (Is Toxic: {res['toxicity']['is_toxic']}, Conf: {res['toxicity']['confidence_percentage']}%)")
        print(f"  Flagged Categories: {res['toxicity']['flagged_categories']}")
        print(f"  Keywords: {res['explainability']['flagged_keywords']}")
        print(f"  Action: {res['decision']['recommended_action']}")
        print(f"  Reason: {res['explainability']['explanation']}")

if __name__ == '__main__':
    asyncio.run(run_tests())
