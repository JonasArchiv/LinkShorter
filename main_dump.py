from flask import Flask, request, redirect

app = Flask(__name__)
links = {}


@app.route('/', methods=['POST', 'GET'])
def index():
    original_url = request.form['url']
    short_url = str(len(links) + 1)
    links[short_url] = original_url
    return f"Short link: {request.url_root}{short_url}"


@app.route('/<short_url>')
def short_url(short_url):
    original_url = links.get(short_url)
    if original_url is None:
        return "Link not found", 404
    return redirect(original_url)


if __name__ == '__main__':
    app.run(debug=True)
