import sys
import yaml
import struct

def interpret(input_file, output_file, memory_range):
    with open(input_file, 'rb') as f:
        binary_data = f.read()

    memory = [0] * 1024  # Предположим, что память УВМ имеет размер 1024 байта
    pc = 0

    while pc < len(binary_data):
        A = binary_data[pc]
        print(f"Processing command at pc={pc}, A={A}")
        if A == 14:  # LOAD_CONST
            B = struct.unpack('>H', binary_data[pc + 1:pc + 3])[0]
            C = struct.unpack('>I', binary_data[pc + 3:pc + 7])[0]
            print(f"LOAD_CONST: B={B}, C={C}")
            memory[B] = C
            pc += 7
        elif A == 25:  # READ_MEM
            B = struct.unpack('>H', binary_data[pc + 1:pc + 3])[0]
            print(f"READ_MEM: B={B}")
            memory[B] = memory[B]
            pc += 3
        elif A == 15:  # WRITE_MEM
            B = struct.unpack('>H', binary_data[pc + 1:pc + 3])[0]
            print(f"WRITE_MEM: B={B}")
            memory[B] = memory[B]
            pc += 3
        elif A == 20:  # MIN
            B = struct.unpack('>H', binary_data[pc + 1:pc + 3])[0]
            print(f"MIN: B={B}")
            value = memory[B]
            memory[B] = min(memory[B], value)
            pc += 3
        else:
            print(f"Unknown command: {A}")
            sys.exit(1)

    result = {f'{i}': memory[i] for i in range(memory_range[0], memory_range[1] + 1)}

    with open(output_file, 'w') as f:
        yaml.dump({'memory': result}, f)

if __name__ == '__main__':
    if len(sys.argv) != 5:
        print("Usage: python interpreter.py <input_file> <output_file> <memory_range_start> <memory_range_end>")
        sys.exit(1)
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    memory_range = list(map(int, sys.argv[3:5]))
    interpret(input_file, output_file, memory_range)
