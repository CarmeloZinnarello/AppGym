from app import create_app, create_admin

# Crea e avvia l'app
app = create_app()
create_admin(app)

if __name__ == '__main__':
    app.run(debug=True)