import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
from flask import abort, render_template, Flask
import logging
import db

APP = Flask(__name__)

# Start page
@APP.route('/')
def index():
    stats = {}
    stats = db.execute('''
    SELECT * FROM
      (SELECT COUNT(*) n_concelhos FROM concelhos)
    JOIN
      (SELECT COUNT(*) n_disciplinas FROM disciplinas)
    JOIN
      (SELECT COUNT(*) n_distritos FROM distritos)
    JOIN 
      (SELECT COUNT(*) n_escolas FROM escolas)
    ''').fetchone()
    logging.info(stats)
    return render_template('index.html',stats=stats)

# Distritos
@APP.route('/distrito/')
def list_distritos():
    distrito = db.execute(
      '''
      SELECT CODIGO, NOME 
      FROM distritos
      ORDER BY NOME
      ''').fetchall()
    return render_template('distritos-list.html', distrito=distrito)

@APP.route('/distrito/<int:id>/')
def view_distrito(id):
  distrito = db.execute(
    '''
    SELECT d.NOME, d.CODIGO
    FROM distritos d
    WHERE d.CODIGO = ?
    ''', [id]).fetchone()

  if distrito is None:
     abort(404, 'Distrito id {} does not exist.'.format(id))
  
  concelho = db.execute(
    '''
    SELECT c.CODIGO, c.NOME
    FROM concelhos c
    INNER JOIN distritos d ON d.CODIGO = c.DISTRITO
    WHERE d.CODIGO = ?
    ORDER BY d.NOME
    ''', [id]).fetchall()

  return render_template('distrito.html', 
           concelho=concelho, distrito=distrito)

@APP.route('/distrito/search/<expr>/')
def search_distrito(expr):
  search = { 'expr': expr }
  # SQL INJECTION POSSIBLE! - avoid this!
  distrito = db.execute(
      ' SELECT CODIGO, NOME'
      ' FROM distritos '
      ' WHERE Nome LIKE \'%' + expr + '%\''
    ).fetchall()

  return render_template('distrito-search.html', 
           search=search,distrito=distrito)

# Concelhos
@APP.route('/concelho/')
def list_concelhos():
    concelho = db.execute(
      '''
      SELECT CODIGO, NOME 
      FROM concelhos
      ORDER BY NOME
      ''').fetchall()
    return render_template('concelhos-list.html', concelho=concelho)


@APP.route('/concelho/<int:id>/')
def view_concelho(id):
  concelho = db.execute(
    '''
    SELECT c.NOME, c.CODIGO
    FROM concelhos c
    WHERE c.CODIGO = ?
    ''', [id]).fetchone()

  if concelho is None:
     abort(404, 'Concelho id {} does not exist.'.format(id))
  
  distrito = db.execute(
    '''
    SELECT d.CODIGO, d.NOME
    FROM distritos d
    INNER JOIN concelhos c ON d.CODIGO = c.DISTRITO
    WHERE c.CODIGO = ?
    ORDER BY d.NOME
    ''', [id]).fetchall()

  return render_template('concelho.html', 
           concelho=concelho, distrito=distrito)

@APP.route('/concelho/search/<expr>/')
def search_concelho(expr):
  search = { 'expr': expr }
  # SQL INJECTION POSSIBLE! - avoid this!
  concelho = db.execute(
      ' SELECT CODIGO, NOME'
      ' FROM concelhos '
      ' WHERE Nome LIKE \'%' + expr + '%\''
    ).fetchall()

  return render_template('concelho-search.html', 
           search=search,concelho=concelho)

# Escola
@APP.route('/escola/')
def list_escola():
    escola = db.execute('''
      SELECT IDEscola, Nome
      FROM escolas 
      ORDER BY Nome;
    ''').fetchall()
    return render_template('escola-list.html', escola=escola)


@APP.route('/escola/<int:id>/')
def view_data_school(id):
  escola = db.execute(
    '''
    SELECT IDEscola, Nome, Tipo
    FROM escolas 
    WHERE IDEscola = ?
    ''', [id]).fetchone()

  if escola is None:
     abort(404, 'Escola id {} does not exist.'.format(id))
  distrito = db.execute(
    '''
    SELECT d.CODIGO, d.NOME
    FROM distritos d
    INNER JOIN concelhos c ON d.CODIGO = c.DISTRITO
    JOIN escolas e ON e.Concelho = c.CODIGO
    WHERE e.IDEscola = ?
    ORDER BY d.NOME
    ''', [id]).fetchall()

  concelho = db.execute(
    '''
    SELECT c.CODIGO, c.NOME
    FROM concelhos c 
    INNER JOIN escolas e ON e.Concelho = c.CODIGO
    WHERE e.IDEscola = ?
    ORDER BY c.NOME
    ''', [id]).fetchall()

  return render_template('escola.html', 
           escola=escola, distrito = distrito, concelho=concelho)
 
@APP.route('/escola/search/<expr>/')
def search_escola(expr):
  search = { 'expr': expr }
  # SQL INJECTION POSSIBLE! - avoid this!
  escola = db.execute(
      ' SELECT idEscola, Nome'
      ' FROM escolas '
      ' WHERE Nome LIKE \'%' + expr + '%\''
    ).fetchall()

  return render_template('escola-search.html', 
           search=search,escola=escola)

# Disciplinas
@APP.route('/disciplina/')
def list_disciplinas():
    disciplina = db.execute('''
      SELECT NOME, idDisciplina
      FROM disciplinas
    ''').fetchall()
    return render_template('disciplina-list.html', disciplina=disciplina)

@APP.route('/disciplina/<int:id>/')
def view_rankingSubject(id):
  disciplina = db.execute(
    '''
    SELECT idDisciplina, NOME
    FROM disciplinas 
    WHERE idDisciplina = ?
    ''', [id]).fetchone()

  if disciplina is None:
     abort(404, 'Subject id {} does not exist.'.format(id))

  ranking = db.execute(
    '''
    SELECT r.Rank, e.NOME as nomeEscola, r.media, r.idEscola
    FROM ranking r
    INNER JOIN escolas e ON r.idEscola = e.idEscola
    JOIN disciplinas d ON r.idDisciplina = d.idDisciplina
    WHERE d.idDisciplina = ?
    ''', [id]).fetchall()

  return render_template('disciplina.html', 
           disciplina=disciplina, ranking=ranking)
