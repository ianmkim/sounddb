from flask import Flask,redirect,request,render_template, Response
import sys
# Tornado web server
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from flask_sqlalchemy import SQLAlchemy
import flask_whooshalchemy as wa

from flask_wtf import FlaskForm

from wtforms.widgets import TextArea
from wtforms import SelectField, StringField, SubmitField,IntegerField
from wtforms.validators import DataRequired

import logging
root = logging.getLogger()
root.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)



def return_dict():
    #Dictionary to store music file information
    dict_here = [
        {'id': 1, 'name': 'Acoustic Breeze', 'link': 'music/acousticbreeze.mp3', 'genre': 'General', 'chill out': 5},
        {'id': 2, 'name': 'Happy Rock','link': 'music/happyrock.mp3', 'genre': 'Bollywood', 'rating': 4},
        {'id': 3, 'name': 'Ukulele', 'link': 'music/ukulele.mp3', 'genre': 'Bollywood', 'rating': 4}
        ]
    return dict_here

# Initialize Flask.
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SECRET_KEY'] = "somethingsecret"
app.config['WHOOSH_BASE'] = 'whoosh'

db = SQLAlchemy(app)

class Song(db.Model):
    __searchable__ = ['id', 'name', 'link', 'description', 'genre']
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.Text)
    link = db.Column(db.Text)
    genre = db.Column(db.Text)
    description = db.Column(db.Text)
    rating = db.Column(db.Integer)
    downloaded = db.Column(db.Integer)

class ShowSong(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.Text)
    link = db.Column(db.Text)
    trigger = db.Column(db.Text)
    genre = db.Column(db.Text)
    description = db.Column(db.Text)
    showName = db.Column(db.Text)
    showId = db.Column(db.Integer)
    page = db.Column(db.Integer)
    cue = db.Column(db.Integer)

wa.whoosh_index(app, Song)


class AddNewSong(FlaskForm):
    show = StringField("Show")
    page = IntegerField("Page Number")
    cue = IntegerField("Cue Number (sub page number)")
    song = IntegerField("song id")
    submit = SubmitField("Add")

@app.after_request
def after_request(response):
    response.headers.add('Accept-Ranges', 'bytes')
    return response

import util
#Route to render GUI
@app.route('/')
def index():
    form = AddNewSong()
    general_Data = {
        'title': 'Music Player'}
    stream_entries = Song.query.limit(10).all()
    return render_template('design.html', entries=stream_entries, **general_Data, header = "Woodberry Drama Sound Database", form=form)


@app.route('/add_to_show_ajax')
def add_to_show_ajax():
    song = request.args.get('song')
    show = request.args.get('show')
    page = request.args.get('page')
    cue = request.args.get('cue')
    trigger = request.args.get('trigger')

    song = Song.query.get(int(song))

    showSong = ShowSong(name = song.name,
            link = song.link,
            genre = song.genre,
            description = song.description,
            showName = show,
            page = page,
            trigger=trigger,
            cue = cue)
    db.session.add(showSong)
    db.session.commit()
    return "Finished adding!"

@app.route('/delete_comp')
def delete_comp():
    name = request.args.get("show_id")
    all_items = ShowSong.query.filter_by(showName=name).all()
    for item in all_items:
        db.session.delete(item)
        db.session.commit()

    return redirect("show_select")

@app.route('/delete_song')
def delete_song():
    name = request.args.get("show_id")
    item = ShowSong.query.get(int( name))
    db.session.delete(item)
    db.session.commit()

    return redirect(request.referrer)


@app.route('/show_select')
def show_select():
    showlist = util.get_shows(ShowSong.query.all())
    return render_template("show_select.html", header="Show Selection", showlist=showlist)

@app.route('/show/<showname>')
def show(showname):
    general_Data = {
        'title': showname}
    showSongList = ShowSong.query.filter_by(showName = showname).all()
    return render_template("show.html", showSongList=showSongList, **general_Data, header=showname)


@app.route('/download_yt/<yt_link>')
def download_yt(yt_link):
    ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': 192
                }]
            }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([yt_link])

@app.route('/search', methods=["GET"])
def search():
    general_data = {"title": "search"}
    search_term = request.args.get('q')
    results = Song.query.whoosh_search(search_term)
    return render_template('design.html', entries=results, ** general_data, header="Search")

@app.route('/cat_browse')
def cat_browse():
    return render_template('category_select.html')


@app.route('/category/<cat>')
def category(cat):
    stream_entries = Song.query.filter_by(genre=cat).all()
    general_data= {
            'title': cat
            }
    return render_template('design.html', entries=stream_entries, ** general_data, header = cat)

#Route to stream music
@app.route('/<int:stream_id>')
def streammp3(stream_id):
    item = Song.query.get(stream_id)
    song = item.link
    def generate():
        with open(song, "rb") as fwav:
            data = fwav.read(1024)
            while data:
                yield data
                data = fwav.read(1024)
                #logging.debug('Music data fragment : ' + str(count))
                #count += 1

    return Response(generate(), mimetype="audio/mp3")

@app.route('/update_database_index')
def update_database_index():
    return "Finished"

#launch a Tornado server with HTTPServer.
if __name__ == "__main__":
    port = 5000
    http_server = HTTPServer(WSGIContainer(app))
    logging.debug("Started Server, Kindly visit http://localhost:" + str(port))
    http_server.listen(port)
    IOLoop.instance().start()

