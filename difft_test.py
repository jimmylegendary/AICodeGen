import subprocess
import json
import os
import re

cmd = "difft.exe --dump-syntax pair_data/input/200/83062842c3601faeddcae8f901c515e3c78f3661/src/core/ext/transport/chttp2/transport/bin_decoder.cc"
r = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
output, error = r.communicate()
joutput = json.dumps(output.decode('utf-8'), separators=(',',':'))
data = json.loads(joutput)
# s2 = re.sub('\s', '', data)
# Surrounding any word with "
# s3 = re.sub('(\w+)', '"\g<1>"', data)
# s3 = re.sub('\{[ \t]+[^\"]*[a-zA-Z]+[^\"][ \t]+:', '"\g<1>"', data)
s1 = re.sub('(\w+ id(?=:))', '"\g<1>"', data)
s2 = re.sub('((?<=:)\w+(?= ))','"\g<1>"', s1)
s3 = re.sub('((?<= )\w+(?=:))','"\g<1>"', s2)

with open('./test.json', 'w') as fout:
    json.dump(s3, fout)
    
with open('./test.json', 'r') as read_file:
    data = json.load(read_file)

# print(s3)
# jdata = json.loads(s3.replace("'", "\""))
# print(jdata)
# fd = os.open('difft_test.output',os.O_RDWR|os.O_CREAT)
# os.write(fd, data)
