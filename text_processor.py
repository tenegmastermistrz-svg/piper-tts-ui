import re
import json

class TextProcessorEngine:
    def __init__(self, rules_file_path: str = 'rules_definitions.json'):
        self.rules = self._load_rules(rules_file_path)

    def _load_rules(self, rules_file_path: str) -> dict:
        with open(rules_file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def __call__(self, text: str) -> str:
        processed_text = text
        processed_text = self._apply_block_replacements(processed_text)
        processed_text = self._apply_regex_patterns_replacements(processed_text)
        processed_text = self._normalize_newlines(processed_text)
        processed_text = self._apply_string_replacements(processed_text)
        processed_text = self._apply_character_replacements(processed_text)
        return processed_text

    def _normalize_newlines(self, text: str) -> str:
        text = text.replace('\r\n', '\n')
        text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)
        text = re.sub(r'\n{2,}', '\n\n', text)
        return text

    def _apply_block_replacements(self, text: str) -> str:
        for start_delim, end_delim, replacement in self.rules.get('block_replacements', []):
            if start_delim and end_delim is not None:
                pattern = re.escape(start_delim) + r'[\s\S]*?' + re.escape(end_delim)
                text = re.sub(pattern, replacement, text)
        return text

    def _apply_regex_patterns_replacements(self, text: str) -> str:
        for pattern, replacement in self.rules.get('regex_patterns_replacements', []):
            if pattern:
                text = re.sub(pattern, replacement, text)
        return text

    def _apply_string_replacements(self, text: str) -> str:
        for old, new in self.rules.get('string_replacements', []):
            if old and new is not None:
                text = text.replace(old, new)
        return text

    def _apply_character_replacements(self, text: str) -> str:
        for old_chars, new_char in self.rules.get('character_replacements', []):
            if old_chars and new_char is not None:
                for char in old_chars:
                    text = text.replace(char, new_char)
        return text
