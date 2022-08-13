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
s0 = re.sub('((?<=[0-9] )(?={))','\g<1>"body":\n', data)
s0 = re.sub('(Atom id)', '{\n"\g<1>"', s0)
s0 = re.sub('(},)', '\g<1>\n},', s0)
s1 = re.sub('(\w+ id(?=:))', '"\g<1>"', s0)
s2 = re.sub('((?<=:)\w+(?= ))','"\g<1>",', s1)
s3 = re.sub('((?<= )\w+(?=: ))','"\g<1>"', s2)
s3 = re.sub('(content(?=:))','"\g<1>"', s3)


print(s3)
# print(tdata[0:39])
# jdata = json.loads(s3)
# s3 = re.sub('\s','', s3)
# print(s3)

# with open('./test.json', 'w') as fout:
#     json.dump(s3, fout)
    
# with open('./test.json', 'r') as read_file:
#     data = json.load(read_file)
# print(s3)
# data = json.loads(s3)
# print(data[0:500])
# print(s3[0:])
# print(data)
# jdata = json.loads(s3.replace("'", "\""))
# print(jdata)
# fd = os.open('test.json',os.O_RDWR|os.O_CREAT)
# os.write(fd, data)
