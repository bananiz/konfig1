import unittest
import os
import subprocess
import shutil
from visualizer import load_config, get_commits_with_file, build_dependency_graph, save_output

class TestVisualizer(unittest.TestCase):
    def setUp(self):
        # Создаем тестовый репозиторий и файл
        self.test_repo_path = 'test_repo'
        os.makedirs(self.test_repo_path, exist_ok=True)
        subprocess.run(['git', 'init'], cwd=self.test_repo_path)
        with open(os.path.join(self.test_repo_path, 'test_file.txt'), 'w') as f:
            f.write('Test content')
        subprocess.run(['git', 'add', '.'], cwd=self.test_repo_path)
        subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=self.test_repo_path)

    def tearDown(self):
        # Удаляем тестовый репозиторий после завершения тестов
        shutil.rmtree(self.test_repo_path)

    def test_load_config(self):
        config = load_config('test_config.yaml')
        self.assertIn('repository_path', config)
        self.assertIn('file_hash', config)
        self.assertIn('output_path', config)

    def test_get_commits_with_file(self):
        commits = get_commits_with_file(self.test_repo_path, 'test_file.txt')
        self.assertTrue(len(commits) > 0)

    def test_build_dependency_graph(self):
        commits = [
            ('commit1', 'Author1', '2023-01-01T00:00:00'),
            ('commit2', 'Author2', '2023-01-02T00:00:00')
        ]
        graph = build_dependency_graph(commits)
        self.assertIn('commit1', graph)
        self.assertIn('commit2', graph)

    def test_save_output(self):
        output_path = os.path.join(self.test_repo_path, 'test_output.md')
        graph_code = "graph TD\n  commit1[\"commit1\nAuthor1\n2023-01-01T00:00:00\"]\n"
        save_output(output_path, graph_code)
        with open(output_path, 'r') as f:
            content = f.read()
        self.assertEqual(content, graph_code)

if __name__ == '__main__':
    unittest.main()
