import os
import subprocess
import sys
import time

main_process = subprocess.Popen(sys.argv[1:], stdout=sys.stdout, stderr=sys.stderr)

while True:
    if os.path.isfile("/pod-data/END"):
        main_process.kill()
        sys.exit(0)

    main_process_exit_code = main_process.poll()
    if main_process.poll() is not None:
        sys.exit(main_process_exit_code)

    time.sleep(1)
