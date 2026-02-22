from typing import List, Dict, Optional
from bson import ObjectId
from pymongo.collection import Collection


class SearchService:
    def __init__(self, db):
        self.db = db
        self.products_collection: Collection = db.inventory
        self.filter_presets_collection: Collection = db.search_filter_presets

    def search_products(
        self,
        query: Optional[str] = None,
        categories: Optional[List[str]] = None,
        suppliers: Optional[List[str]] = None,
        stock_range: Optional[tuple] = None,
        price_range: Optional[tuple] = None,
        sort_by: str = "name",
        sort_order: int = 1,
        skip: int = 0,
        limit: int = 50,
    ) -> Dict:
        """Search products with advanced filtering"""
        search_query = {}

        # Text search across name, SKU, category, supplier
        if query:
            search_query["$or"] = [
                {"name": {"$regex": query, "$options": "i"}},
                {"sku": {"$regex": query, "$options": "i"}},
                {"category": {"$regex": query, "$options": "i"}},
                {"supplier": {"$regex": query, "$options": "i"}},
            ]

        # Category filter
        if categories:
            search_query["category"] = {"$in": categories}

        # Supplier filter
        if suppliers:
            search_query["supplier_id"] = {"$in": [ObjectId(s) for s in suppliers]}

        # Stock level range filter
        if stock_range:
            min_stock, max_stock = stock_range
            search_query["quantity"] = {"$gte": min_stock, "$lte": max_stock}

        # Price range filter
        if price_range:
            min_price, max_price = price_range
            search_query["price"] = {"$gte": min_price, "$lte": max_price}

        # Determine sort field
        sort_field = "name"
        if sort_by == "quantity":
            sort_field = "quantity"
        elif sort_by == "value":
            sort_field = "price"
        elif sort_by == "updated":
            sort_field = "updated_at"

        # Execute search
        total = self.products_collection.count_documents(search_query)

        products = list(
            self.products_collection.find(search_query)
            .sort(sort_field, sort_order)
            .skip(skip)
            .limit(limit)
        )

        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "products": [
                {**p, "_id": str(p["_id"]), "id": str(p["_id"])} for p in products
            ],
        }

    def get_stock_level_ranges(self) -> Dict:
        """Get products grouped by stock level ranges"""
        ranges = {
            "0-10": {"min": 0, "max": 10},
            "11-50": {"min": 11, "max": 50},
            "51-100": {"min": 51, "max": 100},
            "100+": {"min": 100, "max": float("inf")},
        }

        result = {}
        for range_name, range_vals in ranges.items():
            query = {
                "quantity": {
                    "$gte": range_vals["min"],
                    "$lte": range_vals["max"],
                }
            }
            count = self.products_collection.count_documents(query)
            result[range_name] = count

        return result

    def get_available_filters(self) -> Dict:
        """Get all available filter options"""
        categories = list(
            self.products_collection.distinct("category")
        )
        suppliers = list(
            self.products_collection.distinct("supplier_id")
        )

        return {
            "categories": categories,
            "suppliers": suppliers,
            "stock_ranges": self.get_stock_level_ranges(),
        }

    def save_filter_preset(
        self,
        preset_name: str,
        query: Optional[str] = None,
        categories: Optional[List[str]] = None,
        suppliers: Optional[List[str]] = None,
        stock_range: Optional[tuple] = None,
        price_range: Optional[tuple] = None,
        sort_by: str = "name",
        sort_order: int = 1,
    ) -> Dict:
        """Save a filter preset"""
        preset = {
            "name": preset_name,
            "query": query,
            "categories": categories,
            "suppliers": suppliers,
            "stock_range": stock_range,
            "price_range": price_range,
            "sort_by": sort_by,
            "sort_order": sort_order,
        }

        result = self.filter_presets_collection.insert_one(preset)
        return {"id": str(result.inserted_id), **preset}

    def get_filter_presets(self) -> List[Dict]:
        """Get all saved filter presets"""
        presets = list(self.filter_presets_collection.find({}))
        return [
            {**p, "_id": str(p["_id"]), "id": str(p["_id"])} for p in presets
        ]

    def apply_filter_preset(self, preset_id: str) -> Dict:
        """Apply a saved filter preset"""
        preset = self.filter_presets_collection.find_one(
            {"_id": ObjectId(preset_id)}
        )
        if not preset:
            raise ValueError(f"Preset {preset_id} not found")

        return self.search_products(
            query=preset.get("query"),
            categories=preset.get("categories"),
            suppliers=preset.get("suppliers"),
            stock_range=preset.get("stock_range"),
            price_range=preset.get("price_range"),
            sort_by=preset.get("sort_by", "name"),
            sort_order=preset.get("sort_order", 1),
        )

    def delete_filter_preset(self, preset_id: str) -> Dict:
        """Delete a filter preset"""
        result = self.filter_presets_collection.delete_one(
            {"_id": ObjectId(preset_id)}
        )
        if result.deleted_count == 0:
            raise ValueError(f"Preset {preset_id} not found")

        return {"success": True, "message": "Preset deleted"}

    def update_filter_preset(
        self,
        preset_id: str,
        preset_name: Optional[str] = None,
        query: Optional[str] = None,
        categories: Optional[List[str]] = None,
        suppliers: Optional[List[str]] = None,
        stock_range: Optional[tuple] = None,
        price_range: Optional[tuple] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[int] = None,
    ) -> Dict:
        """Update a filter preset"""
        update_data = {}

        if preset_name is not None:
            update_data["name"] = preset_name
        if query is not None:
            update_data["query"] = query
        if categories is not None:
            update_data["categories"] = categories
        if suppliers is not None:
            update_data["suppliers"] = suppliers
        if stock_range is not None:
            update_data["stock_range"] = stock_range
        if price_range is not None:
            update_data["price_range"] = price_range
        if sort_by is not None:
            update_data["sort_by"] = sort_by
        if sort_order is not None:
            update_data["sort_order"] = sort_order

        result = self.filter_presets_collection.update_one(
            {"_id": ObjectId(preset_id)},
            {"$set": update_data},
        )

        if result.matched_count == 0:
            raise ValueError(f"Preset {preset_id} not found")

        preset = self.filter_presets_collection.find_one(
            {"_id": ObjectId(preset_id)}
        )
        return {**preset, "_id": str(preset["_id"]), "id": str(preset["_id"])}

