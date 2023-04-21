from flask import Flask, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_restful import Api, Resource
from marshmallow import post_load, fields, ValidationError
from dotenv import load_dotenv
from os import environ

load_dotenv()

# Create App instance
app = Flask(__name__)

# Add DB URI from .env
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('SQLALCHEMY_DATABASE_URI')

# Registering App w/ Services
db = SQLAlchemy(app)
ma = Marshmallow(app)
api = Api(app)
CORS(app)
Migrate(app, db)

# Models
class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(255), nullable=False)
    model = db.Column(db.String(255), nullable=False)
    year = db.Column(db.Integer)

    def __repr__(self):
        return f'{self.year} {self.make} {self.model}'

# Schemas
class CarSchema(ma.Schema):
    id = fields.Integer(primary_key = True)
    make = fields.String(required = True)
    model = fields.String(required = True)
    year = fields.Integer()

    class Meta:
        fields = ("id", "make", "model", "year")

    @post_load
    def create_car(self, data, **kwargs):
        return Car(**data)

car_schema = CarSchema()
cars_schema = CarSchema(many=True)

# Resources
class CarListResource(Resource):
    def get(self):
        all_cars = Car.query.all()
        return cars_schema.dump(all_cars)
    
    def post(self):
        form_data = request.get_json()
        try:
            new_car = car_schema.load(form_data)
            db.session.add(new_car)
            db.session.commit()
            return car_schema.dump(new_car), 201
        except ValidationError as err:
            return err.messages, 400

class CarResource(Resource):
    def get(self, car_id):
        car_from_db = Car.query.get_or_404(car_id)
        return car_schema.dump(car_from_db)
    
    def delete(self, car_id):
        car_from_db = Car.query.get_or_404(car_id)
        db.session.delete(car_from_db)
        return '', 204
    
    def put(self, car_id):
        car_from_db = Car.query.get_or_404(car_id)

        if 'make' in request.json:
            car_from_db.make = request.json['make']
        if 'model' in request.json:
            car_from_db.model = request.json['model']
        if 'year' in request.json:
            car_from_db.year = request.json['year']
        db.session.commit()
        return car_schema.dump(car_from_db)


# Routes
api.add_resource(CarListResource, '/api/cars')
api.add_resource(CarResource, '/api/cars/<int:car_id>')