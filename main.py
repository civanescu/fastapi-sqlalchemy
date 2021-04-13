import random
import string
from datetime import datetime
from typing import Optional

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

SQLALCHEMY_DATABASE_URL = "postgresql://<user>:<pass>@database-1.cck4faphiwwb.eu-west-1.rds.amazonaws.com"
DB = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True, pool_recycle=60)

Base = declarative_base()
SessionLocal = sessionmaker(bind=DB)
session = SessionLocal()
app = FastAPI()


class CarItem(BaseModel):
    active: Optional[bool] = True
    year: int
    mileage: Optional[int] = 0
    price: Optional[int] = 0
    make_id: str
    model_id: str
    submodel_id: str
    body_type: Optional[str] = None
    fuel_type: Optional[str] = None
    transmission: Optional[str] = None
    exterior_color: Optional[str] = None

    @staticmethod
    def random_id():
        letters = string.digits+string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(32))

    def as_dict(self):
        return {
            "id": self.random_id(),
            "active": self.active,
            "year": self.year,
            "mileage": self.mileage,
            "price": self.price,
            "make_id": self.make_id,
            "model_id": self.model_id,
            "submodel_id": self.submodel_id,
            "body_type": self.body_type,
            "fuel_type": self.fuel_type,
            "transmission": self.transmission,
            "exterior_color": self.exterior_color,
            "created_at": datetime.now()
        }


class Cars(Base):
    __tablename__ = "cars"
    serial_id = Column(Integer, primary_key=True)
    id = Column(String(32), unique=True, nullable=False)
    active = Column(Boolean, nullable=False, default=True)
    year = Column(SmallInteger, nullable=False)
    mileage = Column(BigInteger)
    price = Column(Integer)
    make_id = Column(String(32), ForeignKey("makes.id"), nullable=False)
    model_id = Column(String(32), ForeignKey("models.id"), nullable=False)
    submodel_id = Column(String(32), ForeignKey("submodels.id"), nullable=False)
    body_type = Column(String(16))
    fuel_type = Column(String(16))
    transmission = Column(String(16))
    exterior_color = Column(String(16))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class Makes(Base):
    __tablename__ = "makes"
    serial_id = Column(Integer, primary_key=True)
    id = Column(String(32), unique=True, nullable=False)
    name = Column(String(32), nullable=False)
    active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    cars = relationship("Cars")
    models = relationship("Models")


class Models(Base):
    __tablename__ = "models"
    serial_id = Column(Integer, primary_key=True)
    id = Column(String(32), unique=True, nullable=False)
    name = Column(String(32), nullable=False)
    make_id = Column(String(32), ForeignKey("makes.id"), nullable=False)
    active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    cars = relationship("Cars")
    submodels = relationship("Submodels")


class Submodels(Base):
    __tablename__ = "submodels"
    serial_id = Column(Integer, primary_key=True)
    id = Column(String(32), unique=True, nullable=False)
    name = Column(String(32))
    active = Column(Boolean, nullable=False, default=True)
    model_id = Column(String(32), ForeignKey("models.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    cars = relationship("Cars")


def json_serial(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    else:
        return str(obj)


def query_list(table) -> list:
    list_to_show = []
    for class_instance in session.query(table).all():
        row_dict = vars(class_instance)
        row_dict.pop("_sa_instance_state")
        list_to_show.append(row_dict)
    return list_to_show


def check_pairs(make_id: str, model_id: str, submodel_id: str) -> bool:
    result = session.query(Makes).join(Models).join(Submodels).\
        filter(Makes.id == make_id).filter(Models.id == model_id).filter(Submodels.id == submodel_id).\
        first()
    if result:
        return True
    else:
        return False


def insert(object) -> dict:
    if check_pairs(object.make_id, object.model_id, object.submodel_id):
        try:
            session.add(object)
            session.commit()
            return {"RESULT": "OK"}
        except Exception as e:
            print("ERROR", str(e))
            session.rollback()
            raise ({"ERROR", str(e)})
    else:
        return {"ERROR": "The pair of make:"+object.make_id+", model:"+object.model_id+" or submodel:"+object.submodel_id+" is wrong"}


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"ERROR": exc.errors(), "body": exc.body})
    )


@app.post("/new_car")
async def new_car(car: CarItem):
    try:
        new_car = Cars(**car.as_dict())
        result = insert(new_car)
        return JSONResponse(result)
    except Exception as e:
        session.rollback()
        print("Error entering new car", str(e))
        raise JSONResponse(status_code=404, content=jsonable_encoder({"ERROR": str(e)}))


@app.get("/", response_class=HTMLResponse)
async def root():
    str = """ 
    <html>
    <head>
        <title>Options</title>
    </head>
    <body>
        <h1>Welcome the options are:</h1>
        <p>
        <b>Query for data by "GET"</b></br>
        <a href="../cars" target="_blank">Cars</a></br>
        &nbsp;&nbsp;&nbsp;&nbsp;Optional you can add "price" and "mileage" values in searching for cars.</br>
        <a href="../makes" target="_blank">Makes</a></br>
        <a href="../models" target="_blank">Models</a></br>
        <a href="../submodels" target="_blank">Submodels</a></br>
        </p>
        <p>
        <b>Add new car by "POST"</b></br>
        Send a POST with JSON to new_car</br>
        {</br>
        &nbsp;&nbsp;&nbsp;&nbsp;"active": Optional[bool] = True,</br>
        &nbsp;&nbsp;&nbsp;&nbsp;"year": int,</br>
        &nbsp;&nbsp;&nbsp;&nbsp;"mileage": Optional[int] = 0,</br>
        &nbsp;&nbsp;&nbsp;&nbsp;"price": Optional[int] = 0,</br>
        &nbsp;&nbsp;&nbsp;&nbsp;"make_id": str,</br>
        &nbsp;&nbsp;&nbsp;&nbsp;"model_id": str,</br>
        &nbsp;&nbsp;&nbsp;&nbsp;"submodel_id": str,</br>
        &nbsp;&nbsp;&nbsp;&nbsp;"body_type": Optional[str] = None,</br>
        &nbsp;&nbsp;&nbsp;&nbsp;"fuel_type": Optional[str] = None,</br>
        &nbsp;&nbsp;&nbsp;&nbsp;"transmission": Optional[str] = None,</br>
        &nbsp;&nbsp;&nbsp;&nbsp;"exterior_color": Optional[str] = None</br>
        }</br>
        </p>
    </body>
        """
    return str


@app.get("/cars")
async def join_car_select(price=None, mileage=None):
    try:
        if price and mileage:
            filter_str = "cars.make_id = makes.id AND cars.model_id = models.id AND cars.submodel_id = submodels.id AND " \
                         "price = "+str(price)+" AND "+"mileage = "+str(mileage)
        elif price:
            filter_str = "cars.make_id = makes.id AND cars.model_id = models.id AND cars.submodel_id = submodels.id AND " \
                         "price = "+str(price)
        elif mileage:
            filter_str = "cars.make_id = makes.id AND cars.model_id = models.id AND cars.submodel_id = submodels.id AND " \
                         "mileage = "+str(mileage)
        else:
            filter_str = "cars.make_id = makes.id AND cars.model_id = models.id AND cars.submodel_id = submodels.id"
        list_join_cars = []
        for car, make, model, submodel in session.query(Cars, Makes, Models, Submodels). \
                filter(text(filter_str)).\
                order_by(desc(Cars.updated_at)).\
                all():
            row_dict = (vars(car))
            row_dict.update({"make_name": make.name,
                             "model_name": model.name,
                             "submodel_name": submodel.name})
            row_dict.pop("_sa_instance_state")
            list_join_cars.append(row_dict)
        if list_join_cars:
            return JSONResponse(jsonable_encoder(list_join_cars))
        else:
            return JSONResponse(status_code=400, content=jsonable_encoder(
                {"ERROR": "NO RESULTS for cars with price="+str(price)+" and mileage="+str(mileage)}))
    except Exception as e:
        session.rollback()
        raise JSONResponse(status_code=400, content=jsonable_encoder(
            {"ERROR": str(e)+"for querying cars with price="+str(price)+" and mileage="+str(mileage)}))


@app.get("/makes")
async def makes():
    try:
        list_to_show = query_list(Makes)
        return JSONResponse(jsonable_encoder(list_to_show))
    except Exception as e:
        session.rollback()
        raise JSONResponse(status_code=400, content=jsonable_encoder({"ERROR": str(e)}))


@app.get("/models")
async def models():
    try:
        list_to_show = query_list(Models)
        return list_to_show
    except Exception as e:
        session.rollback()
        raise JSONResponse(status_code=400, content=jsonable_encoder({"ERROR": str(e)}))


@app.get("/submodels")
async def models():
    try:
        list_to_show = query_list(Submodels)
        return list_to_show
    except Exception as e:
        session.rollback()
        raise JSONResponse(status_code=400, content=jsonable_encoder({"ERROR": str(e)}))


if __name__ == "__main__":
    print("Start", datetime.now())
    uvicorn.run(app, host="0.0.0.0", port=8080)
