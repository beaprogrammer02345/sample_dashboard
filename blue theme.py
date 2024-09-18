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
#alt.themes.enable("dark")

# Load and apply the custom CSS
def load_css(file_path):
    with open(file_path) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Call the function with the path to your CSS file
load_css('style.css')


# Apply the gradient background class
st.markdown('<div class="gradient-bg">', unsafe_allow_html=True)


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
st.markdown('<div class="gradient-sidebar">', unsafe_allow_html=True)

st.sidebar.header(" :file_folder: Upload your datasets")
fl = st.sidebar.file_uploader(" ", type=(["csv", "txt", "xlsx", "xls"]))

st.markdown('</div>', unsafe_allow_html=True)


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
        st.markdown('<div class="gradient-sidebar">', unsafe_allow_html=True)
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
        
        color_theme_list = ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo', 'viridis']
        selected_color_theme = st.sidebar.selectbox('Select a color theme', color_theme_list)
    
        st.markdown('</div>', unsafe_allow_html=True)

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
                hole=0.5,
                color_discrete_sequence=px.colors.sequential.Plasma
            )

            fig.update_traces(
                textinfo='label+percent',  # Show both label and percentage
                textposition='inside',  # Place text inside the slices
                pull=[0, 0, 0],  # Slightly pull the first slice for emphasis (optional)

                # Update pie chart layout to fit column widthpull=[0.1, 0, 0],  # Slightly pull the first slice for emphasis (optional)
                marker=dict(
                   line=dict(color='rgba(255, 255, 255, 0.3)', width=2),  # White border around slices
                   
                )
            )






            fig.update_layout(
                height=300,
                title={
                    'text': "Sales by Category",
                    'y':0.9,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top',
                    'font': dict(
                       family='Montserrat, sans-serif',
                       size=20,
                       color='#D3D3D3',  # Light gray text
                    ),
                    
                },
                # paper_bgcolor="rgba(20, 30, 48, 1)",  # Dark background color matching the futuristic theme
                # plot_bgcolor="rgba(255, 255, 255, 0)",  # Transparent plot background
                paper_bgcolor="rgba(255, 255, 255, 0)",  # Transparent chart background
                plot_bgcolor="rgba(255, 255, 255, 0)",
                margin=dict(l=0, r=0, t=70, b=30),  # Remove margins to fit the column
                showlegend=False,  # Hide the legend
                font=dict(color='#D3D3D3'),  # Light gray for all text
            )
            # Adding glow effect to chart elements (lines and slices)
            fig.update_traces(marker_line=dict(width=2, color='rgba(255, 255, 255, 0.3)'), selector=dict(type='pie'))

            # Apply hover effect styling
            fig.update_traces(
                hoverinfo="label+percent+value",  # Display more info on hover
                hoverlabel=dict(
                    #bgcolor="rgba(255, 255, 255, 0.3)",  # Glowing hover background
                    font_size=12,
                    font_family="Montserrat, sans-serif"
                ),
                #bgcolor="rgba(255, 255, 255, 0.3)",  # Glowing hover background
                #ont_size=12,
                #font_family="Montserrat, sans-serif"
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
                        template="plotly_dark",  # You can use a dark template to match the futuristic theme
                        #template="gridon",  # You can change this to your desired template
                        height=300,
                        width=700,
                        color_discrete_map={
                            "Sales": "#1f77b4",  # Custom color for Sales (light blue)
                            "Profit": "#ff7f0e" # Custom color for Profit (orange)
                            
                        })
                        

            # Customize chart appearance with layout updates
            fig.update_layout(
            title={
                'text': "Monthly Sales and Profit",
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': dict(family='Montserrat, sans-serif', size=22, color='#D3D3D3'),
            },
            paper_bgcolor="rgba(255, 255, 255, 0)",  # Transparent background
            plot_bgcolor="rgba(255, 255, 255, 0)",  # Transparent plot background
            margin=dict(t=40, b=10),  # Adjusting the top and bottom margins
            xaxis=dict(showgrid=False, title=None, color="#D3D3D3"),  # Remove x-axis gridlines and set label color
            yaxis=dict(showgrid=False, title=None, color="#D3D3D3"),  # Remove y-axis gridlines and set label color
            )

        


            fig.update_layout(
                margin=dict(t=20, b=10),  # Adjusting the top and bottom margins
                xaxis=dict(showgrid=False),  # Remove x-axis gridlines
                yaxis=dict(showgrid=False)   # Remove y-axis gridlines
            )

            # Add data labels to the chart
            fig.update_traces(mode="lines+markers", textposition="top center")

            # Show the plot with Streamlit
            st.markdown('<div class="element-glow">', unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)   # Ensure no existing 'Month-Day' column
            st.markdown('</div>', unsafe_allow_html=True)

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
                template="plotly_dark",  # White background theme
                title="Sum of Sales by Month, Day, and Segment",
                color_discrete_sequence=["#1f77b4", "#ff7f0e", "#2ca02c"],  # Custom color palette for segments
            )

            #Customize hover information (showing values when hovering over markers)
            line_chart.update_traces(mode="lines+markers", hovertemplate="%{y:.2f}<extra></extra>")

            # Optionally adjust layout to improve readability
            line_chart.update_layout(
                title={
                    'text': "Sum of Sales by Month, Day, and Segment",
                    'y': 0.95,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top',
                    'font': dict(family='Montserrat, sans-serif', size=22, color='#D3D3D3'),  # Title style
                },
                #paper_bgcolor="rgba(255, 255, 255, 0)",  # Transparent background
                #plot_bgcolor="rgba(255, 255, 255, 0)",  # Transparent plot background
                #margin=dict(t=40, b=40),  # Adjust top and bottom margins
                yaxis=dict(showgrid=False, title="Sales Amount", color="#D3D3D3"),  # Hide gridlines and set axis label color
                xaxis=dict(showgrid=False, title="Date", color="#D3D3D3"),  # Hide gridlines and set axis label color
                height=300, 
                showlegend=True,  # Show the segment legend
                legend=dict(
                    font=dict(family='Montserrat, sans-serif', size=12, color='#D3D3D3'),  # Legend font style
                    bordercolor="rgba(255, 255, 255, 0.3)",  # Border around the legend
                ),
                # Add border around the plot area
                paper_bgcolor="rgba(255, 255, 255, 0)",  # Transparent paper background
                plot_bgcolor="rgba(0, 0, 0, 0)",  # Transparent plot background
                margin=dict(l=50, r=50, t=50, b=50),  # Adjust margins to create space for the border
                shapes=[
                   dict(
                       type="rect",
                       xref="paper", yref="paper",
                       x0=0, y0=0, x1=1, y1=1,
                       line=dict(color="rgba(255, 255, 255, 0.3)", width=2),  # Thin, translucent white border
                    )
                ]
            )
            
            # Add animation or glow effect (optional)
            line_chart.update_traces(line=dict(width=2), marker=dict(size=8, opacity=1, line=dict(width=1, color='rgba(255, 255, 255, 0.5)')))  # Marker with glowing outline

            # Show the plot with Streamlit
            st.markdown('<div class="element-glow">', unsafe_allow_html=True)
            st.plotly_chart(line_chart, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

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
                #color_discrete_sequence=px.colors.sequential.Plasma_r,
                color_discrete_sequence=['#743ad5', '#d53a9d', '#7f00ff', '#e100ff', '#6600cc'],  # New color scheme matching futuristic theme
                #color_discrete_sequence=['#00C9FF', '#101859', '#FBAB7E', '#7201A8', '#845EC2'],
                 
                hole=0.4,  # Adding a hoe to make it a donut chart for modern look
                
            )

            fig_pie.update_traces(
                textinfo='label+percent',  # Show both label and percentage
                textposition='inside',  # Place text inside the slices
                #marker=dict(line=dict(color='#000000', width=2)),  # Add sleek black border
                pull=[0, 0, 0, 0, 0],  # Pull two regions slightly out for emphasis
                opacity=0.85, # Slight transparency for a modern touch
                marker=dict(line=dict(color='#000000', width=0))  # Add sleek black border
            )

            # Update pie chart layout to fit column width
            fig_pie.update_layout(
                height=300,  # Set a larger height to accommodate more regions
                margin=dict(l=0, r=0, t=30, b=0),  # Margins
                showlegend=False,
                #title="Sales by Region",
                title=dict(text="Sales by Region", font=dict(size=24, color="white")),  # Futuristic title font
                paper_bgcolor="rgba(0, 0, 0, 0)",  # Transparent background
                plot_bgcolor="rgba(0, 0, 0, 0)",  # Transparent plot area
                font=dict(color="white"),  # Set all font to white
                #annotations=[dict(text='Region Sales', x=0.5, y=0.5, font_size=20, showarrow=False, font_color="white")]  # Central text
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
                #color_continuous_scale='Blues'  # Color scale for better contrast
                color_continuous_scale=['#00C9FF', '#92FE9D', '#FBAB7E', '#FF5F6D', '#845EC2']  # New futuristic color scale
            )

            # Display sales percentages on the bars
            fig_top_products.update_traces(
               text=top_products_sorted['Percentage'].astype(str) + '%',
               texttemplate='%{text}',
               textposition='inside',
               marker_line_width=0,  # Remove marker lines for a cleaner look
               opacity=0.85  # Add slight transparency for a futuristic feel
            )
            # Adjust the layout to match the theme
            fig_top_products.update_layout(
            title='Top 5 Products by Sales',
            title_font=dict(size=18, color='#FFFFFF'),  # White font for the title
            plot_bgcolor='rgba(0, 0, 0, 0)',  # Transparent background
            paper_bgcolor='rgba(0, 0, 0, 0)',  # Transparent paper background
            font=dict(color='white'),  # White font for labels
            margin=dict(l=10, r=10, t=50, b=10),  # Adjust margins
            height=400  # Increased height for more readability
            )


            # Adjust the bar width to better distinguish the values
            fig_top_products.update_traces(marker_line_width=0.5, marker_line_color="darkgray", width=0.55)


            # Adjust the bar width to better distinguish the values
            #fig_top_products.update_traces(marker_line_width=1, marker_line_color="darkgray", width=0.6)



            # Adjust layout for better readability
            #fig_top_products.update_layout(
            #height=400,  # Adjust height as needed
            #margin=dict(l=50, r=10, t=30, b=30),  # Adjust margins
            #xaxis_title="Sales",  # X-axis label for sales
            #yaxis_title="",  # Y-axis label for product names
            #coloraxis_showscale=False,  # Hide the color scale bar
            #yaxis=dict(tickmode='linear', automargin=True), # Adjust y-axis for better spacing
            #)
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
        # Add actual sales line with futuristic color
        fig.add_trace(go.Scatter(
            x=forecast_df['ds'], 
            y=forecast_df['y'], 
            mode='lines', 
            name='Actual Sales', 
            line=dict(color='#FF6F61', width=3)  # Neon blue line for actual sales
        ))      
        # Add predicted sales line
        fig.add_trace(go.Scatter(
            x=forecast['ds'], 
            y=forecast['yhat'], 
            mode='lines', 
            name='Predicted Sales', 
            line=dict(color='#3B9A77', dash='dash', width=3)  # Neon green dashed line for predictions
        ))

        # Add lower confidence interval for forecast
        fig.add_trace(go.Scatter(
            x=forecast['ds'], 
            y=forecast['yhat_lower'], 
            fill=None, 
            mode='lines',
            line=dict(color='rgba(255, 255, 255, 0.2)', width=1),  # Transparent white for lower bound
            showlegend=False, 
            name='Lower Bound'
        ))
        # Add upper confidence interval and fill between upper and lower
        fig.add_trace(go.Scatter(
            x=forecast['ds'], 
            y=forecast['yhat_upper'], 
            fill='tonexty', 
            mode='lines',
            line=dict(color='rgba(255, 255, 255, 0.2)', width=1),  # Transparent white for upper bound
            showlegend=False, 
            name='Upper Bound'
        ))        

        fig.update_layout(
            title="Sales Forecast",
            title_font=dict(size=18, color='#FFFFFF'),  # White title
            xaxis_title="Date",
            yaxis_title="Sales",
            plot_bgcolor='rgba(0, 0, 0, 0)',  # Transparent plot background
            paper_bgcolor='rgba(0, 0, 0, 0)',  # Transparent paper background
            font=dict(color='white'),  # White font for labels
            xaxis=dict(showgrid=False),  # Remove gridlines for a clean look
            yaxis=dict(showgrid=False),  # Remove gridlines for a clean look
            margin=dict(l=0, r=0, t=50, b=50),  # Adjust margins
            height=400,
            yaxis_range=[min(forecast_df['y'].min(), forecast['yhat_lower'].min()), max(forecast_df['y'].max(), forecast['yhat_upper'].max())]  # Set y-axis range to include all values
        )
        

        #7557AF,DC6369,C7A77A
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

        # Generate a color map dynamically for unique categories
        unique_categories = sales_data_sorted['Category'].unique()
        color_scale = ['#00C9FF', '#92FE9D', '#FBAB7E', '#FF5F6D', '#845EC2']
        #7557AF,DC6369,C7A77A
        color_map = {category: color_scale[i % len(color_scale)] for i, category in enumerate(unique_categories)}

        # Add bars for each category
        for category in sales_data_sorted['Category'].unique():
          category_data = sales_data_sorted[sales_data_sorted['Category'] == category]
          fig.add_trace(go.Bar(
            x=category_data['Segment'],
            y=category_data['Percentage'],
            name=category,
            text=category_data['Percentage'].astype(str) + '%',
            textposition='outside',
            marker=dict(color=color_map.get(category, '#FFFFFF'))  # Apply color map # Futuristic color for bars
        ))

        # Update layout
        fig.update_layout(
            title='Sales by Category and Segment',
            xaxis_title='Segment',
            yaxis_title='Sales',
            barmode='stack',  # Stack bars to show sales distribution
            legend_title='Category',
            height=400,
            margin=dict(l=50, r=10, t=30, b=30),
            plot_bgcolor='rgba(0, 0, 0, 0)',  # Transparent plot background
            paper_bgcolor='rgba(0, 0, 0, 0)',  # Transparent paper background
            font=dict(color='white')  # White font for labels
        )

        # Display the chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)

        print(sales_data_sorted['Category'].unique())
        print(color_map)

# Close the div tag
st.markdown('</div>', unsafe_allow_html=True)