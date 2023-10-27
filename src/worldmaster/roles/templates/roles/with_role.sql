-- Get all roletarget ids that the user has the given role on.

{% from "macros.sql" import user_condition %}

-- Grab all target ids that are mastered and their children.
WITH RECURSIVE mastered (id) AS (
    SELECT roles_roletarget.id
        FROM roles_roletarget
        JOIN roles_role
            ON roles_role.target_id = roles_roletarget.id
        WHERE roles_role.type = 'master'
            AND {{ user_condition(vars=vars, user=user, table='roles_role') }}

    UNION

    SELECT roles_roletarget.id
        FROM roles_roletarget
        JOIN mastered
            ON roles_roletarget.parent_id = mastered.id
),

typed_mastered (id) AS (
    SELECT mastered.id FROM mastered
        JOIN {{ table }}
            ON {{ table }}.role_target_id = mastered.id
),

with_role (id) AS (
    SELECT typed_mastered.id FROM typed_mastered

    UNION

    SELECT roles_roletarget.id
        FROM roles_roletarget
        JOIN {{ table }}
            ON {{ table }}.role_target_id = roles_roletarget.id
        JOIN roles_role
            ON roles_role.target_id = roles_roletarget.id
        WHERE (
            roles_role.type = 'editor'
            AND {{ role_type|sql_var(vars) }} IN ('viewer', 'editor')
            OR roles_role.type = 'viewer'
            AND {{ role_type|sql_var(vars) }} = 'viewer'
        ) AND {{ user_condition(vars=vars, user=user, table='roles_role') }}
)

SELECT with_role.id FROM with_role
