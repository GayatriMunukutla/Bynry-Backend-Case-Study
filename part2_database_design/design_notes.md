# Design notes and assumptions
# Database Design Notes

## Relationships
- A **Company** has many **Warehouses** → `warehouses` table has `company_id` as a foreign key.
- A **Product** can exist in multiple **Warehouses**, and each **Warehouse** stores many **Products** → implemented via `inventory` (many-to-many).
- **Suppliers** can supply multiple **Products** and vice versa → `supplier_products` handles this many-to-many mapping.
- A **Bundle Product** can contain other **Products** → represented using `bundle_items` (self-referencing table).
- Every **Inventory entry** can have a history of changes → logged in `inventory_changes`.

## Design Decisions
- `products.sku` is made UNIQUE to ensure platform-wide uniqueness.
- Used `DECIMAL(10,2)` for `price` to prevent floating point issues.
- Used `ON DELETE CASCADE` so deleting a company deletes its warehouses, and so on.
- `bundle_items` uses two product IDs: one for the bundle, one for the item inside it.
- `inventory` has a UNIQUE constraint on `(product_id, warehouse_id)` to prevent duplicates.

## Questions for Product Team
1. Should bundles have inventory, or just be virtual aggregations?
2. Can the same supplier provide to multiple companies or is it company-specific?
3. Should we track product price changes over time?
4. How is recent sales activity stored? Is there a `sales` or `orders` table?
5. Should we allow multiple SKUs for product variants (like sizes/colors)?

## Indexes & Constraints
- PRIMARY KEYs and FOREIGN KEYs on all tables.
- UNIQUE constraint on `products.sku`.
- INDEX implied on all foreign keys.
