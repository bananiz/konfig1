import unittest
from unittest.mock import MagicMock
import os
import tempfile
import tarfile
from io import StringIO
from emulator import ShellEmulator, create_test_tar


class TestShellEmulator(unittest.TestCase):

    def setUp(self):
        """Создаём временные файлы и эмулятор перед каждым тестом."""
        # Создаём временный tar-архив с виртуальной файловой системой
        self.tar_file = tempfile.NamedTemporaryFile(delete=False)
        create_test_tar(self.tar_file.name)

        # Создаём виджет для вывода
        self.output_widget = MagicMock()

        # Создаём эмулятор с тестовыми параметрами
        self.emulator = ShellEmulator(
            username="test_user",
            startup_script="startup.sh",  # Путь к стартовому скрипту (можно использовать пустой файл)
            tar_path=self.tar_file.name,
            output_widget=self.output_widget
        )

    def tearDown(self):
        """Удаляем временные файлы после каждого теста."""
        os.remove(self.tar_file.name)

    def test_list_files(self):
        """Тестируем команду 'ls'"""
        self.emulator.execute_command("ls")
        self.output_widget.insert.assert_called_with(
            'end', 'file2.txt\nfile3.txt\n'
        )

    def test_change_directory(self):
        """Тестируем команду 'cd'"""
        self.emulator.execute_command("cd subdir")
        self.assertEqual(self.emulator.current_path, '/subdir')

        # Попытка смены на несуществующую директорию
        self.emulator.execute_command("cd nonexistent_dir")
        self.output_widget.insert.assert_called_with(
            'end', 'No such directory: nonexistent_dir\n'
        )

    def test_change_owner(self):
        """Тестируем команду 'chown'"""
        self.emulator.execute_command("chown file1.txt new_owner")
        self.output_widget.insert.assert_called_with(
            'end', 'Changed owner of file1.txt to new_owner\n'
        )

    def test_change_owner_invalid(self):
        """Тестируем команду 'chown' с несуществующим файлом"""
        self.emulator.execute_command("chown nonexistent_file new_owner")
        self.output_widget.insert.assert_called_with(
            'end', 'No such file or directory: nonexistent_file\n'
        )

    def test_find_file(self):
        """Тестируем команду 'find'"""
        self.emulator.execute_command("find file2.txt")
        self.output_widget.insert.assert_called_with(
            'end', 'subdir/file2.txt\n'
        )

    def test_invalid_command(self):
        """Тестируем команду с ошибкой"""
        self.emulator.execute_command("invalid_command")
        self.output_widget.insert.assert_called_with(
            'end', 'Unknown command: invalid_command\n'
        )

    def test_exit_emulator(self):
        """Тестируем команду 'exit'"""
        self.emulator.exit_emulator = MagicMock()  # Мокаем метод exit_emulator для предотвращения закрытия GUI
        self.emulator.execute_command("exit")
        self.emulator.exit_emulator.assert_called_once()

    def test_no_files_or_dirs(self):
        """Тестируем сценарий, когда в директории нет файлов или подкаталогов"""
        self.emulator.current_path = '/non_existent_dir'
        self.emulator.execute_command("ls")
        self.output_widget.insert.assert_called_with(
            'end', 'No files or directories found.\n'
        )


if __name__ == '__main__':
    unittest.main()
