import re
import pandas as pd
import plotly.express as px

def processar_info_kill(line, date, values):
    date = line.replace('[', '').replace(']','').replace('  ', ' ').replace(': ',' ').split(' ')
    values = line.replace('[', '').replace(']','').replace('  ', ' ').replace(' : ',' ').replace(': ',' ').replace(' #', '#').split(' ')
    return date, values

def amKill(file):
    re_proc_kill = re.compile(r'([0-9\-]* [.:0-9]*  [0-9]*  [0-9]*  [0-9]* [A-Z] am_kill.*?)\n', flags=re.M|re.S)
    log_proc_kill = re_proc_kill.findall(file)
    timestamp_proc_kill,pid_proc_kill, name_proc_kill, imp_kill, subreason_kill = [],[],[],[],[]
    date=""
    values=""
    for line in log_proc_kill:
        date, values = processar_info_kill(line, date, values)
        timestamp_proc_kill.append("2023-"+date[0]+" "+re.search(r'\d{2}:\d{2}',date[1]).group())
        filter_line=re.search(r'am_kill.*?\[(\d+),(\d+),(.*?),(\d+),(.*?)\]', line)
        pid_proc_kill.append(filter_line.group(2))
        name_proc_kill.append(filter_line.group(3))
        imp_kill.append(filter_line.group(4))
        subreason_kill.append(filter_line.group(5))
    proc_kill_df = {
        'Timestamp': timestamp_proc_kill,
        'PID': pid_proc_kill,
        'Process': name_proc_kill,
        'Importance': imp_kill,
        'Subreason': subreason_kill
    }
    proc_kill_df = pd.DataFrame(proc_kill_df)
    return (proc_kill_df)

def dictDeathReason():
    dict_reason = {}
    dict_reason['UNKNOWN']=0
    dict_reason['EXIT_SELF']=1
    dict_reason['SIGNALED']=2
    dict_reason['LOW_MEMORY']=3
    dict_reason['APP CRASH']=4
    dict_reason['CRASH_NATIVE']=5
    dict_reason['ANR']=6
    dict_reason['INITIALIZATION_FAILURE']=7
    dict_reason['PERMISSION CHANGE']=8
    dict_reason['EXCESSIVE RESOURCE USAGE']=9
    dict_reason['USER REQUESTED']=10
    dict_reason['USER STOPPED']=11
    dict_reason['DEPENDENCY DIED']=12
    dict_reason['OTHER KILLS BY SYSTEM']=13
    dict_reason['FREEZER']=14
    dict_reason['PACKAGE STATE CHANGE']=15
    dict_reason['PACKAGE UPDATED']=16
    return dict_reason

def reasonDeath(file):
    re_rDied = re.compile(r'(ACTIVITY MANAGER PROCESS EXIT INFO.*?)\n\n',flags=re.S)
    pid_reason , name_proc_reason , reason , sub_reason = [], [], [], []
    timestamp_reason , impor_reason= [], []
    date_process = re.split(r':\n', re_rDied.search(file).group(0))[1:]
    for line in date_process:
        pid = re.search(r'pid=(\d+)', line).group(1)
        timestamp_reason.append(re.search(r'timestamp=(.*?)\n', line, flags = re.S).group(1))
        pid_reason.append(pid)
        name_proc_reason.append(re.search(r'process=([\.a-zA-Z]+)', line).group(1).lower())

        reason_str = re.search(r'reason=(.*?)\n', line, flags=re.S).group(1).split('(')[1].replace(')','')
        reason.append(reason_str)
        sub_reason.append(re.search(r'subreason=\d(.*?)\n', line, flags=re.S).group(1).replace(')','').replace('(','').lower())

        impor_reason.append(re.search(r'importance=([0-9,]+)', line).group(1))
    
    # DATASET COM TODAS AS INFORMAÇÕES
    proc_rDied_df = {
        'Time':timestamp_reason,
        'PID': pid_reason,
        'Process': name_proc_reason,
        'Reason': reason,
        'Subreason':sub_reason,
        'Importance': impor_reason
    }

    proc_rDied_df = pd.DataFrame(proc_rDied_df)
    return (proc_rDied_df)


def plotReasonDeath(file):
    proc_rDied_df = reasonDeath(file)
    fig = px.histogram(proc_rDied_df, x='Reason', title='Reasons for Death', color="Reason", labels={'Reason': 'Reason', 'count': 'Frequency'})
    fig.update_layout(
        xaxis_title='',
        yaxis_title='Frequency',
        bargap=0.1, 
        xaxis=dict(showticklabels=False),
        plot_bgcolor='white',
    )

    return fig