import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from main import CarItem, app


@pytest.fixture(scope="module")
def test_app():
    client = TestClient(app)
    yield client


@pytest.fixture(scope="module")
def new_car():
    car = CarItem(
        active=True,
        year=2022,
        mileage=1000,
        price=10000,
        make_id="test_make_id",
        model_id="test_model_id",
        submodel_id="test_submodel_id",
        body_type="Sedan",
        fuel_type="Gasoline",
        transmission="Automatic",
        exterior_color="Black",
    )
    return car


def test_create_car(test_app, new_car):
    response = test_app.post("/create", json=new_car.dict())
    assert response.status_code == 200
    assert response.json() == {"RESULT": "OK"}


def test_read_cars(test_app):
    response = test_app.get("/cars")
    assert response.status_code == 200
    assert len(response.json()) >= 0
