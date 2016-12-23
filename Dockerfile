
FROM python:2.7

# Install anything we'll need
RUN apt-get update && apt-get install -y \
		gcc \
		gettext \
		sqlite3 \
		libpq-dev \
	--no-install-recommends && rm -rf /var/lib/apt/lists/*

# Copy the code into the docker container
RUN mkdir -p /static
RUN mkdir -p /media

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# this file lives at the directory level above what is mounted at /usr/src/app/
# therefore we need to copy it (or move it down a level, lol)
COPY requirements.txt /usr/src/app/
#RUN ls -l
RUN pip install --no-cache-dir -r requirements.txt

# this lets only other docker containers find this port open.
EXPOSE 8000

COPY ./launch_gunicorn.sh /
ENTRYPOINT ["/launch_gunicorn.sh"]
