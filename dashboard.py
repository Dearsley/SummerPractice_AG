import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Water Potability Dashboard",
    layout="wide"
)

st.title("Анохин Г. А. 2023-ФГиИБ-ПИ-1б Вариант 1")

@st.cache_data
def load_original_data():
    df = pd.read_csv('dataset.csv')
    return df

@st.cache_data
def load_scaled_data():
    return pd.read_csv('water_potability_scaled.csv')

df_original = load_original_data()
df_scaled = load_scaled_data()

# Выбор типа данных
data_type = st.radio(
    "Выберите тип данных:",
    ["Исходные", "Стандартизированные"],
    horizontal=True
)


df = df_scaled if data_type == "Стандартизированные" else df_original

st.markdown("""
**Датасет о пригодности воды к питью**  
9 физико-химических показателей + целевая переменная Potability (1 - пригодна, 0 - нет)
""")

st.subheader("Метрики модели")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Accuracy", "65.7%")
with col2:
    st.metric("ROC-AUC", "65.8%")
with col3:
    st.metric("F1-score (Class 1)", "0.54")

# Выбор типа графика
st.subheader("Визуализация")
graph_type = st.radio(
    "Выберите тип графика:",
    ["Scatter plot (признак vs признак + цвет по цели)",
     "Тепловая карта корреляций"],
    horizontal=True
)

if graph_type == "Scatter plot (признак vs признак + цвет по цели)":
    col1, col2 = st.columns(2)

    with col1:
        x_axis = st.selectbox("Ось X:", df.columns[:-1], index=0)
    with col2:
        y_axis = st.selectbox("Ось Y:", df.columns[:-1], index=1)

    fig = px.scatter(
        df,
        x=x_axis,
        y=y_axis,
        color='Potability',
        color_continuous_scale=['red', 'green'],
        title=f'{x_axis} vs {y_axis}',
        opacity=0.7,
        labels={'Potability': 'Пригодность'}
    )
    st.plotly_chart(fig, use_container_width=True)

else:
    all_features = df.columns[:-1].tolist()
    selected_features = st.multiselect(
        "Выберите признаки для тепловой карты:",
        all_features,
        default=all_features[:5]
    )

    if selected_features:
        features_for_corr = selected_features + ['Potability']
        corr_matrix = df[features_for_corr].corr()

        fig = px.imshow(
            corr_matrix,
            text_auto='.2f',
            color_continuous_scale='RdBu_r',
            aspect="auto",
            title="Матрица корреляций",
            zmin=-1, zmax=1
        )
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Выберите хотя бы один признак")

with st.sidebar:
    st.header("О данных")
    st.write(f"**Всего записей:** {len(df)}")
    st.write(f"**Признаков:** {len(df.columns)-1}")
    st.write(f"**Пригодная вода:** {df['Potability'].sum()} ({df['Potability'].mean()*100:.1f}%)")
    st.write(f"**Непригодная:** {len(df)-df['Potability'].sum()} ({(1-df['Potability'].mean())*100:.1f}%)")

    st.divider()
    st.caption("Streamlit Dashboard • 2026")