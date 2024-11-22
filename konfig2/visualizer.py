import os
import zlib
import yaml

def load_config(config_path):
    """Загружает конфигурацию из YAML файла."""
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
        print("Loaded config:")
        print(config)
        return config

def decompress_object(data):
    """Разжимает объект Git."""
    decompressed = zlib.decompress(data)
    header, _, body = decompressed.partition(b'\x00')
    return body.decode('utf-8', errors='ignore')

def get_commit_info(repository_path, commit_hash):
    """Получает информацию о коммите по его хешу."""
    print(f"Repository Path: {repository_path}")
    print(f"Commit Hash: {commit_hash}")

    # Формируем путь к объекту коммита
    object_dir = os.path.join(repository_path, '.git', 'objects', commit_hash[:2])
    object_file = os.path.join(object_dir, commit_hash[2:])

    if not os.path.exists(object_file):
        print(f"Error: The commit object {object_file} does not exist.")
        return None

    # Читаем и разжимаем объект коммита
    with open(object_file, 'rb') as f:
        data = f.read()
        commit_content = decompress_object(data)

    print(f"Commit content:\n{commit_content}")

    # Извлекаем информацию о коммите
    lines = commit_content.split('\n')
    commit_info = {
        'hash': commit_hash,
        'author': '',
        'date': '',
        'message': ''
    }

    for line in lines:
        if line.startswith('author'):
            commit_info['author'] = line.split(' ', 1)[1]
        elif line.startswith('date'):
            commit_info['date'] = line.split(' ', 1)[1]
        elif line.startswith('    '):
            commit_info['message'] += line.strip() + '\n'

    return (commit_info['hash'], commit_info['author'], commit_info['date'])

def get_commits_with_file(repository_path, file_path):
    """Получает коммиты, связанные с файлом, по его пути."""
    print(f"Repository Path: {repository_path}")
    print(f"File Path: {file_path}")

    # Формируем путь к объекту файла
    full_file_path = os.path.join(repository_path, file_path)
    if not os.path.exists(full_file_path):
        print(f"Error: The file {full_file_path} does not exist in the repository.")
        return []

    # Ищем коммиты, связанные с файлом
    commits = []
    for root, dirs, files in os.walk(os.path.join(repository_path, '.git', 'objects')):
        for file in files:
            if file.endswith('.idx'):
                continue
            object_file = os.path.join(root, file)
            with open(object_file, 'rb') as f:
                data = f.read()
                try:
                    object_content = decompress_object(data)
                    if file_path in object_content:
                        commit_hash = os.path.basename(root) + file
                        commit_info = get_commit_info(repository_path, commit_hash)
                        if commit_info:
                            commits.append(commit_info)
                except zlib.error:
                    continue

    return commits

def save_output(output_path, graph_code):
    """Сохраняет граф в файл."""
    # Создание директории, если она не существует
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w') as file:
        file.write(graph_code)
    print(f"Graph saved to {output_path}")
    print(graph_code)

def build_dependency_graph(commits):
    """Строит граф зависимостей для полученных коммитов."""
    graph = "graph TD\n"

    for i, (commit_hash, author, date) in enumerate(commits):
        graph += f"  {commit_hash[:7]}[\"{commit_hash[:7]}\n{author}\n{date}\"]\n"
        if i > 0:
            graph += f"  {commits[i - 1][0][:7]} --> {commit_hash[:7]}\n"

    return graph

def main():
    # Загрузим конфигурацию
    config = load_config('config.yaml')

    repository_path = config['repository_path']
    file_path = config['file_hash']  # Это путь к файлу
    output_path = config['output_path']

    if not os.path.isdir(repository_path):
        print(f"Error: The repository path {repository_path} is not valid.")
        return

    # Получаем коммиты для файла (по пути)
    commits = get_commits_with_file(repository_path, file_path)

    if commits:
        # Строим граф зависимости для найденных коммитов
        graph = build_dependency_graph(commits)

        # Сохраняем граф в файл
        save_output(output_path, graph)
    else:
        print("No commits found for the specified file path.")

if __name__ == '__main__':
    main()
