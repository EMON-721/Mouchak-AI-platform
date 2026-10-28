-- Append-only legacy stock port. No existing user rows or tables are rewritten.

CREATE TABLE IF NOT EXISTS stock_items (
	id VARCHAR NOT NULL, 
	user_id VARCHAR NOT NULL, 
	workspace_id VARCHAR NOT NULL, 
	sku_hash VARCHAR NOT NULL, 
	encrypted TEXT NOT NULL, 
	quantity INTEGER NOT NULL, 
	minimum INTEGER NOT NULL, 
	revision INTEGER NOT NULL, 
	archived BOOLEAN NOT NULL, 
	created_at VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_stock_owner_workspace_sku UNIQUE (user_id, workspace_id, sku_hash), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE, 
	FOREIGN KEY(workspace_id) REFERENCES workspaces (id) ON DELETE CASCADE
)

;
CREATE INDEX IF NOT EXISTS ix_stock_items_user_id ON stock_items (user_id);
CREATE INDEX IF NOT EXISTS ix_stock_items_workspace_id ON stock_items (workspace_id);
ALTER TABLE stock_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE stock_items FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS owner_only ON stock_items;
CREATE POLICY owner_only ON stock_items USING (user_id = current_setting('app.user_id',true)) WITH CHECK (user_id = current_setting('app.user_id',true) AND EXISTS (SELECT 1 FROM workspaces w WHERE w.id=stock_items.workspace_id AND w.user_id=stock_items.user_id));

CREATE TABLE IF NOT EXISTS stock_movements (
	id VARCHAR NOT NULL, 
	user_id VARCHAR NOT NULL, 
	workspace_id VARCHAR NOT NULL, 
	item_id VARCHAR NOT NULL, 
	idempotency_key VARCHAR NOT NULL, 
	encrypted TEXT NOT NULL, 
	occurred_at VARCHAR NOT NULL, 
	created_at VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_stock_movement_retry UNIQUE (user_id, workspace_id, idempotency_key), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE, 
	FOREIGN KEY(workspace_id) REFERENCES workspaces (id) ON DELETE CASCADE, 
	FOREIGN KEY(item_id) REFERENCES stock_items (id) ON DELETE CASCADE
)

;
CREATE INDEX IF NOT EXISTS ix_stock_movements_item_id ON stock_movements (item_id);
CREATE INDEX IF NOT EXISTS ix_stock_movements_user_id ON stock_movements (user_id);
CREATE INDEX IF NOT EXISTS ix_stock_movements_workspace_id ON stock_movements (workspace_id);
ALTER TABLE stock_movements ENABLE ROW LEVEL SECURITY;
ALTER TABLE stock_movements FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS owner_only ON stock_movements;
CREATE POLICY owner_only ON stock_movements USING (user_id = current_setting('app.user_id',true)) WITH CHECK (user_id = current_setting('app.user_id',true) AND EXISTS (SELECT 1 FROM stock_items i WHERE i.id=stock_movements.item_id AND i.workspace_id=stock_movements.workspace_id AND i.user_id=stock_movements.user_id));
