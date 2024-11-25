FROM python:3.9-slim

WORKDIR /app

# Install dependencies for Chrome
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxi6 \
    libxtst6 \
    libnss3 \
    libgconf-2-4 \
    libasound2 \
    fonts-liberation \
    libappindicator3-1 \
    libxrandr2 \
    libgtk-3-0 \  
    libxss1 \      
    && apt-get clean

# Install Google Chrome
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt-get install -y ./google-chrome-stable_current_amd64.deb && \
    rm google-chrome-stable_current_amd64.deb

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]