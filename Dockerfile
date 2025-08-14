# 1. Start from an official Python base image
FROM python:3.12-slim

# 2. Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. Set the working directory inside the container
WORKDIR /app

# 4. Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of the application code into the container
COPY . .

# 6. Expose the port Gunicorn will run on
EXPOSE 8000

# 7. Run Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "spotify_subtitle.wsgi:application"]