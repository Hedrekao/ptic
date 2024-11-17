from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
from dotenv import load_dotenv, find_dotenv
import time

from ml.models import HierarchyModel
from ml.utils.hierarchy import Hierarchy
from ml.inference.utils import StorageClient, base64_to_pil


def start_app():
    load_dotenv(find_dotenv())
    app = FastAPI()
    hierarchy = Hierarchy()
    app.model = HierarchyModel(hierarchy=hierarchy)

    app.categories = hierarchy.get_categories_list()

    app.storage_client = StorageClient()
    return app


app = start_app()


class ImageRequest(BaseModel):
    filePath: str | None = None  # Location of image file
    imageData: str | None = None  # Base64 encoded image


class PredictionResponse(BaseModel):
    predictions: Dict[str, float]
    processing_time: float


@app.post("/predict", response_model=PredictionResponse)
async def predict(request: ImageRequest) -> PredictionResponse:
    """
    Process image and return mock predictions.

    Args:
        request: ImageRequest containing image file path or base64 encoded image

    Returns:
        PredictionResponse with predictions and processing time
    """
    start_time = time.time()

    # Get image from request data
    image = None
    if request.filePath:
        image = app.storage_client.get_image(request.filePath)
    elif request.imageBase64:
        image = base64_to_pil(request.imageBase64)
    else:
        raise HTTPException(status_code=400, detail="No image data provided")

    # preprocess
    tensor = app.model.transform_image(image)

    # add dimension to simulate batch size
    tensor = tensor.unsqueeze(0)

    probs = app.model.predict(tensor)

    probs = probs.squeeze(0)

    # Get top 5 indices
    top5_indices = probs.argsort()[-5:][::-1]

    # Get top 5 probabilities
    top5_probs = probs[top5_indices]

    # Get top 5 categories
    predictions = {
        app.categories[index]: round(float(prob), 5) for index, prob in zip(top5_indices, top5_probs)
    }

    processing_time = time.time() - start_time

    return PredictionResponse(
        predictions=predictions,
        processing_time=processing_time
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
