FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY . .
RUN pip install -r requirements.txt
# Expose the port that the Streamlit app will run on
EXPOSE 8501
# Set the command to run the Streamlit app
CMD ["streamlit", "run", "main.py"]