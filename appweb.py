from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from pymongo import MongoClient
import datetime
import hashlib


cliente = MongoClient("mongodb://localhost:27017")

bd = cliente.infoUsers

collection = bd.users

user = bd.user_login
#Crear una Flask app y configurarlo
app = Flask(__name__)
#Inicializar JWTManager
jwt = JWTManager(app)


def tarjeta_credito(numero_tarjeta):
    valor_escondido = ""
    for index in range(0,len(numero_tarjeta)-4):
        valor_escondido += "#"
    
    valor_escondido += numero_tarjeta[-4:]
    return valor_escondido


def numero_cuenta(numero_cuenta):
    valor_escondido2 = ""
    for index in range(0,len(numero_cuenta)-4):
        valor_escondido2 += "#"
    
    valor_escondido2 += numero_cuenta[-4:]
    return valor_escondido2


app.config["JWT_SECRET_KEY"] = "prioridad-el-acceso-al-usuario"

app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(seconds=180)
#API route para el dashboard
@app.route("/dashboard", methods=['GET'])
@jwt_required()
def dashboard():
    current_user = get_jwt_identity()
    return jsonify(message="Bienvenido! Información de clientes", logged_in_as=current_user), 200


@app.route("/infor_cc/<uid>", methods=['GET'])
@jwt_required()
def infor_cc(uid):
    try:
        resultado = []
        user1 = collection.find_one({"id":uid})
        datos_usuario = {'id':user1['id'],'user_name':user1['user_name'], 'auto':user1['auto'], 'credit_card_num':tarjeta_credito(user1['credit_card_num']), 'cuenta_numero':numero_cuenta(user1['cuenta_numero'])}
        resultado.append(datos_usuario)
        return jsonify(user_info=resultado), 201
    except Exception as e:
        return jsonify(message="error!", info=str(e)), 409



@app.route("/register", methods=["POST"])
def register():
    email = request.form["email"]
    test = user.find_one({"email": email})
    if test:
        return jsonify(message="El usuario ya existe"), 409
    else:
        first_name = request.form["Primer_nombre"]
        last_name = request.form["Apellido"]
        password = request.form["Contraseña"]
        user_info = dict(first_name=first_name,last_name=last_name, email=email, password=password)
        user.insert_one(user_info)
        return jsonify(message="Usuario creado exitosamente!"), 201

@app.route("/login", methods=["POST"])
def login():
    if request.is_json:
        email = request.json["email"]
        password = request.json["contraseña"]
    else:
        email = request.form["email"]
        password = request.form["contraseña"]

    test = user.find_one({"email": email, "password": password})
    if test:
        access_token = create_access_token(identity=email)
        return jsonify(message="Registro Exitoso!", access_token=access_token), 201
    else:
        return jsonify(message="contraseña o email incorrecto"), 401

if __name__=='__main__':
    app.run(host="localhost", debug=True)

   