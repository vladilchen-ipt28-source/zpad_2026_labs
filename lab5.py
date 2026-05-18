import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

st.set_page_config(layout="wide", page_title="VHI Analysis")

@st.cache_data
def load_and_merge_data(folder_path):
    all_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.csv')]
    combined_data = []
    
    for i, file in enumerate(all_files): 
        temp_df = pd.read_csv(file, index_col=False, header=1)
        temp_df.columns = [c.replace(' ', '').strip() for c in temp_df.columns]
        temp_df['Region'] = i + 1  
        combined_data.append(temp_df)
    
    df = pd.concat(combined_data, ignore_index=True)
    df['Year'] = df['Year'].astype(int)
    df['Week'] = df['Week'].astype(int)
    return df

folder = "vhi_data"

try:
    df = load_and_merge_data(folder)
except Exception as e:
    st.error(f"Не вдалося зібрати дані з папки '{folder}'. Переконайся, що вона поруч із цим файлом.")
    st.stop()


st.sidebar.header("Налаштування")
index_choice = st.sidebar.selectbox("Індекс:", ["VCI", "TCI", "VHI"])
region_choice = st.sidebar.selectbox("Область (ID):", sorted(df['Region'].unique()))

week_range = st.sidebar.slider("Тижні:", 1, 52, (1, 52))
year_range = st.sidebar.slider("Роки:", int(df['Year'].min()), int(df['Year'].max()), (2000, 2024))

sort_asc = st.sidebar.checkbox("За зростанням")
sort_desc = st.sidebar.checkbox("За спаданням")

if st.sidebar.button("Скинути"):
    st.rerun()

filtered_df = df[(df['Region'] == region_choice) & 
                 (df['Year'].between(year_range[0], year_range[1])) &
                 (df['Week'].between(week_range[0], week_range[1]))]

if sort_asc and not sort_desc:
    filtered_df = filtered_df.sort_values(by=index_choice)
elif sort_desc and not sort_asc:
    filtered_df = filtered_df.sort_values(by=index_choice, ascending=False)

tab1, tab2, tab3 = st.tabs(["Таблиця", "Графік", "Порівняння"])

with tab1:
    st.dataframe(filtered_df, use_container_width=True)

with tab2:
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(filtered_df[index_choice].values, color='orange', lw=2)
    st.pyplot(fig)

with tab3:
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    for reg in df['Region'].unique():
        reg_data = df[(df['Region'] == reg) & (df['Year'].between(year_range[0], year_range[1]))]
        reg_avg = reg_data.groupby('Year')[index_choice].mean()
        alpha = 1.0 if reg == region_choice else 0.1
        ax2.plot(reg_avg.index, reg_avg.values, alpha=alpha)
    st.pyplot(fig2)