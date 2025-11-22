FROM postgres:18

# Install build tools and pgvector dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    postgresql-server-dev-18 \
    && git clone https://github.com/pgvector/pgvector.git /tmp/pgvector \
    && cd /tmp/pgvector && make && make install \
    && rm -rf /tmp/pgvector \
    && apt-get remove -y git build-essential postgresql-server-dev-18 \
    && apt-get autoremove -y \
    && apt-get clean

# Environment variables are set via docker-compose.yml
# POSTGRES_USER, POSTGRES_PASSWORD, and POSTGRES_DB are configured there

# add SQL init script
COPY init-vector.sql /docker-entrypoint-initdb.d/