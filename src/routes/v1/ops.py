"""Blueprint placeholder for $(basename "$file" .py)."""
from flask import Blueprint

blueprint = Blueprint('$(basename "$file" .py)', __name__)

@blueprint.route('/')
def placeholder():
    return {'data': 'placeholder for $(basename "$file" .py)'}
