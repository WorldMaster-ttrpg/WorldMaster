{% macro and_user(user_id, vars) %}
    {% if user_id is none %}
    AND roles_role.user_id IS NULL
    {% else %}
    AND (
        roles_role.user_id IS NULL
        {% if user_id is not none %}
        OR roles_role.user_id = {{ user_id|var(vars) }}
        {% endif %}
    )
    {% endif %}
{% endmacro %}
