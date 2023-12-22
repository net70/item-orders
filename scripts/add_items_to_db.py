import uuid
import random
import pymongo

# MongoDB & Redis connection settings
mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
db = mongo_client["transactions"]

if "items" not in db.list_collection_names():
    db.create_collection("items")
items_db = db["items"]

if "orders" not in db.list_collection_names():
    db.create_collection("orders")
orders_db = db["orders"]

# Random Items to add to DB (generated with chatGPT)
items = {
    "Smartphone": ["Electronics", "The latest smartphone with high-resolution camera and fast processor.", 699.99],
    "Leather Wallet": ["Fashion & Accessories", "Handcrafted leather wallet with multiple card slots and a cash compartment.", 49.99],
    "Hiking Backpack": ["Outdoor Gear", "Durable backpack with ample storage, perfect for hiking and camping trips.", 89.99],
    "Coffee Maker": ["Home & Kitchen", "Programmable coffee maker for brewing your favorite morning coffee.", 59.99],
    "Running Shoes": ["Sports & Fitness", "Lightweight and comfortable running shoes for your daily workouts.", 79.99],
    "Cookware Set": ["Home & Kitchen", "Non-stick cookware set with pots, pans, and utensils.", 129.99],
    "Digital Camera": ["Electronics", "High-resolution digital camera with various shooting modes.", 499.99],
    "Classic Watch": ["Fashion & Accessories", "Elegant and stylish wristwatch with a stainless steel band.", 129.99],
    "Gaming Console": ["Electronics", "The latest gaming console with a powerful graphics processor.", 399.99],
    "Stainless Steel Water Bottle": ["Sports & Fitness", "Insulated water bottle to keep your drinks cold or hot.", 24.99],
    "Designer Sunglasses": ["Fashion & Accessories", "Trendy sunglasses with UV protection and a stylish frame.", 79.99],
    "Camping Tent": ["Outdoor Gear", "Spacious tent with weather-resistant materials for outdoor adventures.", 149.99],
    "Blender": ["Home & Kitchen", "High-speed blender for smoothies, soups, and more.", 69.99],
    "Laptop": ["Electronics", "Thin and lightweight laptop with a powerful processor and long battery life.", 899.99],
    "Denim Jeans": ["Fashion & Accessories", "Classic denim jeans for a casual and comfortable look.", 59.99],
    "Mountain Bike": ["Sports & Fitness", "Durable mountain bike for off-road cycling adventures.", 499.99],
    "Wireless Earbuds": ["Electronics", "Wireless earbuds with noise-cancellation and long battery life.", 149.99],
    "Handbag": ["Fashion & Accessories", "Stylish handbag with multiple compartments and a detachable strap.", 69.99],
    "Grill Set": ["Home & Kitchen", "Barbecue grill set with all the tools you need for grilling.", 39.99],
    "Fitness Tracker": ["Sports & Fitness", "Smart fitness tracker with heart rate monitor and activity tracking.", 79.99],
    "Dress Shoes": ["Fashion & Accessories", "Classic leather dress shoes for formal occasions.", 89.99],
    "Television": ["Electronics", "High-definition LED TV with a large screen and multiple connectivity options.", 499.99],
    "Headphones": ["Electronics", "Over-ear headphones with superior sound quality and comfortable padding.", 129.99],
    "Puzzle Board Game": ["Toys & Games", "A challenging board game that tests your puzzle-solving skills.", 24.99],
    "Ceramic Dinnerware Set": ["Home & Kitchen", "Elegant ceramic dinnerware set for special occasions.", 79.99],
    "Camping Stove": ["Outdoor Gear", "Compact camping stove for cooking in the wilderness.", 34.99],
    "Desk Chair": ["Furniture", "Ergonomic desk chair with adjustable height and lumbar support.", 89.99],
    "Hooded Sweatshirt": ["Fashion & Accessories", "Warm and cozy hooded sweatshirt for cold weather.", 39.99],
    "Running Watch": ["Sports & Fitness", "GPS running watch with distance tracking and heart rate monitor.", 129.99],
    "Wrist Blood Pressure Monitor": ["Health & Wellness", "Digital wrist blood pressure monitor for at-home use.", 29.99],
    "Robot Vacuum Cleaner": ["Home & Kitchen", "Smart robot vacuum for automated floor cleaning.", 199.99],
    "Backpack Diaper Bag": ["Baby & Kids", "Stylish backpack diaper bag with multiple pockets for baby essentials.", 49.99],
    "Electric Toothbrush": ["Health & Wellness", "Electric toothbrush for effective oral hygiene.", 49.99],
    "Air Purifier": ["Home & Kitchen", "HEPA air purifier for clean and fresh indoor air.", 79.99],
    "Guitar": ["Musical Instruments", "Acoustic guitar for beginners and enthusiasts.", 199.99],
    "Coffee Table": ["Furniture", "Modern coffee table with a sleek design and storage shelf.", 79.99],
    "Dumbbell Set": ["Sports & Fitness", "Adjustable dumbbell set for strength training at home.", 89.99],
    "Instant Pot": ["Home & Kitchen", "Multi-functional pressure cooker for quick and easy cooking.", 59.99],
    "Baby Monitor": ["Baby & Kids", "Video baby monitor with night vision and two-way communication.", 79.99],
    "Wireless Router": ["Electronics", "High-speed wireless router for seamless internet connectivity.", 79.99],
    "Outdoor Hammock": ["Outdoor Gear", "Relaxing outdoor hammock for leisure and camping.", 49.99],
    "Rolling Luggage": ["Travel & Luggage", "Durable rolling luggage with telescopic handle and multiple compartments.", 99.99],
    "Home Security Camera": ["Home & Kitchen", "Wireless home security camera with motion detection and night vision.", 69.99],
    "Electric Kettle": ["Home & Kitchen", "Fast-boiling electric kettle for making hot beverages.", 29.99],
    "Acoustic Guitar": ["Musical Instruments", "Classic acoustic guitar with a rich, resonant sound.", 149.99],
    "Chess Set": ["Toys & Games", "Classic chess set with wooden board and pieces.", 29.99],
    "Massage Chair": ["Furniture", "Shiatsu massage chair with heat and multiple massage modes.", 499.99],
    "Smart Thermostat": ["Home Improvement", "Smart thermostat for energy-efficient temperature control.", 79.99],
    "Fishing Rod and Reel Combo": ["Outdoor Gear", "Fishing rod and reel combo for angling adventures.", 49.99],
    "Electric Scooter": ["Sports & Outdoors", "Electric scooter for convenient urban commuting.", 299.99],
    "Resistance Bands Set": ["Sports & Fitness", "Set of resistance bands for versatile strength training.", 19.99],
    "Smart Home Security System": ["Home Improvement", "Comprehensive smart security system with cameras and sensors.", 299.99],
    "Elegant Diamond Necklace": ["Fashion & Accessories", "Exquisite diamond necklace with a 14k white gold chain.", 2499.99],
    "Kayak with Paddle": ["Outdoor Gear", "Single-seat kayak for water adventures, includes a paddle.", 449.99],
    "Espresso Machine": ["Home & Kitchen", "High-quality espresso machine for barista-style coffee at home.", 799.99],
    "High-Performance Laptop": ["Electronics", "Powerful laptop with a dedicated graphics card for gaming and work.", 1299.99],
    "Hiking Boots": ["Sports & Fitness", "Durable hiking boots with waterproof and breathable features.", 129.99],
    "Stainless Steel Refrigerator": ["Home Appliances", "Large capacity refrigerator with modern design and features.", 999.99],
    "Luxury Watch": ["Fashion & Accessories", "Luxurious Swiss-made watch with automatic movement.", 4999.99],
    "Digital Piano": ["Musical Instruments", "88-key digital piano with weighted keys and multiple sounds.", 899.99],
    "Wireless Speaker System": ["Electronics", "High-fidelity wireless speaker system for home audio.", 349.99],
    "Vintage Vinyl Record Player": ["Electronics", "Retro-style vinyl record player with built-in speakers.", 199.99],
    "Designer Handbag": ["Fashion & Accessories", "Designer handbag with premium leather and elegant design.", 799.99],
    "Mountain Climbing Gear": ["Outdoor Gear", "Complete set of mountain climbing equipment for enthusiasts.", 899.99],
    "Robotic Vacuum and Mop": ["Home & Kitchen", "Smart robotic vacuum and mop for hands-free cleaning.", 349.99],
    "Gaming Keyboard and Mouse Combo": ["Electronics", "Mechanical gaming keyboard and high-precision mouse.", 129.99],
    "High-End Desktop Computer": ["Electronics", "Customizable desktop computer with top-tier components.", 1699.99],
    "Leather Sofa": ["Furniture", "Premium leather sofa with reclining features and cup holders.", 1499.99],
    "Wireless Noise-Canceling Headphones": ["Electronics", "Over-ear wireless headphones with active noise cancellation.", 249.99],
    "Home Theater Projector": ["Electronics", "1080p home theater projector for cinematic experiences at home.", 699.99],
    "Luxury Fountain Pen": ["Office Supplies", "Handcrafted fountain pen with 18k gold nib and inkwell.", 299.99],
    "Action Camera": ["Electronics", "Waterproof action camera for capturing adventures in 4K resolution.", 199.99],
    "Protein Powder": ["Health & Wellness", "High-quality protein powder for post-workout recovery.", 29.99],
    "Professional Studio Microphone": ["Musical Instruments", "Condenser microphone for studio-quality audio recording.", 199.99],
    "Digital Drawing Tablet": ["Electronics", "Graphics tablet for digital artists and illustrators.", 299.99],
    "Electric Skateboard": ["Sports & Outdoors", "Electric skateboard for fun and eco-friendly commuting.", 499.99],
    "Fitness Elliptical Machine": ["Sports & Fitness", "Home elliptical machine for low-impact cardio workouts.", 799.99],
    "Aromatherapy Diffuser": ["Health & Wellness", "Ultrasonic aromatherapy diffuser with LED lighting.", 39.99],
    "Baby Stroller Travel System": ["Baby & Kids", "Travel system with stroller, car seat, and base.", 249.99],
    "Wireless Charging Pad": ["Electronics", "Qi-certified wireless charging pad for smartphones and more.", 19.99],
    "Cooking Knife Set": ["Home & Kitchen", "High-quality knife set for professional cooking.", 99.99],
    "Air Fryer": ["Home & Kitchen", "Air fryer for healthier cooking with less oil.", 79.99],
    "Fitness Exercise Bike": ["Sports & Fitness", "Indoor exercise bike with adjustable resistance.", 299.99],
    "Smart LED Light Bulbs": ["Home Improvement", "Wi-Fi-enabled LED bulbs with color-changing features.", 29.99],
    "Dining Table Set": ["Furniture", "Elegant dining table set with chairs for family meals.", 599.99],
    "Plant-Based Protein Bars": ["Health & Wellness", "Plant-based protein bars for on-the-go nutrition.", 19.99],
    "Cordless Vacuum Cleaner": ["Home Appliances", "Lightweight cordless vacuum for quick cleanups.", 129.99],
    "Handheld Gimbal Stabilizer": ["Electronics", "Handheld gimbal for smooth smartphone and camera shots.", 129.99],
    "Smart Doorbell Camera": ["Home Improvement", "Smart doorbell with camera and two-way audio.", 149.99],
    "Cat Tree and Scratching Post": ["Pets", "Multi-level cat tree with scratching posts and hiding spots.", 69.99],
    "Multi-Function Printer": ["Office Electronics", "All-in-one printer with scanning, copying, and wireless printing.", 149.99],
    "Classic Board Games Bundle": ["Toys & Games", "Bundle of classic board games for family fun.", 49.99],
    "Bluetooth Karaoke Microphone": ["Electronics", "Wireless karaoke microphone for singing enthusiasts.", 29.99],
    "Fitness Resistance Bands Set": ["Sports & Fitness", "Set of resistance bands for home workouts and flexibility.", 19.99],
    "Rechargeable Hand Warmer": ["Outdoor Gear", "Rechargeable hand warmer for outdoor activities in the cold.", 19.99],
    "Ceramic Space Heater": ["Home Appliances", "Compact ceramic space heater with adjustable thermostat.", 39.99],
    "Portable Camping Grill": ["Outdoor Gear", "Portable grill for camping and outdoor cooking.", 49.99],
    "Smart Coffee Mug": ["Home & Kitchen", "Smart coffee mug that keeps beverages at the perfect temperature.", 49.99],
    "Yoga Mat with Carry Bag": ["Sports & Fitness", "Non-slip yoga mat with a convenient carry bag.", 24.99],
    "Collapsible Travel Backpack": ["Travel & Luggage", "Lightweight backpack that folds for easy travel.", 29.99],
    "Professional Hair Dryer": ["Health & Beauty", "Professional-grade hair dryer for salon-quality results.", 69.99]
}


# Function to generate a random item
def generate_random_item(category, name, description, price):
    return {
        "item_id": str(uuid.uuid4()),
        "category": category,
        "name": name,
        "description": description,
        "price": price,
        "num_in_stock": random.randint(1_000, 10_000),
    }


if 'item_id' not in items_db.index_information():
    items_db.create_index("item_id", unique=True)

if "order_id" not in orders_db.index_information():
    orders_db.create_index("order_id", unique=True)

# Number of unique items to add
num_items_to_add = len(items)

# Create and insert unique items into the db
for name, info in items.items():
    unique_item = generate_random_item(info[0], name, info[1], info[2])
    # Ensure uniqueness of the item by using the "name" field
    if not items_db.find_one({"name": unique_item["name"]}):
        items_db.insert_one(unique_item)
        print(f"Added item: {unique_item['name']} to mongo")

print("Items added successfully.")

# Close the MongoDB & Redis client connection
mongo_client.close()