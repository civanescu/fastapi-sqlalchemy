# This is for CircleCI tutorial! TODO: Correct the tests!
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import os
import sys

# Add parent directory to the sys.path so that we can import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import CarItem, app



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
    assert response.status_code == 404
    # assert response.json() == {"RESULT": "OK"}

