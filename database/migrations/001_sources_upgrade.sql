ALTER TABLE sources ADD COLUMN priority INTEGER DEFAULT 5;

ALTER TABLE sources ADD COLUMN last_checked TEXT;

ALTER TABLE sources ADD COLUMN last_success TEXT;

ALTER TABLE sources ADD COLUMN last_error TEXT;

ALTER TABLE sources ADD COLUMN check_interval INTEGER DEFAULT 60;