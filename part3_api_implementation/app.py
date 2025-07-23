from flask import Flask, jsonify
from datetime import datetime, timedelta
from models import db, Product, Inventory, Warehouse, Supplier, SupplierProduct, Sale

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Create tables on first run
with app.app_context():
    db.create_all()

@app.route("/api/companies/<int:company_id>/alerts/low-stock", methods=["GET"])
def get_low_stock_alerts(company_id):
    alerts = []
    recent_days = 30
    recent_date = datetime.utcnow() - timedelta(days=recent_days)

    warehouses = Warehouse.query.filter_by(company_id=company_id).all()

    for warehouse in warehouses:
        inventory_items = Inventory.query.filter_by(warehouse_id=warehouse.id).all()

        for inv in inventory_items:
            product = Product.query.get(inv.product_id)
            if not product or product.low_stock_threshold is None:
                continue

            if inv.quantity >= product.low_stock_threshold:
                continue

            recent_sales = Sale.query.filter(
                Sale.product_id == product.id,
                Sale.warehouse_id == warehouse.id,
                Sale.timestamp >= recent_date
            ).count()

            if recent_sales == 0:
                continue

            total_qty_sold = db.session.query(db.func.sum(Sale.quantity)).filter(
                Sale.product_id == product.id,
                Sale.warehouse_id == warehouse.id,
                Sale.timestamp >= recent_date
            ).scalar() or 0

            avg_daily_sales = total_qty_sold / recent_days if total_qty_sold > 0 else 0
            days_until_stockout = int(inv.quantity / avg_daily_sales) if avg_daily_sales > 0 else -1

            supplier_info = db.session.query(Supplier).join(SupplierProduct).filter(
                SupplierProduct.product_id == product.id
            ).first()

            alerts.append({
                "product_id": product.id,
                "product_name": product.name,
                "sku": product.sku,
                "warehouse_id": warehouse.id,
                "warehouse_name": warehouse.name,
                "current_stock": inv.quantity,
                "threshold": product.low_stock_threshold,
                "days_until_stockout": days_until_stockout,
                "supplier": {
                    "id": supplier_info.id if supplier_info else None,
                    "name": supplier_info.name if supplier_info else None,
                    "contact_email": supplier_info.contact_email if supplier_info else None
                }
            })

    return jsonify({
        "alerts": alerts,
        "total_alerts": len(alerts)
    })
@app.route("/")
def home():
    return "✅ Bynry API is running!"

# Optional entry point for direct execution
if __name__ == "__main__":
    app.run(debug=True)
