from backend.app.services.risk_service import (
    run_risk_assessment,
)

import json


result = run_risk_assessment(
    hazard="flood",
    country="Kenya",
)


print(
    json.dumps(
        result,
        indent=2,
        ensure_ascii=False,
    )
)