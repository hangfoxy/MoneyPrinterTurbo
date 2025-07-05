import json
import locale
import os
from pathlib import Path
import threading
from typing import Any
from uuid import uuid4

import urllib3
from loguru import logger

from app.models import const

urllib3.disable_warnings()


def get_response(status: int, data: Any = None, message: str = ""):
    obj = {
        "status": status,
    }
    if data:
        obj["data"] = data
    if message:
        obj["message"] = message
    return obj


def to_json(obj):
    try:
        # Define a helper function to handle different types of objects
        def serialize(o):
            # If the object is a serializable type, return it directly
            if isinstance(o, (int, float, bool, str)) or o is None:
                return o
            # If the object is binary data, convert it to a base64-encoded string
            elif isinstance(o, bytes):
                return "*** binary data ***"
            # If the object is a dictionary, recursively process each key-value pair
            elif isinstance(o, dict):
                return {k: serialize(v) for k, v in o.items()}
            # If the object is a list or tuple, recursively process each element
            elif isinstance(o, (list, tuple)):
                return [serialize(item) for item in o]
            # If the object is a custom type, attempt to return its __dict__ attribute
            elif hasattr(o, "__dict__"):
                return serialize(o.__dict__)
            # Return None for other cases (or choose to raise an exception)
            else:
                return None

        # Use the serialize function to process the input object
        serialized_obj = serialize(obj)

        # Serialize the processed object into a JSON string
        return json.dumps(serialized_obj, ensure_ascii=False, indent=4)
    except Exception:
        return None


def get_uuid(remove_hyphen: bool = False):
    u = str(uuid4())
    if remove_hyphen:
        u = u.replace("-", "")
    return u


def root_dir():
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


def storage_dir(sub_dir: str = "", create: bool = False):
    d = os.path.join(root_dir(), "storage")
    if sub_dir:
        d = os.path.join(d, sub_dir)
    if create and not os.path.exists(d):
        os.makedirs(d)

    return d


def resource_dir(sub_dir: str = ""):
    d = os.path.join(root_dir(), "resource")
    if sub_dir:
        d = os.path.join(d, sub_dir)
    return d


def task_dir(sub_dir: str = ""):
    d = os.path.join(storage_dir(), "tasks")
    if sub_dir:
        d = os.path.join(d, sub_dir)
    if not os.path.exists(d):
        os.makedirs(d)
    return d


def font_dir(sub_dir: str = ""):
    d = resource_dir("fonts")
    if sub_dir:
        d = os.path.join(d, sub_dir)
    if not os.path.exists(d):
        os.makedirs(d)
    return d


def song_dir(sub_dir: str = ""):
    d = resource_dir("songs")
    if sub_dir:
        d = os.path.join(d, sub_dir)
    if not os.path.exists(d):
        os.makedirs(d)
    return d


def public_dir(sub_dir: str = ""):
    d = resource_dir("public")
    if sub_dir:
        d = os.path.join(d, sub_dir)
    if not os.path.exists(d):
        os.makedirs(d)
    return d


def run_in_background(func, *args, **kwargs):
    def run():
        try:
            func(*args, **kwargs)
        except Exception as e:
            logger.error(f"run_in_background error: {e}")

    thread = threading.Thread(target=run)
    thread.start()
    return thread


def time_convert_seconds_to_hmsm(seconds) -> str:
    hours = int(seconds // 3600)
    seconds = seconds % 3600
    minutes = int(seconds // 60)
    milliseconds = int(seconds * 1000) % 1000
    seconds = int(seconds % 60)
    return "{:02d}:{:02d}:{:02d},{:03d}".format(hours, minutes, seconds, milliseconds)


def text_to_srt(idx: int, msg: str, start_time: float, end_time: float) -> str:
    start_time = time_convert_seconds_to_hmsm(start_time)
    end_time = time_convert_seconds_to_hmsm(end_time)
    srt = """%d
%s --> %s
%s
        """ % (
        idx,
        start_time,
        end_time,
        msg,
    )
    return srt


def str_contains_punctuation(word):
    for p in const.PUNCTUATIONS:
        if p in word:
            return True
    return False


def split_string_by_punctuations(s):
    result = []
    txt = ""

    previous_char = ""
    next_char = ""
    for i in range(len(s)):
        char = s[i]
        if char == "\n":
            result.append(txt.strip())
            txt = ""
            continue

        if i > 0:
            previous_char = s[i - 1]
        if i < len(s) - 1:
            next_char = s[i + 1]

        if char == "." and previous_char.isdigit() and next_char.isdigit():
            # # In the case of "withdraw 10,000, charged at 2.5% fee", the dot in "2.5" should not be treated as a line break marker
            txt += char
            continue

        if char not in const.PUNCTUATIONS:
            txt += char
        else:
            result.append(txt.strip())
            txt = ""
    result.append(txt.strip())
    # filter empty string
    result = list(filter(None, result))
    return result


def md5(text):
    import hashlib

    return hashlib.md5(text.encode("utf-8")).hexdigest()


def get_system_locale():
    try:
        loc = locale.getdefaultlocale()
        # zh_CN, zh_TW return zh
        # en_US, en_GB return en
        language_code = loc[0].split("_")[0]
        return language_code
    except Exception:
        return "en"


def load_locales(i18n_dir):
    _locales = {}
    for root, dirs, files in os.walk(i18n_dir):
        for file in files:
            if file.endswith(".json"):
                lang = file.split(".")[0]
                with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                    _locales[lang] = json.loads(f.read())
    return _locales


def parse_extension(filename):
    return Path(filename).suffix.lower().lstrip('.')


def parse_timestamp(timestamp_str):
    """Convert timestamp string to milliseconds"""
    time_part = timestamp_str.replace(',', '.')
    h, m, s = time_part.split(':')
    return int(float(h) * 3600000 + float(m) * 60000 + float(s) * 1000)

def format_timestamp(milliseconds):
    """Convert milliseconds back to SRT timestamp format"""
    hours = milliseconds // 3600000
    minutes = (milliseconds % 3600000) // 60000
    seconds = (milliseconds % 60000) // 1000
    ms = milliseconds % 1000
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{ms:03d}"

def split_subtitle_line_to_words(subtitle_line):
    """
    Split a subtitle line into individual words with evenly distributed timestamps
    
    Args:
        subtitle_line (str): Single subtitle line in format "start --> end text"
    
    Returns:
        list: List of subtitle lines with individual words
    """
    # Parse the input line
    parts = subtitle_line.split(' --> ')
    if len(parts) != 2:
        raise ValueError("Invalid subtitle format")
    
    start_time_str = parts[0]
    end_and_text = parts[1].split(' ', 1)
    end_time_str = end_and_text[0]
    text = end_and_text[1] if len(end_and_text) > 1 else ""
    
    # Convert timestamps to milliseconds
    start_ms = parse_timestamp(start_time_str)
    end_ms = parse_timestamp(end_time_str)
    
    # Split text into words
    words = text.split()
    if not words:
        return []
    
    # Calculate time duration per word
    total_duration = end_ms - start_ms
    duration_per_word = total_duration / len(words)
    
    # Create subtitle lines for each word
    result = []
    for i, word in enumerate(words):
        word_start = start_ms + int(i * duration_per_word)
        word_end = start_ms + int((i + 1) * duration_per_word)
        
        # Ensure the last word ends at the original end time
        if i == len(words) - 1:
            word_end = end_ms
        
        start_formatted = format_timestamp(word_start)
        end_formatted = format_timestamp(word_end)
        
        result.append(f"{start_formatted} --> {end_formatted} {word}")
    
    return result

def read_srt_file(file_path):
    """
    Read and parse SRT file
    
    Args:
        file_path (str): Path to the SRT file
    
    Returns:
        list: List of subtitle entries, each containing sequence, timing, and text
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Split by double newlines to separate subtitle blocks
    blocks = content.strip().split('\n\n')
    subtitles = []
    
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) >= 3:
            sequence = lines[0]
            timing = lines[1]
            text = ' '.join(lines[2:])  # Join multiple text lines
            subtitles.append({
                'sequence': sequence,
                'timing': timing,
                'text': text
            })
    
    return subtitles

def process_srt_file(subtitles):
    """
    Process subtitle entries and return word-split results with proper SRT formatting
    
    Args:
        subtitles (list): List of subtitle dictionaries from read_srt_file
    
    Returns:
        str: Complete SRT content with word-split subtitles
    """
    result_lines = []
    sequence_counter = 1
    
    for subtitle in subtitles:
        timing = subtitle['timing']
        text = subtitle['text']
        
        # Create the timing line with text for processing
        timing_with_text = f"{timing} {text}"
        
        # Split into words
        word_lines = split_subtitle_line_to_words(timing_with_text)
        
        # Add each word as a separate subtitle entry
        for word_line in word_lines:
            # Split the word line back into timing and text
            parts = word_line.split(' --> ')
            start_time = parts[0]
            end_and_word = parts[1].split(' ', 1)
            end_time = end_and_word[0]
            word = end_and_word[1] if len(end_and_word) > 1 else ""
            word = word.upper()
            
            # Format as SRT entry
            result_lines.append(str(sequence_counter))
            result_lines.append(f"{start_time} --> {end_time}")
            result_lines.append(word)
            result_lines.append("")  # Empty line between entries
            
            sequence_counter += 1
    
    return '\n'.join(result_lines)

def save_srt_file(content, output_path):
    """
    Save SRT content to file
    
    Args:
        content (str): SRT content to save
        output_path (str): Path where to save the file
    """
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(content)

def process_srt_file_complete(input_path, output_path):
    """
    Complete workflow: read SRT file, split words, save result
    
    Args:
        input_path (str): Path to input SRT file
        output_path (str): Path to save output SRT file
    """
    try:
        subtitles = read_srt_file(input_path)
        word_split_content = process_srt_file(subtitles)
        save_srt_file(word_split_content, output_path)
        print(f"Successfully processed {input_path} -> {output_path}")
        print(f"Original subtitles: {len(subtitles)}")
        print(f"Word-split subtitles: {word_split_content.count('-->')}")
    except Exception as e:
        print(f"Error processing SRT file: {e}")
        return ""