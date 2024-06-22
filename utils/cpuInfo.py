import re
import pandas as pd

def blocksCritical(file):
    re_critical = re.compile(r'DUMP OF SERVICE CRITICAL(?:.*?)(?=DUMP?)', flags=re.M|re.S)
    blocks_critical = []
    data_critical = re_critical.findall(file)
    for block in data_critical:
        blocks_critical.append(block)
    return blocks_critical

def cpuInfo(file):
    re_sub_cpu = re.compile(r'^([+\s\d]+%.*?)\n', flags=re.M|re.S)
    cpu_per, cpu_pid, cpu_proc = [],  [],  []
    user_per, ker_per = [],  []
    minor, major = [],  []
    filter_block_cpu = blocksCritical(file)[2]
    for line in re_sub_cpu.findall(filter_block_cpu)[1:]:
        re_pad1 = re.search(r'((\d{1,2})% (.*?))\/(.*?):', line)
        cpu_per.append(re_pad1.group(2))
        cpu_pid.append(re_pad1.group(3))
        cpu_proc.append(re_pad1.group(4))
        re_pad2 = re.search(r'(\d{1,2})% [a-z]+\s+\+\s+([\d\.]+)%\s+[a-z]+', line)

        if(re_pad2==None):
            user_per.append(0)
            ker_per.append(0)
        else:
            user_per.append(re_pad2.group(1))
            ker_per.append(re_pad2.group(2))

        re_pad3 = re.search(r'faults: (.*?)minor ?(?:(.*?)major)?', line)
        if(re_pad3==None):
            minor.append(0)
            major.append(0)
        else:
            if(re_pad3.group(1)==None):
                minor.append(0)
                major.append(int(re_pad3.group(2)))
            elif(re_pad3.group(2)==None):
                minor.append(int(re_pad3.group(1)))
                major.append(0)
            else:
                minor.append(int(re_pad3.group(1)))
                major.append(int(re_pad3.group(2)))
    dafa_cpu={
        'CPU PER(%)': cpu_per,
        'PID': cpu_pid,
        'PROCESS': cpu_proc,
        'USER(%)': user_per,
        'KERNEL(%)': ker_per,
        'MINOR': minor,
        'MAJOR': major,
    }
    df_cpu = pd.DataFrame(dafa_cpu)
    return (df_cpu)