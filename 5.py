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
import io


st.set_page_config(page_title="Sales Dashboard!!!",page_icon=":bar_chart:",layout="wide")
st.title(":bar_chart: Sales Dashboard")
st.markdown('<style>div.block-container{padding-top:2rem;}</style>',unsafe_allow_html=True)

#This code is running for a sales dataset having region, state, order date columns in it.
def parse_dates(df, date_column):
    date_formats = [
        #'%m-%d-%Y', '%d-%m-%Y', '%Y-%m-%d', '%d-%m-%y', '%m/%d/%Y',
        #'%Y-%m-%d %H:%M:%S', '%d/%m/%Y %H:%M:%S', '%d-%m-%Y %H:%M:%S',
        #'%d-%m-%Y', '%d/%m/%Y', '%Y/%m/%d'


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
    
    # If no formats match, try default parsing
    #return pd.to_datetime(df[date_column], errors='coerce')  errors='coerce'


# File uploader
fl = st.file_uploader(":file_folder: Upload a file", type=(["csv","txt","xlsx","xls"]))

if fl is not None:
    st.write(fl.name)  # Show the name of the uploaded file
    
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

        # Continue with your existing processing and visualization
        st.write(df.head())  # Display a preview of the data
    # Parse 'Order Date' into datetime format, allowing flexibility for different formats
    #df["Order Date"] = pd.to_datetime(df["Order Date"], errors='coerce')

    # Drop rows with NaT in 'Order Date' to prevent errors
    #df = df.dropna(subset=["Order Date"])
    # extra code for kpi 

    
    #col1, col2 = st.columns((2))

    # Getting the max and min date from the given data
    #startDate = pd.to_datetime(df["Order Date"]).min()
    #endDate = pd.to_datetime(df["Order Date"]).max()

    #with col1:
        #date1 = pd.to_datetime(st.date_input("Start Date", startDate))

    #with col2:
        #date2 = pd.to_datetime(st.date_input("End Date", endDate))

    #df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)].copy()

    # Sidebar filters
    st.sidebar.header("Choose your filter")
    #Filter by dates
    startDate = pd.to_datetime(df["Order Date"]).min()
    endDate = pd.to_datetime(df["Order Date"]).max()
    date1 = pd.to_datetime(st.sidebar.date_input("Start Date", startDate))
    date2 = pd.to_datetime(st.sidebar.date_input("End Date", endDate))
    df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)].copy()




    # Filter by region
    region = st.sidebar.multiselect("Pick your region", df['Region'].unique())
    if not region:
        df2 = df.copy()
    else:
        df2 = df[df["Region"].isin(region)]
    
    # Filter by state
    state = st.sidebar.multiselect("Pick the state", df2["State"].unique())
    if not state:
       df3 = df2.copy()
    else:
       df3 = df2[df2["State"].isin(state)]
    
    # Filter by city
    city = st.sidebar.multiselect("Pick the city", df3["City"].unique())

    # Final filtering based on selected region, state, and city
    if not region and not state and not city:
        filtered_df = df
    elif not state and not city:
        filtered_df = df[df["Region"].isin(region)]
    elif not region and not city:
        filtered_df = df[df["State"].isin(state)]
    elif state and city:
        filtered_df = df3[df["State"].isin(state) & df3["City"].isin(city)]
    elif region and city:
        filtered_df = df3[df["Region"].isin(region) & df3["City"].isin(city)]
    elif region and state:
        filtered_df = df3[df["Region"].isin(region) & df3["State"].isin(state)]
    elif city:
        filtered_df = df3[df3["City"].isin(city)]
    else:
        filtered_df = df3[df3["Region"].isin(region) & df3["State"].isin(state) & df3["City"].isin(city)]
    
    # extra code for kpi 
    # Calculate KPIs
    total_sales = filtered_df["Sales"].sum()
    total_orders = filtered_df.shape[0]
    total_profit = filtered_df["Profit"].sum()

    # Display KPIs in a box
    st.subheader("Key Performance Indicators")
    kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
    kpi_col1.metric(label=" ⏱ Total Sales", value=f"${total_sales:,.2f}")
    kpi_col2.metric(label=" ⏱ Total Orders", value=f"{total_orders:,}")
    kpi_col3.metric(label="⏱ Total Profit", value=f"${total_profit:,.2f}")
    style_metric_cards(background_color="#e0f7fa",border_left_color="#FF4B4B",border_color="#1f66bd",box_shadow="#F71938")


    # Category wise Sales
    category_df = filtered_df.groupby(by=['Category'], as_index=False)["Sales"].sum()

    col1,col2=st.columns(2)
    
    with col1:
        st.subheader("Category wise Sales")
        fig = px.bar(category_df, x="Category", y="Sales", text=['${:,.2f}'.format(x) for x in category_df["Sales"]], template="seaborn")
        st.plotly_chart(fig, use_container_width=True, height=200)

    with col2:
        st.subheader("Region wise Sales")
        fig = px.pie(filtered_df, values="Sales", names="Region", hole=0.5)
        fig.update_traces(text=filtered_df["Region"], textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

    # View data and download options
    cl1, cl2 = st.columns(2)
    with cl1:
        with st.expander("Category_ViewData"):
            st.write(category_df.style.background_gradient(cmap="Blues"))
            csv = category_df.to_csv(index=False).encode('utf-8')
            st.download_button("Download Data", data=csv, file_name="Category.csv", mime="Text/csv")

    with cl2:
        with st.expander("Region_ViewData"):
            region_sales = filtered_df.groupby(by="Region", as_index=False)["Sales"].sum()
            st.write(region_sales.style.background_gradient(cmap="Oranges"))
            csv = region_sales.to_csv(index=False).encode('utf-8')
            st.download_button("Download Data", data=csv, file_name="Region.csv", mime="text/csv")

    # Time Series Analysis
    filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")
    st.subheader('Time Series Analysis')
    linechart = pd.DataFrame(filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))["Sales"].sum()).reset_index()
    fig2 = px.line(linechart, x="month_year", y="Sales", labels={"Sales": "Amount"}, height=500, width=1000, template="gridon")
    st.plotly_chart(fig2, use_container_width=True)

    with st.expander("View Data of TimeSeries:"):
        st.write(linechart.T.style.background_gradient(cmap="Blues"))
        csv = linechart.to_csv(index=False).encode("utf-8")
        st.download_button('Download Data', data=csv, file_name="TimeSeries.csv", mime='text/csv')

    # Tree map
    st.subheader("Hierarchial View of Sales Using Tree Map")
    fig3 = px.treemap(filtered_df, path=["Region", "Category", "Sub-Category"], values="Sales", hover_data=["Sales"], color="Sub-Category")
    fig3.update_layout(width=800, height=650)
    st.plotly_chart(fig3, use_container_width=True)

    # Segment wise sales and category wise sales
    chart1, chart2 = st.columns(2)
    with chart1:
        st.subheader('Segment wise Sales')
        fig = px.pie(filtered_df, values="Sales", names="Segment", template="plotly_dark")
        fig.update_traces(text=filtered_df["Segment"], textposition="inside")
        st.plotly_chart(fig, use_container_width=True)

    with chart2:
        #st.subheader('Sales Distribution for Region/Sales')
        #fig = px.pie(filtered_df, values="Sales", names="Category", template="gridon")
        #fig.update_traces(text=filtered_df["Category"], textposition="inside")
        #st.plotly_chart(fig, use_container_width=True)
        #fig_distribution = px.violin(filtered_df, y='Sales', x='Category', color='Category', box=True,
                             #title='Sales Distribution by Category')
        #st.plotly_chart(fig_distribution, use_container_width=True)
        # Create a slider for users to choose the number of top products
        top_n = st.slider('Select number of top products to display', min_value=1, max_value=50, value=10, step=1)

        # Compute the top products based on the selected number
        top_products = filtered_df.groupby('Product Name')['Sales'].sum().nlargest(top_n).reset_index()

        # Create a bar chart for the top products
        fig_top_products = px.bar(top_products, x='Product Name', y='Sales', title=f'Top {top_n} Products by Sales')

        # Display the chart
        st.plotly_chart(fig_top_products, use_container_width=True)



    # Summary Table
    st.subheader(":point_right: Month wise Sub-Category Sales Summary")
    with st.expander("Summary_Table"):
        df_sample = df[0:5][["Region", "State", "City", "Category", "Sales", "Profit", "Quantity"]]
        fig = ff.create_table(df_sample, colorscale="Cividis")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("Month wise sub-Category Table")
        filtered_df["month"] = filtered_df["Order Date"].dt.month_name()
        sub_category_Year = pd.pivot_table(data=filtered_df, values="Sales", index=["Sub-Category"], columns="month")
        st.write(sub_category_Year.style.background_gradient(cmap="Blues"))

    # Scatter plot for Sales vs Profit
    st.subheader("Relationship between Sales and Profits")
    data1 = px.scatter(filtered_df, x="Sales", y="Profit", size="Quantity")
    data1['layout'].update(title="Relationship between Sales and Profits using Scatter Plot.",
                           titlefont=dict(size=20), xaxis=dict(title="Sales", titlefont=dict(size=16)),
                           yaxis=dict(title="Profit", titlefont=dict(size=16)))
    st.plotly_chart(data1, use_container_width=True)






    #Extra Code for sales forecasting 
    import plotly.graph_objects as go  # Import for line chart

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
                  template="plotly_white")

    # Show plot in Streamlit
    st.plotly_chart(fig, use_container_width=True)


    # Add a button to navigate to another page
    col1,col2=st.columns(2)
    with col1:
        if st.button("Visualize More"):
            st.write("### Visualizations of the filtered data")
            # Add your visualization code here
            #st.line_chart(df_filtered["Sales"])
            # Upload CSV file
            uploaded_file = st.file_uploader("Upload your Dataset (CSV format)", type="csv")

            # If a file is uploaded
            if uploaded_file is not None:
                df = load_data(uploaded_file)
                # Select the type of plot
                st.write("### Select Visualization Type:")
                chart_type = st.selectbox("Choose the chart type", [
                  "Bar Chart", "Line Chart", "Scatter Plot", "Heatmap", "Area Chart", 
                  "Pie Chart", "Histogram", "Box Plot", "Violin Plot", "Pair Plot", 
                  "Density Plot", "Geographical Map"
                ])

                if chart_type in ["Bar Chart", "Line Chart", "Scatter Plot", "Area Chart"]:
                    st.write("### Select Columns for Plot:")
                    x_col = st.selectbox("Choose X-axis", df.columns)
                    y_col = st.selectbox("Choose Y-axis", df.columns)
                    color = st.color_picker("Pick a color", "#1f77b4")
                    if st.button(f"Generate {chart_type}"):
                       buf = generate_plot(chart_type, x_col, y_col, color)
                       st.image(buf, use_column_width=True)
                       st.download_button("Download Plot", buf, "plot.png", "image/png")

                elif chart_type == "Heatmap":
                    if st.button("Generate Heatmap"):
                       buf = generate_plot(chart_type, None, None, None)
                       st.image(buf, use_column_width=True)
                       st.download_button("Download Heatmap", buf, "heatmap.png", "image/png")

                elif chart_type == "Pie Chart":
                    st.write("### Select Column for Pie Chart:")
                    col = st.selectbox("Choose a Column", df.columns)
                    if st.button("Generate Pie Chart"):
                      buf = generate_plot(chart_type, None, None, None)
                      st.image(buf, use_column_width=True)
                      st.download_button("Download Pie Chart", buf, "pie_chart.png", "image/png")

                elif chart_type == "Histogram":
                    st.write("### Select Column for Histogram:")
                    col = st.selectbox("Choose a Column", df.columns)
                    bins = st.slider("Select number of bins", min_value=10, max_value=100, value=20)
                    if st.button("Generate Histogram"):
                       buf = generate_plot(chart_type, None, None, None, bins)
                       st.image(buf, use_column_width=True)
                       st.download_button("Download Histogram", buf, "histogram.png", "image/png")

                elif chart_type == "Box Plot":
                    st.write("### Select Column for Box Plot:")
                    col = st.selectbox("Choose a Column", df.columns)
                    if st.button("Generate Box Plot"):
                        buf = generate_plot(chart_type, None, None, None)
                        st.image(buf, use_column_width=True)
                        st.download_button("Download Box Plot", buf, "box_plot.png", "image/png")

                elif chart_type == "Violin Plot":
                    st.write("### Select Column for Violin Plot:")
                    col = st.selectbox("Choose a Column", df.columns)
                    if st.button("Generate Violin Plot"):
                        buf = generate_plot(chart_type, None, None, None)
                        st.image(buf, use_column_width=True)
                        st.download_button("Download Violin Plot", buf, "violin_plot.png", "image/png")
                elif chart_type == "Pair Plot":
                    st.write("### Generating Pair Plot for Numerical Data:")
                    if st.button("Generate Pair Plot"):
                        buf = generate_plot(chart_type, None, None, None)
                        st.image(buf, use_column_width=True)
                        st.download_button("Download Pair Plot", buf, "pair_plot.png", "image/png")
                

                elif chart_type == "Density Plot":
                    st.write("### Select Column for Density Plot:")
                    col = st.selectbox("Choose a Column", df.columns)
                    color = st.color_picker("Pick a color", "#1f77b4")
                    if st.button("Generate Density Plot"):
                        buf = generate_plot(chart_type, None, None, color)
                        st.image(buf, use_column_width=True)
                        st.download_button("Download Density Plot", buf, "density_plot.png", "image/png")

                elif chart_type == "Geographical Map":
                    st.write("### Geographical Map:")
                    st.map(df)

            else:
                st.write("Please upload a CSV file to visualize the data.")




    with col2:
        # Download orginal DataSet
        csv = df.to_csv(index = False).encode('utf-8')
        st.download_button('Download Data', data = csv, file_name = "Data.csv",mime = "text/csv")
