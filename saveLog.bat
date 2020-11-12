adb shell rm /sdcard/Download/dmesg.log
adb shell "while true; do dmesg -c >> /sdcard/Download/dmesg.log; sleep 1; done"