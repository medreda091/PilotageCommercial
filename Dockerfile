FROM python:3.12-slim
WORKDIR /app
COPY . .
CMD ["python", "main.py", "--entree", "donnees_exemple.csv", "--sortie", "rapport.html"]
