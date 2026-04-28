DROP FUNCTION IF EXISTS search_contacts(TEXT);
DROP FUNCTION IF EXISTS get_contacts_paginated(INTEGER, INTEGER);

CREATE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE (
    id INTEGER,
    first_name VARCHAR(100),
    surname VARCHAR(100),
    email VARCHAR(100),
    birthday DATE,
    group_name VARCHAR(50),
    phone VARCHAR(20),
    phone_type VARCHAR(10)
)
AS $$
BEGIN
    RETURN QUERY
    SELECT c.id, c.first_name, c.surname, c.email, c.birthday,
           g.name AS group_name,
           p.phone, p.type
    FROM contacts c
    LEFT JOIN groups g ON c.group_id = g.id
    LEFT JOIN phones p ON c.id = p.contact_id
    WHERE c.first_name ILIKE '%' || p_query || '%'
       OR c.surname ILIKE '%' || p_query || '%'
       OR c.email ILIKE '%' || p_query || '%'
       OR p.phone ILIKE '%' || p_query || '%';
END;
$$ LANGUAGE plpgsql;


CREATE FUNCTION get_contacts_paginated(limit_count INTEGER, offset_count INTEGER)
RETURNS TABLE (
    id INTEGER,
    first_name VARCHAR(100),
    surname VARCHAR(100),
    email VARCHAR(100),
    birthday DATE,
    group_name VARCHAR(50)
)
AS $$
BEGIN
    RETURN QUERY
    SELECT c.id, c.first_name, c.surname, c.email, c.birthday, g.name AS group_name
    FROM contacts c
    LEFT JOIN groups g ON c.group_id = g.id
    ORDER BY c.id
    LIMIT limit_count OFFSET offset_count;
END;
$$ LANGUAGE plpgsql;