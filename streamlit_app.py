import streamlit as st
import pandas as pd
import plotly.express as px

# Load dataset
@st.cache_data
def load_data():
    data = pd.read_csv('combined_dose_data_for_app.csv')
    return data

df = load_data()

# Filter out concentrations that are 1 or above
df = df[df['compound_dose_uM'] < 1]

# Custom CSS for styling
st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
    }
    .sidebar .sidebar-content {
        background-color: #e6e6e6;
    }
    .sidebar .sidebar-content h1 {
        color: #4b4b4b;
    }
    .sidebar .sidebar-content .element-container {
        padding: 10px;
    }
    .sidebar .sidebar-content .element-container label {
        font-size: 16px;
        color: #333;
    }
    .title {
        text-align: center;
        font-size: 32px;
        color: #4b4b4b;
        margin-bottom: 20px;
    }
    .header {
        font-size: 24px;
        color: #333;
        margin-top: 20px;
        margin-bottom: 10px;
    }
    .no-data-message {
        text-align: center;
        font-size: 24px;
        color: #ff4b4b;
        margin-top: 50px;
    }
    .stacked-message {
        text-align: center;
        font-size: 16px;
        color: #333;
        margin-top: 20px;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar for user input
st.sidebar.header('Filter Options')
compare_option = st.sidebar.radio(
    "Select Comparison Type",
    ('Single', 'Compare')
)

if compare_option == 'Single':
    selected_radio = st.sidebar.radio(
        "Select type",
        ('Compound', 'Kinase')
    )

    if selected_radio == 'Compound':
        selected_item = st.sidebar.selectbox(
            'Select Compound',
            df['compound_pubchem_name'].unique()
        )
    else:
        selected_item = st.sidebar.selectbox(
            'Select Kinase',
            df['target'].unique()
        )

else:
    selected_radio = st.sidebar.radio(
        "Select type to compare",
        ('Compounds', 'Kinases')
    )

    if selected_radio == 'Compounds':
        selected_item1 = st.sidebar.selectbox(
            'Select First Compound',
            df['compound_pubchem_name'].unique()
        )
        selected_item2 = st.sidebar.selectbox(
            'Select Second Compound',
            df['compound_pubchem_name'].unique()
        )
    else:
        selected_item1 = st.sidebar.selectbox(
            'Select First Kinase',
            df['target'].unique()
        )
        selected_item2 = st.sidebar.selectbox(
            'Select Second Kinase',
            df['target'].unique()
        )

selected_concentration_range = st.sidebar.slider(
    'Select Concentration Range (μM)',
    min_value=float(df['compound_dose_uM'].min()),
    max_value=float(df['compound_dose_uM'].max()),
    value=(float(df['compound_dose_uM'].min()), float(df['compound_dose_uM'].max())),
    step=0.01
)

# Main title
st.markdown('<div class="title">Kinase-Drug Interaction Visualization</div>', unsafe_allow_html=True)

# Instructions
st.markdown(
    """
    <div style='text-align: center;'>
        Use the sidebar to select a compound or kinase and a concentration range. 
        The bar chart below will display the inhibition data based on your selections.
    </div>
    """, unsafe_allow_html=True
)

# Filter data based on user input
if compare_option == 'Single':
    if selected_radio == 'Compound':
        filtered_df = df[(df['compound_pubchem_name'] == selected_item) & 
                         (df['compound_dose_uM'] >= selected_concentration_range[0]) & 
                         (df['compound_dose_uM'] <= selected_concentration_range[1]) & 
                         (df['percent_inhibition'] < 100) & 
                         (df['percent_inhibition'] > 0)]
        x_label = 'target'
        x_axis_label = f"Kinases Inhibited by {selected_item}"
        title_prefix = f"Kinase Inhibition for {selected_item}"
    else:
        filtered_df = df[(df['target'] == selected_item) & 
                         (df['compound_dose_uM'] >= selected_concentration_range[0]) & 
                         (df['compound_dose_uM'] <= selected_concentration_range[1]) & 
                         (df['percent_inhibition'] < 100) & 
                         (df['percent_inhibition'] > 0)]
        x_label = 'compound_pubchem_name'
        x_axis_label = f"Compounds Inhibiting {selected_item}"
        title_prefix = f"Kinase Inhibition for {selected_item}"
else:
    if selected_radio == 'Compounds':
        filtered_df = df[((df['compound_pubchem_name'] == selected_item1) | 
                          (df['compound_pubchem_name'] == selected_item2)) & 
                         (df['compound_dose_uM'] >= selected_concentration_range[0]) & 
                         (df['compound_dose_uM'] <= selected_concentration_range[1]) & 
                         (df['percent_inhibition'] < 100) & 
                         (df['percent_inhibition'] > 0)]
        x_label = 'target'
        x_axis_label = f"Kinases Inhibited by {selected_item1} and {selected_item2}"
        title_prefix = f"Kinase Inhibition for {selected_item1} and {selected_item2}"
    else:
        filtered_df = df[((df['target'] == selected_item1) | 
                          (df['target'] == selected_item2)) & 
                         (df['compound_dose_uM'] >= selected_concentration_range[0]) & 
                         (df['compound_dose_uM'] <= selected_concentration_range[1]) & 
                         (df['percent_inhibition'] < 100) & 
                         (df['percent_inhibition'] > 0)]
        x_label = 'compound_pubchem_name'
        x_axis_label = f"Compounds Inhibiting {selected_item1} and {selected_item2}"
        title_prefix = f"Kinase Inhibition for {selected_item1} and {selected_item2}"

# Check if filtered dataframe is empty
if filtered_df.empty:
    st.markdown("<div class='no-data-message'>No data available for the selected options. Please try different selections.</div>", unsafe_allow_html=True)
else:
    st.markdown("<div class='stacked-message'>The concentrations are stacked on top of each other.</div>", unsafe_allow_html=True)
    # Sort the dataframe by 'percent_inhibition' in descending order
    filtered_df = filtered_df.sort_values(by='percent_inhibition', ascending=False)

    # Plotly chart
    fig = px.bar(filtered_df, x=x_label, y='percent_inhibition', 
                 color='compound_pubchem_name' if selected_radio == 'Compounds' or compare_option == 'Compare' and selected_radio == 'Kinases' else 'target',
                 barmode='group',
                 hover_data=['compound_pubchem_name', 'target', 'compound_dose_uM'])

    fig.update_layout(title=f"{title_prefix} at {selected_concentration_range[0]} - {selected_concentration_range[1]} μM",
                      xaxis_title=x_axis_label,
                      yaxis_title='Inhibition',
                      margin=dict(t=80))

    st.plotly_chart(fig)

# Final instructions
st.markdown(
    """
    <div style='text-align: center; margin-top: 20px;'>
        Adjust the selections in the sidebar to explore different interactions between kinases and drugs at various concentrations.
    </div>
    """, unsafe_allow_html=True
)
