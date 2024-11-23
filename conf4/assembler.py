import sys
import yaml
import struct

def assemble(input_file, output_file, log_file):
    commands = []
    with open(input_file, 'r') as f:
        for line in f:
            line = line.strip()
            # Пропуск пустых строк и комментариев (если строки начинаются с #)
            if not line or line.startswith('#'):
                continue
            parts = line.split()
            if len(parts) < 1:
                print(f"Ошибка: Неправильный формат строки: {line}")
                sys.exit(1)
            
            command = parts[0]
            try:
                args = [int(arg, 16) if arg.startswith('0x') else int(arg) for arg in parts[1:]]
            except ValueError as e:
                print(f"Ошибка в строке: {line}")
                print(f"Детали ошибки: {e}")
                sys.exit(1)
            
            commands.append((command, args))

    binary_output = bytearray()
    log_output = []

    for command, args in commands:
        if command == 'LOAD_CONST':
            if len(args) != 2:
                print(f"Ошибка: Команда LOAD_CONST ожидает 2 аргумента, получено {len(args)}")
                sys.exit(1)
            A, B, C = 14, args[0], args[1]
            binary_output.extend(struct.pack('>BHI', A, B, C))
            log_output.append({'command': 'LOAD_CONST', 'address': B, 'constant': C})
        elif command == 'READ_MEM':
            if len(args) != 1:
                print(f"Ошибка: Команда READ_MEM ожидает 1 аргумент, получено {len(args)}")
                sys.exit(1)
            A, B = 25, args[0]
            binary_output.extend(struct.pack('>BH', A, B))
            log_output.append({'command': 'READ_MEM', 'address': B})
        elif command == 'WRITE_MEM':
            if len(args) != 1:
                print(f"Ошибка: Команда WRITE_MEM ожидает 1 аргумент, получено {len(args)}")
                sys.exit(1)
            A, B = 15, args[0]
            binary_output.extend(struct.pack('>BH', A, B))
            log_output.append({'command': 'WRITE_MEM', 'address': B})
        elif command == 'MIN':
            if len(args) != 1:
                print(f"Ошибка: Команда MIN ожидает 1 аргумент, получено {len(args)}")
                sys.exit(1)
            A, B = 20, args[0]
            binary_output.extend(struct.pack('>BH', A, B))
            log_output.append({'command': 'MIN', 'address': B})
        else:
            print(f"Ошибка: Неизвестная команда {command}")
            sys.exit(1)

    with open(output_file, 'wb') as f:
        f.write(binary_output)

    with open(log_file, 'w') as f:
        yaml.dump(log_output, f)

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python assembler.py <input_file> <output_file> <log_file>")
        sys.exit(1)
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    log_file = sys.argv[3]
    assemble(input_file, output_file, log_file)
