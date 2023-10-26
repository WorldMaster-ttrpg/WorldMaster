-- Get all roletarget ids that the user has the given role on.

{% from "macros.sql" import and_user %}

-- Grab all target ids that are mastered and their children.
WITH RECURSIVE mastered (id) AS (
    SELECT roles_roletarget.id
        FROM roles_roletarget
        JOIN roles_role
            ON roles_role.target_id = roles_roletarget.id
        WHERE roles_role.type = 'master'
            {{ and_user(vars=vars, user_id=user_id) }}

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
            AND {{ role_type|var(vars) }} IN ('viewer', 'editor')
            {{ and_user(vars=vars, user_id=user_id) }}

    UNION

    SELECT roles_roletarget.id
        FROM roles_roletarget

        JOIN roles_role
            ON roles_role.target_id = roles_roletarget.id
        WHERE roles_role.type = 'viewer'
            AND {{ role_type|var(vars) }} = 'viewer'
            {{ and_user(vars=vars, user_id=user_id) }}
)

SELECT with_role.id FROM with_role
