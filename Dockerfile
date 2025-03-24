# Utiliser une image légère avec Python
FROM python:3.10-slim

# Définir le répertoire de travail
WORKDIR /DPExplorer-interface

# Copier les fichiers nécessaires
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le projet
COPY . .

# Exposer le port utilisé par Streamlit
EXPOSE 8501

# Commande de lancement de l'application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
