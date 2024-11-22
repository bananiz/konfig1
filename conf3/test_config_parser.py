import unittest
from config_parser import ConfigParser

class TestConfigParser(unittest.TestCase):

    def test_parse_number(self):
        parser = ConfigParser("123")
        result = parser._parse_number()
        self.assertEqual(result, 123)

    def test_parse_string(self):
        parser = ConfigParser('"hello world"')
        result = parser._parse_string()
        self.assertEqual(result, "hello world")

    def test_parse_dict(self):
        parser = ConfigParser('{KEY: "value", NUMBER: 42}')
        result = parser.parse()
        self.assertEqual(result, {"KEY": "value", "NUMBER": 42})

    def test_parse_constant(self):
        ConfigParser.CONSTANTS = {"THRESHOLD": 90}
        parser = ConfigParser('?[THRESHOLD]')
        result = parser._parse_constant()
        self.assertEqual(result, 90)

    def test_error_handling(self):
        parser = ConfigParser('{KEY: "value", NUMBER: 42')
        with self.assertRaises(ValueError):
            parser.parse()

    def test_parse_nested_dict(self):
        parser = ConfigParser('{OUTER: {INNER: "value"}}')
        result = parser.parse()
        self.assertEqual(result, {"OUTER": {"INNER": "value"}})

    def test_parse_multiple_constants(self):
        ConfigParser.CONSTANTS = {"THRESHOLD": 90, "HOSTNAME": "server1"}
        parser = ConfigParser('{HOSTNAME: ?[HOSTNAME], THRESHOLD: ?[THRESHOLD]}')
        result = parser.parse()
        self.assertEqual(result, {"HOSTNAME": "server1", "THRESHOLD": 90})

    def test_parse_complex_config(self):
        ConfigParser.CONSTANTS = {"THRESHOLD": 90, "HOSTNAME": "server1"}
        config = '''
        {
            HOSTNAME: ?[HOSTNAME],
            METRICS: {
                CPU: {
                    WARNING: ?[THRESHOLD],
                    CRITICAL: 95
                },
                MEMORY: {
                    WARNING: 80,
                    CRITICAL: 90
                }
            }
        }
        '''
        parser = ConfigParser(config)
        result = parser.parse()
        expected = {
            "HOSTNAME": "server1",
            "METRICS": {
                "CPU": {
                    "WARNING": 90,
                    "CRITICAL": 95
                },
                "MEMORY": {
                    "WARNING": 80,
                    "CRITICAL": 90
                }
            }
        }
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()
