"""
Convenience launcher:  python run_api.py
"""

import os

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.api.server:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("APP_ENV", "development") != "production",
    )
