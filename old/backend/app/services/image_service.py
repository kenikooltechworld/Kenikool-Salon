import cloudinary
import cloudinary.uploader
from typing import Optional, Dict
from datetime import datetime
from bson import ObjectId
from pymongo.collection import Collection
from PIL import Image
import io
import os


class ImageService:
    def __init__(self, db, cloudinary_config: Optional[Dict] = None):
        self.db = db
        self.products_collection: Collection = db.inventory

        if cloudinary_config:
            cloudinary.config(
                cloud_name=cloudinary_config.get("cloud_name"),
                api_key=cloudinary_config.get("api_key"),
                api_secret=cloudinary_config.get("api_secret"),
            )

    def upload_product_image(
        self,
        product_id: str,
        image_file,
        generate_thumbnail: bool = True,
    ) -> Dict:
        """Upload and optimize product image"""
        product = self.products_collection.find_one({"_id": ObjectId(product_id)})
        if not product:
            raise ValueError(f"Product {product_id} not found")

        try:
            # Read image file
            image_data = image_file.file.read()
            image = Image.open(io.BytesIO(image_data))

            # Optimize image
            image.thumbnail((1200, 1200), Image.Resampling.LANCZOS)
            optimized_image = io.BytesIO()
            image.save(optimized_image, format="JPEG", quality=85, optimize=True)
            optimized_image.seek(0)

            # Upload to Cloudinary
            upload_result = cloudinary.uploader.upload(
                optimized_image,
                folder=f"salon/products/{product_id}",
                resource_type="image",
                public_id="main",
                overwrite=True,
            )

            image_url = upload_result["secure_url"]

            # Generate thumbnail if requested
            thumbnail_url = None
            if generate_thumbnail:
                thumb_image = Image.open(io.BytesIO(image_data))
                thumb_image.thumbnail((300, 300), Image.Resampling.LANCZOS)
                thumb_buffer = io.BytesIO()
                thumb_image.save(thumb_buffer, format="JPEG", quality=80, optimize=True)
                thumb_buffer.seek(0)

                thumb_result = cloudinary.uploader.upload(
                    thumb_buffer,
                    folder=f"salon/products/{product_id}",
                    resource_type="image",
                    public_id="thumbnail",
                    overwrite=True,
                )
                thumbnail_url = thumb_result["secure_url"]

            # Update product with image URLs
            self.products_collection.update_one(
                {"_id": ObjectId(product_id)},
                {
                    "$set": {
                        "image_url": image_url,
                        "thumbnail_url": thumbnail_url,
                        "image_uploaded_at": datetime.utcnow(),
                    }
                },
            )

            return {
                "product_id": product_id,
                "image_url": image_url,
                "thumbnail_url": thumbnail_url,
                "upload_result": upload_result,
            }

        except Exception as e:
            raise ValueError(f"Failed to upload image: {str(e)}")

    def delete_product_image(self, product_id: str) -> Dict:
        """Delete product image from Cloudinary and database"""
        product = self.products_collection.find_one({"_id": ObjectId(product_id)})
        if not product:
            raise ValueError(f"Product {product_id} not found")

        try:
            # Delete from Cloudinary
            cloudinary.uploader.destroy(f"salon/products/{product_id}/main")
            cloudinary.uploader.destroy(f"salon/products/{product_id}/thumbnail")

            # Update product to remove image URLs
            self.products_collection.update_one(
                {"_id": ObjectId(product_id)},
                {
                    "$unset": {
                        "image_url": "",
                        "thumbnail_url": "",
                        "image_uploaded_at": "",
                    }
                },
            )

            return {"success": True, "message": "Image deleted successfully"}

        except Exception as e:
            raise ValueError(f"Failed to delete image: {str(e)}")

    def get_product_image(self, product_id: str) -> Optional[Dict]:
        """Get product image URLs"""
        product = self.products_collection.find_one({"_id": ObjectId(product_id)})
        if not product:
            raise ValueError(f"Product {product_id} not found")

        return {
            "product_id": product_id,
            "image_url": product.get("image_url"),
            "thumbnail_url": product.get("thumbnail_url"),
            "image_uploaded_at": product.get("image_uploaded_at"),
        }

    def get_category_placeholder(self, category: str) -> str:
        """Get placeholder image URL for category"""
        placeholders = {
            "hair_care": "https://via.placeholder.com/300?text=Hair+Care",
            "skincare": "https://via.placeholder.com/300?text=Skincare",
            "makeup": "https://via.placeholder.com/300?text=Makeup",
            "tools": "https://via.placeholder.com/300?text=Tools",
            "other": "https://via.placeholder.com/300?text=Product",
        }
        return placeholders.get(category.lower(), placeholders["other"])



