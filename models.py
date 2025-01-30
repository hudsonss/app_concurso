from extensions import db  # Importa db de extensions.py

# Modelo da tabela de Users
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# Modelo da tabela de concursos
class Concurso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    data = db.Column(db.String(10), nullable=False)
    banca = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

# Associação entre Concursos e Disciplinas (M:N)
concurso_disciplina = db.Table(
    'concurso_disciplina',
    db.Column('concurso_id', db.Integer, db.ForeignKey('concurso.id'), primary_key=True),
    db.Column('disciplina_id', db.Integer, db.ForeignKey('disciplina.id'), primary_key=True)
)

# Modelo de Categoria
class CategoriaConcurso(db.Model):
    __tablename__ = 'categoria_concurso'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)

    def __repr__(self):
        return f'<CategoriaConcurso {self.nome}>'

# Modelo de Disciplina
class Disciplina(db.Model):
    __tablename__ = 'disciplina'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)

    # Relacionamento com Concursos (M:N)
    concursos = db.relationship('Concurso', secondary=concurso_disciplina, backref='disciplinas')

    def __repr__(self):
        return f'<Disciplina {self.nome}>'

# Modelo de Assunto
class Assunto(db.Model):
    __tablename__ = 'assunto'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)

    # Relacionamento com Disciplina (1:N)
    disciplina_id = db.Column(db.Integer, db.ForeignKey('disciplina.id'), nullable=False)
    disciplina = db.relationship('Disciplina', backref='assuntos')

    def __repr__(self):
        return f'<Assunto {self.nome}>'