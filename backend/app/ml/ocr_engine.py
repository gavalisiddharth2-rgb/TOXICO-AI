"""
OCR Engine for Image and Meme Analysis
Uses Windows Media WinRT OCR with image preprocessing (contrast enhancement, resizing).
Extracts text from uploaded images, memes, and screenshots for downstream toxicity analysis.
"""

import io
import asyncio
import logging
from typing import Dict, Any, Optional
from PIL import Image, ImageEnhance, ImageFilter

logger = logging.getLogger(__name__)

class OcrEngine:
    def __init__(self):
        self.available = False
        try:
            import winocr
            self.winocr = winocr
            self.available = True
            logger.info("Windows Media WinRT OCR initialized successfully.")
        except Exception as e:
            logger.warning(f"WinOCR not available: {e}")
            self.winocr = None

    def preprocess_image(self, img: Image.Image) -> Image.Image:
        """Enhances image contrast and resolution for better OCR recognition."""
        try:
            # Ensure RGB
            if img.mode != 'RGB' and img.mode != 'RGBA':
                img = img.convert('RGB')

            # Upscale if dimensions are small
            width, height = img.size
            if width < 600 or height < 300:
                scale = max(600 / width, 300 / height)
                new_w = int(width * scale)
                new_h = int(height * scale)
                img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

            # Enhance contrast slightly
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.4)
            # Enhance sharpness
            sharpener = ImageEnhance.Sharpness(img)
            img = sharpener.enhance(1.3)

            return img
        except Exception as e:
            logger.warning(f"Preprocess error: {e}")
            return img

    async def extract_text_from_bytes(self, image_bytes: bytes, lang: str = "en-US") -> Dict[str, Any]:
        """Extracts text from raw image bytes."""
        try:
            pil_img = Image.open(io.BytesIO(image_bytes))
            return await self.extract_text_from_pil(pil_img, lang)
        except Exception as e:
            logger.error(f"Failed to process image bytes: {e}")
            return {
                'success': False,
                'extracted_text': '',
                'word_count': 0,
                'lines': [],
                'engine': 'Error',
                'error': str(e)
            }

    async def extract_text_from_pil(self, pil_img: Image.Image, lang: str = "en-US") -> Dict[str, Any]:
        """Extracts text from PIL Image instance."""
        if not self.available:
            return {
                'success': False,
                'extracted_text': '',
                'word_count': 0,
                'lines': [],
                'engine': 'Unavailable',
                'error': 'Windows Media OCR is not available on this platform.'
            }

        try:
            processed_img = self.preprocess_image(pil_img)

            # Run winocr recognize_pil
            ocr_result = await self.winocr.recognize_pil(processed_img, lang)
            extracted_text = ocr_result.text.strip() if hasattr(ocr_result, 'text') else str(ocr_result).strip()

            lines = []
            if hasattr(ocr_result, 'lines'):
                for line in ocr_result.lines:
                    lines.append({
                        'text': getattr(line, 'text', str(line)),
                    })

            return {
                'success': True,
                'extracted_text': extracted_text,
                'word_count': len(extracted_text.split()) if extracted_text else 0,
                'lines': lines,
                'engine': 'Windows Media WinRT OCR',
                'error': None
            }
        except Exception as e:
            logger.error(f"OCR execution error: {e}")
            return {
                'success': False,
                'extracted_text': '',
                'word_count': 0,
                'lines': [],
                'engine': 'Windows Media WinRT OCR',
                'error': str(e)
            }

    def extract_text_sync(self, pil_img: Image.Image, lang: str = "en-US") -> Dict[str, Any]:
        """Synchronous wrapper for OCR extraction."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # In running event loop, create task or run in thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self.extract_text_from_pil(pil_img, lang))
                    return future.result()
            else:
                return asyncio.run(self.extract_text_from_pil(pil_img, lang))
        except Exception as e:
            return asyncio.run(self.extract_text_from_pil(pil_img, lang))

ocr_engine = OcrEngine()
