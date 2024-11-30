import os
import unittest
import tempfile
from assembler import Assembler, Instruction

class TestAssembler(unittest.TestCase):
    def test_instruction_encoding(self):
        # Test LOAD_CONST (A=14, B=129)
        instr = Instruction(14, 129)
        encoded = instr.encode()
        self.assertEqual(encoded, bytes([0x2E, 0x10, 0x00, 0x00, 0x00]))

        # Test MEMORY_READ (A=25, B=10)
        instr = Instruction(25, 10)
        encoded = instr.encode()
        self.assertEqual(encoded, bytes([0x59, 0x01, 0x00]))

        # Test MEMORY_WRITE (A=15, B=761)
        instr = Instruction(15, 761)
        encoded = instr.encode()
        self.assertEqual(encoded, bytes([0x2F, 0x5F, 0x00]))

        # Test MIN_OP (A=20, B=935)
        instr = Instruction(20, 935)
        encoded = instr.encode()
        self.assertEqual(encoded, bytes([0xF4, 0x74, 0x00]))

    def test_assembler_process(self):
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as source_file, \
             tempfile.NamedTemporaryFile(mode='wb', delete=False) as output_file, \
             tempfile.NamedTemporaryFile(mode='w', delete=False) as log_file:
            
            # Write test program using mnemonics
            source_file.write("""
            LOAD 129   ; Load constant 129
            READ 10    ; Read from address 10
            WRITE 761  ; Write to address 761
            MIN 935    ; Min operation with address 935
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
                    
                # Expected binary output based on instruction encoding
                expected = bytes([
                    0x2E, 0x10, 0x00, 0x00, 0x00,  # LOAD 129
                    0x59, 0x01, 0x00,               # READ 10
                    0x2F, 0x5F, 0x00,               # WRITE 761
                    0xF4, 0x74, 0x00                # MIN 935
                ])
                
                self.assertEqual(binary, expected)

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
