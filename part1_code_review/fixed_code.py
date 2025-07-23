# Fixed version with explanations
# ✅ FIXED create_product API with improvements and comments
#
# 🛑 Issues in Original Code:
# 1. No validation for required fields → leads to KeyError or bad data.
# 2. SKU uniqueness not checked → allows duplicate SKUs across products.
# 3. 'price' might not be parsed as Decimal → risk of precision loss.
# 4. No error handling → any failure leaves inconsistent DB state.
# 5. No transaction wrapping both inserts → inventory might save even if product fails.
# 6. Assumes 'initial_quantity' always present → crash if missing.
# 7. Hard commits without rollback on error.

from flask import request, jsonify
from sqlalchemy.exc import IntegrityError
from decimal import Decimal
from app import app, db
from models import Product, Inventory  # Assuming these exist

@app.route('/api/products', methods=['POST'])
def create_product():
    data = request.get_json()

    required_fields = ['name', 'sku', 'price', 'warehouse_id', 'initial_quantity']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    # Check for existing SKU (must be unique across platform)
    existing = Product.query.filter_by(sku=data['sku']).first()
    if existing:
        return jsonify({"error": "SKU already exists"}), 409

    try:
        # Use a DB transaction block
        with db.session.begin_nested():
            # Create new product
            product = Product(
                name=data['name'],
                sku=data['sku'],
                price=Decimal(str(data['price'])),  # Ensure correct Decimal type
                warehouse_id=data['warehouse_id']
            )
            db.session.add(product)
            db.session.flush()  # To get product.id before commit

            # Update inventory count
            inventory = Inventory(
                product_id=product.id,
                warehouse_id=data['warehouse_id'],
                quantity=data['initial_quantity']
            )
            db.session.add(inventory)

        db.session.commit()
        return jsonify({"message": "Product created", "product_id": product.id}), 201

    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Database integrity error", "details": str(e)}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Unexpected error", "details": str(e)}), 500

#Fixes: 
# Missing fields - Validation loop 
# SKU not unique - Checked Product.query.filter_by(sku=...)
# Decimal issue	- Converted price using Decimal(str(...))
# No error handling	- Added try-except and rollback
# Two separate commits- Used db.session.begin_nested() for atomic transaction
# Crash on missing initial_quantity	- Added validation check
# No response codes	- Used appropriate 201, 400, 409, 500 codes