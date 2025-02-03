import os
import re
output_dir = 'output'
dirs = [os.path.join(output_dir, d) for d in os.listdir(output_dir)
        if os.path.isdir(os.path.join(output_dir, d)) and d.endswith('_LOG')]
cnt = 0

unique_commands = set()
for dir_path in dirs:
    for filename in os.listdir(dir_path):
        if filename.startswith('LOG.txt') and "write" in filename:
            file_path = os.path.join(dir_path, filename)
            with open(file_path, 'r') as file:
                for line in file:
                    if 'taintFinish' in line and ('IpcTx' in line or 'Key:' in line or 'StaticFlag:' in line):
                        if 'Solved taintPath' in line:
                            print()
                            matches = re.findall(r'\(([^)]+)\)', line.strip())
                            cnt += 1
                            if matches:
                                unique_commands.add(matches[-1])
                        print(line.strip().removeprefix("[INFO] [taintFinish] "))
print(cnt)
for cmd in unique_commands:
    print(cmd)

#save to file
with open('unique_RIL_solicited_commands.txt', 'w') as file:
    for cmd in unique_commands:
        file.write(cmd + '\n')

print(len(unique_commands))

