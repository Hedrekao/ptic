from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import base64
from PIL import Image
import io
from typing import Dict
import time

from ml.models import HierarchyModel
from ml.utils.hierarchy import Hierarchy


def start_app():
    app = FastAPI()
    hierarchy = Hierarchy()
    app.model = HierarchyModel(hierarchy=hierarchy)

    app.categories = hierarchy.get_categories_list()
    return app


app = start_app()


class ImageRequest(BaseModel):
    filePath: str  # Location of image file


class PredictionResponse(BaseModel):
    predictions: Dict[str, float]
    processing_time: float


def base64_to_pil(base64_string: str) -> Image.Image:
    # We should use that later for supporting base64 encoded images
    """Convert base64 string to PIL Image."""
    try:
        # Remove data URL prefix if present
        if "base64," in base64_string:
            base64_string = base64_string.split("base64,")[1]

        # Decode base64 string
        image_data = base64.b64decode(base64_string)

        # Convert to PIL Image
        image = Image.open(io.BytesIO(image_data))

        return image
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Invalid image data: {str(e)}")


@app.post("/predict", response_model=PredictionResponse)
async def predict(request: ImageRequest) -> PredictionResponse:
    """
    Process image and return mock predictions.

    Args:
        request: ImageRequest containing image file path

    Returns:
        PredictionResponse with mock predictions and processing time
    """
    start_time = time.time()

    # Get image from file system
    # TODO this should work either with a file path or a base64 encoded image
    # TODO this should be abstracted to detect whether to use azure blob storage or not
    image = Image.open('backend/uploads/' + request.filePath)

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
