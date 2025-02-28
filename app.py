# app.py
import streamlit as st
import requests

st.title("Titanic Dataset Chatbot")
st.write("Ask any question about the Titanic dataset, for example:")
st.markdown("""
- What percentage of passengers were male on the Titanic?
- Show me a histogram of passenger ages.
- What was the average ticket fare?
- How many passengers embarked from each port?
""")

question = st.text_input("Enter your question:")

if st.button("Submit") and question:
    try:
        response = requests.post("http://localhost:8000/ask", json={"question": question})
        response.raise_for_status()
    except Exception as e:
        st.error(f"Error: {e}")
    else:
        data = response.json()
        st.subheader("Answer")
        st.write(data['answer'])
        
        if data.get('plot'):
            st.subheader("Visualization")
            st.image(data['plot'], use_column_width=True)
