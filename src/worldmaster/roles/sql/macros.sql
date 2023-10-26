{% macro user_condition(user, vars, table) %}
    {% if user.id is none %}
    {{table}}.user_id IS NULL
    {% else %}
    (
        {{table}}.user_id IS NULL
        {% if user.id is not none %}
        OR {{table}}.user_id = {{ user.id|var(vars) }}
        {% endif %}
    )
    {% endif %}
{% endmacro %}
