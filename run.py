import os
import uvicorn
from test import app

if __name__ == "__main__":
    port = int(os.environ["PORT"])  # ← do NOT provide a fallback
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        reload=False,
    )
