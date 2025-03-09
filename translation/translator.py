from googletrans import Translator, LANGUAGES
from gtts import gTTS
import os
import tempfile
from playsound import playsound

class TranslationHandler:
    def __init__(self, speak_callback):
        self.translator = Translator()
        self.speak_callback = speak_callback
        # Common language mappings
        self.language_mapping = {
            'spanish': 'es',
            'french': 'fr',
            'german': 'de',
            'italian': 'it',
            'portuguese': 'pt',
            'russian': 'ru',
            'chinese': 'zh-cn',
            'japanese': 'ja',
            'korean': 'ko',
            'hindi': 'hi',
            'arabic': 'ar',
            'dutch': 'nl',
            'greek': 'el',
            'turkish': 'tr'
        }

    def get_language_code(self, language_name):
        """Convert full language name to language code"""
        language_name = language_name.lower().strip()
        
        # First check our common mappings
        if language_name in self.language_mapping:
            return self.language_mapping[language_name]
            
        # Then check LANGUAGES dict
        for code, name in LANGUAGES.items():
            if name.lower() == language_name:
                return code
        return None

    def speak_in_language(self, text, lang_name):
        """Convert text to speech in specified language"""
        try:
            # Get the language code
            lang_code = self.get_language_code(lang_name)
            if not lang_code:
                self.speak_callback(f"Sorry, I don't support speaking in {lang_name}")
                return False

            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                temp_path = temp_file.name

            # Generate speech
            tts = gTTS(text=text, lang=lang_code, slow=False)
            tts.save(temp_path)
            
            # Play the audio
            playsound(temp_path)
            
            # Clean up
            os.unlink(temp_path)
            return True
        except Exception as e:
            print(f"Error in text-to-speech: {str(e)}")
            self.speak_callback("I encountered an error while trying to speak the translation.")
            return False

    def translate_text(self, text, from_lang='auto', to_lang='en'):
        """Translate text between languages"""
        try:
            # Convert language names to codes
            if from_lang != 'auto':
                from_lang = self.get_language_code(from_lang)
                if not from_lang:
                    raise ValueError(f"Source language '{from_lang}' not recognized")

            to_lang = self.get_language_code(to_lang)
            if not to_lang:
                raise ValueError(f"Target language '{to_lang}' not recognized")

            translation = self.translator.translate(text, src=from_lang, dest=to_lang)
            return translation.text
        except Exception as e:
            print(f"Translation error: {str(e)}")
            return None

    def get_supported_languages(self):
        """Get list of supported languages"""
        return list(self.language_mapping.keys())
