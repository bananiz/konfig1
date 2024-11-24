import os
import unittest
import tempfile
import yaml
from interpreter import UVMInterpreter

def create_test_binary(instructions):
    """Helper function to create a binary file with test instructions"""
    with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
        for instr in instructions:
            f.write(instr)
    return f.name

class TestInterpreter(unittest.TestCase):
    def test_load_constant(self):
        interpreter = UVMInterpreter()
        # Test LOAD_CONST (A=14, B=129)
        interpreter.execute_instruction(14, 129)
        self.assertEqual(interpreter.accumulator, 129)

    def test_memory_operations(self):
        interpreter = UVMInterpreter()
        
        # Test MEMORY_WRITE
        interpreter.accumulator = 42
        interpreter.execute_instruction(15, 10)  # Write 42 to address 10
        self.assertEqual(interpreter.memory[10], 42)

        # Test MEMORY_READ
        interpreter.execute_instruction(25, 10)  # Read from address 10
        self.assertEqual(interpreter.accumulator, 42)

    def test_min_operation(self):
        interpreter = UVMInterpreter()
        
        # Setup: Write values to memory
        interpreter.accumulator = 50
        interpreter.execute_instruction(15, 0)  # Write 50 to address 0
        
        # Test MIN with larger value in accumulator
        interpreter.accumulator = 100
        interpreter.execute_instruction(20, 0)  # MIN with value at address 0
        self.assertEqual(interpreter.accumulator, 50)

        # Test MIN with smaller value in accumulator
        interpreter.accumulator = 25
        interpreter.execute_instruction(20, 0)  # MIN with value at address 0
        self.assertEqual(interpreter.accumulator, 25)

    def test_full_program_execution(self):
        # Create a test program that:
        # 1. Loads constant 42
        # 2. Stores it at address 0
        # 3. Loads constant 17
        # 4. Takes min of 17 and value at address 0
        instructions = [
            bytes([0x2E, 0x2A, 0x00, 0x00, 0x00]),  # LOAD_CONST 42
            bytes([0x2F, 0x00, 0x00]),              # MEMORY_WRITE 0
            bytes([0x2E, 0x11, 0x00, 0x00, 0x00]),  # LOAD_CONST 17
            bytes([0xF4, 0x00, 0x00]),              # MIN_OP 0
        ]
        
        binary_file = create_test_binary(instructions)
        result_file = tempfile.NamedTemporaryFile(delete=False).name

        try:
            interpreter = UVMInterpreter()
            interpreter.execute(binary_file, 0, 1, result_file)

            # Read and verify results
            with open(result_file, 'r') as f:
                result = yaml.safe_load(f)
                self.assertEqual(result['memory_range']['values'][0], 42)  # Value at address 0
                self.assertEqual(interpreter.accumulator, 17)  # Final value in accumulator

        finally:
            os.unlink(binary_file)
            os.unlink(result_file)

    def test_invalid_memory_access(self):
        interpreter = UVMInterpreter()
        
        # Test invalid read
        with self.assertRaises(ValueError):
            interpreter.execute_instruction(25, 9999)
        
        # Test invalid write
        with self.assertRaises(ValueError):
            interpreter.execute_instruction(15, 9999)

    def test_invalid_opcode(self):
        interpreter = UVMInterpreter()
        with self.assertRaises(ValueError):
            interpreter.execute_instruction(99, 0)

if __name__ == '__main__':
    unittest.main()
