import streamlit as st
import pandas as pd
import requests
import plotly.express as px


st.title('💸 SWD Pay Analysis')

@st.dialog("Login to SWD")
def login():
    userid = st.text_input("User ID")
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

with st.expander("Show Full Data"):
    st.write(dataframe)

# Filter by sem

sem = st.selectbox("Select Semester", (dataframe['sem'].unique().tolist())[::-1] + ['All Semesters'])

if sem != 'All':
    dataframe = dataframe[dataframe['sem'] == sem]

st.subheader('Data Analysis')
# st.write(dataframe.describe())

total_amount_spent = dataframe['total_amount'].sum()
avg_amount_spent_per_day = dataframe.groupby('time')['total_amount'].sum().mean()
avg_amount_spent_per_month = dataframe.groupby('time')['total_amount'].sum().mean() * 30

c1, c2, c3 = st.columns(3)
c1.metric('Total Amount Spent', f"₹{total_amount_spent:.2f}")
c2.metric('Average amount spent every day', f"₹{avg_amount_spent_per_day:.2f}")
c3.metric('Average amount spent every month', f"₹{avg_amount_spent_per_month:.2f}")



st.write('#### Total Amount Spent per Product')
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
