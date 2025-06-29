# diagnostic_analytics.py
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from sklearn.preprocessing import LabelEncoder

# Helper function to prepare data for correlation analysis
@st.cache_data
def prepare_correlation_data(df):
    df_corr = df.copy()
    
    # Select features that are relevant and can be numerically encoded
    # Exclude 'age' and 'year' for this specific correlation as they are already numerical and might skew perception if directly correlated with binary categories
    # Focus on perception, policy, and demographic factors related to mental health
    features_for_corr = [
        'gender', 'self_employed', 'family_history', 'benefits', 
        'care_options', 'wellness_program', 'seek_help', 'anonymity', 
        'leave', 'mental_health_consequence', 'coworkers', 'supervisor', 
        'no_employees', 'tech_company', 'treatment', 'work_interfere'
    ]
    
    # Filter for relevant columns
    df_corr = df_corr[features_for_corr]

    # Map 'work_interfere' and 'leave' to numerical values first
    interference_map = {'Never': 0, 'Rarely': 1, 'Sometimes': 2, 'Often': 3}
    # Ensure 'work_interfere' is string before mapping and fill N/A
    df_corr['work_interfere'] = df_corr['work_interfere'].astype(str).map(interference_map).fillna(0) # Fill N/A with 0 for correlation (no interference)

    leave_map = {
        "Very easy": 0, "Somewhat easy": 1, "Don't know": 2, 
        "Somewhat difficult": 3, "Very difficult": 4
    }
    # Ensure 'leave' is string before mapping and fill 'Don't know'
    df_corr['leave'] = df_corr['leave'].astype(str).map(leave_map).fillna(leave_map["Don't know"]) 

    # Identify remaining categorical columns to one-hot encode
    # These are the ones that are still 'object' type and not 'treatment' (already int from utils.py)
    categorical_cols_to_encode = [col for col in df_corr.columns if df_corr[col].dtype == 'object' and col != 'treatment']

    # Apply one-hot encoding using pd.get_dummies
    df_corr_encoded = pd.get_dummies(df_corr, columns=categorical_cols_to_encode, drop_first=True)
    
    # Ensure 'treatment' is int (it should be from utils.py, but good to be explicit for safety)
    df_corr_encoded['treatment'] = df_corr_encoded['treatment'].astype(int)

    return df_corr_encoded


def show(df):
    st.header("🔍 Mental Wellness Correlations & Workplace Dynamics")
    
    tab1, tab2, tab3 = st.tabs(["Treatment Analysis", "Work Interference", "Correlation Heatmap & Stigma"])
    
    with tab1:
        st.subheader("Treatment Seeking Behavior")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**By Gender**")
            fig, ax = plt.subplots(figsize=(8, 5))
            sns.countplot(x='gender', hue='treatment', data=df, palette='Set2', ax=ax)
            ax.set_title('Treatment Seeking by Gender')
            ax.set_xlabel('Gender')
            ax.set_ylabel('Count')
            ax.legend(title='Sought Treatment', labels=['No', 'Yes'])
            st.pyplot(fig)
            
        with col2:
            st.write("**By Company Size**")
            fig, ax = plt.subplots(figsize=(10, 6))
            company_size_order = ['1-5', '6-25', '26-100', '100-500', '500-1000', 'More than 1000']
            sns.countplot(x='no_employees', hue='treatment', data=df, 
                          order=company_size_order, palette='viridis', ax=ax)
            ax.set_title('Treatment Seeking by Company Size')
            ax.set_xlabel('Number of Employees')
            ax.set_ylabel('Count')
            ax.legend(title='Sought Treatment', labels=['No', 'Yes'])
            plt.xticks(rotation=45)
            st.pyplot(fig)
        
        st.subheader("Treatment by Family History")
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.countplot(x='family_history', hue='treatment', data=df, palette='coolwarm', ax=ax)
        ax.set_title('Treatment Seeking by Family History')
        ax.set_xlabel('Family History of Mental Illness')
        ax.set_ylabel('Count')
        ax.legend(title='Sought Treatment', labels=['No', 'Yes'])
        st.pyplot(fig)
    
    with tab2:
        st.subheader("Work Interference Analysis")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Work Interference Distribution**")
            filtered_df = df[df['work_interfere'] != 'N/A']
            fig, ax = plt.subplots(figsize=(8, 5))
            sns.countplot(x='work_interfere', data=filtered_df, 
                          order=['Never', 'Rarely', 'Sometimes', 'Often'], 
                          palette='magma', ax=ax)
            ax.set_title('Work Interference Levels')
            ax.set_xlabel('Interference Frequency')
            ax.set_ylabel('Count')
            st.pyplot(fig)
            
        with col2:
            st.write("**Interference by Benefits Availability**")
            fig, ax = plt.subplots(figsize=(8, 5))
            sns.countplot(x='benefits', hue='work_interfere', data=filtered_df, 
                          palette='viridis', ax=ax,
                          hue_order=['Never', 'Rarely', 'Sometimes', 'Often'])
            ax.set_title('Work Interference by Mental Health Benefits')
            ax.set_xlabel('Benefits Provided')
            ax.set_ylabel('Count')
            ax.legend(title='Interference Level')
            st.pyplot(fig)
        
        st.subheader("Interference by Company Size")
        fig, ax = plt.subplots(figsize=(12, 6))
        company_size_order = ['1-5', '6-25', '26-100', '100-500', '500-1000', 'More than 1000']
        sns.countplot(x='no_employees', hue='work_interfere', data=filtered_df, 
                      order=company_size_order, palette='coolwarm', ax=ax,
                      hue_order=['Never', 'Rarely', 'Sometimes', 'Often'])
        ax.set_title('Work Interference by Company Size')
        ax.set_xlabel('Number of Employees')
        ax.set_ylabel('Count')
        ax.legend(title='Interference Level')
        plt.xticks(rotation=45)
        st.pyplot(fig)

    with tab3:
        st.subheader("Correlation Heatmap: Understanding Key Drivers")
        st.markdown("""
        This heatmap visualizes the linear relationships between various workplace factors and mental health outcomes (`treatment` and `work_interfere`).
        Values closer to 1 or -1 indicate stronger positive or negative correlations, respectively.
        """)
        
        df_corr = prepare_correlation_data(df)
        
        # Calculate correlation matrix
        correlation_matrix = df_corr.corr()
        
        # Focus on correlations with 'treatment' and 'work_interfere'
        target_correlations = correlation_matrix[['treatment', 'work_interfere']].sort_values(by='treatment', ascending=False)
        
        fig_corr, ax_corr = plt.subplots(figsize=(8, 10))
        sns.heatmap(target_correlations, annot=True, cmap='coolwarm', fmt=".2f", linewidths=.5, ax=ax_corr)
        ax_corr.set_title('Correlation Matrix with Treatment & Work Interference')
        st.pyplot(fig_corr)

        st.markdown("""
        **Insights from Correlation:**
        * Positive correlations with `treatment` suggest factors that increase the likelihood of seeking help.
        * Positive correlations with `work_interfere` indicate factors that are associated with more frequent work interference due to mental health issues.
        * **Actionable:** Identify factors with strong positive/negative correlations to guide intervention strategies. For example, if 'benefits' correlates highly with 'treatment', reinforce benefit communication.
        """)

        st.subheader("Perceived Stigma and Support Gap Analysis")
        st.markdown("""
        Understanding employee comfort levels and fears about discussing mental health is crucial for fostering a supportive environment.
        """)

        col_stigma1, col_stigma2 = st.columns(2)
        with col_stigma1:
            st.write("**Fear of Negative Consequences vs. Treatment Seeking**")
            fig_consequence, ax_consequence = plt.subplots(figsize=(8, 5))
            sns.countplot(x='mental_health_consequence', hue='treatment', data=df, palette='pastel', ax=ax_consequence,
                          order=['Yes', 'No', 'Maybe'])
            ax_consequence.set_title('Fear of Negative Consequences vs. Treatment')
            ax_consequence.set_xlabel('Fear Negative Consequences')
            ax_consequence.set_ylabel('Count')
            ax_consequence.legend(title='Sought Treatment', labels=['No', 'Yes'])
            st.pyplot(fig_consequence)
            st.markdown("""
            **Insight:** Even among those who fear negative consequences, some still seek treatment. This highlights the severity of need but also the courage required. Focus on reducing this fear.
            """)

        with col_stigma2:
            st.write("**Comfort Discussing Mental Health (Coworkers vs. Supervisor)**")
            
            # Combine 'coworkers' and 'supervisor' into a single series for plotting
            comfort_data = df[['coworkers', 'supervisor']].melt(var_name='Relationship', value_name='Comfort Level')
            
            # Order for plotting
            comfort_order = ['Yes', 'No', 'Some of them'] # Assuming 'Some of them' exists for coworkers
            
            fig_comfort, ax_comfort = plt.subplots(figsize=(8, 5))
            sns.countplot(x='Comfort Level', hue='Relationship', data=comfort_data, palette='Set3', ax=ax_comfort,
                          order=comfort_order)
            ax_comfort.set_title('Comfort Discussing Mental Health by Relationship')
            ax_comfort.set_xlabel('Comfort Level')
            ax_comfort.set_ylabel('Count')
            ax_comfort.legend(title='Discuss With')
            st.pyplot(fig_comfort)
            st.markdown("""
            **Insight:** Compare comfort levels with coworkers vs. supervisors. A significant gap suggests a need for management training or fostering a more open leadership culture.
            """)
