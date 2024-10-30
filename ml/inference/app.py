from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import base64
from PIL import Image
import io
import random
from typing import Dict, List, Optional
import time

app = FastAPI()


class ImageRequest(BaseModel):
    filePath: str  # Location of image file


class BatchImageRequest(BaseModel):
    filePaths: List[str]  # Location of image files
    batch_size: Optional[int] = Field(default=16, gt=0, le=64)


class PredictionResponse(BaseModel):
    predictions: Dict[str, float]


class BatchPredictionResponse(BaseModel):
    predictions: List[Dict[str, float]]


MOCK_CATEGORIES = [
    "iron", "washer, automatic washer, washing machine", "refrigerator, icebox", "dishwasher, dish washer, dishwashing machine",
    "rotisserie", "Dutch oven", "espresso maker", "microwave, microwave oven", "toaster", "waffle iron",
]


def base64_to_pil(base64_string: str) -> Image.Image:
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


def generate_mock_predictions(n_categories: int = 10) -> Dict[str, float]:
    """Generate mock predictions with random probabilities that sum to 1."""
    raw_predictions = [random.random() for _ in range(n_categories)]
    total = sum(raw_predictions)
    normalized_predictions = [p/total for p in raw_predictions]

    return {
        # Convert to float for JSON serialization
        category: round(float(pred), 5)
        for category, pred in zip(MOCK_CATEGORIES, normalized_predictions)
    }


@app.post("/predict", response_model=PredictionResponse)
async def predict(request: ImageRequest) -> PredictionResponse:
    """
    Process image and return mock predictions.

    Args:
        request: ImageRequest containing base64 encoded image

    Returns:
        PredictionResponse with mock predictions and processing time
    """
    start_time = time.time()


    # Get image from file system
    image = Image.open('backend/uploads/' + request.filePath)

    # TODO: Preprocess image

    # Simulate some processing time (100-300ms)
    time.sleep(random.uniform(0.1, 0.3))

    # TODO: Generate mock predictions ( should be replaced with actual model inference)
    predictions = generate_mock_predictions()

    processing_time = time.time() - start_time

    return PredictionResponse(
        predictions=predictions,
        processing_time=processing_time
    )


@app.post("/batch_predict", response_model=BatchPredictionResponse)
def batch_predict(request: BatchImageRequest) -> BatchPredictionResponse:
    """
    Process images in batch and return mock predictions.

    Args:
        request: BatchImageRequest containing list of base64 encoded images

    Returns:

    """

    # Get images from file system
    images = [Image.open('backend/uploads/' + filePath) for filePath in request.filePaths]

    # Simulate some processing time (100-300ms)

    time.sleep(random.uniform(0.1, 0.3))

    # TODO: Generate mock predictions for each image (normally it would one call for entire batch)
    predictions = [generate_mock_predictions() for _ in images]

    return BatchPredictionResponse(predictions=predictions)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
