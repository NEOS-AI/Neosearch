FROM python:3

ENV VERSION 0.1.0

WORKDIR /neosearch

COPY neosearch .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port for networking
EXPOSE 5018
