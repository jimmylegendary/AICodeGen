import subprocess
import json
import os
import re

cmd = "difft.exe --dump-syntax pair_data/input/200/83062842c3601faeddcae8f901c515e3c78f3661/src/core/ext/transport/chttp2/transport/bin_decoder.cc"
r = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
output, error = r.communicate()
joutput = json.dumps(output.decode('utf-8'), separators=(',',':'))
data = json.loads(joutput)
s2 = re.sub('\s', '', output)
# Surrounding any word with "
s3 = re.sub('(\w+)', '"\g<1>"', s2)
# print(s2)
print(output)
# print(data)
# fd = os.open('difft_test.output',os.O_RDWR|os.O_CREAT)
# os.write(fd, data)
