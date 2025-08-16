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

# 6. Accept build-time arguments
ARG SECRET_KEY
ARG DEBUG=0

# 7. Set them as environment variables for the collectstatic command
ENV SECRET_KEY=${SECRET_KEY}
ENV DEBUG=${DEBUG}

# 8. Run collectstatic
RUN python manage.py collectstatic --no-input

# 9. Copy the entrypoint script and make it executable
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

# 10. Expose the port and set the final command
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "spotify_subtitle.wsgi:application"]