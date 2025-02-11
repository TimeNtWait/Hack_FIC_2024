import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Скрипка", layout="wide", initial_sidebar_state="auto")
main_title_cfg = """<div><h1 style="color:#FF64DA; text-align:center; font-size:40px; 
                             font-family: 'Archivo', sans-serif; margin-top:-50px;margin-bottom:20px;">
                    Решение команды "Скрипка"
                    </h1></div>"""

# Load data from CSV
df = pd.read_csv('LLM_buch_dataset.csv')

# Ensure the date column is in datetime format
df['date'] = pd.to_datetime(df['date'], errors='coerce')

# Check for necessary columns
if 'Тема' in df.columns and 'date' in df.columns:
    # Drop rows with incorrect date values
    df = df.dropna(subset=['date'])

    # Add month filter
    st.title('1. Тренды по задаваемым вопросам')

    # Create a list of unique months
    df['year_month'] = df['date'].dt.to_period('M').astype(str)
    months = sorted(df['year_month'].unique())

    # Select month
    selected_months = st.multiselect('Выберите месяцы:', months, default=months)

    # Filter data by selected months
    filtered_data = df[df['year_month'].isin(selected_months)]

    # Group by category, count, and select top 10
    category_counts = (
        filtered_data['Категория']
        .value_counts()
        .head(10)
        .reset_index()
    )
    category_counts.columns = ['Категория', 'Количество']

    # Function to wrap text for labels
    def wrap_text(text, max_len=15):
        if len(text) > max_len:
            space_index = text.rfind(' ', 0, max_len)
            if space_index != -1:
                return text[:space_index] + '<br>' + text[space_index:].lstrip()
            else:
                return text[:max_len] + '<br>' + text[max_len:]
        else:
            return text

    # Apply text wrapping to 'Тема' column
    category_counts['Категория'] = category_counts['Категория'].apply(wrap_text)

    # Select chart type
    chart_type = st.selectbox(
        "Выберите тип диаграммы:",
        ["Столбиковая диаграмма", "Круговая диаграмма", "Горизонтальная диаграмма"]
    )

    # Create plot based on selected type
    if chart_type == "Столбиковая диаграмма":
        fig = px.bar(
            category_counts,
            x="Категория",
            y="Количество",
            title=f"Топ-10 категорий за выбранные месяцы",
            labels={"Количество": "Количество", "Тема": "Темы"},
            color="Количество",
            color_continuous_scale="viridis",
            width=1400,
            height=800
        )
        fig.update_xaxes(tickangle=90)  # Make x-axis labels vertical
        fig.update_layout(xaxis_tickfont_size=30)  # Adjust font size if needed
        # Fix the Y-axis scale by setting a range
        fig.update_yaxes(range=[0, category_counts['Количество'].max() + 10])

    elif chart_type == "Круговая диаграмма":
        fig = px.pie(
            category_counts,
            names="Категория",
            values="Количество",
            title=f"Топ-10 категорий за выбранные месяцы",
            color_discrete_sequence=px.colors.sequential.Viridis,
            width=1400,
            height=800
        )
        fig.update_layout(
            margin=dict(l=20, r=10, t=50, b=50),
            xaxis_title_standoff=50,
            yaxis_title_standoff=50,
            title_font_size=50
        )
    elif chart_type == "Горизонтальная диаграмма":
        fig = px.bar(
            category_counts,
            y="Категория",
            x="Количество",
            title=f"Топ-10 категорий за выбранные месяцы",
            labels={"Количество": "Количество", "Тема": "Темы"},
            orientation="h",
            color="Количество",
            color_continuous_scale="viridis",
            width=1400,
            height=800
        )
        fig.update_yaxes(tickangle=0)  # Keep y-axis labels horizontal
        fig.update_layout(yaxis_tickfont_size=50)  # Adjust font size if needed

    # Update layout for smaller text and larger plot area
    fig.update_layout(
        margin=dict(l=30, r=30, t=70, b=70),
        xaxis_title_standoff=40,
        yaxis_title_standoff=40,
        title_font_size=40
    )
    fig.update_xaxes(tickfont=dict(size=15))
    fig.update_yaxes(tickfont=dict(size=15))

    # Display the plot in Streamlit
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("Данные не содержат нужных колонок. Пожалуйста, проверьте CSV-файл.")
# _________________________________________________________

st.title('Анализ количества вопросов по месяцам')
if 'date' in df.columns and 'Тема' in df.columns and 'Категория' in df.columns:
    # Создаем месяц из даты
    df['месяц'] = df['date'].dt.to_period('M').astype(str)

    # Подсчитываем количество по месяцам
    month_counts = df.groupby('месяц').size().reset_index(name='Количество вопросов')

    # Подсчитываем количество уникальных тем по месяцам
    unique_theme_counts = df.groupby('месяц')['Тема'].nunique().reset_index(name='Количество обсуждаемых тем')

    # Подсчитываем количество уникальных категорий по месяцам
    unique_category_counts = df.groupby('месяц')['Категория'].nunique().reset_index(name='Количество категорий')

    # Сначала объединяем month_counts и unique_theme_counts
    merged_counts = pd.merge(month_counts, unique_theme_counts, on='месяц')

    # Затем объединяем результат с unique_category_counts
    merged_counts = pd.merge(merged_counts, unique_category_counts, on='месяц')

    # Выбор типа графика
    graph_type = st.selectbox(
        "Выберите вид графика:",
        ['Отдельные графики','Совмещенный график']
    )


    if graph_type == 'Совмещенный график':
        # Совмещенный график
        fig = px.bar(
            merged_counts,
            x='месяц',
            y=['Количество вопросов', 'Количество обсуждаемых тем', 'Количество категорий'],
            title="Обработанные вопросы по месяцам",
            labels={"месяц": "Месяц", "value": "Количество", "variable": "Категория"},
            color_continuous_scale="viridis",
            width=800,
            height=800,
            barmode='group'  # Группируем бары для визуализации
        )

        # Настройка графика
        fig.update_xaxes(tickangle=90)  # Поворот меток по оси X
        fig.update_layout(
            margin=dict(l=30, r=20, t=60, b=60),
            xaxis_title_standoff=30,
            yaxis_title_standoff=30,
            title_font_size=30
        )


        fig.update_xaxes(tickfont=dict(size=15))
        fig.update_yaxes(tickfont=dict(size=15))

        # Отображение графика в Streamlit
        st.plotly_chart(fig, use_container_width=True)

    else:
        # Отдельные графики для каждой группы
        for column in ['Количество вопросов', 'Количество обсуждаемых тем', 'Количество категорий']:
            fig = px.bar(
                merged_counts,
                x='месяц',
                y=column,
                title=f"{column} по месяцам",
                labels={"месяц": "Месяц", column: "Количество"},
                color_continuous_scale="viridis",
                width=800,
                height=400,
                color=column
            )

            # Настройка графика
            fig.update_xaxes(tickangle=90)  # Поворот меток по оси X
            fig.update_layout(xaxis_tickfont_size=20)

            # Получаем больше пространства для текста
            fig.update_layout(
                margin=dict(l=30, r=20, t=60, b=60),
                xaxis_title_standoff=30,
                yaxis_title_standoff=30,
                title_font_size=30
            )
            fig.update_xaxes(tickfont=dict(size=15))
            fig.update_yaxes(tickfont=dict(size=15))

            # Отображение графика в Streamlit
            st.plotly_chart(fig, use_container_width=True)

else:
    st.error("Данные не содержат нужных колонок.")

# _________________________________________________________

st.title('2. Поиск упоминаний о компании "БухЭксперт8"')

df_emotion = pd.read_csv('emotion_buhexpert8_df.csv')

if 'date' in df_emotion.columns and 'emotion' in df_emotion.columns:
    # Создаем месяц из даты
    df_emotion['date'] = pd.to_datetime(df_emotion['date'], errors='coerce')
    df_emotion['месяц'] = df_emotion['date'].dt.to_period('M').astype(str)

    # Подсчитываем количество по месяцам
    emotion_counts = df_emotion.groupby('месяц').size().reset_index(name='Количество упоминаний')

    # Подсчитываем количество позитивных упоминаний по месяцам
    positive_counts = (
        df_emotion[df_emotion['emotion'] == 'positive']
        .groupby('месяц')
        .size()
        .reset_index(name='Количество позитивных упоминаний')
    )

    # Подсчитываем количество негативных упоминаний по месяцам
    negative_counts = (
        df_emotion[df_emotion['emotion'] == 'negative']
        .groupby('месяц')
        .size()
        .reset_index(name='Количество негативных упоминаний')
    )

    # Объединяем все данные
    merged_emotion = (
        emotion_counts
        .merge(positive_counts, on='месяц', how='left')  # 'left' для сохранения всех месяцев
        .merge(negative_counts, on='месяц', how='left')
    )

    # Заполняем NaN значением 0 (если для месяца отсутствуют позитивные или негативные упоминания)
    merged_emotion.fillna(0, inplace=True)

    # Выбор типа графика
    graph_type_2 = st.selectbox(
        "Выберите вид графика:",
        ['Отдельные графики','Совмещенный график'],
    key = 'graph_type_2'  # Уникальный ключ
    )

    if graph_type_2 == 'Совмещенный график':
        # Совмещенный график
        fig = px.bar(
            merged_emotion,
            x='месяц',
            y=['Количество упоминаний', 'Количество позитивных упоминаний', 'Количество негативных упоминаний'],
            title="Обработанные эмоции по месяцам",
            labels={"месяц": "Месяц", "value": "Количество", "variable": "Категория"},
            color_continuous_scale="viridis",
            width=800,
            height=800,
            barmode='group'  # Группируем бары для визуализации
        )

        # Настройка графика
        fig.update_xaxes(tickangle=90)
        fig.update_layout(
            margin=dict(l=30, r=20, t=60, b=60),
            xaxis_title_standoff=30,
            yaxis_title_standoff=30,
            title_font_size=30
        )

        # Отображение графика
        st.plotly_chart(fig, use_container_width=True)

    else:
        # Отдельные графики для каждой группы
        for column in ['Количество упоминаний', 'Количество позитивных упоминаний', 'Количество негативных упоминаний']:
            fig = px.bar(
                merged_emotion,
                x='месяц',
                y=column,
                title=f"{column} по месяцам",
                labels={"месяц": "Месяц", column: "Количество"},
                width=800,
                height=400,
                color=column,  # Используем столбец как категорию для цвета
                color_discrete_map={
                    'Количество упоминаний': 'blue',  # Общие упоминания — синий
                    'Количество позитивных упоминаний': 'green',  # Позитивные — зеленый
                    'Количество негативных упоминаний': 'red'  # Негативные — красный
                }
            )

            # Настройка графика
            fig.update_xaxes(tickangle=90)
            fig.update_layout(
                margin=dict(l=30, r=20, t=60, b=60),
                xaxis_title_standoff=30,
                yaxis_title_standoff=30,
                title_font_size=30
            )

            # Отображение графика
            st.plotly_chart(fig, use_container_width=True)

else:
    st.error("Данные не содержат нужных колонок.")

# _________________________________________________________
df_emotion = df_emotion.drop(['Unnamed: 0','contains_similar_buhexpert','clear_text'], axis=1)

st.title('Комментарии с упоминаниями "БухЭксперт8"')
st.markdown("""
    <style>
        .stTable {
            width: 100%;
            overflow-x: auto;
        }
    </style>
""", unsafe_allow_html=True)

# Выводим таблицу с масштабированием на всю ширину
df_emotion