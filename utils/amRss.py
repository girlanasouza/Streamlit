import re
import pandas as pd
import plotly.express as px
from utils import amPss

def totalRss(data):
    reg_total_process = re.compile(r'(Total\s+[A-Z]+\s+by\s+[a-zA-Z ]+:.*?)\n\n', flags=re.DOTALL)
    re_rss_process = re.compile(r'([0-9,]+[A-Z]:.*?\))(?:\n|)', flags=re.DOTALL)
    process_consume_rss, process_name_rss, process_id_rss = [],[],[]

    re_rss_process = re.compile(r'([0-9,]+[A-Z]:.*?\))(?:\n|)', flags=re.DOTALL)
    data_to_process = reg_total_process.findall(data)[0]

    for line in re_rss_process.findall(data_to_process):
        values = line.replace(",", "").replace("K", "").replace(":", "").replace("(", "").replace(")", "").split()

        process_consume_rss.append(((float(values[0]))/1024))
        process_name_rss.append(values[1])
        process_id_rss.append(values[3])

    data_amrss = {
        'PID': process_id_rss,
        'Process': process_name_rss,
        'RSS(MB)': process_consume_rss
    }

    df_amRss = pd.DataFrame(data_amrss)

    return df_amRss

def plotAmRss(file):
    df_amRss = amPss.am_pss(file)  
    df_amRss['Timestamp'] = pd.to_datetime(df_amRss['Timestamp'])
    df_amRss = df_amRss.sort_values(by='Timestamp')
    fig = px.line(df_amRss, x='Timestamp', y='RSS', title='RSS Consumption Over Time')
    fig.update_traces(line=dict(color='black'))
    fig.update_layout(
        xaxis_title='Timestamp',
        yaxis_title='RSS Consumption',
        xaxis=dict(tickangle=-45),
        showlegend=True,
    )
    return fig