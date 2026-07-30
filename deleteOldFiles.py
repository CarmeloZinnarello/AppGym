import os
import time

# Cartella da pulire
FOLDER = "/home/QLApp/backups"

# Giorni massimi
DAYS = 15

# Tempo limite in secondi
limit_time = time.time() - (DAYS * 86400)

for filename in os.listdir(FOLDER):
    file_path = os.path.join(FOLDER, filename)

    # Solo file, non sottocartelle
    if os.path.isfile(file_path):
        file_mtime = os.path.getmtime(file_path)

        if file_mtime < limit_time:
            os.remove(file_path)
            print(f"Eliminato: {file_path}")