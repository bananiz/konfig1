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
        if self.opcode < 0 or self.opcode > 31:  # 5 бит для опкода
            raise ValueError(f"Opcode must be 0-31 (5 bits), got {self.opcode}")
            
        if self.opcode == self.LOAD_CONST:  # A=14
            # Константа занимает биты 5-33 (29 бит)
            if self.operand < 0 or self.operand > 0x1FFFFFFF:  # 29 бит
                raise ValueError(f"Constant must be 0-536870911 (29 bits), got {self.operand}")
            
            # Первый байт: опкод в битах 0-4
            first_byte = self.opcode & 0x1F
            
            # Сдвигаем операнд на 5 бит влево (освобождаем место для опкода)
            shifted_operand = (self.operand << 5) & 0xFFFFFFFF
            
            # Комбинируем опкод и операнд
            combined = first_byte | shifted_operand
            
            # Преобразуем в 5 байт
            return combined.to_bytes(5, byteorder='little')
            
        else:  # MEMORY_READ, MEMORY_WRITE, MIN_OP - все 3 байта
            # Адрес занимает биты 5-21 (17 бит)
            if self.operand < 0 or self.operand > 0x1FFFF:  # 17 бит
                raise ValueError(f"Address must be 0-131071 (17 bits), got {self.operand}")
            
            # Первый байт: опкод в битах 0-4
            first_byte = self.opcode & 0x1F
            
            # Сдвигаем операнд на 5 бит влево (освобождаем место для опкода)
            shifted_operand = (self.operand << 5) & 0xFFFFFF
            
            # Комбинируем опкод и операнд
            combined = first_byte | shifted_operand
            
            # Преобразуем в 3 байта
            return combined.to_bytes(3, byteorder='little')


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
        instructions = []
        
        # Read and parse source file
        with open(source_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith(';'):
                    continue
                    
                # Split line into opcode and operand
                parts = line.split(';')[0].strip().split()
                if len(parts) != 2:
                    continue
                    
                opcode = int(parts[0])
                operand = int(parts[1])
                
                instruction = Instruction(opcode, operand)
                instructions.append(instruction)
                print(f"Assembled: opcode={opcode}, operand={operand}")
                print(f"Binary: {' '.join(hex(b) for b in instruction.encode())}")
        
        # Write binary file
        with open(output_path, 'wb') as f:
            for instruction in instructions:
                binary = instruction.encode()
                f.write(binary)
                
        # Write log file
        log = {
            'instructions': [
                {
                    'opcode': instr.opcode,
                    'operand': instr.operand,
                    'binary': ' '.join(hex(b) for b in instr.encode())
                }
                for instr in instructions
            ]
        }
        with open(log_path, 'w') as f:
            yaml.dump(log, f)

def main():
    import sys
    if len(sys.argv) != 4:
        print("Usage: python assembler.py <source_file> <output_file> <log_file>")
        sys.exit(1)

    assembler = Assembler()
    assembler.assemble(sys.argv[1], sys.argv[2], sys.argv[3])

if __name__ == '__main__':
    main()
