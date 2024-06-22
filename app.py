import streamlit as st
import pandas as pd
import re
import base64
import zipfile
import io
from utils import amPss, amRss, cpuInfo, processInterruption

# EXPRESSOES REGULARES
reg_total_process = re.compile(r'(Total [A-Z]+ by [a-zA-Z ]+:.*?)\n\n', flags=re.DOTALL)
reg_component = re.compile(r'\s{3}([0-9,]*K: [A-Z][a-z].*?\))\n', flags=re.DOTALL)

# FUNÇÕES AUXILIARES
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

def infoRam(file):
    re_info_ram = re.compile(r'(Total RAM.*?)----------', flags=re.DOTALL)
    t_ram = re.search('Total RAM:(.*?)\n', re_info_ram.findall(file)[0]).group(1)
    f_ram = re.search('Free RAM:(.*?)\n', re_info_ram.findall(file)[0]).group(1)
    ion_ram = re.search('ION:(.*?)\n', re_info_ram.findall(file)[0]).group(1)
    u_ram = re.search('Used RAM:(.*?)\n', re_info_ram.findall(file)[0]).group(1)
    l_ram = re.search('Lost RAM:(.*?)\n', re_info_ram.findall(file)[0]).group(1)
    zram = re.search('ZRAM:(.*?)\n', re_info_ram.findall(file)[0]).group(1)
    tu_ram = re.search('Tuning:(.*?)\n', re_info_ram.findall(file)[0]).group(1)
    d_ram = re.search('-{5,}(.*?)\n', re_info_ram.findall(file)[0]).group(1)
    return t_ram, f_ram, ion_ram, u_ram, l_ram, zram, tu_ram, d_ram


st.title("Memory Tracer")

uploaded_file = st.file_uploader("Upload a file", type=["zip", "txt"])

if uploaded_file is not None:
    content_type = uploaded_file.type
    content_string = uploaded_file.read()
    decoded = base64.b64decode(base64.b64encode(content_string))

    if zipfile.is_zipfile(io.BytesIO(decoded)):
        with zipfile.ZipFile(io.BytesIO(decoded), 'r') as zip:
            file_pattern = re.compile(r'bugreport-caprip_retail-S0RCS32')
            for file_name in zip.namelist():
                if file_pattern.search(file_name) is not None:
                    zip.extract(file_name)
                    with open(file_name, 'r', encoding='latin-1') as extracted_file:
                        extracted_content = extracted_file.read()
                        uploaded_file_contents = extracted_content
    elif 'text' in content_type:
        uploaded_file_contents = decoded.decode('latin-1')
    else:
        st.error("Arquivo incorreto!")
        st.stop()

    # GENERATION DATAFRAME RSS AND PSS 
    df_rss = amRss.totalRss(uploaded_file_contents)
    df_pss = amPss.totalPssRss(uploaded_file_contents)

    df_reason_death = processInterruption.reasonDeath(uploaded_file_contents)
    df_kill = processInterruption.amKill(uploaded_file_contents)
    df_cpuinfo = cpuInfo.cpuInfo(uploaded_file_contents)
    df_ampss = amPss.am_pss(uploaded_file_contents)

    # GENERATION SCATTER PLOT AND BOX PLOT AM PSS
    scatterPlotAmPSS = amPss.scatterPlot(df_ampss)
    boxPlotAmPSS = amPss.boxPlot(df_ampss)
    boxPlotAmRSS = amPss.boxPlotRss(df_ampss)

    # GENERATION LINE CHART RSS AND LINE CHART PSS AND REASONS DEATH HISTOGRAM
    pss_rss_fig = amPss.plotAmPssRss(df_ampss)
    proc_death_fig = processInterruption.plotReasonDeath(uploaded_file_contents)

    # Display Data and Graphs
    st.subheader("AM-PSS")
    st.dataframe(df_ampss)
    st.download_button(label="Download CSV", data=df_ampss.to_csv().encode('utf-8'), file_name='ampss.csv', mime='text/csv')
    st.plotly_chart(scatterPlotAmPSS)  # Plotly chart
    st.plotly_chart(boxPlotAmPSS)      # Plotly chart

    st.subheader("Proportional Set Size (PSS)")
    st.dataframe(df_pss)
    st.download_button(label="Download CSV", data=df_pss.to_csv().encode('utf-8'), file_name='pss.csv', mime='text/csv')
    st.plotly_chart(pss_rss_fig)       # Plotly chart

    st.subheader("Reasons Process Died")
    st.dataframe(df_reason_death)
    st.download_button(label="Download CSV", data=df_reason_death.to_csv().encode('utf-8'), file_name='reason_death.csv', mime='text/csv')
    st.plotly_chart(proc_death_fig)    # Plotly chart

    st.subheader("AM-KILL")
    st.dataframe(df_kill)
    st.download_button(label="Download CSV", data=df_kill.to_csv().encode('utf-8'), file_name='am_kill.csv', mime='text/csv')

    st.subheader("CPU INFO")
    st.dataframe(df_cpuinfo)
    st.download_button(label="Download CSV", data=df_cpuinfo.to_csv().encode('utf-8'), file_name='cpu_info.csv', mime='text/csv')
