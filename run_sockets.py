import os
import django
import eventlet
import eventlet.wsgi

# ✅ Setup Django before importing anything from main.sockets
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Light2.settings")
django.setup()

from main.sockets import app  # <-- now it's safe to import, models will work

if __name__ == "__main__":
    print("🔌 Starting Socket.IO server on http://localhost:5000 ...")
    eventlet.wsgi.server(eventlet.listen(("0.0.0.0", 5000)), app)
