import streamlit as st
import requests
import os
import base64  
from dotenv import load_dotenv 

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL")

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
        response = requests.post(f"{BACKEND_URL}/ask", json={"question": question})
        response.raise_for_status()
    except Exception as e:
        st.error(f"❌ Error: {e}")
    else:
        data = response.json()
        st.subheader("Answer")
        st.write(data["answer"])
        
        #decode and display the base64-encoded chart
        if data.get("plot"):
            st.subheader("Visualization")
            image_data = base64.b64decode(data["plot"])  
            st.image(image_data, use_column_width=True)
