This is an exercise to create a API with endpoints for a group of cars.

# It is made on:
<pre>
Python 3.8
FastAPI
SQLAlchemy
PostreSQL
</pre>

# To run you have to:
1. Change the SQLALCHEMY_DATABASE_URL variable to what you need!
2. Run "docker build --tag fastapi_sqlalchemy ."
3. Run "docker run -p 8080:8080 fastapi_sqlalchemy"

# Endpoints:
<pre>
GET / - general info
GET /cars?price=0&mileage=0 - price & mileage are optional
GET /makes
GET /models
GET /submodels
POST /new_car
</pre>

# Post data format
Where "Optional" it's optional :).
And for each it's set the type of data (str, int, bool) 
<pre>
{
    "active": Optional[bool] = True,
    "year": int,
    "mileage": Optional[int] = 0,
    "price": Optional[int] = 0,
    "make_id": str,
    "model_id": str,
    "submodel_id": str,
    "body_type": Optional[str] = None,
    "fuel_type": Optional[str] = None,
    "transmission": Optional[str] = None,
    "exterior_color": Optional[str] = None
}
</pre>
# 
More details:
* A car has a make,
* a make has many models, and
* a model has many submodels.

################# LAST INFO ###############

The project have new versions, but they are private, still you can use the current one.
The current code has the following problems that should be solved:
1. I used the rollback too many times.
2. The connection to the DB is global.
