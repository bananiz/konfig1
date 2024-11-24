import struct
import yaml
from typing import Dict, List, Tuple

class Instruction:
    # Opcodes
    LOAD_CONST = 14  # 5 bytes
    MEMORY_READ = 25  # 3 bytes
    MEMORY_WRITE = 15  # 3 bytes
    MIN_OP = 20  # 3 bytes

    def __init__(self, opcode: int, operand: int):
        if opcode not in [self.LOAD_CONST, self.MEMORY_READ, self.MEMORY_WRITE, self.MIN_OP]:
            raise ValueError(f"Invalid opcode: {opcode}")
        self.opcode = opcode
        self.operand = operand

    def encode(self) -> bytes:
        # Shift opcode to create the correct binary pattern
        shifted_opcode = (self.opcode & 0x1F) << 3  # Shift left by 3 to match the required pattern
        
        if self.opcode == self.LOAD_CONST:
            # 5-byte instruction: 1 byte opcode (5 bits) + 4 bytes operand
            return bytes([shifted_opcode]) + struct.pack('<I', self.operand)
        else:
            # 3-byte instruction: 1 byte opcode (5 bits) + 2 bytes operand
            return bytes([shifted_opcode]) + struct.pack('<H', self.operand)

class Assembler:
    def __init__(self):
        self.instructions: List[Instruction] = []
        self.log_entries: List[Dict] = []

    def parse_line(self, line: str) -> Tuple[int, int]:
        # Remove comments and strip whitespace
        line = line.split(';')[0].strip()
        if not line:
            return None

        parts = line.split()
        if len(parts) < 2:
            raise ValueError(f"Invalid instruction format: {line}")

        opcode = int(parts[0])
        operand = int(parts[1])
        return opcode, operand

    def assemble(self, source_path: str, output_path: str, log_path: str):
        # Read source file
        with open(source_path, 'r') as f:
            lines = f.readlines()

        # Process each line
        binary_output = bytearray()
        for i, line in enumerate(lines, 1):
            try:
                parsed = self.parse_line(line)
                if parsed:
                    opcode, operand = parsed
                    instr = Instruction(opcode, operand)
                    encoded = instr.encode()
                    binary_output.extend(encoded)
                    
                    # Add to log
                    self.log_entries.append({
                        'line': i,
                        'opcode': opcode,
                        'operand': operand,
                        'bytes': ' '.join(f'0x{b:02X}' for b in encoded)
                    })
            except Exception as e:
                raise ValueError(f"Error on line {i}: {str(e)}")

        # Write binary output
        with open(output_path, 'wb') as f:
            f.write(binary_output)

        # Write log
        with open(log_path, 'w') as f:
            yaml.dump(self.log_entries, f, sort_keys=False)

def main():
    import sys
    if len(sys.argv) != 4:
        print("Usage: python assembler.py <source_file> <output_file> <log_file>")
        sys.exit(1)

    assembler = Assembler()
    assembler.assemble(sys.argv[1], sys.argv[2], sys.argv[3])

if __name__ == '__main__':
    main()
