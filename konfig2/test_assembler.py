import os
import unittest
import tempfile
from assembler import Assembler, Instruction

class TestAssembler(unittest.TestCase):
    def test_instruction_encoding(self):
        # Test LOAD_CONST (A=14, B=129)
        instr = Instruction(14, 129)
        encoded = instr.encode()
        self.assertEqual(encoded, bytes([0x70, 0x81, 0x00, 0x00, 0x00]))  # 0x70 = 14 << 3

        # Test MEMORY_READ (A=25, B=10)
        instr = Instruction(25, 10)
        encoded = instr.encode()
        self.assertEqual(encoded, bytes([0xC8, 0x0A, 0x00]))  # 0xC8 = 25 << 3

        # Test MEMORY_WRITE (A=15, B=761)
        instr = Instruction(15, 761)
        encoded = instr.encode()
        self.assertEqual(encoded, bytes([0x78, 0xF9, 0x02]))  # 0x78 = 15 << 3

        # Test MIN_OP (A=20, B=935)
        instr = Instruction(20, 935)
        encoded = instr.encode()
        self.assertEqual(encoded, bytes([0xA0, 0xA7, 0x03]))  # 0xA0 = 20 << 3

    def test_assembler_process(self):
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as source_file, \
             tempfile.NamedTemporaryFile(mode='wb', delete=False) as output_file, \
             tempfile.NamedTemporaryFile(mode='w', delete=False) as log_file:
            
            # Write test program
            source_file.write("""
            14 42    ; Load constant 42
            15 0     ; Store at address 0
            25 0     ; Read from address 0
            20 1     ; Min operation with address 1
            """)
            source_file.close()
            output_file.close()
            log_file.close()

            try:
                # Assemble the program
                assembler = Assembler()
                assembler.assemble(source_file.name, output_file.name, log_file.name)

                # Verify binary output
                with open(output_file.name, 'rb') as f:
                    binary = f.read()
                    # First instruction (LOAD_CONST)
                    self.assertEqual(binary[0:5], bytes([0x70, 0x2A, 0x00, 0x00, 0x00]))
                    # Second instruction (MEMORY_WRITE)
                    self.assertEqual(binary[5:8], bytes([0x78, 0x00, 0x00]))
                    # Third instruction (MEMORY_READ)
                    self.assertEqual(binary[8:11], bytes([0xC8, 0x00, 0x00]))
                    # Fourth instruction (MIN_OP)
                    self.assertEqual(binary[11:14], bytes([0xA0, 0x01, 0x00]))

            finally:
                # Cleanup
                os.unlink(source_file.name)
                os.unlink(output_file.name)
                os.unlink(log_file.name)

    def test_invalid_instruction(self):
        with self.assertRaises(ValueError):
            instr = Instruction(99, 0)  # Invalid opcode
            instr.encode()

if __name__ == '__main__':
    unittest.main()
