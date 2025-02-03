import subprocess
import os
import re
import time

# Configuration
cur_dir = os.path.dirname(os.path.abspath(__file__))
test_data = "07, 00, 00, 00, 01, 03, 05"

cur_dir = os.path.dirname(os.path.abspath(__file__))

logs_dir = "logs"
frida_server_command = ["adb", "shell", "su", "-c", "/data/local/tmp/frida-server-16.2.1-android-arm64"]
frida_reader_command = ["python3", os.path.join(cur_dir, "hooking-native-code.py")]
test_command = ["adb", "shell", "su", "-c", "/data/local/tmp/test_cmd"]
dump_sys_command = ["dumpsys", "telephony.registry", "|", "grep", "mServiceState", "|", "sed", "-n", "2p"]

bad_status = [
    "OUT_OF_SERVICE",
    "mChannelNumber=-1", 
    # "mCellBandwidths=[]",
    "Unknown",
    "NOT_REG_OR_SEARCHING",
    "UNKNOWN",
    "availableServices=[]"
]


def get_connected_devices():
    devices = []
    try:
        result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
        output_lines = result.stdout.strip().split('\n')
        # Skip the first line which contains header information
        for line in output_lines[1:]:
            device_info = line.split('\t')
            if len(device_info) == 2 and device_info[1] == 'device':
                devices.append(device_info[0])
    except FileNotFoundError:
        print("ADB command not found. Please make sure ADB is installed and added to your PATH.")
    # if devices:
    #     print("Connected devices:")
    #     for device in devices:
    #         print(device)
    # else:
    #     print("No devices connected.")
    return devices

def execute_adb_command(command, device_serial=None, su=False):
    adb_cmd = ['adb']
    if device_serial:
        adb_cmd.extend(['-s', device_serial])
    if su:
        adb_cmd.extend(['shell', 'su -c'])
    adb_cmd.extend(command)

    process = subprocess.Popen(adb_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return stdout.decode(), stderr.decode(), process.returncode

def create_test_file(hex_string):
    with open("hex_data.txt", "w") as f:
        f.write(hex_string)

def is_bad_status(line):
    for status in bad_status:
        if status in line:
            print("Bad Status:" + status)
            return True
    return False

def dump_sys(device_serial):
    dump_try = 10
    while True:
        stdout, stderr, returncode = execute_adb_command(dump_sys_command, device_serial, True)
        sys_output = stdout


        # return service state
        lines = sys_output.splitlines()
        for line in lines:
            if "mServiceState" in line:
                if is_bad_status(line):
                    print("Bad Status:" + line)
                    return True
                else:
                    return False
        print("No mServiceState Try: " + str(dump_try))
        dump_try -= 1
        if dump_try <= 0:
            return True
        else:
            time.sleep(30)


def test_cmds(device_serial):

    create_test_file(test_data)
    push_command = ['push', os.path.join(cur_dir, 'hex_data.txt'), '/data/local/tmp/']
    stdout, stderr, returncode = execute_adb_command(push_command, device_serial)
    if returncode != 0:
        print("Error in push", stderr)

    # prepare logs
    log_file_path = "hex_one_cmd.log"
    frida_server_process = subprocess.Popen(frida_server_command)
    time.sleep(3)
    with open(log_file_path, "w") as log_file:
        frida_read_process = subprocess.Popen(frida_reader_command, stdout=log_file)
    print("Start test")
    test_process = subprocess.Popen(test_command)
    print("Test done")
    test_process.wait()
    frida_server_process.terminate()
    frida_read_process.terminate()
    dump_crash = dump_sys(device_serial)
    if dump_crash:
        print("Dump crash: " + test_data)
    else:
        print("No crash")

def main():
    # Replace 'your_device_serial' with the actual serial number of your device,
    # or leave it as None to execute the command on any connected device.
    device_serials = get_connected_devices()
    if(device_serials):
        device_tar = device_serials[0]
        test_cmds(device_tar)
        print("Everything is done")

if __name__ == "__main__":
    main()
