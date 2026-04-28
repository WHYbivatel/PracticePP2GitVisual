DROP PROCEDURE IF EXISTS add_phone(VARCHAR, VARCHAR, VARCHAR);
DROP PROCEDURE IF EXISTS move_to_group(VARCHAR, VARCHAR);
DROP PROCEDURE IF EXISTS insert_or_update_user(VARCHAR, VARCHAR, VARCHAR, VARCHAR, DATE, VARCHAR);

CREATE PROCEDURE insert_or_update_user(
    p_name VARCHAR(100),
    p_surname VARCHAR(100),
    p_email VARCHAR(100),
    p_phone VARCHAR(20),
    p_birthday DATE,
    p_group_name VARCHAR(50)
)
AS $$
DECLARE
    v_group_id INTEGER;
    v_contact_id INTEGER;
BEGIN
    INSERT INTO groups(name)
    VALUES (p_group_name)
    ON CONFLICT (name) DO NOTHING;

    SELECT id INTO v_group_id FROM groups WHERE name = p_group_name;

    SELECT id INTO v_contact_id
    FROM contacts
    WHERE first_name = p_name AND surname = p_surname;

    IF v_contact_id IS NULL THEN
        INSERT INTO contacts(first_name, surname, email, birthday, group_id, phone)
        VALUES (p_name, p_surname, p_email, p_birthday, v_group_id, p_phone)
        RETURNING id INTO v_contact_id;
    ELSE
        UPDATE contacts
        SET email = p_email,
            birthday = p_birthday,
            group_id = v_group_id,
            phone = p_phone
        WHERE id = v_contact_id;
    END IF;

    INSERT INTO phones(contact_id, phone, type)
    VALUES (v_contact_id, p_phone, 'mobile')
    ON CONFLICT DO NOTHING;
END;
$$ LANGUAGE plpgsql;


CREATE PROCEDURE add_phone(
    p_contact_name VARCHAR,
    p_phone VARCHAR,
    p_type VARCHAR
)
AS $$
DECLARE
    v_contact_id INTEGER;
BEGIN
    SELECT id INTO v_contact_id
    FROM contacts
    WHERE first_name = p_contact_name
    LIMIT 1;

    IF v_contact_id IS NULL THEN
        RAISE NOTICE 'Contact not found';
        RETURN;
    END IF;

    INSERT INTO phones(contact_id, phone, type)
    VALUES (v_contact_id, p_phone, p_type);
END;
$$ LANGUAGE plpgsql;


CREATE PROCEDURE move_to_group(
    p_contact_name VARCHAR,
    p_group_name VARCHAR
)
AS $$
DECLARE
    v_group_id INTEGER;
BEGIN
    INSERT INTO groups(name)
    VALUES (p_group_name)
    ON CONFLICT (name) DO NOTHING;

    SELECT id INTO v_group_id
    FROM groups
    WHERE name = p_group_name;

    UPDATE contacts
    SET group_id = v_group_id
    WHERE first_name = p_contact_name;
END;
$$ LANGUAGE plpgsql;