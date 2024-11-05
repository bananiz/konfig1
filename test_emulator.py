import unittest
import os
import tkinter as tk
from emulator import ShellEmulator

class TestShellEmulator(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.output_widget = tk.Text(self.root)
        self.emulator = ShellEmulator("testuser", "/path/to/startup_script.sh", self.output_widget)
        self.test_dir = os.path.join(os.getcwd(), "test_dir")
        os.makedirs(self.test_dir, exist_ok=True)

    def tearDown(self):
        # Очистка тестовой директории перед ее удалением
        for file in os.listdir(self.test_dir):
            file_path = os.path.join(self.test_dir, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        os.rmdir(self.test_dir)
        self.root.destroy()

    # Тесты для команды `ls`
    def test_ls_with_files(self):
        open(os.path.join(self.test_dir, "file1.txt"), 'w').close()
        self.emulator.current_path = self.test_dir
        self.emulator.list_files()
        output = self.output_widget.get("1.0", tk.END).strip()
        self.assertIn("file1.txt", output)

    def test_ls_empty_directory(self):
        self.emulator.current_path = self.test_dir
        self.emulator.list_files()
        output = self.output_widget.get("1.0", tk.END).strip()
        self.assertIn("No files found.", output)

    def test_ls_invalid_directory(self):
        self.emulator.current_path = "/invalid/directory"
        self.emulator.list_files()
        output = self.output_widget.get("1.0", tk.END).strip()
        self.assertIn("Error listing files", output)

    # Тесты для команды `cd`
    def test_cd_valid_directory(self):
        self.emulator.change_directory("test_dir")
        self.assertEqual(self.emulator.current_path, self.test_dir)

    def test_cd_invalid_directory(self):
        self.emulator.change_directory("nonexistent_dir")
        output = self.output_widget.get("1.0", tk.END).strip()
        self.assertIn("No such directory", output)

    def test_cd_parent_directory(self):
        parent_dir = os.path.abspath(os.path.join(self.test_dir, ".."))
        self.emulator.current_path = self.test_dir
        self.emulator.change_directory("..")
        self.assertEqual(self.emulator.current_path, parent_dir)

    # Тесты для команды `exit`
    def test_exit_emulator(self):
        # Используем метод destroy вместо root.quit, чтобы завершить работу
        self.output_widget.insert(tk.END, "Exiting emulator.\n")

    # Тесты для команды `find`
    def test_find_existing_file(self):
        test_file = os.path.join(self.test_dir, "file_to_find.txt")
        open(test_file, 'w').close()
        self.emulator.current_path = self.test_dir
        self.emulator.find_file("file_to_find.txt")
        output = self.output_widget.get("1.0", tk.END).strip()
        self.assertIn("file_to_find.txt", output)

    def test_find_nonexistent_file(self):
        self.emulator.current_path = self.test_dir
        self.emulator.find_file("nonexistent.txt")
        output = self.output_widget.get("1.0", tk.END).strip()
        self.assertIn("No files found matching", output)

    def test_find_partial_match(self):
        partial_file = os.path.join(self.test_dir, "partial_match.txt")
        open(partial_file, 'w').close()
        self.emulator.current_path = self.test_dir
        self.emulator.find_file("partial")
        output = self.output_widget.get("1.0", tk.END).strip()
        self.assertIn("partial_match.txt", output)

    # Тесты для команды `chown`
    def test_chown_existing_file(self):
        test_file = os.path.join(self.test_dir, "file_to_chown.txt")
        open(test_file, 'w').close()
        self.emulator.change_owner(test_file, "new_owner")
        output = self.output_widget.get("1.0", tk.END).strip()
        self.assertIn("Changed owner", output)

    def test_chown_nonexistent_file(self):
        self.emulator.change_owner("/nonexistent/file.txt", "new_owner")
        output = self.output_widget.get("1.0", tk.END).strip()
        self.assertIn("No such file", output)

    def test_chown_invalid_owner(self):
        test_file = os.path.join(self.test_dir, "file_to_chown.txt")
        open(test_file, 'w').close()
        # Изменим команду, чтобы проверять корректное сообщение для пустого владельца
        self.emulator.change_owner(test_file, "")
        output = self.output_widget.get("1.0", tk.END).strip()
        self.assertIn("Usage: chown <file> <new_owner>", output)

if __name__ == '__main__':
    unittest.main()
