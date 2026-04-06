-- 1. Function: search by pattern (name or phone)
CREATE OR REPLACE FUNCTION search_contacts(search_pattern TEXT)
RETURNS TABLE (
    id INTEGER,
    first_name VARCHAR(100),
    phone VARCHAR(20)
)
AS $$
BEGIN
    RETURN QUERY
    SELECT c.id, c.first_name, c.phone
    FROM contacts c
    WHERE c.first_name ILIKE '%' || search_pattern || '%'
       OR c.phone ILIKE '%' || search_pattern || '%';
END;
$$ LANGUAGE plpgsql;


-- 2. Function: pagination with LIMIT and OFFSET
CREATE OR REPLACE FUNCTION get_contacts_paginated(limit_count INTEGER, offset_count INTEGER)
RETURNS TABLE (
    id INTEGER,
    first_name VARCHAR(100),
    phone VARCHAR(20)
)
AS $$
BEGIN
    RETURN QUERY
    SELECT c.id, c.first_name, c.phone
    FROM contacts c
    ORDER BY c.id
    LIMIT limit_count OFFSET offset_count;
END;
$$ LANGUAGE plpgsql;