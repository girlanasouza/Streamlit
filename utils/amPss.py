import re
import pandas as pd
import plotly.express as px

def kb_to_mb(kilobytes):
    megabytes = kilobytes / 1024
    return megabytes

def arredondar_numero(numero, casas_decimais=0):
    return round(numero, casas_decimais)

def truncar_numero(numero):
  numero_truncado = float("{:.3f}".format(numero))
  return numero_truncado

def bytes_to_mb(bytes_value):
    mb_value = bytes_value / (1024 * 1024)
    return mb_value
    
def bits_to_mb(bits_value):
    bytes_value = bits_value / 8
    mb_value = bytes_value / (1024 * 1024)
    return mb_value

# INFORMATION EXTRACT TOTAL PSS BY PROCESS
def totalPssRss(file):
    reg_total_process = re.compile(r'(Total\s+[A-Z]+\s+by\s+[a-zA-Z ]+:.*?)\n\n', flags=re.DOTALL)
    process_consume_pss , process_name_pss, process_id_pss = [], [], []
    
    re_pss_process = re.compile(r'([0-9,]+)[A-Z]:\s+(\w+)\s+\(pid\s+(\d+)', flags=re.DOTALL)
    data_to_process_pss = re_pss_process.findall(reg_total_process.findall(file)[3])

    re_rss_process = re.compile(r'([0-9,]+)[A-Z]:\s+(\w+)\s+\(pid\s+(\d+)', flags=re.DOTALL)
    data_to_process_rss = re_rss_process.findall(reg_total_process.findall(file)[0])
    process_consume_rss, process_name_rss, process_id_rss = [],[],[]
    

    for line in data_to_process_rss:  
        process_consume_rss.append(round(int(line[0].replace(',',''))/1024,2))
        process_name_rss.append(line[1])
        process_id_rss.append(line[2])

    for line in data_to_process_pss:
        process_consume_pss.append((round(int(line[0].replace(',',''))/1024,2)))
        process_name_pss.append(line[1])
        process_id_pss.append(line[2])
    
    data_ampss = {
        'PID': process_id_pss,
        # 'Process':process_name_pss,
        'PSS(MB)': process_consume_pss
    }

    data_amrss = {
        'PID': process_id_rss,
        'Process': process_name_rss,
        'RSS(MB)': process_consume_rss
    }

    df_amRss = pd.DataFrame(data_amrss)
    df_amPss = pd.DataFrame(data_ampss)
    df_merged = pd.merge(df_amRss,df_amPss,on='PID', how='inner')

    return df_merged

def processInfoPss(line, values1, values2):
    values1 = line.replace('[', '').replace(']','').replace('  ', ' ').replace(': ',' ').split(' ')
    values2 = line.replace('[', '').replace(']','').replace('  ', ' ').split(' ')[-1].split(',')
    return values1, values2


# ACTVITY MANAGER PSS 
# def am_pss(file):
#     re_proc_am_pss = re.compile(r'([0-9\-]* [.:0-9]*  [0-9]*  [0-9]*  [0-9]* [A-Z] am_pss.*?)\n', flags= re.S)
#     timestamp_am_pss, pid_am_pss, name_am_pss, pss_am_pss, rss_am_pss = [], [], [], [], []
#     values_proc_am_pss_p1 = ""
#     values_proc_am_pss_p2 = ""
#     for line in re_proc_am_pss.findall(file):
#         values_proc_am_pss_p1, values_proc_am_pss_p2 = processInfoPss(line, values_proc_am_pss_p1, values_proc_am_pss_p2)
#         date_value = "2023-"+values_proc_am_pss_p1[0]
#         time_value = (re.search(r'\d{2}:\d{2}', values_proc_am_pss_p1[1]).group())
#         timestamp_value = (date_value + " " + time_value)
#         timestamp_am_pss.append(timestamp_value)
#         pid_am_pss.append(values_proc_am_pss_p2[0])
#         name_am_pss.append(values_proc_am_pss_p2[2])
#         pss_am_pss.append(int(arredondar_numero(bytes_to_mb(int(values_proc_am_pss_p2[3])))))
#         rss_am_pss.append(int(arredondar_numero(bytes_to_mb(int(values_proc_am_pss_p2[6])))))

#     data_ampss = {
#         'Timestamp': timestamp_am_pss,
#         'PID': pid_am_pss,
#         'Process': name_am_pss,
#         'PSS': pss_am_pss,
#         'RSS': rss_am_pss
#     }
#     df_amPss = pd.DataFrame(data_ampss)
#     return (df_amPss)

# def plotAmPss(file):
#     df_amPss = am_pss(file)  
#     df_amPss['Timestamp'] = pd.to_datetime(df_amPss['Timestamp'])
#     df_amPss = df_amPss.sort_values(by='Timestamp')
#     fig = px.line(df_amPss, x='Timestamp', y='PSS')
#     fig.update_traces(line=dict(color='black'))
    
#     fig.update_layout(
#         title='PSS Consumption Over Time',
#         xaxis_title='Timestamp',
#         yaxis_title='PSS Consumption',
#         xaxis=dict(tickangle=-45),
#         showlegend=True,
#     )
#     return fig 

def plotAmPssRss(proc_am_pss_df):
    fig = px.line(proc_am_pss_df, 
        x='Timestamp', 
        y=['RSS', 'PSS'], 
        markers=True, 
        line_shape='linear', 
        title='RSS and PSS Consumption Over Time',
        labels={'value': 'Memória (MB)'}, 
        hover_data={'Process': True}
    )
    fig.update_layout(
        xaxis_title='Timestamp', 
        yaxis_title='Memória (MB)',
        xaxis=dict(tickangle=-45),
    ) 
    return fig

def scatterPlot(df):
    proc_am_pss_df_summed = df.groupby('Process')['PSS'].sum().reset_index()
    fig = px.scatter(proc_am_pss_df_summed, x="PSS", y="PSS",
                 size="PSS", color="Process", hover_name="Process",
                 log_x=True, size_max=60)
    fig.update_layout(title='Visualization of Memory Consumption by Process through Bubble Size')
    return fig


def am_pss(file):
    re_proc_am_pss = re.compile(r'([0-9\-]* [.:0-9]*  [0-9]*  [0-9]*  [0-9]* [A-Z] am_pss.*?)\n', flags= re.S)
    timestamp_am_pss, date_am_pss , pid_am_pss, name_am_pss, pss_am_pss, rss_am_pss = [], [], [], [], [], []
    values_proc_am_pss_p1 = ""
    values_proc_am_pss_p2 = ""
    date_re = re.compile(r'dumpstate:\s+(\d{4}\-\d{2}\-\d{2})\s+\d{2}:\d{2}:\d{2}')
    date_value=date_re.findall(file)[0]
    for line in re_proc_am_pss.findall(file):
        values_proc_am_pss_p1, values_proc_am_pss_p2 = processInfoPss(line, values_proc_am_pss_p1, values_proc_am_pss_p2)
        time_value = (re.search(r'\d{2}:\d{2}:\d{2}', values_proc_am_pss_p1[1]).group())
        timestamp_am_pss.append(time_value)
        date_am_pss.append(date_value)
        pid_am_pss.append(values_proc_am_pss_p2[0])
        name_am_pss.append(values_proc_am_pss_p2[2])
        pss_am_pss.append(int(arredondar_numero(bytes_to_mb(int(values_proc_am_pss_p2[3])))))
        rss_am_pss.append(int(arredondar_numero(bytes_to_mb(int(values_proc_am_pss_p2[6])))))

    data_ampss = {
        'Date': date_am_pss,
        'Timestamp': timestamp_am_pss,
        'PID': pid_am_pss,
        'Process': name_am_pss,
        'PSS': pss_am_pss,
        'RSS': rss_am_pss
    }
    df_amPss = pd.DataFrame(data_ampss)
    return (df_amPss)

def boxPlot(proc_am_pss_df):
    fig_pss = px.box(proc_am_pss_df,
                     y='PSS',
                     title='Distribuição do PSS (Proportional Set Size)',
                     labels={'PSS': 'Memória (MB)'},
                     hover_data=['Process'], 
                     points='outliers')  

    # Modifica a cor dos outliers
    fig_pss.update_traces(marker=dict(color='blue', outliercolor='red', line=dict(outliercolor='red', outlierwidth=2)))

    return fig_pss

def boxPlotRss(proc_am_pss_df):
    # Cria o gráfico de caixa com outliers mostrados como pontos
    fig_pss = px.box(proc_am_pss_df,
                     y='PSS',
                     title='Distribuição do PSS (Proportional Set Size)',
                     labels={'PSS': 'Memória (MB)'},
                     hover_data=['Process'], 
                     points='outliers')  

    # Modifica a cor dos outliers
    fig_pss.update_traces(marker=dict(color='blue', outliercolor='red', line=dict(outliercolor='red', outlierwidth=2)))

    return fig_pss

def logPlot(df_am_pss):
    fig = px.scatter(df_am_pss, x="Timestamp", y="PSS", hover_name="Process", log_x=True)
    fig.show()
