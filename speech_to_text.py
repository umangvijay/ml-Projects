import os
import speech_recognition as sr
from pydub import AudioSegment
import torch
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
import numpy as np
import tempfile
import logging
import librosa

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SpeechToText:
    def __init__(self, use_advanced_model=False):
        """
        Initialize the speech to text converter.
        
        Args:
            use_advanced_model (bool): Whether to use the advanced Wav2Vec2 model
                                      or the basic Google Speech Recognition API.
        """
        self.recognizer = sr.Recognizer()
        self.use_advanced_model = use_advanced_model
        
        # Load advanced model if requested
        if use_advanced_model:
            try:
                logger.info("Loading Wav2Vec2 model...")
                self.processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
                self.model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-base-960h")
                logger.info("Wav2Vec2 model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load Wav2Vec2 model: {e}")
                logger.info("Falling back to basic speech recognition")
                self.use_advanced_model = False
    
    def convert_audio_format(self, audio_file, target_format="wav"):
        """
        Convert audio file to the required format.
        
        Args:
            audio_file (str): Path to the audio file
            target_format (str): Target audio format
            
        Returns:
            str: Path to the converted audio file
        """
        try:
            # Get the file extension
            file_extension = os.path.splitext(audio_file)[1][1:].lower()
            
            # If the file is already in the target format, return it
            if file_extension == target_format:
                return audio_file
                
            # Create a temporary file for the converted audio
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f".{target_format}")
            temp_filename = temp_file.name
            temp_file.close()
            
            # Convert the audio file
            audio = AudioSegment.from_file(audio_file, format=file_extension)
            audio.export(temp_filename, format=target_format)
            
            logger.info(f"Converted {audio_file} to {target_format} format")
            return temp_filename
            
        except Exception as e:
            logger.error(f"Error converting audio format: {e}")
            return audio_file
    
    def transcribe_with_wav2vec2(self, audio_file):
        """
        Transcribe audio using the Wav2Vec2 model.
        
        Args:
            audio_file (str): Path to the audio file
            
        Returns:
            str: Transcribed text
        """
        try:
            # Convert audio to wav format if needed
            wav_file = self.convert_audio_format(audio_file, "wav")
            
            # Load audio
            audio, _ = librosa.load(wav_file, sr=16000)
            
            # Process audio
            input_values = self.processor(
                torch.tensor(audio), 
                sampling_rate=16000, 
                return_tensors="pt"
            ).input_values
            
            # Get logits
            with torch.no_grad():
                logits = self.model(input_values).logits
            
            # Get predicted ids
            predicted_ids = torch.argmax(logits, dim=-1)
            
            # Convert ids to text
            transcription = self.processor.batch_decode(predicted_ids)[0]
            
            # Clean up temporary file if created
            if wav_file != audio_file:
                os.unlink(wav_file)
                
            return transcription
            
        except Exception as e:
            logger.error(f"Error in Wav2Vec2 transcription: {e}")
            return None
    
    def transcribe_with_google(self, audio_file):
        """
        Transcribe audio using Google Speech Recognition.
        
        Args:
            audio_file (str): Path to the audio file
            
        Returns:
            str: Transcribed text
        """
        try:
            # Convert audio to wav format if needed
            wav_file = self.convert_audio_format(audio_file, "wav")
            
            # Load the audio file
            with sr.AudioFile(wav_file) as source:
                audio_data = self.recognizer.record(source)
            
            # Recognize speech using Google Speech Recognition
            text = self.recognizer.recognize_google(audio_data)
            
            # Clean up temporary file if created
            if wav_file != audio_file:
                os.unlink(wav_file)
                
            return text
            
        except sr.UnknownValueError:
            logger.warning("Google Speech Recognition could not understand audio")
            return None
        except sr.RequestError as e:
            logger.error(f"Could not request results from Google Speech Recognition service: {e}")
            return None
        except Exception as e:
            logger.error(f"Error in Google transcription: {e}")
            return None
    
    def transcribe_from_file(self, audio_file):
        """
        Transcribe speech from an audio file.
        
        Args:
            audio_file (str): Path to the audio file
            
        Returns:
            str: Transcribed text
        """
        if not os.path.exists(audio_file):
            logger.error(f"Audio file not found: {audio_file}")
            return None
            
        logger.info(f"Transcribing audio file: {audio_file}")
        
        if self.use_advanced_model:
            text = self.transcribe_with_wav2vec2(audio_file)
            if text is None:
                logger.info("Falling back to Google Speech Recognition")
                text = self.transcribe_with_google(audio_file)
        else:
            text = self.transcribe_with_google(audio_file)
            
        return text
    
    def transcribe_from_microphone(self, duration=5):
        """
        Transcribe speech from microphone.
        
        Args:
            duration (int): Recording duration in seconds
            
        Returns:
            str: Transcribed text
        """
        try:
            logger.info(f"Recording audio for {duration} seconds...")
            
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source, timeout=duration)
            
            logger.info("Recording complete, transcribing...")
            
            if self.use_advanced_model:
                # Save audio to a temporary file
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
                temp_filename = temp_file.name
                temp_file.close()
                
                with open(temp_filename, "wb") as f:
                    f.write(audio.get_wav_data())
                
                text = self.transcribe_with_wav2vec2(temp_filename)
                os.unlink(temp_filename)
                
                if text is None:
                    logger.info("Falling back to Google Speech Recognition")
                    text = self.recognizer.recognize_google(audio)
            else:
                text = self.recognizer.recognize_google(audio)
                
            return text
            
        except sr.UnknownValueError:
            logger.warning("Google Speech Recognition could not understand audio")
            return None
        except sr.RequestError as e:
            logger.error(f"Could not request results from Google Speech Recognition service: {e}")
            return None
        except Exception as e:
            logger.error(f"Error in microphone transcription: {e}")
            return None


# Example usage
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Convert speech to text")
    parser.add_argument("--input", help="Path to the audio file")
    parser.add_argument("--advanced", action="store_true", help="Use advanced model")
    parser.add_argument("--mic", action="store_true", help="Use microphone as input")
    parser.add_argument("--duration", type=int, default=5, help="Recording duration in seconds")
    
    args = parser.parse_args()
    
    converter = SpeechToText(use_advanced_model=args.advanced)
    
    if args.mic:
        text = converter.transcribe_from_microphone(duration=args.duration)
    elif args.input:
        text = converter.transcribe_from_file(args.input)
    else:
        parser.print_help()
        exit(1)
    
    if text:
        print(f"Transcribed text: {text}")
    else:
        print("Transcription failed") 