import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

# Налаштування сторінки (на весь екран)
st.set_page_config(layout="wide", page_title="VHI Інтерактивний Аналіз")

# Реєстр областей за українським алфавітом (з Лабораторної №2)
ua_regions = {
    1: 'Вінницька', 2: 'Волинська', 3: 'Дніпропетровська', 4: 'Донецька', 
    5: 'Житомирська', 6: 'Закарпатська', 7: 'Запорізька', 8: 'Івано-Франківська', 
    9: 'Київська', 10: 'Кіровоградська', 11: 'Луганська', 12: 'Львівська', 
    13: 'Миколаївська', 14: 'Одеська', 15: 'Полтавська', 16: 'Рівненська', 
    17: 'Сумська', 18: 'Тернопільська', 19: 'Харківська', 20: 'Херсонська', 
    21: 'Хмельницька', 22: 'Черкаська', 23: 'Чернівецька', 24: 'Чернігівська', 
    25: 'Крим', 26: 'Київ', 27: 'Севастополь'
}

# Карта відповідності старих індексів NOAA до назв
noaa_to_ua_dict = {
    1: 'Черкаська', 2: 'Чернігівська', 3: 'Чернівецька', 4: 'Крим', 
    5: 'Дніпропетровська', 6: 'Донецька', 7: 'Івано-Франківська', 8: 'Харківська', 
    9: 'Херсонська', 10: 'Хмельницька', 11: 'Київська', 12: 'Кіровоградська', 
    13: 'Луганська', 14: 'Львівська', 15: 'Миколаївська', 16: 'Одеська', 
    17: 'Полтавська', 18: 'Рівненська', 19: 'Севастополь', 20: 'Сумська', 
    21: 'Тернопільська', 22: 'Вінницька', 23: 'Волинська', 24: 'Закарпатська', 
    25: 'Запорізька', 26: 'Житомирська', 27: 'Київ'
}

@st.cache_data
def load_and_clean_data(folder_path):
    """Зчитує, очищує файли NOAA та приводить до української індексації"""
    if not os.path.exists(folder_path):
        return pd.DataFrame()
        
    all_files = [f for f in os.listdir(folder_path) if f.startswith('vhi_id_')]
    combined_data = []
    
    ua_name_to_id = {v: k for k, v in ua_regions.items()}
    
    for file in all_files:
        try:
            old_id = int(file.split('_')[2])
        except:
            continue
            
        file_path = os.path.join(folder_path, file)
        valid_rows = []
        
        with open(file_path, 'r') as f:
            for line in f:
                if '<' in line or '>' in line or 'html' in line:
                    continue
                parts = line.strip().split(',')
                if len(parts) >= 7 and parts[0].strip().isdigit():
                    valid_rows.append([float(x.strip()) for x in parts[:7]])
        
        if not valid_rows:
            continue
            
        temp_df = pd.DataFrame(valid_rows, columns=['Year','Week','SMN','SMT','VCI','TCI','VHI'])
        
        region_name = noaa_to_ua_dict.get(old_id, "Невідомо")
        new_id = ua_name_to_id.get(region_name, old_id)
        
        temp_df['Area_ID'] = new_id
        temp_df['Area'] = region_name
        combined_data.append(temp_df)
        
    if not combined_data:
        return pd.DataFrame()
        
    df = pd.concat(combined_data, ignore_index=True)
    df['Year'] = df['Year'].astype(int)
    df['Week'] = df['Week'].astype(int)
    return df

# Завантажуємо датасет
folder = "vhi_data"
df = load_and_clean_data(folder)

if df.empty:
    st.error(f"Критична помилка: Не вдалося знайти чисті дані у папці '{folder}'.")
    st.stop()

# Початкові константи для фільтрів
MIN_YEAR = int(df['Year'].min())
MAX_YEAR = int(df['Year'].max())

# --- СИНХРОНІЗАЦІЯ СТАНУ (SESSION STATE) ---
if 'index_choice' not in st.session_state: st.session_state.index_choice = "VHI"
if 'region_choice' not in st.session_state: st.session_state.region_choice = "Київська"
if 'week_range' not in st.session_state: st.session_state.week_range = (1, 52)
if 'year_range' not in st.session_state: st.session_state.year_range = (MIN_YEAR, MAX_YEAR)
if 'asc_check' not in st.session_state: st.session_state.asc_check = False
if 'desc_check' not in st.session_state: st.session_state.desc_check = False

# Функція скидання для кнопки Reset
def reset_filters():
    st.session_state.index_choice = "VHI"
    st.session_state.region_choice = "Київська"
    st.session_state.week_range = (1, 52)
    st.session_state.year_range = (MIN_YEAR, MAX_YEAR)
    st.session_state.asc_check = False
    st.session_state.desc_check = False

# Функції обробки взаємовиключних чекбоксів
def click_asc():
    if st.session_state.asc_check:
        st.session_state.desc_check = False

def click_desc():
    if st.session_state.desc_check:
        st.session_state.asc_check = False

# --- ВЕРСТКА ІНТЕРФЕЙСУ (ДВІ КОЛОНКИ ЗА ТЗ) ---
st.title(" Веб-додаток для інтерактивного аналізу індексів рослинності (VCI, TCI, VHI)")
st.markdown("---")

col_controls, col_charts = st.columns([1, 2.5], gap="large")

with col_controls:
    st.subheader(" Панель фільтрів")
    
    index_choice = st.selectbox("Оберіть часовий ряд:", ["VCI", "TCI", "VHI"], key="index_choice")
    
    sorted_regions = sorted(df['Area'].unique())
    region_choice = st.selectbox("Оберіть область:", sorted_regions, key="region_choice")
    
    # ПРАВИЛЬНІ ІНТЕРВАЛЬНІ СЛАЙДЕРИ (передаємо кортеж у value для двох повзунків)
    week_range = st.slider("Інтервал тижнів:", 1, 52, value=st.session_state.week_range, key="week_range")
    year_range = st.slider("Інтервал років:", MIN_YEAR, MAX_YEAR, value=st.session_state.year_range, key="year_range")
    
    st.markdown("**Сортування таблиці:**")
    sort_asc = st.checkbox("За зростанням значень", key="asc_check", on_change=click_asc)
    sort_desc = st.checkbox("За спаданням значень", key="desc_check", on_change=click_desc)
    
    st.markdown(" ")
    st.button(" Скинути всі фільтри", on_click=reset_filters, use_container_width=True)

# --- ОБРОБКА ДАНИХ ЧЕРЕЗ PANDAS ---
filtered_df = df[(df['Area'] == region_choice) & 
                 (df['Year'].between(year_range[0], year_range[1])) &
                 (df['Week'].between(week_range[0], week_range[1]))].copy()

# Застосування сортування
if st.session_state.asc_check:
    filtered_df = filtered_df.sort_values(by=index_choice, ascending=True)
elif st.session_state.desc_check:
    filtered_df = filtered_df.sort_values(by=index_choice, ascending=False)

# Виведення результатів у праву колонку (Вкладки за ТЗ)
with col_charts:
    tab1, tab2, tab3 = st.tabs(["📋 Таблиця даних", "📈 Часовий ряд області", "🗺️ Порівняння областей"])
    
    with tab1:
        st.caption(f"Знайдено записів: {len(filtered_df)} для регіону: {region_choice}")
        st.dataframe(filtered_df[['Year', 'Week', 'SMN', 'SMT', 'VCI', 'TCI', 'VHI', 'Area_ID', 'Area']], 
                     use_container_width=True, height=450)
        
    with tab2:
        if filtered_df.empty:
            st.warning("⚠️ Немає даних для побудови графіка. Оберіть ширший діапазон фільтрації.")
        else:
            # Для лінійного графіка завжди сортуємо хронологічно
            plot_df = filtered_df.sort_values(by=['Year', 'Week']).reset_index(drop=True)
            plot_df['Time_Label'] = plot_df['Year'].astype(str) + "-w" + plot_df['Week'].astype(str)
            
            fig, ax = plt.subplots(figsize=(10, 4.5))
            # Малюємо по індексах, щоб уникнути каші на осі X
            ax.plot(plot_df.index, plot_df[index_choice], color='tab:orange', lw=2, label=index_choice)
            
            # Налаштовуємо красиві кроки міток на осі X
            step = max(1, len(plot_df) // 10)
            ax.set_xticks(plot_df.index[::step])
            ax.set_xticklabels(plot_df['Time_Label'][::step], rotation=45, fontsize=8)
            
            ax.set_title(f"Динаміка індексу {index_choice} для області: {region_choice}", fontsize=12, weight='bold')
            ax.set_xlabel("Хронологічний період (Рік - Тиждень)", fontsize=9)
            ax.set_ylabel(f"Значення {index_choice}", fontsize=9)
            ax.grid(True, linestyle='--', alpha=0.5)
            ax.legend()
            st.pyplot(fig)
            
    with tab3:
        # Графік порівняння обраної області з усіма іншими
        fig2, ax2 = plt.subplots(figsize=(10, 4.5))
        
        # Обчислюємо середнє за обраний інтервал для КОЖНОЇ області розробника
        for reg in df['Area'].unique():
            reg_data = df[(df['Area'] == reg) & 
                          (df['Year'].between(year_range[0], year_range[1])) &
                          (df['Week'].between(week_range[0], week_range[1]))]
            
            if reg_data.empty:
                continue
                
            reg_avg = reg_data.groupby('Year')[index_choice].mean()
            
            # Стилізація: обрана область — виділена червоним коліром, інші — сірий фон
            if reg == region_choice:
                ax2.plot(reg_avg.index, reg_avg.values, color='tab:red', lw=3.5, label=f"{reg} (Обрано)", zorder=5)
            else:
                ax2.plot(reg_avg.index, reg_avg.values, color='tab:gray', alpha=0.2, lw=1.2, zorder=1)
        
        ax2.set_title(f"Порівняння середніх значень {index_choice}: {region_choice} проти інших областей", fontsize=11, weight='bold')
        ax2.set_xlabel("Рік", fontsize=9)
        ax2.set_ylabel(f"Середнє значення {index_choice}", fontsize=9)
        ax2.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
        ax2.grid(True, linestyle='--', alpha=0.5)
        ax2.legend(loc='upper left')
        st.pyplot(fig2)