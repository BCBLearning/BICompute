#!/usr/bin/env python3
"""
BI-COMPUTE COORDINATOR
Version Railway deployable
"""

import os
from app import app   # réutilise TOUT le backend Flask existant

# --------------------------------------------------
# Railway configuration
# --------------------------------------------------

def main():
    port = int(os.environ.get("PORT", 5000))

    print("🚀 BI-COMPUTE COORDINATOR (Railway)")
    print(f"🌐 Listening on port {port}")

    # IMPORTANT : 0.0.0.0 pour Railway
    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )


if __name__ == "__main__":
    main()