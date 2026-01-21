"""Global script template."""

{% for v in config.get('version_locations', [config.get('script_location')]) %}
# path: ${v}
{% endfor %}

from alembic import op
import sqlalchemy as sa


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
