# data_overview.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def show(df):
    st.header("📊 Dataset Overview & Trends (2014 vs. 2016)")
    st.write("This dashboard analyzes mental health attitudes in tech workplaces using survey data from 2014 and 2016. Below, you can see a summary of the combined dataset and key trends over time.")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Combined Dataset Summary")
        st.metric("Total Records", len(df))
        st.metric("Variables", len(df.columns) -1) # Excluding the 'year' column
        st.metric("Years Covered", "2014 & 2016")
        
        st.subheader("Key Variables")
        st.markdown("""
        - `treatment`: Whether employee sought treatment
        - `work_interfere`: How mental health affects work
        - `benefits`: Mental health benefits provided
        - `care_options`: Knowledge of care options
        - `gender`, `age`: Demographic information
        - `year`: Survey year (2014 or 2016)
        """)
    
    with col2:
        st.subheader("Data Preview")
        st.dataframe(df.head(10), height=300)
        
        st.subheader("Missing Values (Combined Dataset)")
        missing_df = pd.DataFrame(df.isnull().sum(), columns=["Missing Values"])
        st.dataframe(missing_df.style.background_gradient(cmap="Reds"))
    
    st.markdown("---")
    st.subheader("Comparison: 2014 vs. 2016 Trends")
    
    # Calculate treatment distribution by year
    treatment_by_year = df.groupby('year')['treatment'].value_counts(normalize=True).unstack().fillna(0)
    
    # Ensure columns exist for both 'No' (0) and 'Yes' (1) treatment
    if 0 not in treatment_by_year.columns:
        treatment_by_year[0] = 0
    if 1 not in treatment_by_year.columns:
        treatment_by_year[1] = 0
    
    treatment_by_year.columns = ['No Treatment', 'Sought Treatment']
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.metric(
            label="Sought Treatment (2014)", 
            value=f"{treatment_by_year.loc[2014, 'Sought Treatment']:.1%}"
        )
    with col_t2:
        st.metric(
            label="Sought Treatment (2016)", 
            value=f"{treatment_by_year.loc[2016, 'Sought Treatment']:.1%}",
            delta=f"{(treatment_by_year.loc[2016, 'Sought Treatment'] - treatment_by_year.loc[2014, 'Sought Treatment']):.1%} from 2014"
        )

    st.markdown("#### Treatment Seeking Behavior Over Time")
    fig_treatment_trend, ax_treatment_trend = plt.subplots(figsize=(8, 4))
    treatment_by_year['Sought Treatment'].plot(kind='line', marker='o', color='#1f77b4', ax=ax_treatment_trend)
    ax_treatment_trend.set_title('Percentage of Employees Who Sought Treatment (2014 vs. 2016)')
    ax_treatment_trend.set_xlabel('Year')
    ax_treatment_trend.set_ylabel('Percentage Who Sought Treatment')
    ax_treatment_trend.set_xticks(treatment_by_year.index)
    ax_treatment_trend.set_ylim(0, 1) # Set y-axis limits for percentage
    ax_treatment_trend.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.0%}'))
    st.pyplot(fig_treatment_trend)

    st.markdown("#### Workplace Support Perceptions Over Time")
    support_cols = ['benefits', 'care_options', 'wellness_program', 'seek_help', 'anonymity']
    
    # Create a DataFrame to hold percentages of 'Yes' for support columns by year
    support_trends = pd.DataFrame(index=[2014, 2016])
    for col in support_cols:
        # Filter out 'Don't know'/'Not sure' for a clearer 'Yes'/'No' trend
        filtered_df = df[df[col].isin(['Yes', 'No'])]
        if not filtered_df.empty: # Check if filtered_df is not empty
            yes_percentages = filtered_df.groupby('year')[col].apply(lambda x: (x == 'Yes').mean())
            support_trends[col] = yes_percentages
        else:
            support_trends[col] = 0 # If no data, set to 0 or NaN

    # Rename columns for better plotting labels
    support_trends.columns = ['Benefits', 'Care Options', 'Wellness Program', 'Seek Help', 'Anonymity Protected']

    fig_support_trend, ax_support_trend = plt.subplots(figsize=(10, 6))
    support_trends.plot(kind='line', marker='o', ax=ax_support_trend)
    ax_support_trend.set_title('Perception of Workplace Mental Health Support Over Time')
    ax_support_trend.set_xlabel('Year')
    ax_support_trend.set_ylabel('Percentage Responded "Yes"')
    ax_support_trend.set_xticks(support_trends.index)
    ax_support_trend.set_ylim(0, 1)
    ax_support_trend.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.0%}'))
    ax_support_trend.legend(title='Support Aspect', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    st.pyplot(fig_support_trend)

    st.markdown("""
    **Insight:** The change in 'Sought Treatment' percentage from 2014 to 2016, along with trends in workplace support features, can indicate the effectiveness of initiatives or shifting attitudes.
    """)

