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

# 6. Run collectstatic during the build process
# This creates the /app/staticfiles directory inside the image
RUN python manage.py collectstatic --no-input

# 7. Expose the port Gunicorn will run on
EXPOSE 8000

# 8. Set the entrypoint script to run migrations
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

# 9. Set the default command to run
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "spotify_subtitle.wsgi:application"]