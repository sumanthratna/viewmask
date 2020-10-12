# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.8.6-slim-buster

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE 1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED 1

# Creates /viewmask in container if it does not already exist
WORKDIR /viewmask

COPY pyproject.toml pyproject.toml

# Install pip requirements
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    # psutil:
    "gcc=4:8.3.0-1" \
    "libtiff-dev=4.1.0+git191117-2~deb10u1" \
    "openslide-tools=3.4.1+dfsg-4" \
    && rm -rf /var/lib/apt/lists/* \
    && python3 -m pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install

# Ports code into /viewmask
COPY . /viewmask

# Switches to a non-root user and changes the ownership of the /viewmask folder"
# RUN useradd appuser && chown -R appuser /viewmask
# USER appuser

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
# CMD ["poetry", "run", "viewmask"]
# CMD ["poetry", "run", "python"]
CMD ["bash"]
