## Spotify Subtitle API
A Django-based REST API powering a browser extension for community-driven subtitle management on Spotify.

## Core Features
- Secure Session Authentication: Robust user login, registration, and password management powered by dj-rest-auth and django-allauth.
- Full Subtitle CRUD: Complete API for creating, reading, updating, and deleting subtitles.
- Multi-Format Parsing: Intelligently parses both .srt and .lrc file formats, as well as raw text input.
- Social Features: Endpoints for liking/unliking subtitles, viewing liked lists, and setting a user-specific active subtitle for each song.
- Advanced Filtering & Pagination: Server-side filtering by language or user, and sorting by likes or creation date, with infinite scroll support.
- Secure Spotify API Proxy: A server-side endpoint to fetch public track metadata from Spotify without exposing client tokens.

## Tech Stack
- Framework: Django, Django REST Framework
- Database: PostgreSQL
- Authentication: dj-rest-auth, django-allauth
- API Docs: drf-spectacular (Swagger UI)
- Deployment: Docker, Gunicorn, Whitenoise

#### FrontEnd: [spotify-subtitle-frontend](https://github.com/ardent83/spotify-subtitle-frontend)
