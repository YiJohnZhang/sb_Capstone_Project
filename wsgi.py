from main import app;

if __name__ == "__main__":
    app.run();
	
# Start Command Choices:
	# gunicorn wsgi:app
	# python main.py
	# FLASK_ENV="development" flask run