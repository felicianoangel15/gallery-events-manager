import os

from dotenv import load_dotenv
from flask import Flask

from routes.main import main_bp


load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")
app.register_blueprint(main_bp)


if __name__ == "__main__":
    app.run(debug=True)
