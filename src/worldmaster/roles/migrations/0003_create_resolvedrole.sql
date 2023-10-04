CREATE VIEW roles_resolvedrole AS

-- All targets mastered by all users.
WITH RECURSIVE mastered_targets (target_id, user_id) AS (

    -- Select all mastered roletargets by all users
    SELECT roles_roletarget.id, roles_role.user_id FROM roles_roletarget
        JOIN roles_role
            ON roles_role.target_id = roles_roletarget.id
        WHERE roles_role.type = 'master'

    UNION ALL

    -- Union with all children of mastered roletargets
    SELECT
        roles_roletarget.id,
        mastered_targets.user_id
    FROM roles_roletarget
        JOIN mastered_targets
            ON roles_roletarget.parent_id = mastered_targets.target_id
),

-- All roles all users have on all targets.
resolvedrole (target_id, user_id, type) AS (
    -- Start with all roles on all role targets
    SELECT
        roles_roletarget.id,
        roles_role.user_id,
        roles_role.type
    FROM roles_roletarget
        JOIN roles_role
            ON roles_role.target_id = roles_roletarget.id

    -- Filter master because we'll get it via the union anyway
    WHERE roles_role.type != 'master'

    UNION ALL

    -- Union with the computed masterships
    SELECT target_id, user_id, 'master' FROM mastered_targets

    UNION

    -- Add 'editor' if the inferred types had 'master'
    SELECT target_id, user_id, 'editor' FROM resolvedrole
        WHERE resolvedrole.type = 'master'

    UNION

    -- Add 'viewer' if the inferred types had 'editor'
    SELECT target_id, user_id, 'viewer' FROM resolvedrole
        WHERE resolvedrole.type = 'editor'
)

-- Need an arbitrary ID to act as the primary key
SELECT (target_id || '.' || user_id || '.' || type) as id, target_id, user_id, type FROM resolvedrole
