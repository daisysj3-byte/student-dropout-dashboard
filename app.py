import streamlit as st
import pandas as pd
import altair as alt

@st.cache_data
def load_data():
    # adjust filename if you keep the space
    df = pd.read_csv("student_dropout_3.csv")
    # make sure Dropped_Out is boolean
    if df["Dropped_Out"].dtype == "object":
        df["Dropped_Out"] = df["Dropped_Out"].map({"True": True, "False": False})
    return df

df = load_data()

st.title("Student Performance & Dropout Dashboard")

st.sidebar.header("Filters")

# Sidebar filters
schools = st.sidebar.multiselect(
    "School",
    options=sorted(df["School"].unique()),
    default=list(df["School"].unique())
)

genders = st.sidebar.multiselect(
    "Gender",
    options=sorted(df["Gender"].unique()),
    default=list(df["Gender"].unique())
)

age_min, age_max = int(df["Age"].min()), int(df["Age"].max())
age_range = st.sidebar.slider(
    "Age range",
    min_value=age_min,
    max_value=age_max,
    value=(age_min, age_max)
)

# Apply filters
filtered = df[
    (df["School"].isin(schools)) &
    (df["Gender"].isin(genders)) &
    (df["Age"].between(age_range[0], age_range[1]))
]

st.subheader("Summary")

n_students = len(filtered)
dropout_rate = 100 * filtered["Dropped_Out"].mean() if n_students > 0 else 0
avg_final = filtered["Final_Grade"].mean() if n_students > 0 else 0

col1, col2, col3 = st.columns(3)
col1.metric("Number of students", n_students)
col2.metric("Dropout rate (%)", f"{dropout_rate:.1f}")
col3.metric("Average final grade", f"{avg_final:.2f}")

st.markdown("---")

# 1. Dropout rate by school
st.subheader("Dropout rate by school")

if len(filtered) > 0:
    school_stats = (
        filtered.groupby("School")["Dropped_Out"]
        .mean()
        .reset_index()
        .rename(columns={"Dropped_Out": "Dropout_Rate"})
    )
    school_stats["Dropout_Rate"] *= 100

    chart1 = (
        alt.Chart(school_stats)
        .mark_bar()
        .encode(
            x=alt.X("School:N", title="School"),
            y=alt.Y("Dropout_Rate:Q", title="Dropout rate (%)"),
            tooltip=["School", alt.Tooltip("Dropout_Rate:Q", format=".1f")]
        )
    )
    st.altair_chart(chart1, use_container_width=True)
else:
    st.info("No data for current filter selection.")

# 2. Final grade by dropout status (boxplot)
st.subheader("Final grade by dropout status")

if len(filtered) > 0:
    filtered2 = filtered.copy()
    filtered2["Dropped_Out_Label"] = filtered2["Dropped_Out"].map(
        {True: "Dropped Out", False: "Stayed"}
    )

    chart2 = (
        alt.Chart(filtered2)
        .mark_boxplot()
        .encode(
            x=alt.X("Dropped_Out_Label:N", title="Status"),
            y=alt.Y("Final_Grade:Q", title="Final grade"),
            tooltip=["Dropped_Out_Label", "Final_Grade"]
        )
    )
    st.altair_chart(chart2, use_container_width=True)
else:
    st.info("No data for current filter selection.")

# 3. Absences vs final grade scatter
st.subheader("Absences vs final grade")

if len(filtered) > 0:
    chart3 = (
        alt.Chart(filtered2)
        .mark_circle(size=60)
        .encode(
            x=alt.X("Number_of_Absences:Q", title="Number of absences"),
            y=alt.Y("Final_Grade:Q", title="Final grade"),
            color=alt.Color("Dropped_Out_Label:N", title="Status"),
            tooltip=[
                "School",
                "Gender",
                "Age",
                "Number_of_Absences",
                "Final_Grade",
                "Dropped_Out_Label"
            ]
        )
    )
    st.altair_chart(chart3, use_container_width=True)
else:
    st.info("No data for current filter selection.")

st.markdown("---")
st.caption("Data: Student dropout dataset")
