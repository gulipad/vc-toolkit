import streamlit as st
import pandas as pd
import growth_accounting as ga
from datetime import datetime
import numpy as np
import base64
import plotly.graph_objs as go
from plotly.subplots import make_subplots
	
def get_table_download_link(df):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}" download="data.csv">Download CSV File</a>'
    return href

st.write(
	'''
	# The Growth Accounting Toolkit :hammer_and_pick:
	## Volume 1: Quick Ratio

	Welcome to this first volumen on Growth Accounting. The purpose of this toolkit is to give 
	founders and VCs an easy to use interface to evaluate the quality of their growth. In this
	first volume, we will take a look at the [Rolling Quick Ratios](https://medium.com/theventurecity/rolling-quick-ratios-for-product-decision-making-ec758166a10f).
	This first version is simply a *Proof of Concept*, to evaluate if this tool may be useful.

	### Upload your file :file_folder:
	Please upload a *csv* file with your data. Usually transaction data is the most common, 
	but you can use any type of time-bound data (e.g. Log-ins, Key activities...). Make sure it has a **header**.
	'''
)

# uploaded_file = './sample_transactions_short.csv'
uploaded_file = st.file_uploader('Pleasu upload a csv file.', 'csv', )

if uploaded_file is not None:
	data = pd.read_csv(uploaded_file)
	options = [ '---' ]
	columns = data.columns.tolist()
	options = options + columns

	st.write(
		'''
		### Great! Now you have to tell us which columns contain valuable information.
		I need the column that contains the **ID** of each transaction, the one that contains the **timestamp**, and the one that contains the **value to measure**.
		'''
	)
	user_id_field = st.selectbox('Which column contains the unique ID?', options)
	timestamp_field = st.selectbox('Which column contains the timestamp?', options)
	transaction_field = st.selectbox('Which column contains the value to measure?', options)
	# TODO: Add a validation system for the inputs.

	st.write('Once you have selected the fields, generate the charts!')
	generate_dau = st.button('Generate Rolling Quick Ratio')

	if generate_dau:
		with st.spinner('Wait for it...'):
			dau = ga.create_dau_df(data, 
		       user_id = user_id_field, 
		       activity_date = timestamp_field, 
		       inc_amt = transaction_field)
			dau_decorated = ga.create_dau_decorated_df(dau, use_segment = False)
			
			window_day_sizes = [7]
			rolling_df_no_segment = pd.DataFrame()
			for w in window_day_sizes:
			    this_rolling_df = ga.calc_rolling_qr_window(dau_decorated, window_days = w, use_segment = False)
			    rolling_df_no_segment = rolling_df_no_segment.append(this_rolling_df)
			st.success('Done!')
			st.markdown(get_table_download_link(rolling_df_no_segment), unsafe_allow_html=True)

			## Build chart
			fig = go.Figure()
			fig = make_subplots(specs=[[{"secondary_y": True}]])
			time_series = rolling_df_no_segment['window_end_date']
			fig.add_trace(go.Scatter(
			    x=time_series, y=rolling_df_no_segment['new'],
			    name="New users",
			    mode='lines',
			    line=dict(width=0.5, color='rgb(40, 180, 99)'),
			    stackgroup='one', # define stack group
			    hovertemplate =
				    '<br><b>Date</b>: %{x}<br>' +
				    '<b>New</b>: %{y:.2s} users'
			))
			fig.add_trace(go.Scatter(
			    x=time_series, y=rolling_df_no_segment['resurrected'],
			    name="Resurrected users",
			    mode='lines',
			    line=dict(width=0.5, color='rgb(171, 235, 198)'),
			    stackgroup='one', # define stack group
			    hovertemplate =
				    '<br><b>Date</b>: %{x}<br>' +
				    '<b>Resurrected</b>: %{y:.2s} users'
			))
			fig.add_trace(go.Scatter(
			    x=time_series, y=rolling_df_no_segment['churned'],
			    mode='lines',
			    name="Churned users",
			    fill="tozeroy",
			    line=dict(width=0.5, color='rgb(235, 152, 78)'),
			    stackgroup='two', # define stack group
			    hovertemplate =
				    '<br><b>Date</b>: %{x}<br>' +
				    '<b>Churned</b>: %{y:.2s} users'
			))
			fig.add_trace(
			go.Scatter(
			    x=time_series, y=rolling_df_no_segment['user_quick_ratio'],
			    mode='lines',
			    name="Quick Ratio",
			    line_color='rgb(93, 109, 126)',
			    line=dict(width=2),
			    hovertemplate =
				    '<br><b>Date</b>: %{x}<br>' +
				    '<b>Quick ratio</b>: %{y:.2s}'
				),
			secondary_y=True,
			)
			fig.update_layout(
			    legend=dict(
			        x=0,
			        y=-0.2,
			        orientation="h"
			    )
			)
			fig.update_yaxes(title_text="<b>User Status</b>", secondary_y=False)
			fig.update_yaxes(title_text="<b>Quick Ratio</b>", secondary_y=True)
			max_abs_qr = abs(max(rolling_df_no_segment['user_quick_ratio'], key=abs)) * 1.1
			fig.update_yaxes(range=[-max_abs_qr, max_abs_qr], secondary_y=True)

			chart = st.plotly_chart(fig)













