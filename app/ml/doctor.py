import logging
from typing import Annotated

from fastapi import APIRouter, Body, Depends
from pydantic import create_model

from app.ml.utils import symptoms_list

ml_model = {}
REPO_ID = "AWeirdDev/human-disease-prediction"
FILENAME = "sklearn_model.joblib"


# @contextmanager
# def lifespan(app: FastAPI):
#     ml_model["doctor"] = joblib.load(
#         hf_hub_download(
#             repo_id=REPO_ID, filename=FILENAME
#         )
#     )
#
#     yield
#     ml_model.clear()


router = APIRouter()
logger = logging.getLogger("uvicorn")

query_parameters = {symp: (bool, False) for symp in symptoms_list[:10]}

Symptoms = create_model("Symptoms", **query_parameters)


@router.get("/diagnosis")
async def get_diagnosis(
    symptoms: Annotated[Symptoms, Depends()],
):
    array = [int(value) for _, value in symptoms.model_dump().items()]
    array.extend(  # adapt the array to the model's input shape
        [0] * (len(symptoms_list) - len(array))
    )
    diseases = ml_model["doctor"].predict([array])
    return {"diseases": [disease for disease in diseases]}


@router.post("/send")
async def send(message: str = Body()):
    logger.info(f"Message: {message}")
    return message
