import streamlit as st
import plotly.express as px
import pandas as pd
import os 
import warnings
from prophet import Prophet 
warnings.filterwarnings('ignore')
import plotly.graph_objects as go  # Import for line chart
import plotly.figure_factory as ff

st.set_page_config(page_title="Sales Dashboard!!!",page_icon=":bar_chart:",layout="wide")
st.title(":bar_chart: Sales Dashboard")
st.markdown('<style>div.block-container{padding-top:2rem;}</style>',unsafe_allow_html=True)

#This code is running for a sales dataset having region, state, order date columns in it.
def parse_dates(df, date_column):
    date_formats = [
        '%m-%d-%Y', '%d-%m-%Y', '%Y-%m-%d', '%d-%m-%y', '%m/%d/%Y',
        '%Y-%m-%d %H:%M:%S', '%d/%m/%Y %H:%M:%S', '%d-%m-%Y %H:%M:%S',
        '%d-%m-%Y', '%d/%m/%Y', '%Y/%m/%d'
    ]
    
    for fmt in date_formats:
        try:
            return pd.to_datetime(df[date_column], format=fmt, errors='coerce', dayfirst=fmt.startswith('%d'))
        except ValueError:
            continue
    
    # If no formats match, try default parsing
    return pd.to_datetime(df[date_column], errors='coerce')


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
    
    col1, col2 = st.columns((2))

    # Getting the max and min date from the given data
    startDate = pd.to_datetime(df["Order Date"]).min()
    endDate = pd.to_datetime(df["Order Date"]).max()

    with col1:
        date1 = pd.to_datetime(st.date_input("Start Date", startDate))

    with col2:
        date2 = pd.to_datetime(st.date_input("End Date", endDate))

    df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)].copy()

    # Sidebar filters
    st.sidebar.header("Choose your filter")

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

    # Category wise Sales
    category_df = filtered_df.groupby(by=['Category'], as_index=False)["Sales"].sum()
    
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
        st.subheader('Category wise Sales')
        fig = px.pie(filtered_df, values="Sales", names="Category", template="gridon")
        fig.update_traces(text=filtered_df["Category"], textposition="inside")
        st.plotly_chart(fig, use_container_width=True)

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
    future = model.make_future_dataframe(periods=60)  # Forecast for 0 days
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





    # Download orginal DataSet
    csv = df.to_csv(index = False).encode('utf-8')
    st.download_button('Download Data', data = csv, file_name = "Data.csv",mime = "text/csv")
