#!/bin/bash

BINARY_PATH="./usb_proxy.py"
LOGFOLDER="./logs"
LOGFILE=${LOGFOLDER}/capture_all_in.out
TEST_MODULE=./test_modules/modify_data_in.py

DELAY=5
EXTRA=1

# Replace with the proxied device's information
VENDOR_ID=0xABCD
PRODUCT_ID=0x1234

init_fs() {
    [[ ! -d ${LOGFOLDER} ]] && mkdir ${LOGFOLDER}
}

terminate_process() {
    if [[ $PID != 0 ]]; then
        echo "Killing process: $PID"
        kill $PID
        
        # Ensure the process is terminated
        wait $PID 2>/dev/null
        PID=0;
    fi
}

log_journalctl() {
    ./scripts/ssh-access.sh -c "journalctl --since \"$((DELAY + EXTRA)) seconds ago\"" >> ${LOGFILE}
    sync
}

trap "echo -e '\nProcess terminated by user.'; terminate_process; exit 0" SIGINT
init_fs
while true; do
    echo "Launching: ${BINARY_PATH}"
    ${BINARY_PATH} --product_id ${PRODUCT_ID} --vendor_id ${VENDOR_ID} --logfile ${LOGFILE} --module ${TEST_MODULE} &
    PID=$!
    
    sleep $DELAY
    terminate_process
    log_journalctl
done
