WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY IG-beta-sample-email.png IG-beta-sample-email.png
COPY IG-ExampleResponse.txt IG-ExampleResponse.txt
COPY igpro_signup.py igpro_signup.py
COPY intergalacticpro-firebase-key.json intergalacticpro-firebase-key.json
COPY LICENSE.md LICENSE.md
COPY main.py main.py
COPY mappings.py mappings.py
COPY README.md README.md
COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

EXPOSE 8080

HEALTHCHECK CMD curl --fail http://localhost:8080/_stcore/health

ENTRYPOINT ["streamlit", "run", "main.py", "--server.port=8080", "--server.address=0.0.0.0"]
