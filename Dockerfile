FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the bot script and requirements
COPY telegram_bot.py /app/telegram_bot.py
COPY requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Replace CMD with ENTRYPOINT
ENTRYPOINT ["uvicorn", "telegram_bot:main", "--host", "0.0.0.0", "--port", "7860"]
