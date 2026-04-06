-- 1. Procedure: insert one user, if exists -> update phone
CREATE OR REPLACE PROCEDURE insert_or_update_user(p_name VARCHAR(100), p_phone VARCHAR(20))
AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM contacts WHERE first_name = p_name
    ) THEN
        UPDATE contacts
        SET phone = p_phone
        WHERE first_name = p_name;
    ELSE
        INSERT INTO contacts(first_name, phone)
        VALUES (p_name, p_phone);
    END IF;
END;
$$ LANGUAGE plpgsql;


-- 2. Procedure: insert many users, validate phones, return incorrect data
CREATE OR REPLACE PROCEDURE insert_many_users(
    p_names TEXT[],
    p_phones TEXT[],
    OUT invalid_data TEXT
)
AS $$
DECLARE
    i INTEGER;
    current_name TEXT;
    current_phone TEXT;
    bad_rows TEXT := '';
BEGIN
    IF array_length(p_names, 1) IS DISTINCT FROM array_length(p_phones, 1) THEN
        invalid_data := 'Names and phones arrays must have the same length';
        RETURN;
    END IF;

    FOR i IN 1 .. array_length(p_names, 1)
    LOOP
        current_name := p_names[i];
        current_phone := p_phones[i];

        -- phone validation: only digits, length 6-20
        IF current_phone ~ '^[0-9]{6,20}$' THEN
            IF EXISTS (
                SELECT 1 FROM contacts WHERE first_name = current_name
            ) THEN
                UPDATE contacts
                SET phone = current_phone
                WHERE first_name = current_name;
            ELSE
                INSERT INTO contacts(first_name, phone)
                VALUES (current_name, current_phone);
            END IF;
        ELSE
            bad_rows := bad_rows || '(' || current_name || ', ' || current_phone || '); ';
        END IF;
    END LOOP;

    invalid_data := bad_rows;
END;
$$ LANGUAGE plpgsql;


-- 3. Procedure: delete by username or phone
CREATE OR REPLACE PROCEDURE delete_user(p_value TEXT)
AS $$
BEGIN
    DELETE FROM contacts
    WHERE first_name = p_value
       OR phone = p_value;
END;
$$ LANGUAGE plpgsql;