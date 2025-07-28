from typing import Optional, Dict, Any
import asyncio
import os
from app.models.requests import TranslationRequest, TranslationResponse

# Try to import Google Cloud Translate
try:
    from google.cloud import translate_v2 as translate
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    GOOGLE_CLOUD_AVAILABLE = False

# Try to import googletrans fallback
try:
    from googletrans import Translator, LANGUAGES as GOOGLETRANS_LANGUAGES
    GOOGLETRANS_AVAILABLE = True
except (ImportError, AttributeError):
    GOOGLETRANS_AVAILABLE = False

# Language codes mapping
LANGUAGES = {
    'af': 'afrikaans', 'sq': 'albanian', 'am': 'amharic', 'ar': 'arabic',
    'hy': 'armenian', 'az': 'azerbaijani', 'eu': 'basque', 'be': 'belarusian',
    'bn': 'bengali', 'bs': 'bosnian', 'bg': 'bulgarian', 'ca': 'catalan',
    'ceb': 'cebuano', 'ny': 'chichewa', 'zh-cn': 'chinese (simplified)',
    'zh-tw': 'chinese (traditional)', 'co': 'corsican', 'hr': 'croatian',
    'cs': 'czech', 'da': 'danish', 'nl': 'dutch', 'en': 'english',
    'eo': 'esperanto', 'et': 'estonian', 'tl': 'filipino', 'fi': 'finnish',
    'fr': 'french', 'fy': 'frisian', 'gl': 'galician', 'ka': 'georgian',
    'de': 'german', 'el': 'greek', 'gu': 'gujarati', 'ht': 'haitian creole',
    'ha': 'hausa', 'haw': 'hawaiian', 'iw': 'hebrew', 'hi': 'hindi',
    'hmn': 'hmong', 'hu': 'hungarian', 'is': 'icelandic', 'ig': 'igbo',
    'id': 'indonesian', 'ga': 'irish', 'it': 'italian', 'ja': 'japanese',
    'jw': 'javanese', 'kn': 'kannada', 'kk': 'kazakh', 'km': 'khmer',
    'ko': 'korean', 'ku': 'kurdish (kurmanji)', 'ky': 'kyrgyz', 'lo': 'lao',
    'la': 'latin', 'lv': 'latvian', 'lt': 'lithuanian', 'lb': 'luxembourgish',
    'mk': 'macedonian', 'mg': 'malagasy', 'ms': 'malay', 'ml': 'malayalam',
    'mt': 'maltese', 'mi': 'maori', 'mr': 'marathi', 'mn': 'mongolian',
    'my': 'myanmar (burmese)', 'ne': 'nepali', 'no': 'norwegian',
    'ps': 'pashto', 'fa': 'persian', 'pl': 'polish', 'pt': 'portuguese',
    'pa': 'punjabi', 'ro': 'romanian', 'ru': 'russian', 'sm': 'samoan',
    'gd': 'scots gaelic', 'sr': 'serbian', 'st': 'sesotho', 'sn': 'shona',
    'sd': 'sindhi', 'si': 'sinhala', 'sk': 'slovak', 'sl': 'slovenian',
    'so': 'somali', 'es': 'spanish', 'su': 'sundanese', 'sw': 'swahili',
    'sv': 'swedish', 'tg': 'tajik', 'ta': 'tamil', 'te': 'telugu', 'th': 'thai',
    'tr': 'turkish', 'uk': 'ukrainian', 'ur': 'urdu', 'uz': 'uzbek',
    'vi': 'vietnamese', 'cy': 'welsh', 'xh': 'xhosa', 'yi': 'yiddish',
    'yo': 'yoruba', 'zu': 'zulu'
}

class TranslationService:
    def __init__(self):
        self.supported_languages = LANGUAGES
        self.google_cloud_client = None
        self.googletrans_client = None
        
        # Initialize available translation services
        if GOOGLE_CLOUD_AVAILABLE and os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
            try:
                self.google_cloud_client = translate.Client()
                print("✅ Google Cloud Translate initialized")
            except Exception as e:
                print(f"⚠️ Google Cloud Translate failed: {e}")
        
        if GOOGLETRANS_AVAILABLE and not self.google_cloud_client:
            try:
                from googletrans import Translator
                self.googletrans_client = Translator()
                print("✅ GoogleTrans fallback initialized")
            except Exception as e:
                print(f"⚠️ GoogleTrans fallback failed: {e}")
        
        if not self.google_cloud_client and not self.googletrans_client:
            print("⚠️ No translation service available")
        
    async def translate_text(
        self,
        request: TranslationRequest
    ) -> TranslationResponse:
        """Translate text to target language."""
        if not self.google_cloud_client and not self.googletrans_client:
            # Return mock translation when no service is available
            return TranslationResponse(
                original_text=request.text,
                translated_text=f"[MOCK TRANSLATION] {request.text}",
                source_language=request.source_language or "auto",
                target_language=request.target_language,
                confidence=0.5
            )
        
        try:
            # Run translation in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self._translate_sync,
                request.text,
                request.target_language,
                request.source_language
            )
            
            return result
            
        except Exception as e:
            # Return mock translation on error
            return TranslationResponse(
                original_text=request.text,
                translated_text=f"[ERROR] Translation failed: {str(e)}",
                source_language=request.source_language or "auto",
                target_language=request.target_language,
                confidence=0.0
            )

    def _translate_sync(
        self,
        text: str,
        target_lang: str,
        source_lang: Optional[str] = None
    ) -> TranslationResponse:
        """Synchronous translation function."""
        try:
            if self.google_cloud_client:
                # Use Google Cloud Translate
                result = self.google_cloud_client.translate(
                    text,
                    target_language=target_lang,
                    source_language=source_lang
                )
                
                return TranslationResponse(
                    original_text=text,
                    translated_text=result['translatedText'],
                    source_language=result.get('detectedSourceLanguage', source_lang or 'auto'),
                    target_language=target_lang,
                    confidence=0.9
                )
                
            elif self.googletrans_client:
                # Use googletrans as fallback
                if source_lang:
                    result = self.googletrans_client.translate(
                        text,
                        dest=target_lang,
                        src=source_lang
                    )
                else:
                    result = self.googletrans_client.translate(text, dest=target_lang)
                
                return TranslationResponse(
                    original_text=text,
                    translated_text=result.text,
                    source_language=result.src,
                    target_language=target_lang,
                    confidence=getattr(result.extra_data, 'confidence', 0.8) if hasattr(result, 'extra_data') else 0.8
                )
            else:
                raise Exception("No translation service available")
                
        except Exception as e:
            raise Exception(f"Translation error: {str(e)}")

    async def detect_language(self, text: str) -> Dict[str, Any]:
        """Detect the language of the given text."""
        if not self.google_cloud_client and not self.googletrans_client:
            # Return mock detection when no service is available
            return {
                "language": "en",
                "language_name": "english",
                "confidence": 0.5
            }
        
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self._detect_language_sync,
                text
            )
            
            return result
            
        except Exception as e:
            # Return fallback detection
            return {
                "language": "en",
                "language_name": "english", 
                "confidence": 0.0
            }

    def _detect_language_sync(self, text: str) -> Dict[str, Any]:
        """Synchronous language detection."""
        try:
            if self.google_cloud_client:
                result = self.google_cloud_client.detect_language(text)
                lang_code = result['language']
                return {
                    "language": lang_code,
                    "language_name": LANGUAGES.get(lang_code, lang_code),
                    "confidence": result.get('confidence', 0.9)
                }
            
            elif self.googletrans_client:
                result = self.googletrans_client.detect(text)
                return {
                    "language": result.lang,
                    "language_name": LANGUAGES.get(result.lang, result.lang),
                    "confidence": result.confidence
                }
            else:
                raise Exception("No translation service available")
                
        except Exception as e:
            raise Exception(f"Language detection error: {str(e)}")

    def get_supported_languages(self) -> Dict[str, str]:
        """Get list of supported languages."""
        return self.supported_languages.copy()

    async def translate_multiple(
        self,
        texts: list[str],
        target_language: str,
        source_language: Optional[str] = None
    ) -> list[TranslationResponse]:
        """Translate multiple texts at once."""
        try:
            translations = []
            
            # Process in batches to avoid rate limiting
            batch_size = 10
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                batch_tasks = [
                    self.translate_text(TranslationRequest(
                        text=text,
                        target_language=target_language,
                        source_language=source_language
                    ))
                    for text in batch
                ]
                
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                
                for j, result in enumerate(batch_results):
                    if isinstance(result, Exception):
                        # Create error response for failed translations
                        translations.append(TranslationResponse(
                            original_text=batch[j],
                            translated_text=f"Translation failed: {str(result)}",
                            source_language="unknown",
                            target_language=target_language,
                            confidence=0.0
                        ))
                    else:
                        translations.append(result)
                
                # Small delay between batches to be respectful to the service
                if i + batch_size < len(texts):
                    await asyncio.sleep(0.1)
            
            return translations
            
        except Exception as e:
            raise Exception(f"Batch translation failed: {str(e)}")

    def is_language_supported(self, language_code: str) -> bool:
        """Check if a language is supported."""
        return language_code.lower() in self.supported_languages

    def get_language_name(self, language_code: str) -> str:
        """Get the full name of a language from its code."""
        return self.supported_languages.get(language_code.lower(), language_code)

    async def auto_translate_note_content(
        self,
        content: str,
        target_language: str,
        preserve_formatting: bool = True
    ) -> str:
        """
        Translate note content while preserving markdown formatting.
        """
        try:
            if not preserve_formatting:
                # Simple translation
                result = await self.translate_text(TranslationRequest(
                    text=content,
                    target_language=target_language
                ))
                return result.translated_text
            
            # Advanced: Preserve markdown formatting
            # Split content into translatable parts and non-translatable parts
            import re
            
            # Patterns for markdown elements to preserve
            patterns = [
                r'```[\s\S]*?```',  # Code blocks
                r'`[^`\n]+`',       # Inline code
                r'!\[.*?\]\(.*?\)', # Images
                r'\[.*?\]\(.*?\)',  # Links
                r'#{1,6}\s',        # Headers
                r'\*\*|\*|__',      # Bold/italic markers
                r'^\s*[-*+]\s',     # List markers
                r'^\s*\d+\.\s',     # Numbered lists
            ]
            
            # For now, do simple translation - full markdown parsing would be complex
            result = await self.translate_text(TranslationRequest(
                text=content,
                target_language=target_language
            ))
            
            return result.translated_text
            
        except Exception as e:
            raise Exception(f"Note translation failed: {str(e)}")