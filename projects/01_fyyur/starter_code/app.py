#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from datetime import date
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    genres = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    website = db.Column(db.String(120), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)
    seeking_talent = db.Column(db.Boolean(), default=True)
    seeking_description = db.Column(db.String(120), nullable=True)
    image_link = db.Column(db.String(500), nullable=True)
    shows_venue = db.relationship('Show', backref='venue', lazy=True)

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    genres = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    website = db.Column(db.String(120), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)
    seeking_venue = db.Column(db.Boolean(), default=True)
    seeking_description = db.Column(db.String(120), nullable=True)
    image_link = db.Column(db.String(500), nullable=True)
    shows_artist = db.relationship('Show', backref='artist', lazy=True)

class Show(db.Model):
  __tablename__ = 'show'
  id = db.Column(db.Integer(), primary_key=True)
  venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'))
  artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'))
  start_time = db.Column(db.String(120), nullable=False)
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  areas = []
  today = date.today().strftime("%Y-%m-%d")
  for venue in Venue.query.distinct(Venue.city):
    areas.append(venue.city)
  
  data = []
  for area in areas:
    venues_data = Venue.query.filter_by(city=area).all()

    result = {
        "city": area,
        "state": venues_data[0].__dict__["state"],
        "venues": []
      }

    for venue in venues_data:
      upcoming_shows = Show.query.filter_by(venue_id=venue.__dict__["id"]).filter(Show.start_time > today).all()

      venue_obj = {
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": len(upcoming_shows)
      }
      result["venues"].append(venue_obj)
    
    data.append(result)

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  query = request.form.get('search_term', '').lower()
  today = date.today().strftime("%Y-%m-%d")
  response_data = Venue.query.all()
  filtered_data = []

  def split(word): 
    return [char for char in word] 

  for venue in response_data:
    if len(query) == 1:
      words = venue.__dict__["name"].split()
      for word in words:
        letters = split(word.lower())
        for char in letters: 
          if char == query:
            filtered_data.append(venue)
    elif len(query) > 1:
      result = venue.__dict__["name"].lower().find(query)
      if result == -1:
        continue
      else: filtered_data.append(venue)
  filtered_data = set(filtered_data)

  response = {
    "count": len(filtered_data),
    "data": []
  }

  for result in filtered_data:
    upcoming_shows = Show.query.filter_by(venue_id=result.__dict__["id"]).filter(Show.start_time > today).all()
    result_obj = {
      "id": result.__dict__["id"],
      "name": result.__dict__["name"],
      "num_upcoming_shows": len(upcoming_shows)
    }
    response["data"].append(result_obj)
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  today = date.today().strftime("%Y-%m-%d")
  venue = Venue.query.filter_by(id=venue_id).all()
  past_shows = Show.query.filter_by(venue_id=venue_id).filter(Show.start_time < today).all()
  upcoming_shows = Show.query.filter_by(venue_id=venue_id).filter(Show.start_time > today).all()

  past_shows_results = []
  upcoming_shows_results = []
  if len(past_shows) > 0: 
    for show in past_shows:
      artist = Artist.query.filter_by(id=show.__dict__["artist_id"]).all()[0]
      show_obj = {
        "artist_id": artist.__dict__["id"],
        "artist_name": artist.__dict__["name"],
        "artist_image_link": artist.__dict__["image_link"],
        "start_time": show.__dict__["start_time"]
      }
      past_shows_results.append(show_obj)

  if len(upcoming_shows) > 0:
    for show in upcoming_shows:
      artist = Artist.query.filter_by(id=show.__dict__["artist_id"]).all()[0]
      show_obj = {
        "artist_id": artist.__dict__["id"],
        "artist_name": artist.__dict__["name"],
        "artist_image_link": artist.__dict__["image_link"],
        "start_time": show.__dict__["start_time"]
      }
      upcoming_shows_results.append(show_obj)

  data = venue[0].__dict__
  data["genres"] = json.loads(data["genres"])
  data["past_shows"] = past_shows_results
  data["upcoming_shows"] = upcoming_shows_results
  data["past_shows_count"] = len(past_shows_results)
  data["upcoming_shows_count"] = len(upcoming_shows_results)

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: modify data to be the data object returned from db insertion
  # ^^^ do not understand the purpose of this todo 
  error = False

  try:
    genres = json.dumps(request.form.getlist("genres"))

    venue = Venue(name=request.form["name"],\
      genres=genres,\
      address=request.form["address"],\
      city=request.form["city"],\
      state=request.form["state"],\
      phone=request.form["phone"],\
      facebook_link=request.form["facebook_link"])
    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue ' + request.form["name"] + ' could not be listed.')
  else:
  # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  error = False
  try:
    venue = Venue.query.filter_by(id=venue_id).all()
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()

  if error:
    flash('Some shit went wrong')
  else: 
    flash('Successfully deleted')

  return render_template('pages/home.html')
  # delete is working but redirect is not
#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists = Artist.query.all()
  data = []
  for artist in artists:
    artist_dict = {
      "id": artist.id,
      "name": artist.name
    }
    data.append(artist_dict)
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  query = request.form.get('search_term', '').lower()
  today = date.today().strftime("%Y-%m-%d")
  response_data = Artist.query.all()
  filtered_data = []

  def split(word): 
    return [char for char in word]  

  for artist in response_data:
    if len(query) == 1:
      words = artist.__dict__["name"].split()
      for word in words:
        letters = split(word.lower())
        for char in letters: 
          if char == query:
            filtered_data.append(artist)
    elif len(query) > 1:
      result = artist.__dict__["name"].lower().find(query)
      if result == -1:
        continue
      else: filtered_data.append(artist)
  filtered_data = set(filtered_data)
  
  data = []

  for artist in filtered_data:
    upcoming_shows = Show.query.filter_by(artist_id=artist.__dict__["id"]).filter(Show.start_time > today).all()
    artist = {
      "id": artist.__dict__["id"],
      "name": artist.__dict__["name"],
      "num_upcoming_shows": len(upcoming_shows)
    }
    data.append(artist)
  
  response={
    "count": len(filtered_data),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  today = date.today().strftime("%Y-%m-%d")
  artist = Artist.query.filter_by(id=artist_id).all()
  past_shows = Show.query.filter_by(artist_id=artist_id).filter(Show.start_time < today).all()
  upcoming_shows = Show.query.filter_by(artist_id=artist_id).filter(Show.start_time > today).all()

  past_shows_results = []
  upcoming_shows_results = []

  if len(past_shows) > 0: 
    for show in past_shows:
      venue = Venue.query.filter_by(id=show.__dict__["venue_id"]).all()[0]
      show_obj = {
        "venue_id": venue.__dict__["id"],
        "venue_name": venue.__dict__["name"],
        "venue_image_link": venue.__dict__["image_link"],
        "start_time": show.__dict__["start_time"]
      }
      past_shows_results.append(show_obj)

  if len(upcoming_shows) > 0:
    for show in upcoming_shows:
      venue = Venue.query.filter_by(id=show.__dict__["venue_id"]).all()[0]
      show_obj = {
        "venue_id": venue.__dict__["id"],
        "venue_name": venue.__dict__["name"],
        "venue_image_link": venue.__dict__["image_link"],
        "start_time": show.__dict__["start_time"]
      }
      upcoming_shows_results.append(show_obj)

  data = artist[0].__dict__
  data["genres"] = json.loads(data["genres"])
  data["past_shows"] = past_shows_results
  data["upcoming_shows"] = upcoming_shows_results
  data["past_shows_count"] = len(past_shows_results)
  data["upcoming_shows_count"] = len(upcoming_shows_results)

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist= Artist.query.filter_by(id=artist_id)[0]

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error = False
  try:
    form_data = request.form
    genres = json.dumps(form_data.getlist("genres"))

    artist = Artist.query.filter_by(id=artist_id).all()[0]
    setattr(artist, "name", request.form["name"])
    setattr(artist, "genres", genres)
    setattr(artist, "city", request.form["city"])
    setattr(artist, "state", request.form["state"])
    setattr(artist, "phone", request.form["phone"])
    setattr(artist, "facebook_link", request.form["facebook_link"])
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Artist ' + request.form["name"] + ' could not be updated.')
  else:
    flash('Artist ' + request.form['name'] + ' was successfully updated!')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  error = False
  try:
    form_data = request.form
    genres = json.dumps(form_data.getlist("genres"))

    venue = Venue.query.filter_by(id=venue_id).all()[0]
    setattr(venue, "name", request.form["name"])
    setattr(venue, "genres", genres)
    setattr(venue, "address", request.form["address"])
    setattr(venue, "city", request.form["city"])
    setattr(venue, "state", request.form["state"])
    setattr(venue, "phone", request.form["phone"])
    setattr(venue, "facebook_link", request.form["facebook_link"])
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue ' + request.form["name"] + ' could not be updated.')
  else:
    flash('Venue ' + request.form['name'] + ' was successfully updated!')

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # TODO: modify data to be the data object returned from db insertion
  error = False
  genres = json.dumps(form_data.getlist("genres"))

  try:
    artist = Artist(name=request.form["name"],\
      genres=genres,\
      city=request.form["city"],\
      state=request.form["state"],\
      phone=request.form["phone"],\
      facebook_link=request.form["facebook_link"])
    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Artist ' + request.form["name"] + ' could not be listed.')
  else:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows = Show.query.all()
  data = []
  for show in shows:
    venue = Venue.query.filter_by(id=show.__dict__["venue_id"]).all()[0]
    artist = Artist.query.filter_by(id=show.__dict__["artist_id"]).all()[0]

    show_dict = {
      "venue_id": show.__dict__["venue_id"],
      "venue_name": venue.__dict__["name"],
      "artist_id": show.__dict__["artist_id"],
      "artist_name": artist.__dict__["name"],
      "artist_image_link": artist.__dict__["image_link"],
      "start_time": show.__dict__["start_time"]
    }
    data.append(show_dict)

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False

  try:
    show = Show(venue_id=request.form["venue_id"],\
      artist_id=request.form["artist_id"],\
      start_time=request.form["start_time"])
    db.session.add(show)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Show could not be listed.')
  else:
    flash('Show was successfully listed!')

  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
