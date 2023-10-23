-- Get user roles on the given target id.


-- Grab the hierarchy of targets from the target id up the chain.
WITH RECURSIVE ancestors (id, parent_id) AS (
    SELECT roles_roletarget.id, roles_roletarget.parent_id
        FROM roles_roletarget
        WHERE roles_roletarget.id = %s

    UNION ALL

    SELECT roles_roletarget.id, roles_roletarget.parent_id
        FROM roles_roletarget
        JOIN ancestors
            ON roles_roletarget.id = ancestors.parent_id
),

has_master (value) AS (
    SELECT ancestors.id
        FROM ancestors
        JOIN roles_roletarget
            ON ancestors.id = roles_roletarget.id
        JOIN roles_role
            ON roles_role.target_id = roles_roletarget.id
        WHERE roles_role.type = 'master'
            AND roles_role.user_id = %s
            -- TODO: handle anonymous users too with an optional IS NULL
)

-- All roles the user has on the target
roles (type) AS (
    -- Start with all roles on all role targets
    SELECT roles_role.type
    FROM roles_role
        JOIN roles_roletarget
            ON roles_role.target_id = roles_roletarget.id
        WHERE roles_role.target_id = %s
            AND roles_role.user_id = %s
            -- TODO: handle anonymous users too with an optional IS NULL

    -- Filter master because we'll get it in the next term anyway.
    WHERE roles_role.type != 'master'

    UNION ALL

    SELECT 'master' FROM has_master LIMIT 1

    UNION

    -- Add 'editor' if the inferred types had 'master'
    SELECT 'editor' FROM roles
        WHERE roles.type = 'master'

    UNION

    -- Add 'viewer' if the inferred types had 'editor'
    SELECT 'viewer' FROM roles
        WHERE roles.type = 'editor'
)

SELECT type FROM roles
