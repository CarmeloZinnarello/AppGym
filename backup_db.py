import os
import shutil
import zipfile
import requests
from datetime import datetime
from dotenv import load_dotenv
# usa la variabile HOME del sistema
home = os.environ["HOME"]

# sorgente e destinazione
source = os.path.join(home, "WebFit", "instance", "app.db")
backup_dir = os.path.join(home, "backups")
os.makedirs(backup_dir, exist_ok=True)

# sempre lo stesso file -> sovrascrive il precedente
dest = os.path.join(backup_dir, "backup.db")
shutil.copy2(source, dest)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
# zip
zip_path = os.path.join(
    backup_dir,
    f"app_{timestamp}.zip"
)
print("zip_path", zip_path)
with zipfile.ZipFile(
    zip_path,
    "w",
    zipfile.ZIP_DEFLATED
) as zipf:

    zipf.write(
        dest,
        arcname=os.path.basename(dest)
    )

# telegram
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

print("TOKEN", TOKEN)
print("CHAT_ID", CHAT_ID)
url = f"https://api.telegram.org/bot{TOKEN}/sendDocument"

with open(zip_path, "rb") as f:

    response = requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "caption": f"Backup WebFit {timestamp}"
        },
        files={
            "document": f
        }
    )

print(response.text)

print("Backup aggiornato:", dest)