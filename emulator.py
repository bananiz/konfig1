import argparse
import os
import tkinter as tk
from tkinter import scrolledtext


class ShellEmulator:
    def __init__(self, username, startup_script, output_widget):
        self.username = username
        self.startup_script = startup_script
        self.current_path = os.getcwd()  # Устанавливаем текущий путь на рабочую директорию
        self.output_widget = output_widget
        self.run_startup_script()

    def run_startup_script(self):
        if os.path.isfile(self.startup_script):
            with open(self.startup_script, 'r') as f:
                for command in f:
                    self.execute_command(command.strip())

    def execute_command(self, command):
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
        try:
            file_list = os.listdir(self.current_path)
            self.output_widget.insert(tk.END, f"Files in {self.current_path}:\n")
            if file_list:
                self.output_widget.insert(tk.END, "\n".join(file_list) + "\n")
            else:
                self.output_widget.insert(tk.END, "No files found.\n")
        except Exception as e:
            self.output_widget.insert(tk.END, f"Error listing files: {str(e)}\n")

    def change_directory(self, path):
        try:
            new_path = os.path.abspath(os.path.join(self.current_path, path))
            if os.path.isdir(new_path):
                self.current_path = new_path
            else:
                self.output_widget.insert(tk.END, f"No such directory: {path}\n")
        except Exception as e:
            self.output_widget.insert(tk.END, f"Error changing directory: {str(e)}\n")

    def exit_emulator(self):
        self.output_widget.insert(tk.END, "Exiting emulator.\n")
        root.quit()

    def find_file(self, filename):
        found_files = []
        for root, dirs, files in os.walk(self.current_path):
            for name in files:
                if filename in name:
                    found_files.append(os.path.join(root, name))

        if found_files:
            self.output_widget.insert(tk.END, "Found files: " + ', '.join(found_files) + "\n")
        else:
            self.output_widget.insert(tk.END, f"No files found matching: {filename}\n")

    def change_owner(self, file_path, new_owner):
        try:
            if not new_owner:  # Проверка на наличие второго аргумента
                self.output_widget.insert(tk.END, "Usage: chown <file> <new_owner>\n")
                return

            if os.path.exists(file_path):
                # Изменение владельца файла требует привилегий, поэтому это просто пример
                self.output_widget.insert(tk.END, f"Changed owner of {file_path} to {new_owner}\n")
            else:
                self.output_widget.insert(tk.END, f"No such file: {file_path}\n")
        except Exception as e:
            self.output_widget.insert(tk.END, f"Error changing owner: {str(e)}\n")


def main():
    global root
    parser = argparse.ArgumentParser(description='Shell Emulator')
    parser.add_argument('--username', required=True, help='Username for the shell prompt')
    parser.add_argument('--startup_script', required=True, help='Path to the startup script')

    args = parser.parse_args()

    root = tk.Tk()
    root.title("Shell Emulator")

    output_widget = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=20)
    output_widget.pack()

    emulator = ShellEmulator(args.username, args.startup_script, output_widget)

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
