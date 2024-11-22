import json
import re
import argparse
import sys

class ConfigParser:
    CONSTANTS = {}

    def __init__(self, text):
        self.text = text
        self.index = 0

    def parse(self):
        """Запуск парсинга текста конфигурации."""
        return self._parse_dict()

    def _parse_dict(self):
        """Парсинг словаря."""
        self._consume_whitespace()
        if self._peek() != '{':
            self._error("Ожидался символ '{'")
        self._consume_char()

        dictionary = {}
        while True:
            self._consume_whitespace()
            if self._peek() == '}':
                self._consume_char()
                break
            if len(dictionary) > 0:
                if self._peek() != ',':
                    self._error("Ожидался символ ',' между элементами словаря")
                self._consume_char()
                self._consume_whitespace()

            key = self._parse_name()
            self._consume_whitespace()
            if self._peek() != ':':
                self._error("Ожидался символ ':' после имени ключа")
            self._consume_char()
            self._consume_whitespace()

            value = self._parse_value()
            dictionary[key] = value

        return dictionary

    def _parse_value(self):
        """Парсинг значения (число, строка или словарь)."""
        self._consume_whitespace()
        char = self._peek()

        if char.isdigit() or char == '-':
            return self._parse_number()
        elif char == '"':
            return self._parse_string()
        elif char == '{':
            return self._parse_dict()
        elif char == '?':
            return self._parse_constant()
        else:
            self._error(f"Неизвестный символ для значения: {char}")

    def _parse_number(self):
        """Парсинг числа."""
        number_match = re.match(r'-?\d+', self.text[self.index:])
        if not number_match:
            self._error("Неверный формат числа")
        number = int(number_match.group(0))
        self.index += len(number_match.group(0))
        return number

    def _parse_string(self):
        """Парсинг строки."""
        if self._peek() != '"':
            self._error("Ожидался символ '\"' для начала строки")
        self._consume_char()
        end_index = self.text.find('"', self.index)
        if end_index == -1:
            self._error("Строка не закрыта")
        string_value = self.text[self.index:end_index]
        self.index = end_index + 1
        return string_value

    def _parse_name(self):
        """Парсинг имени."""
        # Регулярное выражение для имени поддерживает заглавные буквы и цифры.
        name_match = re.match(r'[_A-Z][_A-Z0-9]*', self.text[self.index:])
        if not name_match:
            self._error("Неверный формат имени")
        name = name_match.group(0)
        self.index += len(name)
        return name

    def _parse_constant(self):
        """Вычисление значения константы."""
        if not self.text[self.index:].startswith("?["):
            self._error("Ожидалось вычисление константы")
        self.index += 2
        const_name = self._parse_name()
        self._consume_whitespace()
        if self._peek() != ']':
            self._error("Ожидался символ ']' после имени константы")
        self._consume_char()
        if const_name not in ConfigParser.CONSTANTS:
            self._error(f"Неизвестная константа: {const_name}")
        return ConfigParser.CONSTANTS[const_name]

    def _consume_whitespace(self):
        """Пропуск пробельных символов."""
        while self.index < len(self.text) and self.text[self.index].isspace():
            self.index += 1

    def _consume_char(self):
        """Потребление одного символа."""
        char = self.text[self.index]
        self.index += 1
        return char

    def _peek(self):
        """Получение текущего символа без потребления."""
        if self.index >= len(self.text):
            return ''
        return self.text[self.index]

    def _error(self, message):
        """Генерация ошибки синтаксиса."""
        raise ValueError(f"Синтаксическая ошибка на позиции {self.index}: {message}")

def main():
    parser = argparse.ArgumentParser(description="Парсер конфигурационного языка в JSON")
    parser.add_argument('input_file', help="Путь к файлу с конфигурацией")
    args = parser.parse_args()

    try:
        with open(args.input_file, 'r') as file:
            text = file.read()

        # Обработка констант
        for match in re.finditer(r'set\s+([_A-Z][_A-Z0-9]*)\s*=\s*(.+)', text):
            const_name, const_value = match.groups()
            # Обработка числовых значений
            if re.match(r'-?\d+', const_value):
                ConfigParser.CONSTANTS[const_name] = int(const_value)
            # Обработка строковых значений
            elif re.match(r'"[^"]*"', const_value):
                ConfigParser.CONSTANTS[const_name] = const_value.strip('"')
            else:
                raise ValueError(f"Неверное значение константы: {const_value}")

        # Удаляем определения констант из текста
        text = re.sub(r'set\s+[_A-Z][_A-Z0-9]*\s*=\s*.+', '', text)

        parser = ConfigParser(text)
        parsed = parser.parse()

        # Вывод результата
        print(json.dumps(parsed, indent=4, ensure_ascii=False))
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
