import streamlit as st
import plotly.express as px
import pandas as pd
import os 
import warnings
from prophet import Prophet 
warnings.filterwarnings('ignore')
from streamlit_extras.metric_cards import style_metric_cards
import plotly.graph_objects as go  # Import for line chart
import plotly.figure_factory as ff
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt
import numpy as np
import io
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from datetime import datetime, timedelta
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error



st.set_page_config(page_title="Sales Dashboard!!!", page_icon=":bar_chart:", layout="wide")
# HTML to include Font Awesome
st.markdown(
    """
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    """,
    unsafe_allow_html=True
)
# Title with Font Awesome icon
st.markdown(
    """
    <h1 style='color: #FFFFF;'>
        <i class="fa-sharp fa-solid fa-chart-line"  style="color: white;"></i> Analytics
        
    </h1>
    """,
    unsafe_allow_html=True
)
#st.title(":bar_chart: Sales Dashboard")
st.markdown('<style>div.block-container{padding-top:2rem;}</style>',unsafe_allow_html=True)
alt.themes.enable("dark")

# Set up session state for page navigation
if 'page' not in st.session_state:
    st.session_state.page = 'dashboard'  # Default to dashboard



#######################
#for .stmetric background-color: #0B1739;
#background-color: rgba(11, 23, 57, 0.4);
# for datasets [stmetric] background-color: #393939;
# CSS styling
# Inject CSS into the Streamlit app for styling
st.markdown("""
    <style>
        body {
            background: rgb(27, 27, 54);
            animation: backgroundChange 10s infinite;
        }

        @keyframes backgroundChange {
            0% { background-color: rgb(27, 27, 54); }
            50% { background-color: rgb(30, 30, 60); }
            100% { background-color: rgb(27, 27, 54); }
        }

        .stButton > button {
            background-color: #0E43FB;  /* Button color */
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            width: 100%;
            # margin-top:5px;
            font-size: 16px;
            cursor: pointer;
        }
        .sd-a{
            margin-top: 20px;  /* Add top margin */
        }
    
        .sidebar-button:hover {
            background-color: #0B36C3; /* Darker shade on hover */
        }
    
        .sidebar-container {
            margin-top: 30px; /* Adjusts margin for the whole container */
        }
    
    </style>
    """,
    unsafe_allow_html=True
)



st.markdown("""
<style>

.stChart, .stmetric {
        background-color: rgba(26, 47, 109, 0.4); 
        padding: 10px;
        border-radius: 10px;
    }
[data-testid="block-container"] {
    padding-left: 0rem;
    padding-right: 0rem;
    padding-top: 0rem;
    padding-bottom: 0rem;
    margin-bottom: -7rem;/
}

[data-testid="stVerticalBlock"] {
    padding-left: 0rem;
    padding-right: 0rem;
}

[data-testid="stMetric"] {
   
    background-color: rgba(26, 47, 109, 0.4); 
    text-align: center;
    padding: 4px 0;
    margin:0px;
    border-radius: 15px;
    animation: pulse 1.5s infinite; /* Subtle pulse animation */
}

[data-testid="stMetricLabel"] {
  display: flex;
  justify-content: center;
  align-items: center;
  margin:0px;
}

[data-testid="stMetricDeltaIcon-Up"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

[data-testid="stMetricDeltaIcon-Down"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

/* Animation */
[data-testid="stMetric"] {
    animation: pulse 1.5s infinite; /* Subtle pulsing animation */
}

</style>
""", unsafe_allow_html=True)

###End of css style

#In order to create the custom css for metric
def custom_metric(label, value, percentage_change, icon_color="#CB3CFF", label_color="#CB3CFF"):
    # Determine the color for the percentage change
    change_color = "#CB3CFF" if percentage_change >= 0 else "#FF3C3C"
    
    # Create HTML with the specified colors
    st.markdown(f"""
    <div style="background-color:#0B1739; padding:10px; border-radius:10px; text-align:left; display: flex; align-items: center;">
        <div style="flex: 1;">
            <h3 style="color:#fafafa;">{value}</h3>
            <p style="color:{label_color}; font-size:18px;">
                <span style="color:{icon_color}; font-size:20px;">{label[:1]}</span>{label[1:]}
            </p>
        </div>
        <div style="flex-shrink: 0; margin-left: 20px;">
            <p style="color:{change_color}; font-size:16px;">
                {percentage_change:.2f}%
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)


# Helper function to format large numbers
def format_number(value):
    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f}B"
    elif value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    elif value >= 1_000:
        return f"{value / 1_000:.2f}K"
    else:
        return f"{int(value)}"





def parse_dates(df, date_column):
    date_formats = [
        #added more date format

        #'%m-%d-%Y', '%d-%m-%Y', '%Y-%m-%d', '%d-%m-%y', '%m/%d/%Y',
        #'%Y-%m-%d %H:%M:%S', '%d/%m/%Y %H:%M:%S', '%d-%m-%Y %H:%M:%S',
        #'%d-%m-%Y', '%d/%m/%Y', '%Y/%m/%d',
        #'%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%SZ',  # ISO 8601
        #'%d %B %Y', '%d %b %Y',  # Full and abbreviated month names
        #'%a, %d %b %Y',  # Weekday with date
        #'%m-%d-%Y %I:%M %p', '%m/%d/%Y %I:%M %p'  # 12-hour format with AM/PM

        #changed some format

        '%d-%m-%Y', '%d/%m/%Y',  # Day-first formats
        '%m-%d-%Y', '%m/%d/%Y',  # Month-first formats
        '%Y-%m-%d', '%Y/%m/%d',  # ISO formats
        '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S',  # ISO 8601 with time
        '%d %B %Y', '%d %b %Y',  # Full and abbreviated month names
        '%a, %d %b %Y',  # Weekday with date
        '%m-%d-%Y %I:%M %p', '%m/%d/%Y %I:%M %p'  # 12-hour format with AM/PM




    ]
    
    for fmt in date_formats:
        try:
            return pd.to_datetime(df[date_column], format=fmt, dayfirst=fmt.startswith('%d'),errors='coerce')
        except ValueError:
            continue
    return(None)

st.sidebar.header(" :file_folder: Upload your datasets")
fl = st.sidebar.file_uploader(" ", type=(["csv", "txt", "xlsx", "xls"]))

if fl is not None:
    # Check the file extension to determine how to read it
    if fl.name.endswith('.csv'):
        df = pd.read_csv(fl, encoding='latin1')
    elif fl.name.endswith('.xls'):
        df = pd.read_excel(fl, engine='xlrd')  # Use xlrd for .xls files
    elif fl.name.endswith('.xlsx'):
        df = pd.read_excel(fl, engine='openpyxl')  # Use openpyxl for .xlsx files
    else:
        st.error("Unsupported file type. Please upload a valid file.")
        df = None  # Set df to None if no valid file is uploaded

    ##if df is not None:
    if 'Order Date' in df.columns:
        # Ensure proper date parsing and remove rows with NaT in 'Order Date'
        df["Order Date"] = pd.to_datetime(df["Order Date"], errors='coerce')
        #df["Order Date"] = pd.to_datetime(df["Order Date"])
        ##df["Order Date"] = parse_dates(df, "Order Date")
        #st.write(df["Order Date"].head())

        df = df.dropna(subset=["Order Date"])
        ##if 'Order Date' in df.columns:
        ##df["Order Date"] = pd.to_datetime(df["Order Date"], errors='coerce')  # Parse dates
        # Drop rows with NaT in 'Order Date'
        ##df = df.dropna(subset=["Order Date"])

        # Create 'Order Year' and 'Order Month' columns if not present
        df['Order Year'] = df['Order Date'].dt.year
        ##df['Order Month'] = df['Order Date'].dt.month  # Extract month for use
        df['Month'] = df['Order Date'].dt.month  # Extract month for use



        # Create or modify columns safely
        if 'Order Year' not in df.columns:
            df['Order Year'] = df['Order Date'].dt.year

        # Filter by year
        st.sidebar.subheader("Choose your filter")
        year_list = sorted(list(df['Order Year'].unique()), reverse=True)
        selected_year = st.sidebar.selectbox("Select a year", year_list)

        # Filter the DataFrame by the selected year
        df_selected_year = df[df['Order Year'] == selected_year].copy()

        # Filter by country (only show countries from the selected year data)
        Country = st.sidebar.multiselect("Pick the Country", df_selected_year["Country"].unique())

        if not Country:
            filtered_df = df_selected_year.copy()  # If no country is selected, show data for all countries
        else:
            filtered_df = df_selected_year[df_selected_year["Country"].isin(Country)]  # Filter by selected countries
        
        #color_theme_list = ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo', 'viridis']
        #selected_color_theme = st.sidebar.selectbox('Select a color theme', color_theme_list)
        # Sidebar menu with styled button
        with st.sidebar:
            # Create a div container for the button to simulate margin and styling
            st.markdown('<div class="sidebar-container ">', unsafe_allow_html=True)

            # Add custom styled button using HTML
            # The custom button itself does nothing here
    
            # Create the button with custom class for styling
            #if st.markdown('<button class="sidebar-button sd-a">Data Preview</button>', unsafe_allow_html=True):
            if st.button('Data Preview'):
                st.session_state.page = 'data_preview'
                #st.experimental_rerun() 
    
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div class="sidebar-container ">', unsafe_allow_html=True)


            # Add custom styled button using HTML
            
            # Create the button with custom class for styling
            #if st.markdown('<button class="sidebar-button">Dashboard</button>', unsafe_allow_html=True):
            if st.button('Dashboard'):
                st.session_state.page = 'dashboard'
    
            st.markdown('</div>', unsafe_allow_html=True)

        # Main content based on page navigation
        if st.session_state.page == 'data_preview':
            st.title("Data Preview")
            st.dataframe(df,height=1000)
            # Custom color map with your theme colors
            colors = ["#00C2FF", "#0E43FB", "#C97DD7"]
            cmap_custom = LinearSegmentedColormap.from_list("custom_theme", colors)
            col1,col2=st.columns((1,1),gap="medium")
            # Custom CSS to expand the table width
            css = """
                <style>
                    .dataframe tbody tr th:only-of-type {
                        vertical-align: middle;
                    }
                    .dataframe tbody tr td {
                        text-align: center;
                    }
                    .dataframe thead th {
                        text-align: center;
                    }
                    .dataframe {
                        width: 80% !important; /* Adjust this value to control the table width */
                        margin: auto;
                    }
                </style>
            """

            with col1:
                st.subheader("Category Wise Sales Data ")
                category_df = filtered_df.groupby(by=['Category'], as_index=False)["Sales"].sum()
                # Apply custom color gradient based on your theme
                #styled_category_df = category_df.style.background_gradient(cmap=cmap_custom)
                #st.dataframe(category_df.style.background_gradient(cmap=cmap_custom), width=1200,height=170)  # Adjust width as needed
                st.dataframe(category_df, width=1200,height=170)  # Adjust width as needed
                 
            with col2: 
                st.subheader("Region Wise Sales Data")
                region_sales = filtered_df.groupby(by="Region", as_index=False)["Sales"].sum()
                #styled_region_sales = region_sales.style.background_gradient(cmap=cmap_custom)
                # Display dataframe with adjustable width
                #st.dataframe(region_sales.style.background_gradient(cmap=cmap_custom), width=1000)  # Adjust width as needed
                st.dataframe(region_sales, width=1000)  # Adjust width as needed
    
            # Define columns with equal width
            col1 = st.columns([1])[0]  
            with col1:
                st.subheader("Month-wise Sub-Category Table")
    
                # Prepare filtered data for the month-wise sub-category table
                filtered_df["month"] = filtered_df["Order Date"].dt.month_name()
                sub_category_Year = pd.pivot_table(data=filtered_df, values="Sales", index=["Sub-Category"], columns="month")
                # Fill NaN values with 0 or any default value
                sub_category_Year = sub_category_Year.fillna(0)
                # Custom CSS to apply theme colors to DataFrame styling         
                st.dataframe(sub_category_Year,width=3000)


        elif st.session_state.page == 'dashboard':
            #New code ---
            col=st.columns((2,2,2,2),gap='small')
            total_sales = filtered_df["Sales"].sum()
            #total_sales = df["Sales"].sum()
            total_orders = filtered_df.shape[0]
            #total_orders = df.shape[0]
            total_profit = filtered_df["Profit"].sum()
            #total_profit = df["Profit"].sum()


            # Calculate Profit Margin Percentage
            if total_sales != 0:  # To avoid division by zero error
                profit_margin_percentage = (total_profit / total_sales) * 100
            else:
                profit_margin_percentage = 0

            #for kpi like 
            # Calculate the number of unique customers
            total_customers = filtered_df["Customer Name"].nunique()
            # Calculate Order Frequency (Number of Orders / Total Customers)
            if total_customers != 0:  # To avoid division by zero
                order_frequency = total_orders / total_customers
            else:
                order_frequency = 0


            #Get current date
            today = datetime.today()
            # Get the latest date in the dataset
            max_date = df['Order Date'].max()

            # Define current period (e.g., current month)
            current_period_start = max_date.replace(day=1)  # First day of the current month
            next_month = (current_period_start + pd.DateOffset(months=1)).replace(day=1)  # First day of the next month
            current_period_end = next_month - pd.DateOffset(days=1)  # Last day of the current month

            # Define previous period based on the current period
            previous_month_start = (current_period_start - pd.DateOffset(months=1)).replace(day=1)
            previous_month_end = current_period_start - pd.DateOffset(days=1)
        
        
            # Convert to datetime
            current_period_start = pd.to_datetime(current_period_start)
            current_period_end = pd.to_datetime(current_period_end)
            previous_month_start = pd.to_datetime(previous_month_start)
            previous_month_end = pd.to_datetime(previous_month_end)

            # Filter data for current and previous periods
            current_period_df = df[(df['Order Date'] >= current_period_start) & (df['Order Date'] <= current_period_end)]
            previous_period_df = df[(df['Order Date'] >= previous_month_start) & (df['Order Date'] <= previous_month_end)]
       
            # Calculate metrics for current period
            current_total_sales = current_period_df['Sales'].sum()
            current_total_profit = current_period_df['Profit'].sum()
            current_profit_margin = (current_total_profit / current_total_sales) * 100 if current_total_sales != 0 else 0

            # Calculate metrics for previous period
            previous_total_sales = previous_period_df['Sales'].sum()
            previous_total_profit = previous_period_df['Profit'].sum()
            previous_profit_margin = (previous_total_profit / previous_total_sales) * 100 if previous_total_sales != 0 else 0
            # Calculate order frequencies
            current_orders = current_period_df.shape[0]
            current_customers = current_period_df['Customer Name'].nunique()
            current_order_frequency = current_orders / current_customers if current_customers != 0 else 0

            previous_orders = previous_period_df.shape[0]
            previous_customers = previous_period_df['Customer Name'].nunique()
            previous_order_frequency = previous_orders / previous_customers if previous_customers != 0 else 0




            # Calculate percentage changes
            sales_change = ((current_total_sales - previous_total_sales) / previous_total_sales) * 100 if previous_total_sales != 0 else 0
            profit_change = ((current_total_profit - previous_total_profit) / previous_total_profit) * 100 if previous_total_profit != 0 else 0
            profit_margin_change = current_profit_margin - previous_profit_margin
            order_frequency_change = ((current_order_frequency - previous_order_frequency) / previous_order_frequency) * 100 if previous_order_frequency != 0 else 0


            # Calculate percentage change
            if previous_order_frequency != 0:
                order_frequency_change = ((current_order_frequency - previous_order_frequency) / previous_order_frequency) * 100
            else:
                order_frequency_change = 0

            #checking for data filtering 
            # Displaying all KPIs inside col[0]
            with col[0]:
                #custom_metric(value=f"{format_number(total_sales)}", label=" 📈  Total Sales")
                custom_metric("📈 Current Sales", f"{format_number(current_total_sales)}", sales_change)
            

            with col[1]:
                #custom_metric(value=f"{format_number(total_orders)}", label="📦 Total Order")
                #custom_metric("🔄 Order Frequency", f"{order_frequency:.2f}")
                custom_metric(
                    "💵 Current Profit", 
                    f"{format_number(current_total_profit)}", 
                    profit_change, 
                    icon_color="#FF6347",  # Tomato for the icon
                    label_color="#1E90FF"  # Dodger Blue for the label
                )

            with col[2]:
                #custom_metric(value=f"{format_number(total_profit)}", label="💰 Total Profit")
                custom_metric(
                    "🔄 Order Frequency", 
                    f"{current_order_frequency:.2f}", 
                    order_frequency_change, 
                    icon_color="#FF1493",  # Deep Pink for the icon
                    label_color="#00BFFF"  # Deep Sky Blue for the label
                )

            with col[3]:
                # Adding KPI for Profit Margin Percentage
                #custom_metric(value=f"{profit_margin_percentage:.2f}%", label="📊 Profit Margin")
                custom_metric(
                    "📊 Profit Margin", 
                    #f"{current_profit_margin:.2f}%", 
                    f"{current_profit_margin:.2f}%", 
                    profit_margin_change, 
                    icon_color="#FFD700",  # Gold for the icon
                    label_color="#ADFF2F"  # Green Yellow for the label
                )

            # Add a gap using st.markdown()
            st.markdown("<br>", unsafe_allow_html=True)  # Adds vertical space between sections
            col=st.columns((3,5),gap='medium')
            with col[0]:
                # Group by Category and sum Sales
                category_df = filtered_df.groupby(by=['Category'], as_index=False)["Sales"].sum()
                # Calculate the total sales
                total_sales = category_df['Sales'].sum()

                # Calculate percentages
                category_df['Percentage'] = (category_df['Sales'] / total_sales) * 100


                # Define colors
                ring_colours = ['#CB3CFF', '#0E43FB', '#00C2FF']

                # Create a pie chart with Plotly Express
                fig = px.pie(
                    category_df,
                    values="Sales",
                    names="Category",
                    hole=0.7,
                    color_discrete_sequence=ring_colours  # Use the custom color sequence
                )

                # Update pie chart traces
                fig.update_traces(
                    textinfo='label',  # Show both label and percentage
                    textposition='inside',  # Place text inside the slices
                    pull=[0, 0, 0],  # Slightly pull the first slice for emphasis (optional)
                    marker=dict(
                        line=dict(color='rgba(255, 255, 255, 0.3)', width=1),  # White border around slices
                    )
                )
                # Calculate the total sales and top category for central text
                total_sales = filtered_df['Sales'].sum()
                top_category = filtered_df.loc[filtered_df['Sales'].idxmax(), 'Category']
                top_sales = filtered_df['Sales'].max()


                #Update annoatation
                # Add annotations
            

                # Update layout
                fig.update_layout(
                    #height=400,
                    height=400,
                    title={
                        'text': "Sales by Category",
                        'y':0.9,
                        'x':0.1,
                        'xanchor': 'left',
                        'yanchor': 'top',
                        'font': dict(
                            family='Montserrat, sans-serif',
                            size=19,
                            color='#D3D3D3',  # Light gray text
                        ),
                    },
                    paper_bgcolor="#0B1739",  # Dark background color
                    plot_bgcolor="#0B1739",  # Dark background color for the plot area
                    margin=dict(l=0, r=0, t=70, b=80),  # Adjust margins to fit the column
                    showlegend=True,  # Hide the legend
                    legend=dict(
                        orientation="h",  # Horizontal legend
                        yanchor="bottom",
                        y=-0.3,  # Position the legend below the chart
                        xanchor="left",

                        x=0.1,  # Position the legend to the left
                        font=dict(color='#D3D3D3'),  # Light gray for legend text
                    ),  
                    font=dict(color='#D3D3D3'),  # Light gray for all text
                )
                # Adding glow effect to chart elements (lines and slices)
                fig.update_traces(marker_line=dict(width=2, color='rgba(255, 255, 255, 0.3)'), selector=dict(type='pie'))

                # Apply hover effect styling
                fig.update_traces(
                    hoverinfo="label+percent+value",  # Display more info on hover
                    hoverlabel=dict(
                        font_size=12,
                        font_family="Montserrat, sans-serif"
                    )
                )
                # Display the pie chart
                st.plotly_chart(fig, use_container_width=True)
                #Extra code for this 
                #Compute the total sales for each product
                top_products = filtered_df.groupby('Product Name')['Sales'].sum().reset_index()
                # To show top 3 products
                top_products_sorted = top_products.sort_values(by='Sales', ascending=False).head(3)
                # Calculate the total sales for percentage calculation
                total_sales = top_products_sorted['Sales'].sum()    

                # Calculate percentage sales and add it as a new column
                top_products_sorted['Percentage'] = (top_products_sorted['Sales'] / total_sales * 100).round(2)
            
                # Truncate product names to a maximum of 2 words
                def truncate_product_name(name, max_words=2):
                    words = name.split()
                    return ' '.join(words[:max_words]) + ('...' if len(words) > max_words else '')


                # Shorten long product names if they exceed a certain length
                top_products_sorted['Product Name'] = top_products_sorted['Product Name'].apply(lambda x: truncate_product_name(x, max_words=2))


                # Display the data in Streamlit with custom styling
                st.markdown(
                    """
                    <style>
                        .top-products-container {
                            background-color: #0B1739;
                            color: #D3D3D3;
                            padding: 20px;
                            height:150px;
                            font-family: 'Montserrat', sans-serif;
                        }
                        .top-products-item {
                            display: flex;
                            align-items: center;
                            #justify-content: space-between;
                            margin-bottom: 10px;
                        }
                        .top-products-item i {
                            margin-right: 10px; /* Space between icon and text */
                            font-size: 14px;
                            color: #00C2FF; /* Light blue color for icons */
                        }    
                        .top-products-item strong {
                            color: #00C2FF;
                            flex-grow: 1; /* Take up remaining space */
                        }
                        .top-products-item span {
                            color: #00C2FF; /* Light blue color for percentages */
                        }
                    </style>
                    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
                    <div class="top-products-container">
                        <h3>Products</h3>
                        
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                # Generate the content for top products
                content = ""
                for _, row in top_products_sorted.iterrows():
                    content += (
                        f'<div class="top-products-item">'
                        f'<i class="fas fa-box" style="margin-right: 2px; font-size: 14px;"></i>'  # Inline style for icon
                        f'<strong>{row["Product Name"]}</strong>'
                        f'<span>{row["Percentage"]}%</span>'
                        f'</div>'
                    )
                # Inject the content into the markdown
                st.markdown(f'<div class="top-products-container">{content}</div>', unsafe_allow_html=True)
            with col[1]:
                # Aggregate sales data by Segment and Month
                # Define color mapping for segments
                sales_data = filtered_df.groupby(['Segment', 'Month'], as_index=False)['Sales'].sum()
                #segment_colors = {
                    #'Segment1': '#CB3CFF',  # Change 'Segment1' to the actual name
                    #'Segment2': '#0E43FB',  # Change 'Segment2' to the actual name
                    #'Segment3': '#00C2FF'   # Change 'Segment3' to the actual name
                #}
                segment_colors = {
                    'Consumer': '#CB3CFF',  # Segment 'Consumer' will be purple
                    'Corporate': '#0E43FB',  # Segment 'Corporate' will be blue
                    'Home Office': '#00C2FF'  # Segment 'Home Office' will be light blue

                }
        
                # Create a bar chart
                fig = go.Figure()
                #print(sales_data['Segment'].unique())  # Check the segment names
                # # Add bars for each segment
                #for segment in sales_data['Segment'].unique():
                #segment_data = sales_data[sales_data['Segment'] == segment]
                #fig.add_trace(go.Bar(
                #x=segment_data['Month'],
                #y=segment_data['Sales'],
                #name=segment,
                #text=segment_data['Sales'].astype(str),
                #textposition='outside',
                #width=0.2 , # Thin bars
                #marker=dict(color=color)  # Set the color explicitly using marker
                #marker_color=segment_colors.get(segment)  # Assign color based on the segment
                #))
                for segment in sales_data['Segment'].unique():
                    segment_data = sales_data[sales_data['Segment'] == segment]
                    # Get the color for the current segment from the dictionary
                    color = segment_colors.get(segment, '#FFFFFF')  # Use white as fallback if no match

                    # Add bar trace for each segment
                    fig.add_trace(go.Bar(
                        x=segment_data['Month'],
                        y=segment_data['Sales'],
                        name=segment,
                        text=segment_data['Sales'].astype(str),
                        textposition='outside',
                        width=0.1,
                        marker=dict(color=color)  # Set the color explicitly using marker
                    ))
                    #Extra code end

                    # Update the layout of the bar chart
                    #extra 
                    fig.update_layout(
                        xaxis_title='Month',
                        yaxis_title='Sales',
                        barmode='stack',
                        legend_title='Segment',
                        height=400,
                        margin=dict(l=50, r=10, t=30, b=30),
                        xaxis=dict(
                            tickvals=sales_data['Month'].unique(),
                            ticktext=sales_data['Month'].unique(),
                            showgrid=False
                        ),
                        yaxis=dict(
                            showgrid=False
                        ),
                        bargap=0.1,
                        plot_bgcolor='#0B1739',
                        paper_bgcolor='#0B1739',
                        font_color='white'
                    )
                # Display the chart in Streamlit
                st.plotly_chart(fig, use_container_width=True)

                #code for area graph
                # Ensure no existing 'month_year' column
                if 'month_year' in filtered_df.columns:
                    filtered_df.drop(columns=['month_year'], inplace=True)
                # Create new 'month_year' column
                filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")

                # Create a new dataframe with sum of Sales grouped by month
                monthly_sales = filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b")).agg({
                    'Sales': 'sum'
                }).reset_index()

                # Create an area chart with sales by month
                fig = px.area(monthly_sales,
                    x="month_year",
                    y="Sales",
                    labels={"Sales": "Sales Amount"},
                    template="gridon",  # You can change this to your desired template
                    height=300,
                    width=700)
            
                # Update layout
                fig.update_layout(
                
                    margin=dict(t=20, b=10),  # Adjusting the top and bottom margins
                    xaxis=dict(showgrid=False),  # Remove x-axis gridlines
                    yaxis=dict(showgrid=False) ,  # Remove y-axis gridlines
                    plot_bgcolor='#0B1739',  # Set the plot area background color
                    paper_bgcolor='#0B1739'  # Set the paper (outer) background color
                )
                # Add transparency to the area fill
                fig.update_traces(
                    fillcolor='rgba(10, 37, 73, 0.4)'  # RGBA color with 30% opacity
                )

                # Add data labels to the chart
                fig.update_traces(mode="lines+markers", textposition="top center")

                # Show the plot with Streamlit
                st.plotly_chart(fig, use_container_width=True)
        
            col=st.columns((5.5,2.5),gap='medium')
            with col[0]:
                # Prepare data for Prophet
                forecast_df = filtered_df.groupby("Order Date").agg({"Sales": "sum"}).reset_index()
                forecast_df.rename(columns={"Order Date": "ds", "Sales": "y"}, inplace=True)

                #extra code 
                # Split the data into training and validation sets
                #train_size = int(len(forecast_df) * 0.8)  # Use 80% for training, 20% for testing        
                #train = forecast_df[:train_size]
                #test = forecast_df[train_size:]

                #end of extra code 
                # Fit the Prophet model
                model = Prophet()
                model.fit(forecast_df)
                #extra code
                #model.fit(train)
                #extra code
                # Make future dataframe for the test period
                future = model.make_future_dataframe(periods=30)  # Match test period length
                forecast = model.predict(future)
                
            
                fig = go.Figure()

                # Add actual sales line
                
                fig.add_trace(go.Scatter(x=forecast_df['ds'], y=forecast_df['y'], mode='lines', name='Actual Sales',
                            line=dict(color='#0E43FB')))  # Actual Sales color

                # Add predicted sales line
                fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], mode='lines', name='Predicted Sales',
                            line=dict(color='#CB3CFF')))  # Predicted Sales color

                # Add lower and upper confidence interval for forecast
                fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_lower'], fill=None, mode='lines',
                        line=dict(color='rgba(10, 37, 73, 0.4)'), showlegend=False, name='Lower Bound'))
                fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_upper'], fill='tonexty', mode='lines',
                        line=dict(color='rgba(10, 37, 73, 0.4)'), showlegend=False, name='Upper Bound'))

                # Update layout
                fig.update_layout(
                    yaxis_title="Sales",
                    yaxis=dict(
                    showgrid=False  # Remove grid lines from x-axis
                    ),
                    template="plotly_white",
                    height=580,
                    paper_bgcolor="#0B1739",  # Dark background color
                    plot_bgcolor="#0B1739",   # Dark background color for the plot area
                    font=dict(color='#D3D3D3'),  # Light gray for text
                    margin=dict(l=0, r=0, t=30, b=30)  # Adjust margins to reduce extra spacing
                )

                # Show plot in Streamlit
                st.plotly_chart(fig, use_container_width=True)

            with col[1]:
                # Total Sales
                total_sales = filtered_df['Sales'].sum()

                # Predefined target scenarios
                target_options = {
                    "Previous Year's Sales": total_sales * 1.1,  # 10% increase
                    "Quarterly Sales Target": total_sales * 1.2,  # 20% increase
                    "Annual Sales Goal": total_sales * 1.5  # 50% increase
                }
                
                # User selects a target scenario
                selected_target = st.selectbox(
                    "Select Target Scenario",
                    options=list(target_options.keys())
                )
                # Get the target sales value based on the selected scenario
                target_sales = target_options[selected_target]
                # Calculate the progress
                progress_percentage = (total_sales / target_sales) * 100
                progress = min(progress_percentage, 100)
                # Create the circular progress bar
                bar_color = "#0E43FB" if progress_percentage <= 100 else "#FF0000"  # Red for overachievement
            
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=progress_percentage,
                    gauge={
                        #'axis': {'range': [0, max(100, progress_percentage)]},
                        'axis': {'range': [0, 100], 'visible': False},
                        #'bar': {'color': "rgba(14, 67, 251, 0.5)", 'line': {'color': 'rgba(0,0,0,0)', 'width': 0}},  # Add transparency to the bar color
                        'bar': {'color': "#00C2FF", 'line': {'color': 'rgba(0,0,0,0)', 'width': 0}},  # Add transparency to the bar color
                        'bgcolor': "#0B1739",
                        'steps': [
                            {'range': [0, 100], 'color': "#0B1739"}
                        ]

                    },
                    title={'text': "Sales Target Completion", 'font': {'size': 24, 'color': "#D3D3D3"}},
                    number={'suffix': "%", 'font': {'color': "#D3D3D3"}}
                ))
                # Update the layout for the chart
                fig.update_layout(
                    paper_bgcolor="#0B1739",
                    font=dict(color='#D3D3D3'),
                    #height=320,  # Adjust height
                    #width=450,   # Adjust width
                    margin=dict(l=10, r=10, t=10, b=10),
                )
                # Create a container with specific dimensions and background color
                with st.container():  # Use st.container() for your layout needs
                    st.markdown(
                        """
                        <div style="background-color: #0B1739; padding: 20px; display: flex; flex-direction: column;">
                        """,
                        unsafe_allow_html=True
                    )

                # Display the chart in Streamlit
                st.plotly_chart(fig)
                st.markdown(
                    """
                        </div>
                    """,
                    unsafe_allow_html=True
                )
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            

        

        

