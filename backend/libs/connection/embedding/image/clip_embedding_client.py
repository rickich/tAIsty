import asyncio
import base64
import io

import clip
import torch
from PIL import Image

from libs.connection.embedding.image.interface import IImageEmbeddingClient


class CLIPEmbeddingClient(IImageEmbeddingClient):
    def __init__(self, model: str = "ViT-B/32"):
        self._device = "cuda" if torch.cuda.is_available() else "cpu"
        self._model, self._preprocess = clip.load(model, device=self._device)

    async def embed(self, image: str) -> list[float]:  # text: base64 image
        image = self.convert_base64_to_image(image)

        loop = asyncio.get_event_loop()
        embs = await loop.run_in_executor(None, self.get_clip_embeddings, [image])
        return embs[0]

    async def embed_many(self, images: list[str]) -> list[list[float]]:
        images = [self.convert_base64_to_image(img) for img in images]

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.get_clip_embeddings, images)

    @staticmethod
    def convert_base64_to_image(image_str: str) -> Image:
        image_str = image_str.split(",")[-1]
        image_data = base64.b64decode(image_str)
        return Image.open(io.BytesIO(image_data)).convert("RGB")

    def get_clip_embeddings(self, images: list[Image.Image]) -> list[list[float]]:
        images = [self._preprocess(image) for image in images]
        images = torch.stack(images).to(self._device)
        with torch.no_grad():
            image_features = self._model.encode_image(images)
        return image_features.cpu().numpy().tolist()
