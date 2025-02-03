import os, time
from subprocess import *
import threading
import sys

if(sys.version[:1] == "3"):
    import _thread as thread
else:
    import thread


tids = list(range(3))
start_time = 0


def run_one(app, tid):
	project = "Test" + str(tid)
	os.system('java -cp lib/ghidra.jar:lib/json.jar:main.jar main %s %s' % (app, project))
	tids.append(tid)

def get_ril_paths():
	current_dir = os.path.dirname(os.path.abspath(__file__))
	ril_dir = os.path.join(current_dir, "ril_binaries")
	output_dir = os.path.join(current_dir, "output")
	print(ril_dir)
	result = []

	for root, dirs, files in os.walk(ril_dir):
		for file in files:
			if (file == "libsec-ril.so") or (file == "libril.so"):
				file_path = os.path.join(root, file)
				print(file_path)
				base_name = os.path.splitext(os.path.basename(root))[0]
				print(base_name)
				output_path = os.path.join(output_dir, base_name)
				print(output_path)
				if not os.path.exists(output_path):
					result.append(file_path)
				else:
					print(f"Skipping {file_path} - output already exists")
	return result

def run_all():
    global start_time
    start_time = time.time()
    so_paths = get_ril_paths()

    for app in so_paths:
        while len(tids) == 0:
            time.sleep(60)
        tid = tids.pop()
        run_one(app, tid)
		# thread.start_new_thread( run_one, (app, tid) )

def debug_one():
	"""Run analysis on a single test case for debugging"""
	global start_time
	start_time = time.time()
	current_dir = os.path.dirname(os.path.abspath(__file__))
	ril_dir = os.path.join(current_dir, "ril_binaries")

	# Get the first available RIL binary
	so_paths = get_ril_paths()
	if not so_paths:
		print("No RIL binaries found to analyze")
		return
		
	test_binary = so_paths[0]
	print(f"Testing binary: {test_binary}")

	# Run analysis with Test0 project
	print("in debug mode")
	os.environ['DEBUG_COMMAND'] = 'IpcTxModemPowerOff'  # Set environment variable to filter command
	os.system('java -cp lib/ghidra.jar:lib/json.jar:main.jar main %s Test0' % test_binary)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--debug':
        debug_one()
    else:
        run_all()
    total_time = time.time() - start_time
    print("finish time: %f" % total_time)
