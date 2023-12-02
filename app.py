import os
import sys
import pandas as pd

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import render_template
from flask import request
from flask import redirect,url_for
from sqlalchemy import func

filename = "C:/Users/23256/Desktop/actor.csv"
df = pd.read_csv(filename)
actor_data = df.to_dict(orient='records')

filename = "C:/Users/23256/Desktop/box.csv"
df = pd.read_csv(filename)
box_data = df.to_dict(orient='records')

filename = "C:/Users/23256/Desktop/relation.csv"
df = pd.read_csv(filename)
relation_data = df.to_dict(orient='records')

filename = "C:/Users/23256/Desktop/movie.csv"
df = pd.read_csv(filename)
movie_data = df.to_dict(orient='records')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控
# 在扩展类实例化前加载配置
db = SQLAlchemy(app)

class actor(db.Model): 
    actor_id = db.Column(db.Integer, primary_key=True)  
    actor_name = db.Column(db.String(20),unique=True, nullable=False) 
    gender = db.Column(db.String(20),unique=False,nullable=False)
    country = db.Column(db.String(20),unique=False,nullable=False)

class box(db.Model): 
    movie_id = db.Column(db.Integer, primary_key=True)  
    box = db.Column(db.Float,unique=False, nullable=False)  

class relation(db.Model): 
    id = db.Column(db.Integer, primary_key=True) 
    movie_id = db.Column(db.Integer,unique=False, nullable=False) 
    actor_id = db.Column(db.Integer,unique=False,nullable=False)
    relation_type = db.Column(db.String(20),unique=False,nullable=False)

class movie(db.Model): 
    movie_id = db.Column(db.Integer, primary_key=True)  
    movie_name = db.Column(db.String(20),unique=True, nullable=False) 
    release_date = db.Column(db.String(20),unique=False,nullable=False)
    country = db.Column(db.String(20),unique=False,nullable=False)
    type = db.Column(db.String(20),unique=False,nullable=False)
    year = db.Column(db.Integer,unique=False,nullable=False)


import click

@app.route('/')
def index():
    return render_template('index.html')

@app.cli.command()  # 注册为命令，可以传入 name 参数来自定义命令
def forge():
    db.create_all()

    for a in actor_data:
        act = actor(actor_id=a['actor_id'], actor_name=a['actor_name'],gender=a['gender'],country=a['country'])
        db.session.add(act)
    for b in box_data:
        bo = box(movie_id=b['movie_id'], box=b['box'])
        db.session.add(bo)
    for r in relation_data:
        re = relation(id=r['id'], movie_id=r['movie_id'],actor_id=r['actor_id'],relation_type=r['relation_type'])
        db.session.add(re)
    for m in movie_data:
        mo = movie(movie_id=m['movie_id'], movie_name=m['movie_name'],release_date=m['release_date'],country=m['country'],type=m['type'],year=m['year'])
        db.session.add(mo)    
    db.session.commit()
    click.echo('Done.')

@app.route('/search_actor', methods=['GET', 'POST'])
def search_actor():
    if request.method == 'POST':
        actor_query = request.form.get('actor_query')
        actors = actor.query.filter(actor.actor_name.contains(actor_query)).all()
        return render_template('search_actor_results.html', actors=actors)
    return render_template('search_actor.html')

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/search_movie', methods=['GET','POST'])
def search_movie():
    if request.method == 'POST':
        movie_query = request.form.get('movie_query')
        movies = movie.query.filter(movie.movie_name.contains(movie_query)).all()
        return render_template('search_movie_results.html', movies=movies)
    return render_template('search_movie.html')

@app.route('/add_movie', methods=['GET', 'POST'])
def add_movie():
    if request.method == 'POST':
        new_movie = movie(
            movie_id=request.form['movie_id'],
            movie_name=request.form['movie_name'],
            release_date=request.form['release_date'],
            country=request.form['country'],
            type=request.form['type'],
            year=request.form['year']
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_movie.html')

@app.route('/box_analysis/by_type')
def box_by_type():
    type_results = db.session.query(
        movie.type,
        func.avg(box.box).label('average_box')
    ).join(movie, movie.movie_id == box.movie_id).group_by(movie.type).all()
    type_results = [(t[0], '{:.2f}'.format(t[1])) for t in type_results]
    return render_template('box_analysis_result.html', results=type_results,category='类型')

@app.route('/box_analysis/by_year')
def box_by_year():
    year_results = db.session.query(
        movie.year,
        func.avg(box.box).label('average_box')
    ).join(box, movie.movie_id == box.movie_id).group_by(movie.year).all()
    year_results = [(t[0], '{:.2f}'.format(t[1])) for t in year_results]
    return render_template('box_analysis_result.html', results=year_results,category='年份')

@app.route('/box_analysis/by_country')
def box_by_country():
    country_results = db.session.query(
        movie.country,
        func.avg(box.box).label('average_box')
    ).join(box, movie.movie_id == box.movie_id).group_by(movie.country).all()
    country_results = [(t[0], '{:.2f}'.format(t[1])) for t in country_results]
    return render_template('box_analysis_result.html', results=country_results,category='国家')


@app.route('/box_analysis')
def initial_box_office_analysis():
    return render_template('box_analysis.html')
