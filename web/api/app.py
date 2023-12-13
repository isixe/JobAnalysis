from api import App

app = App(__name__)

if __name__ == '__main__':
    app.debug = True
    app.run()
