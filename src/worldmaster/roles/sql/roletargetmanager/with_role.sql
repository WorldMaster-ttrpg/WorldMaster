-- Get all roletarget ids that the user has the given role on.

WITH RECURSIVE user_id (id) AS (SELECT ?),

role_type (role_type) AS (SELECT ?),

-- Grab all target ids that are mastered and their children.
mastered (id) AS (
    SELECT roles_roletarget.id
        FROM roles_roletarget
        JOIN roles_role
            ON roles_role.target_id = roles_roletarget.id
        WHERE roles_role.type = 'master'
            AND (
                roles_role.user_id IS NULL
                OR roles_role.user_id = (SELECT user_id.id FROM user_id)
            )

    UNION

    SELECT roles_roletarget.id
        FROM roles_roletarget
        JOIN mastered
            ON roles_roletarget.parent_id = mastered.id
),

with_role (id) AS (
    SELECT mastered.id FROM mastered

    UNION

    SELECT roles_roletarget.id
        FROM roles_roletarget

        JOIN roles_role
            ON roles_role.target_id = roles_roletarget.id
        WHERE roles_role.type = 'editor'
            AND (SELECT role_type.role_type FROM role_type) IN ('viewer', 'editor')
            AND (
                roles_role.user_id IS NULL
                OR roles_role.user_id = (SELECT user_id.id FROM user_id)
            )

    UNION

    SELECT roles_roletarget.id
        FROM roles_roletarget

        JOIN roles_role
            ON roles_role.target_id = roles_roletarget.id
        WHERE roles_role.type = 'viewer'
            AND (SELECT role_type.role_type FROM role_type) = 'viewer'
            AND (
                roles_role.user_id IS NULL
                OR roles_role.user_id = (SELECT user_id.id FROM user_id)
            )
)

SELECT with_role.id FROM with_role
