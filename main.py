import streamlit as st
import pandas as pd
import requests
import plotly.express as px


st.title('💸 SWD Pay Analysis')

@st.dialog("Login to SWD")
def login():
    userid = st.text_input("User ID", placeholder="f2023xxxx")
    password = st.text_input("Password", type="password")

    if st.button("Submit"):
        result = requests.post("https://swd.bits-hyderabad.ac.in/api/auth", json={"uid":userid,"password":password,"type":"0"})
        
        result_json = result.json()
        if result_json['err']:
            st.write(result_json['msg'])
            st.stop()
        st.session_state.token = result.headers['Authorization']
        st.rerun()



if 'token' not in st.session_state:
    login()
    st.stop()
else:
    data = requests.get("https://swd.bits-hyderabad.ac.in/api/deductions", headers={"Authorization": st.session_state.token}).json() 
    if data['err']:
        st.error(data['msg'])
        st.stop()

dataframe = pd.DataFrame(data["data"])

with st.expander("Show All Transaction Data"):
    st.write(dataframe)

st.subheader('Data Analysis')
# st.write(dataframe.describe())

total_amount_spent = dataframe['total_amount'].sum()
avg_amount_spent_per_transaction = dataframe.groupby('time')['total_amount'].sum().mean()
avg_amount_spent_per_semester = dataframe.groupby('sem')['total_amount'].sum().mean()

c1, c2, c3 = st.columns(3)
c1.metric('Total Amount Spent (Lifetime)', f"₹{total_amount_spent:.2f}")
c2.metric('Avg amount spent per transaction', f"₹{avg_amount_spent_per_transaction:.2f}")
c3.metric('Avg amount spent per semester', f"₹{avg_amount_spent_per_semester:.2f}")

# Filter by sem

sem = st.selectbox("Select Semester", (dataframe['sem'].unique().tolist())[::-1] + ['All Semesters'])

if sem != 'All Semesters':
    dataframe = dataframe[dataframe['sem'] == sem]

total_amount_spent = dataframe['total_amount'].sum()
avg_amount_spent_per_transaction = dataframe.groupby('time')['total_amount'].sum().mean()
# most_visited_vendor = dataframe['g_name'].mode().values[0]
dataframe['day_of_week'] = pd.to_datetime(dataframe['time'], unit='s', origin='unix').dt.day_name()
most_active_day = dataframe.groupby('day_of_week')['total_amount'].sum().idxmax()

c1, c2, c3 = st.columns(3)
c1.metric('Total Amount Spent', f"₹{total_amount_spent:.2f}")
c2.metric('Avg amount spent per transaction', f"₹{avg_amount_spent_per_transaction:.2f}")
c3.metric('Most Active Day by Spendings', most_active_day)


st.write('#### Total Amount Spent per Vendor / Product')
pie_data = dataframe.groupby('g_name')['total_amount'].sum().reset_index()
sorted_pie_data = pie_data.sort_values(by='total_amount', ascending=False)

fig = px.pie(pie_data, names='g_name', values='total_amount')
st.plotly_chart(fig)

with st.expander("Show More"):
    st.write(sorted_pie_data)


st.write('#### Total Amount spent over time')

line_data = dataframe.groupby('time')['total_amount'].sum().reset_index()
line_data['time'] =  pd.to_datetime(line_data['time'], unit="s", origin='unix')
line_data = line_data.sort_values(by='time')

st.line_chart(line_data.set_index('time'))
with st.expander("Show More"):
    st.write(line_data)

st.write('#### Spendings per day of the week')

vendor = st.selectbox("Select Vendor", ['All Vendors'] + dataframe['g_name'].unique().tolist())
if vendor != 'All Vendors':
    dataframe = dataframe[dataframe['g_name'] == vendor]


bar_data = dataframe.groupby('day_of_week')['total_amount'].sum().reset_index()

# sort by day of week
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
bar_data['day_of_week'] = pd.Categorical(bar_data['day_of_week'], categories=days, ordered=True)
bar_data = bar_data.sort_values(by='day_of_week')

st.bar_chart(bar_data.set_index('day_of_week'))