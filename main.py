from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from enum import Enum
from fastapi.responses import RedirectResponse

app = FastAPI(title="Professional Categorized To-Do List API", description="A categorized, interactive to-do list app with FastAPI.", version="2.0")

"""
This is a professional to-do list application built with FastAPI.
Supports categories, filtering, and all CRUD operations.
Author: Prashant Dubey
"""

# Enum for category validation
class CategoryEnum(str, Enum):
    mental = "mental"
    physical = "physical"
    experimental = "experimental"
    nature = "nature"
    adventurous = "adventurous"
    nutrition = "nutrition"

# Define the item model with category and description
class Item(BaseModel):
    category: CategoryEnum
    description: str

# In-memory list to store tasks (pre-populated with example tasks)
items: List[Dict[str, str]] = [
    {"category": "mental", "description": "Meditate for 10 minutes under a tree"},
    {"category": "mental", "description": "Write a gratitude journal entry"},
    {"category": "mental", "description": "Unplug from all screens for 1 hour"},
    {"category": "mental", "description": "Call a friend and laugh for no reason"},
    {"category": "mental", "description": "Try deep breathing exercises during work break"},
    {"category": "physical", "description": "Do 25 push-ups and 30 squats"},
    {"category": "physical", "description": "Go for a sunrise jog in the neighborhood"},
    {"category": "physical", "description": "Try a new yoga pose every morning"},
    {"category": "physical", "description": "Dance like nobody's watching for 15 minutes"},
    {"category": "physical", "description": "Bike to the coffee shop instead of driving"},
    {"category": "experimental", "description": "Try cold shower challenge for 7 days"},
    {"category": "experimental", "description": "Track sleep with a wearable and adjust routine"},
    {"category": "experimental", "description": "Do a 24-hour intermittent fast"},
    {"category": "experimental", "description": "Test blue-light blockers before bed"},
    {"category": "experimental", "description": "Drink a beetroot smoothie and monitor stamina"},
    {"category": "nature", "description": "Take a barefoot walk on grass"},
    {"category": "nature", "description": "Go forest bathing (Shinrin-yoku)"},
    {"category": "nature", "description": "Identify 5 different birds in the park"},
    {"category": "nature", "description": "Pick up litter during a nature walk"},
    {"category": "nature", "description": "Do yoga at sunrise on the beach"},
    {"category": "adventurous", "description": "Try goat yoga in a nearby farm"},
    {"category": "adventurous", "description": "Join a laughter therapy session"},
    {"category": "adventurous", "description": "Do a random act of kindness anonymously"},
    {"category": "adventurous", "description": "Hike a trail you've never tried before"},
    {"category": "adventurous", "description": "Float in a sensory deprivation tank"},
    {"category": "nutrition", "description": "Make a smoothie with 5 different greens"},
    {"category": "nutrition", "description": "Try going sugar-free for a day"},
    {"category": "nutrition", "description": "Cook a vegan recipe from a different culture"},
    {"category": "nutrition", "description": "Replace coffee with herbal tea for 1 day"},
    {"category": "nutrition", "description": "Hydrate with 2L of water and track it"},
]

@app.get("/", include_in_schema=False)
def root():
    """
    Redirect root to the interactive API docs for a professional landing.
    """
    return RedirectResponse(url="/docs")

@app.get("/items/", response_model=List[Dict[str, str]])
def get_items(category: Optional[CategoryEnum] = None):
    """
    Get the list of all to-do items, optionally filtered by category.
    """
    if category:
        return [item for item in items if item["category"] == category]
    return items

@app.post("/items/", response_model=List[Dict[str, str]], status_code=201)
def create_item(item: Item):
    """
    Add a new categorized item to the to-do list.
    """
    items.append({"category": item.category, "description": item.description})
    return items

@app.get("/items/{item_id}", response_model=Dict[str, str])
def get_item(item_id: int):
    """
    Retrieve a specific item by its index.
    """
    if item_id < 0 or item_id >= len(items):
        raise HTTPException(status_code=404, detail="Item not found")
    return items[item_id]

@app.put("/items/{item_id}", response_model=Dict[str, str])
def update_item(item_id: int, item: Item):
    """
    Update an existing item by its index.
    """
    if item_id < 0 or item_id >= len(items):
        raise HTTPException(status_code=404, detail="Item not found")
    items[item_id] = {"category": item.category, "description": item.description}
    return items[item_id]

@app.delete("/items/{item_id}", response_model=dict)
def delete_item(item_id: int):
    """
    Delete an item by its index.
    """
    if item_id < 0 or item_id >= len(items):
        raise HTTPException(status_code=404, detail="Item not found")
    removed = items.pop(item_id)
    return {"deleted": removed}

# For more info, see: https://www.youtube.com/watch?v=iWS9ogMPOI0