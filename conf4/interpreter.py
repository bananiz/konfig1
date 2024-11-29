import struct
import yaml
from typing import List

class UVMInterpreter:
    def __init__(self):
        self.memory = [0] * 1024  # 1024 memory locations
        self.accumulator = 0

    def load_constant(self, value: int):
        self.accumulator = value

    def memory_read(self, address: int):
        if 0 <= address < len(self.memory):
            self.accumulator = self.memory[address]
        else:
            raise ValueError(f"Invalid memory address: {address}")

    def memory_write(self, address: int):
        if 0 <= address < len(self.memory):
            self.memory[address] = self.accumulator
        else:
            raise ValueError(f"Invalid memory address: {address}")

    def min_operation(self, address: int):
        if 0 <= address < len(self.memory):
            self.accumulator = min(self.accumulator, self.memory[address])
        else:
            raise ValueError(f"Invalid memory address: {address}")

    def execute_instruction(self, opcode: int, operand: int):
        if opcode == 14:  # LOAD_CONST
            self.load_constant(operand)
        elif opcode == 25:  # MEMORY_READ
            self.memory_read(operand)
        elif opcode == 15:  # MEMORY_WRITE
            self.memory_write(operand)
        elif opcode == 20:  # MIN_OP
            self.min_operation(operand)
        else:
            raise ValueError(f"Unknown opcode: {opcode}")

    def execute(self, binary_path: str, start_addr: int, end_addr: int, output_path: str):
        # Read binary file
        with open(binary_path, 'rb') as f:
            binary_data = f.read()

        # Execute instructions
        pos = 0
        while pos < len(binary_data):
            # Получаем опкод из первых 5 бит
            opcode = binary_data[pos] & 0x1F
            
            if opcode == 14:  # LOAD_CONST (5 bytes)
                # Для LOAD_CONST операнд находится в битах 5-33 (29 бит)
                operand = ((binary_data[pos] >> 5) | 
                          (binary_data[pos+1] << 3) |
                          (binary_data[pos+2] << 11) |
                          (binary_data[pos+3] << 19) |
                          (binary_data[pos+4] << 27)) & 0x1FFFFFFF
                pos += 5
            else:  # Other instructions (3 bytes)
                # Для остальных команд операнд находится в битах 5-21 (17 бит)
                operand = ((binary_data[pos] >> 5) |
                          (binary_data[pos+1] << 3) |
                          (binary_data[pos+2] << 11)) & 0x1FFFF
                pos += 3
            
            self.execute_instruction(opcode, operand)

        # Save memory range to output file
        result = {
            'memory_range': {
                'start': start_addr,
                'end': end_addr,
                'values': self.memory[start_addr:end_addr+1]
            }
        }
        
        with open(output_path, 'w') as f:
            yaml.dump(result, f)

def main():
    import sys
    if len(sys.argv) != 5:
        print("Usage: python interpreter.py <binary_file> <start_addr> <end_addr> <output_file>")
        sys.exit(1)

    interpreter = UVMInterpreter()
    interpreter.execute(
        sys.argv[1],
        int(sys.argv[2]),
        int(sys.argv[3]),
        sys.argv[4]
    )

if __name__ == '__main__':
    main()
