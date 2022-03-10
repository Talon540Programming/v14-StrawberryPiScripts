# !/bin/bash
i = 0
while ! ifconfig | grep -F "10.5.40." > /dev/null; do
    echo "Waiting for Connection"
done

/bin/bash/python3 ~/ballDetection/nonTestedFinal.py



# fix ifconfig
# find and fix paths for python and python script