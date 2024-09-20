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
import io



st.set_page_config(page_title="Sales Dashboard!!!", page_icon=":bar_chart:", layout="wide")
st.title(":bar_chart: Sales Dashboard")
st.markdown('<style>div.block-container{padding-top:2rem;}</style>',unsafe_allow_html=True)
alt.themes.enable("dark")


# Set up session state for page navigation
if 'page' not in st.session_state:
    st.session_state.page = 'dashboard'  # Default to dashboard


#######################
# CSS styling
st.markdown("""
<style>

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
    background-color: #393939;
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

        '%m-%d-%Y', '%d-%m-%Y', '%Y-%m-%d', '%d-%m-%y', '%m/%d/%Y',
        '%Y-%m-%d %H:%M:%S', '%d/%m/%Y %H:%M:%S', '%d-%m-%Y %H:%M:%S',
        '%d-%m-%Y', '%d/%m/%Y', '%Y/%m/%d',
        '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%SZ',  # ISO 8601
        '%d %B %Y', '%d %b %Y',  # Full and abbreviated month names
        '%a, %d %b %Y',  # Weekday with date
        '%m-%d-%Y %I:%M %p', '%m/%d/%Y %I:%M %p'  # 12-hour format with AM/PM

    ]
    
    for fmt in date_formats:
        try:
            return pd.to_datetime(df[date_column], format=fmt, dayfirst=fmt.startswith('%d'))
        except ValueError:
            continue

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

    if df is not None:
        # Ensure proper date parsing and remove rows with NaT in 'Order Date'
        df["Order Date"] = pd.to_datetime(df["Order Date"], errors='coerce')
        df = df.dropna(subset=["Order Date"])

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


        # Sidebar option to navigate between Data Preview and Dashboard
        st.sidebar.title("Navigation")
        if st.sidebar.button('Data Preview'):
            st.session_state.page = 'data_preview'
        if st.sidebar.button('Dashboard'):
            st.session_state.page = 'dashboard'
    
        # Page-specific rendering
        if st.session_state.page == 'data_preview':
            st.title("Data Preview")
            #st.dataframe(df)  # Display the dataset as a dataframe
            st.dataframe(df,width=3000,height=600)  # Display the dataset as a dataframe
            col1=st.columns((5,5),gap="medium")
            with col1[0]:
                st.subheader("Category Wise Sales Data ")
                category_df = filtered_df.groupby(by=['Category'], as_index=False)["Sales"].sum()
                st.write(category_df.style.background_gradient(cmap="Blues"))
                csv = category_df.to_csv(index=False).encode('utf-8')
                #st.download_button("Download Data", data=csv, file_name="Category.csv", mime="Text/csv") 
            with col1[1]: 
                st.subheader("Region Wise Sales Data")
                region_sales = filtered_df.groupby(by="Region", as_index=False)["Sales"].sum()
                st.write(region_sales.style.background_gradient(cmap="Oranges"))
                csv = region_sales.to_csv(index=False).encode('utf-8')
                #st.download_button("Download Data", data=csv, file_name="Region.csv", mime="text/csv")
            col1=st.columns([7])[0]
            with col1:
               df_sample = df[0:5][["Region", "State", "City", "Category", "Sales", "Profit", "Quantity"]]
               fig = ff.create_table(df_sample, colorscale="Cividis")
               st.plotly_chart(fig, use_container_width=True)

               st.markdown("Month wise sub-Category Table")
               filtered_df["month"] = filtered_df["Order Date"].dt.month_name()
               sub_category_Year = pd.pivot_table(data=filtered_df, values="Sales", index=["Sub-Category"], columns="month")
               st.write(sub_category_Year.style.background_gradient(cmap="Blues"))
           

        elif st.session_state.page == 'dashboard':
            # Dashboard Main Panel
            col = st.columns((1.5, 4, 2.5), gap='medium')
            with col[0]:
                total_sales = filtered_df["Sales"].sum()
                total_orders = filtered_df.shape[0]
                total_profit = filtered_df["Profit"].sum()

                # Displaying all KPIs inside col[0]
                st.metric(value=f"{format_number(total_sales)}", label=" :chart_with_upwards_trend: Total Sales")
                st.metric(value=f"{format_number(total_orders)}", label=" :package: Total Order")
                st.metric(value=f"{format_number(total_profit)}", label=":moneybag: Total Profit")

                #this code for category 
                category_df = filtered_df.groupby(by=['Category'], as_index=False)["Sales"].sum()

                fig = px.pie(
                    filtered_df,
                    values="Sales",
                    names="Category",
                    hole=0.5
                )
                fig.update_traces(
                    textinfo='label+percent',  # Show both label and percentage
                    textposition='inside'  # Place text inside the slices
                )

                # Update pie chart layout to fit column width
                fig.update_layout(
                    height=300,
                    title="Sales by Category ",  # Set height to fit the column
                    margin=dict(l=0, r=0, t=30, b=30) , # Remove margins to fit the column
                    showlegend=False  # Hide the legend
                )

                # Display the pie chart
                st.plotly_chart(fig, use_container_width=True)

            # View data and download options
            with col[1]:
                # Ensure no existing 'month_year' column
                if 'month_year' in filtered_df.columns:
                  filtered_df.drop(columns=['month_year'], inplace=True)

                # Create new 'month_year' column
                filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")

                # Create a new dataframe with sum of Sales and Profit grouped by month
                monthly_sales_profit = filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b")).agg({
                   'Sales': 'sum',
                   'Profit': 'sum'
                }).reset_index()

                # Create an area chart with sales and profit by month
                fig = px.area(monthly_sales_profit,
                        x="month_year",
                        y=["Sales", "Profit"],
                        labels={"value": "Amount", "variable": "Metrics"},
                        template="gridon",  # You can change this to your desired template
                        height=300,
                        width=700)
                fig.update_layout(
                    title={
                    'text': "Monthly Sales and Profit",
                    'y': 0.95,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top',
                    'font': dict(family='Montserrat, sans-serif', size=22, color='#D3D3D3'),
                    },
                    margin=dict(t=20, b=10),  # Adjusting the top and bottom margins
                    xaxis=dict(showgrid=False),  # Remove x-axis gridlines
                    yaxis=dict(showgrid=False)   # Remove y-axis gridlines
                )
                # Add data labels to the chart
                fig.update_traces(mode="lines+markers", textposition="top center")

                # Show the plot with Streamlit
                st.plotly_chart(fig, use_container_width=True)   # Ensure no existing 'Month-Day' column
                if 'Month-Day' in filtered_df.columns:
                   filtered_df = filtered_df.drop(columns=['Month-Day'])

                # Extract month and day from 'Order Date' and create a new DataFrame for aggregation
                filtered_df['Month'] = filtered_df['Order Date'].dt.month
                filtered_df['Day'] = filtered_df['Order Date'].dt.day

                # Sample data: Sum of sales by month, day, and segment
                sales_by_segment = filtered_df.groupby(['Month', 'Day', 'Segment'])['Sales'].sum().reset_index()

                # Create 'Month-Day' column for visualization
                sales_by_segment['Month-Day'] = sales_by_segment.apply(lambda row: f"{row['Month']:02d}-{row['Day']:02d}", axis=1)

                # Create a line graph with bullet points (markers)
                line_chart = px.line(
                    sales_by_segment,
                    x="Month-Day",
                    y="Sales",
                    color="Segment",  # To differentiate segments
                    markers=True,  # Adds bullet points (markers)
                    labels={"Sales": "Sales Amount", "Month-Day": "Date"},
                    template="plotly_white",  # White background theme
                    title="Sum of Sales by Month, Day, and Segment"
                )

                # Customize hover information (showing values when hovering over markers)
                line_chart.update_traces(mode="lines+markers", hovertemplate="%{y:.2f}<extra></extra>")

                # Optionally adjust layout to improve readability
                line_chart.update_layout(
                   margin=dict(t=25, b=40),  # Reduce top and bottom margins
                   yaxis_title="Sales Amount",  # Y-axis title
                   xaxis_title="Date",  # X-axis title
                   height=300, 
                   showlegend=True  # Show the segment legend
                )

                # Display the chart
                st.plotly_chart(line_chart, use_container_width=True)

            with col[2]:
                # Sum of Sales by Region
                region_sales = filtered_df.groupby('Region', as_index=False)["Sales"].sum()

                # Sort by sales in descending order and select the top 5 regions
                region_sales_sorted = region_sales.sort_values(by="Sales", ascending=False).head(5)

                # Create a pie chart (without hole for donut)
                fig_pie = px.pie(
                   region_sales_sorted,
                   values="Sales",
                   names="Region",
                )

                fig_pie.update_traces(
                   textinfo='label+percent',  # Show both label and percentage
                   textposition='inside'  # Place text inside the slices
                )

                # Update pie chart layout to fit column width
                fig_pie.update_layout(
                   height=200,  # Set a larger height to accommodate more regions
                   margin=dict(l=0, r=0, t=30, b=30),  # Margins
                   showlegend=False,
                   title="Sales by Region",
            
                )

                # Display the pie chart
                st.plotly_chart(fig_pie, use_container_width=True)
        
                # Compute the total sales for each product
                top_products = filtered_df.groupby('Product Name')['Sales'].sum().reset_index()
            
                #To show top 5 product 
                top_products_sorted = top_products.sort_values(by='Sales', ascending=True).head(5)

                # Calculate the total sales for percentage calculation
                total_sales = top_products_sorted['Sales'].sum()     
 
                # Calculate percentage sales and add it as a new column
                top_products_sorted['Percentage'] = (top_products_sorted['Sales'] / total_sales * 100).round(2)
  
            
                # Shorten long product names if they exceed a certain length
                top_products_sorted['Product Name'] = top_products_sorted['Product Name'].apply(lambda x: x if len(x) <= 20 else x[:17] + '...')
            
            
                # Create a horizontal bar chart for the top products
                fig_top_products = px.bar(
                   top_products_sorted,
                   x='Sales',  # Set 'Sales' on the x-axis
                   y='Product Name',  # Set 'Product Name' on the y-axis
                   title='Top 5 Products by Sales',
                   orientation='h',  # Horizontal orientation
                   color='Sales',  # Color bars based on sales for contrast
                   color_continuous_scale='Blues'  # Color scale for better contrast
                )

                # Display sales percentages on the bars
                fig_top_products.update_traces(
                    text=top_products_sorted['Percentage'].astype(str) + '%',
                    texttemplate='%{text}',
                    textposition='inside'
                )
                # Adjust the bar width to better distinguish the values
                fig_top_products.update_traces(marker_line_width=1, marker_line_color="darkgray", width=0.6)
                # Adjust layout for better readability
                fig_top_products.update_layout(
                    height=400,  # Adjust height as needed
                    margin=dict(l=50, r=10, t=30, b=30),  # Adjust margins
                    xaxis_title="Sales",  # X-axis label for sales
                    yaxis_title="",  # Y-axis label for product names
                    coloraxis_showscale=False,  # Hide the color scale bar
                    yaxis=dict(tickmode='linear', automargin=True), # Adjust y-axis for better spacing
                )
                # Display the chart in col[2]
                st.plotly_chart(fig_top_products, use_container_width=True)


            col1=st.columns((4.5,2.5),gap='small')
            with col1[0]: 
                #Extra Code for sales forecasting 
                import plotly.graph_objects as go  # Import for line chart
                from prophet import Prophet 
                # Prepare data for Prophet
                forecast_df = filtered_df.groupby("Order Date").agg({"Sales": "sum"}).reset_index()
                forecast_df.rename(columns={"Order Date": "ds", "Sales": "y"}, inplace=True)

                # Fit the Prophet model
                model = Prophet()
                model.fit(forecast_df)

                # Make future dataframe (e.g., forecast for the next 30 days)
                future = model.make_future_dataframe(periods=30)  # Forecast for 0 days
                forecast = model.predict(future)
                # Create a line plot for actual sales and predicted sales
                fig = go.Figure()

                # Add actual sales line
                fig.add_trace(go.Scatter(x=forecast_df['ds'], y=forecast_df['y'], mode='lines', name='Actual Sales'))

                # Add predicted sales line
                fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], mode='lines', name='Predicted Sales'))

                # Add lower and upper confidence interval for forecast
                fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_lower'], fill=None, mode='lines',
                         line=dict(color='lightgrey'), showlegend=False, name='Lower Bound'))
                fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_upper'], fill='tonexty', mode='lines',
                         line=dict(color='lightgrey'), showlegend=False, name='Upper Bound'))

                # Update layout
                fig.update_layout(title="Sales Forecast",
                    xaxis_title="Date",
                    yaxis_title="Sales",
                    template="plotly_white",
                    height=400,
                    margin=dict(l=0, r=0, t=30, b=30)  # Adjust margins to reduce extra spacing
                )
                # Show plot in Streamlit
                st.plotly_chart(fig, use_container_width=True)
            with col1[1]:
                import plotly.graph_objects as go
                # Aggregate sales data by Category and Segment
                sales_data = filtered_df.groupby(['Category', 'Segment'], as_index=False)['Sales'].sum()

                # Calculate total sales by Segment
                total_sales_by_segment = sales_data.groupby('Segment')['Sales'].sum().reset_index()
                total_sales_by_segment.rename(columns={'Sales': 'Total_Sales'}, inplace=True)

                # Merge total sales with the original sales_data
                sales_data = pd.merge(sales_data, total_sales_by_segment, on='Segment')
                sales_data['Percentage'] = (sales_data['Sales'] / sales_data['Total_Sales'] * 100).round(2)

                # Sort the sales_data by 'Sales' in descending order
                sales_data_sorted = sales_data.sort_values(by='Sales', ascending=False)


                # Create a bar chart
                fig = go.Figure()


                # Add bars for each category
                for category in sales_data_sorted['Category'].unique():
                  category_data = sales_data_sorted[sales_data_sorted['Category'] == category]
                  fig.add_trace(go.Bar(
                    x=category_data['Segment'],
                    y=category_data['Percentage'],
                    name=category,
                    text=category_data['Percentage'].astype(str) + '%',
                    textposition='outside'
                ))

                # Update layout
                fig.update_layout(
                    title='Sales by Category and Segment',
                    xaxis_title='Segment',
                    yaxis_title='Sales',
                    barmode='stack',  # Stack bars to show sales distribution
                    legend_title='Category',
                    height=400,
                    margin=dict(l=50, r=10, t=30, b=30)
                )

                # Display the chart in Streamlit
                st.plotly_chart(fig, use_container_width=True)


