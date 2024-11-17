import argparse
import os
import tarfile
import tkinter as tk
from tkinter import scrolledtext


def create_test_tar(tar_path):
    """Создание тестового tar-архива для демонстрации с несколькими папками."""
    base_dir = "virtual_fs"
    os.makedirs(base_dir, exist_ok=True)

    # Создание нескольких файлов и директорий
    os.makedirs(os.path.join(base_dir, "subdir"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "another_subdir"), exist_ok=True)

    # Добавление файлов в различные директории
    with open(os.path.join(base_dir, "file1.txt"), "w") as f:
        f.write("This is file1.txt\n")
    with open(os.path.join(base_dir, "subdir", "file2.txt"), "w") as f:
        f.write("This is file2.txt in subdir\n")
    with open(os.path.join(base_dir, "subdir", "file3.txt"), "w") as f:
        f.write("This is file3.txt in subdir\n")
    with open(os.path.join(base_dir, "another_subdir", "file4.txt"), "w") as f:
        f.write("This is file4.txt in another_subdir\n")
    with open(os.path.join(base_dir, "another_subdir", "file5.txt"), "w") as f:
        f.write("This is file5.txt in another_subdir\n")

    # Создание tar-архива
    with tarfile.open(tar_path, "w") as tar:
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                file_path = os.path.join(root, file)
                tar.add(file_path, arcname=os.path.relpath(file_path, base_dir))

    # Удаление временной структуры файлов после архивации
    for root, dirs, files in os.walk(base_dir, topdown=False):
        for file in files:
            os.remove(os.path.join(root, file))
        for dir in dirs:
            os.rmdir(os.path.join(root, dir))
    os.rmdir(base_dir)

    print(f"Test tar archive created at {tar_path}")


class ShellEmulator:
    def __init__(self, username, startup_script, tar_path, output_widget=None):
        self.root = tk.Tk()
        self.username = username
        self.startup_script = startup_script
        self.tar_path = tar_path
        self.file_system = {}
        self.current_path = '/'
        self.output_widget = output_widget
        self.load_virtual_fs()
        self.run_startup_script()

    def load_virtual_fs(self):
        """Загрузка виртуальной файловой системы из tar-архива."""
        try:
            with tarfile.open(self.tar_path, "r") as tar:
                for member in tar.getmembers():
                    if member.isfile():
                        # Считываем содержимое файла и сохраняем в словарь
                        self.file_system[member.name] = tar.extractfile(member).read().decode('utf-8')
            self.output_widget.insert(tk.END, f"Virtual filesystem loaded from {self.tar_path}\n")
        except Exception as e:
            self.output_widget.insert(tk.END, f"Error loading virtual filesystem: {str(e)}\n")

    def run_startup_script(self):
        """Запуск стартового скрипта."""
        if os.path.isfile(self.startup_script):
            with open(self.startup_script, 'r') as f:
                for command in f:
                    self.execute_command(command.strip())

    def execute_command(self, command):
        """Исполнение команды."""
        if not command.strip():  # Игнорирование пустых команд
            return
        if command.startswith('ls'):
            self.list_files()
        elif command.startswith('cd'):
            args = command.split()
            if len(args) > 1:
                self.change_directory(args[1])
            else:
                self.output_widget.insert(tk.END, "Usage: cd <directory>\n")
        elif command.startswith('exit'):
            self.exit_emulator()
        elif command.startswith('find'):
            args = command.split()
            if len(args) > 1:
                self.find_file(args[1])
            else:
                self.output_widget.insert(tk.END, "Usage: find <filename>\n")
        elif command.startswith('chown'):
            args = command.split()
            if len(args) > 2:
                self.change_owner(args[1], args[2])
            else:
                self.output_widget.insert(tk.END, "Usage: chown <file> <new_owner>\n")
        else:
            self.output_widget.insert(tk.END, f"Unknown command: {command}\n")

    def list_files(self):
        """Вывод списка файлов и директорий в текущей директории."""
        dir_path = self.current_path.lstrip('/') + '/' if self.current_path != '/' else ''

        # Разделяем файлы и каталоги
        files = []
        directories = set()

        for name in self.file_system.keys():
            if name.startswith(dir_path):
                remaining_path = name[len(dir_path):]
                if '/' in remaining_path:
                    directories.add(remaining_path.split('/')[0])
                else:
                    files.append(remaining_path)

        self.output_widget.insert(tk.END, f"Files in {self.current_path}:\n")
        if directories:
            self.output_widget.insert(tk.END, "Directories:\n")
            self.output_widget.insert(tk.END, "\n".join(sorted(directories)) + "\n")
        if files:
            self.output_widget.insert(tk.END, "Files:\n")
            self.output_widget.insert(tk.END, "\n".join(sorted(files)) + "\n")
        if not files and not directories:
            self.output_widget.insert(tk.END, "No files or directories found.\n")

    def change_directory(self, path):
        """Изменение текущей директории."""
        if path == '/':
            self.current_path = '/'
            return

        new_path = os.path.normpath(os.path.join(self.current_path, path)).lstrip('/')
        if new_path == '':
            new_path = '/'

        # Проверка на существование директории в virtual_fs
        if any(key.startswith(new_path + '/') or new_path == key for key in self.file_system.keys()):
            self.current_path = '/' + new_path
        else:
            self.output_widget.insert(tk.END, f"No such directory: {path}\n")

    def get_directories(self):
        """Возвращает список директорий в виртуальной файловой системе."""
        return set(os.path.dirname(path) for path in self.file_system.keys())

    def exit_emulator(self):
        """Выход из эмулятора."""
        if self.root:
            self.root.quit()
            self.root.destroy()

    def find_file(self, filename):
        """Поиск файла или директории в виртуальной файловой системе."""
        found_items = []
        for name in self.file_system.keys():
            # Проверяем, содержит ли путь искомое имя (файлы и папки)
            if filename in os.path.basename(name) or filename in os.path.dirname(name):
                found_items.append(name)

        if found_items:
            self.output_widget.insert(tk.END, "Found items:\n")
            self.output_widget.insert(tk.END, "\n".join(found_items) + "\n")
        else:
            self.output_widget.insert(tk.END, f"No items found matching: {filename}\n")

    def change_owner(self, file_path, new_owner):
        """Изменение владельца файла или директории."""
        try:
            if file_path not in self.file_system:
                self.output_widget.insert(tk.END, f"No such file or directory: {file_path}\n")
                return

            # Эмуляция изменения владельца
            self.file_system[file_path] = {'owner': new_owner}
            self.output_widget.insert(tk.END, f"Changed owner of {file_path} to {new_owner}\n")
        except Exception as e:
            self.output_widget.insert(tk.END, f"Error changing owner: {str(e)}\n")


def main():
    global root
    parser = argparse.ArgumentParser(description='Shell Emulator')
    parser.add_argument('--username', required=True, help='Username for the shell prompt')
    parser.add_argument('--startup_script', required=True, help='Path to the startup script')
    parser.add_argument('--tar_path', required=True, help='Path to the tar archive of the virtual filesystem')

    args = parser.parse_args()

    # Если архив не существует, создаём его
    if not os.path.exists(args.tar_path):
        create_test_tar(args.tar_path)

    root = tk.Tk()
    root.title("Shell Emulator")

    output_widget = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=20)
    output_widget.pack()

    emulator = ShellEmulator(args.username, args.startup_script, args.tar_path, output_widget)

    def on_command_entered(event):
        command = command_entry.get()
        emulator.execute_command(command)
        command_entry.delete(0, tk.END)

    command_entry = tk.Entry(root)
    command_entry.pack()
    command_entry.bind('<Return>', on_command_entered)

    root.mainloop()


if __name__ == '__main__':
    main()
