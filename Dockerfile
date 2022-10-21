FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "-m", "streamlit", "run", "project_streamlit.py", "--server.port", "80", "--server.address", "0.0.0.0" ]
