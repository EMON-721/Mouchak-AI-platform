-- DESIGN REFERENCE ONLY: run in reviewed transaction after verifying live schema.
-- Idempotently add new 15 modules without deleting/changing old IDs.
BEGIN;
INSERT INTO portal_modules(id,name,category,enabled,menu_order) VALUES ('drainpulse-bd','DrainPulse BD','climate',FALSE,36) ON CONFLICT (id) DO NOTHING;
INSERT INTO portal_modules(id,name,category,enabled,menu_order) VALUES ('agunpath-bd','AgunPath BD','safety',FALSE,37) ON CONFLICT (id) DO NOTHING;
INSERT INTO portal_modules(id,name,category,enabled,menu_order) VALUES ('matisense-bd','MatiSense BD','agri',FALSE,38) ON CONFLICT (id) DO NOTHING;
INSERT INTO portal_modules(id,name,category,enabled,menu_order) VALUES ('biddutplan-bd','BiddutPlan BD','home',FALSE,39) ON CONFLICT (id) DO NOTHING;
INSERT INTO portal_modules(id,name,category,enabled,menu_order) VALUES ('scamsignal-bd','ScamSignal BD','digital',FALSE,40) ON CONFLICT (id) DO NOTHING;
INSERT INTO portal_modules(id,name,category,enabled,menu_order) VALUES ('oshudhkhoj-bd','OshudhKhoj BD','health',FALSE,41) ON CONFLICT (id) DO NOTHING;
INSERT INTO portal_modules(id,name,category,enabled,menu_order) VALUES ('shebaqueue-bd','ShebaQueue BD','civic',FALSE,42) ON CONFLICT (id) DO NOTHING;
INSERT INTO portal_modules(id,name,category,enabled,menu_order) VALUES ('jatrapulse-bd','JatraPulse BD','transport',FALSE,43) ON CONFLICT (id) DO NOTHING;
INSERT INTO portal_modules(id,name,category,enabled,menu_order) VALUES ('skillbridge-bd','SkillBridge BD','education',FALSE,44) ON CONFLICT (id) DO NOTHING;
INSERT INTO portal_modules(id,name,category,enabled,menu_order) VALUES ('foodlabel-lens-bd','FoodLabel Lens BD','health',FALSE,45) ON CONFLICT (id) DO NOTHING;
INSERT INTO portal_modules(id,name,category,enabled,menu_order) VALUES ('odhikarsetu-bd','OdhikarSetu BD','civic',FALSE,46) ON CONFLICT (id) DO NOTHING;
INSERT INTO portal_modules(id,name,category,enabled,menu_order) VALUES ('repairright-bd','RepairRight BD','home',FALSE,47) ON CONFLICT (id) DO NOTHING;
INSERT INTO portal_modules(id,name,category,enabled,menu_order) VALUES ('jhoralert-bd','JhorAlert BD','climate',FALSE,48) ON CONFLICT (id) DO NOTHING;
INSERT INTO portal_modules(id,name,category,enabled,menu_order) VALUES ('schoolroute-bd','SchoolRoute BD','education',FALSE,49) ON CONFLICT (id) DO NOTHING;
INSERT INTO portal_modules(id,name,category,enabled,menu_order) VALUES ('hishabbondhu-bd','HishabBondhu BD','retail',FALSE,50) ON CONFLICT (id) DO NOTHING;
-- Newly added modules stay disabled until real model evaluation and data permission review.
COMMIT;
