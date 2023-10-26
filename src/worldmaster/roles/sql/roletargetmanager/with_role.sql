-- Get all roletarget ids that the user has the given role on.

-- Grab all target ids that are mastered and their children.
WITH RECURSIVE mastered (id) AS (
    SELECT roles_roletarget.id
        FROM roles_roletarget
        JOIN roles_role
            ON roles_role.target_id = roles_roletarget.id
        WHERE roles_role.type = 'master'
            AND (
                roles_role.user_id IS NULL
                {% if user_id is not none %}
                OR roles_role.user_id = {{ user_id|var(vars) }}
                {% endif %}
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
            AND {{ role_type|var(vars) }} IN ('viewer', 'editor')
            AND (
                roles_role.user_id IS NULL
                {% if user_id is not none %}
                OR roles_role.user_id = {{ user_id|var(vars) }}
                {% endif %}
            )

    UNION

    SELECT roles_roletarget.id
        FROM roles_roletarget

        JOIN roles_role
            ON roles_role.target_id = roles_roletarget.id
        WHERE roles_role.type = 'viewer'
            AND {{ role_type|var(vars) }} = 'viewer'
            AND (
                roles_role.user_id IS NULL
                {% if user_id is not none %}
                OR roles_role.user_id = {{ user_id|var(vars) }}
                {% endif %}
            )
)

SELECT with_role.id FROM with_role
