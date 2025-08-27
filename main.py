import sys

import uvicorn

from src.app import compose_app

try:
    app = compose_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)
except Exception as e:
    print(f"Failed to compose app: {e}", file=sys.stderr)
    sys.exit(1)
