from langchain_experimental.agents import create_pandas_dataframe_agent
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
import os
from dotenv import load_dotenv  # Import dotenv to load environment variables

from langchain_openai import OpenAI  # Corrected OpenAI import

app = FastAPI()

class QueryRequest(BaseModel):
    question: str

try:
    df = pd.read_csv("train 2.csv")
except Exception as e:
    raise Exception("Dataset titanic.csv not found. Please make sure it is placed in the same directory.")

# ✅ Load API Key from .env file
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    print("⚠️ OPENAI_API_KEY is missing. Available environment variables:", os.environ)
    raise ValueError("Missing OpenAI API Key. Set OPENAI_API_KEY in Railway Variables.")
else:
    print("✅ OPENAI_API_KEY Loaded Successfully!")


# Initialize OpenAI LLM
llm = OpenAI(temperature=0, openai_api_key=openai_api_key)

# Create Pandas Agent
agent = create_pandas_dataframe_agent(
    llm,
    df,
    verbose=True,
    allow_dangerous_code=True
)

# Helper function: Generate a histogram for passenger ages
def generate_histogram_age():
    fig, ax = plt.subplots()
    ax.hist(df['Age'].dropna(), bins=20, color='skyblue', edgecolor='black')
    ax.set_title("Histogram of Passenger Ages")
    ax.set_xlabel("Age")
    ax.set_ylabel("Count")
    
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return img_base64

# Helper function: Generate a bar chart for number of passengers by embarkation port
def generate_bar_embarked():
    fig, ax = plt.subplots()
    embarked_counts = df['Embarked'].value_counts()
    embarked_counts.plot(kind='bar', ax=ax, color='lightgreen', edgecolor='black')
    ax.set_title("Number of Passengers by Embarked Port")
    ax.set_xlabel("Port")
    ax.set_ylabel("Count")
    
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return img_base64

@app.post("/ask")
async def ask_question(query: QueryRequest):
    question = query.question

    # Use the LangChain agent to get a text answer
    try:
        answer = agent.run(question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    # Check for keywords in the question to decide if a plot should be returned
    plot = None
    q_lower = question.lower()
    if "histogram" in q_lower and "age" in q_lower:
        plot = generate_histogram_age()
    elif "embarked" in q_lower and "port" in q_lower:
        plot = generate_bar_embarked()
    
    return {"answer": answer, "plot": plot}
