from fastapi import APIRouter
from fastapi.responses import HTMLResponse


router = APIRouter(tags=["Test UI"])


@router.get("/test-ui", response_class=HTMLResponse)
def test_ui():
    return """
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <title>MONJED Backend Tester</title>

    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1000px;
            margin: 40px auto;
            padding: 20px;
            background: #f4f6f8;
        }

        h1 {
            text-align: center;
            margin-bottom: 10px;
        }

        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }

        .card {
            background: white;
            padding: 25px;
            margin-bottom: 30px;
            border-radius: 14px;
            box-shadow: 0 3px 12px rgba(0, 0, 0, 0.08);
        }

        .buttons {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin: 20px 0;
        }

        button {
            padding: 12px 18px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 15px;
            background: #eeeeee;
        }

        button:hover {
            opacity: 0.8;
        }

        textarea {
            width: 100%;
            min-height: 200px;
            padding: 15px;
            box-sizing: border-box;
            border-radius: 8px;
            border: 1px solid #ccc;
            font-family: monospace;
            font-size: 14px;
        }

        pre {
            background: #111827;
            color: #f9fafb;
            padding: 18px;
            border-radius: 8px;
            min-height: 100px;
            overflow-x: auto;
            white-space: pre-wrap;
        }
    </style>
</head>


<body>

<h1>MONJED Backend Tester</h1>

<p class="subtitle">
    Test hazard risk, community evidence, and operational decisions.
</p>


<!-- ===================================================== -->
<!-- FLOOD -->
<!-- ===================================================== -->

<div class="card">

    <h2>Flood Risk</h2>

    <p>
        Load a predefined flood scenario and execute the Risk Engine.
    </p>

    <div class="buttons">

        <button onclick="loadFlood('low')">
            Low
        </button>

        <button onclick="loadFlood('moderate')">
            Moderate
        </button>

        <button onclick="loadFlood('high')">
            High
        </button>

        <button onclick="loadFlood('critical')">
            Critical
        </button>

        <button onclick="testFlood()">
            Execute Flood Test
        </button>

    </div>

    <textarea id="floodJson"></textarea>

    <h3>Result</h3>

    <pre id="floodResult">Waiting for test...</pre>

</div>


<!-- ===================================================== -->
<!-- EARTHQUAKE -->
<!-- ===================================================== -->

<div class="card">

    <h2>Earthquake Risk</h2>

    <p>
        Load a predefined earthquake scenario and execute the Risk Engine.
    </p>

    <div class="buttons">

        <button onclick="loadEarthquake('low')">
            Low
        </button>

        <button onclick="loadEarthquake('moderate')">
            Moderate
        </button>

        <button onclick="loadEarthquake('high')">
            High
        </button>

        <button onclick="loadEarthquake('critical')">
            Critical
        </button>

        <button onclick="testEarthquake()">
            Execute Earthquake Test
        </button>

    </div>

    <textarea id="earthquakeJson"></textarea>

    <h3>Result</h3>

    <pre id="earthquakeResult">Waiting for test...</pre>

</div>


<!-- ===================================================== -->
<!-- COMMUNITY REPORT -->
<!-- ===================================================== -->

<div class="card">

    <h2>Community Report</h2>

    <p>
        Submit a community report. MONJED will analyze it and store
        it temporarily for the Decision Engine.
    </p>

    <div class="buttons">

        <button onclick="loadCommunityReport('floodedRoad')">
            Flooded Road
        </button>

        <button onclick="loadCommunityReport('risingWater')">
            Rising Water
        </button>

        <button onclick="submitCommunityReport()">
            Submit Report
        </button>

    </div>

    <textarea id="communityReportJson"></textarea>

    <h3>Result</h3>

    <pre id="communityReportResult">Waiting for report...</pre>

</div>


<!-- ===================================================== -->
<!-- AUTOMATIC DECISION -->
<!-- ===================================================== -->

<div class="card">

    <h2>Decision Engine</h2>

    <p>
        Send only the hazard risk. MONJED will automatically retrieve
        recent community reports for the same zone and adjust the
        operational decision when needed.
    </p>

    <div class="buttons">

        <button onclick="loadAutomaticDecision('floodHigh')">
            High Flood Risk
        </button>

        <button onclick="loadAutomaticDecision('earthquakeHigh')">
            High Earthquake Risk
        </button>

        <button onclick="testAutomaticDecision()">
            Evaluate Using Community Reports
        </button>

    </div>

    <textarea id="decisionJson"></textarea>

    <h3>Result</h3>

    <pre id="decisionResult">Waiting for decision...</pre>

</div>

<div class="card">

    <h2>MONJED End-to-End</h2>

    <p>
        Run hazard assessment and automatically use recent
        community evidence to produce the final operational decision.
    </p>

    <div class="buttons">

        <button onclick="loadPipeline('flood')">
            High Flood Scenario
        </button>

        <button onclick="loadPipeline('earthquake')">
            High Earthquake Scenario
        </button>

        <button onclick="runPipeline()">
            Run Full MONJED Assessment
        </button>

    </div>

    <textarea id="pipelineJson"></textarea>

    <h3>Result</h3>

    <pre id="pipelineResult">Waiting for full assessment...</pre>

</div>

<div class="card">

    <h2>Assistance & Volunteer Matching</h2>

    <p>
        Register a volunteer, create an assistance request,
        then match the request automatically.
    </p>

    <div class="buttons">

        <button onclick="registerTestVolunteer()">
            1. Register Volunteer
        </button>

        <button onclick="createTestAssistance()">
            2. Create Assistance Request
        </button>

        <button onclick="matchTestAssistance()">
            3. Match Volunteer
        </button>

    </div>

    <h3>Result</h3>

    <pre id="assistanceResult">Waiting for test...</pre>

</div>

<script>


// ======================================================
// HELPER
// ======================================================

async function readResponse(response) {

    const result = await response.json();

    if (!response.ok) {
        throw new Error(
            "HTTP " + response.status + "\\n" +
            JSON.stringify(result, null, 2)
        );
    }

    return result;
}


// ======================================================
// FLOOD
// ======================================================

const floodTests = {

    low: {
        zone_id: "suez_01",
        rainfall_1h_mm: 3,
        rainfall_24h_mm: 10,
        previous_rainfall_24h_mm: 8,
        community_reports: 0,
        data_age_minutes: 15
    },

    moderate: {
        zone_id: "suez_01",
        rainfall_1h_mm: 20,
        rainfall_24h_mm: 50,
        previous_rainfall_24h_mm: 35,
        community_reports: 1,
        data_age_minutes: 30
    },

    high: {
        zone_id: "suez_01",
        rainfall_1h_mm: 20,
        rainfall_24h_mm: 70,
        previous_rainfall_24h_mm: 45,
        community_reports: 2,
        data_age_minutes: 20
    },

    critical: {
        zone_id: "suez_01",
        rainfall_1h_mm: 40,
        rainfall_24h_mm: 100,
        previous_rainfall_24h_mm: 60,
        community_reports: 5,
        data_age_minutes: 10
    }
};


function loadFlood(level) {

    document.getElementById("floodJson").value =
        JSON.stringify(
            floodTests[level],
            null,
            2
        );
}


async function testFlood() {

    const resultBox =
        document.getElementById("floodResult");

    resultBox.textContent = "Loading...";

    try {

        const data = JSON.parse(
            document.getElementById("floodJson").value
        );

        const response = await fetch(
            "/risk/flood",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify(data)
            }
        );

        const result =
            await readResponse(response);

        resultBox.textContent =
            JSON.stringify(
                result,
                null,
                2
            );

    }

    catch (error) {

        resultBox.textContent =
            "Error:\\n" + error.message;
    }
}


// ======================================================
// EARTHQUAKE
// ======================================================

const earthquakeTests = {

    low: {
        zone_id: "suez_01",
        magnitude: 3.5,
        depth_km: 50,
        distance_km: 150,
        data_age_minutes: 5,
        source_verified: true
    },

    moderate: {
        zone_id: "suez_01",
        magnitude: 5.2,
        depth_km: 50,
        distance_km: 100,
        data_age_minutes: 5,
        source_verified: true
    },

    high: {
        zone_id: "suez_01",
        magnitude: 6.0,
        depth_km: 20,
        distance_km: 80,
        data_age_minutes: 5,
        source_verified: true
    },

    critical: {
        zone_id: "suez_01",
        magnitude: 7.2,
        depth_km: 10,
        distance_km: 30,
        data_age_minutes: 5,
        source_verified: true
    }
};


function loadEarthquake(level) {

    document.getElementById(
        "earthquakeJson"
    ).value = JSON.stringify(
        earthquakeTests[level],
        null,
        2
    );
}


async function testEarthquake() {

    const resultBox =
        document.getElementById(
            "earthquakeResult"
        );

    resultBox.textContent = "Loading...";

    try {

        const data = JSON.parse(
            document.getElementById(
                "earthquakeJson"
            ).value
        );

        const response = await fetch(
            "/risk/earthquake",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify(data)
            }
        );

        const result =
            await readResponse(response);

        resultBox.textContent =
            JSON.stringify(
                result,
                null,
                2
            );

    }

    catch (error) {

        resultBox.textContent =
            "Error:\\n" + error.message;
    }
}


// ======================================================
// COMMUNITY REPORTS
// ======================================================

const communityReportTests = {

    floodedRoad: {
        report_text:
            "The main road is blocked because flood water is rising rapidly.",
        zone_id: "suez_01",
        location: "Suez"
    },

    risingWater: {
        report_text:
            "Water level is rising quickly near houses in the area.",
        zone_id: "suez_01",
        location: "Suez"
    }
};


function loadCommunityReport(type) {

    document.getElementById(
        "communityReportJson"
    ).value = JSON.stringify(
        communityReportTests[type],
        null,
        2
    );
}


async function submitCommunityReport() {

    const resultBox =
        document.getElementById(
            "communityReportResult"
        );

    resultBox.textContent =
        "Analyzing and storing report...";

    try {

        const data = JSON.parse(
            document.getElementById(
                "communityReportJson"
            ).value
        );

        const response = await fetch(
            "/api/community-reports/submit",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify(data)
            }
        );

        const result =
            await readResponse(response);

        resultBox.textContent =
            JSON.stringify(
                result,
                null,
                2
            );

    }

    catch (error) {

        resultBox.textContent =
            "Error:\\n" + error.message;
    }
}


// ======================================================
// AUTOMATIC DECISION ENGINE
// ======================================================

const automaticDecisionTests = {

    floodHigh: {
        hazard: "flood",
        zone_id: "suez_01",
        risk_score: 60,
        risk_level: "high",
        confidence: 0.90
    },

    earthquakeHigh: {
        hazard: "earthquake",
        zone_id: "suez_01",
        risk_score: 65,
        risk_level: "high",
        confidence: 0.90
    }
};


function loadAutomaticDecision(type) {

    document.getElementById(
        "decisionJson"
    ).value = JSON.stringify(
        automaticDecisionTests[type],
        null,
        2
    );
}


async function testAutomaticDecision() {

    const resultBox =
        document.getElementById(
            "decisionResult"
        );

    resultBox.textContent =
        "Loading recent community evidence and evaluating decision...";

    try {

        const data = JSON.parse(
            document.getElementById(
                "decisionJson"
            ).value
        );

        const response = await fetch(
            "/decision/from-risk",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify(data)
            }
        );

        const result =
            await readResponse(response);

        resultBox.textContent =
            JSON.stringify(
                result,
                null,
                2
            );

    }

    catch (error) {

        resultBox.textContent =
            "Error:\\n" + error.message;
    }
}


// ======================================================
// DEFAULT VALUES
// ======================================================

loadFlood("low");
loadEarthquake("low");
loadCommunityReport("floodedRoad");
loadAutomaticDecision("floodHigh");

const pipelineTests = {

    flood: {
        endpoint: "/pipeline/flood",

        data: {
            zone_id: "suez_01",
            rainfall_1h_mm: 20,
            rainfall_24h_mm: 70,
            previous_rainfall_24h_mm: 45,
            community_reports: 0,
            data_age_minutes: 20
        }
    },

    earthquake: {
        endpoint: "/pipeline/earthquake",

        data: {
            zone_id: "suez_01",
            magnitude: 6.0,
            depth_km: 20,
            distance_km: 80,
            data_age_minutes: 5,
            source_verified: true
        }
    }
};


let currentPipelineEndpoint =
    "/pipeline/flood";


function loadPipeline(type) {

    const test =
        pipelineTests[type];

    currentPipelineEndpoint =
        test.endpoint;

    document.getElementById(
        "pipelineJson"
    ).value = JSON.stringify(
        test.data,
        null,
        2
    );
}


async function runPipeline() {

    const resultBox =
        document.getElementById(
            "pipelineResult"
        );

    resultBox.textContent =
        "Running full MONJED pipeline...";

    try {

        const data = JSON.parse(
            document.getElementById(
                "pipelineJson"
            ).value
        );

        const response = await fetch(
            currentPipelineEndpoint,
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify(data)
            }
        );

        const result =
            await readResponse(response);

        resultBox.textContent =
            JSON.stringify(
                result,
                null,
                2
            );

    }

    catch (error) {

        resultBox.textContent =
            "Error:\\n" + error.message;
    }
}
loadPipeline("flood");

let currentRequestId = null;


async function registerTestVolunteer() {

    const resultBox =
        document.getElementById("assistanceResult");

    resultBox.textContent =
        "Registering volunteer...";

    const data = {
        name: "Test Volunteer",
        zone_id: "suez_01",
        available: true,
        vehicle_type: "car",
        capacity: 3,
        skills: [
            "transportation",
            "mobility_assistance",
            "first_aid"
        ]
    };

    try {

        const response = await fetch(
            "/assistance/volunteers",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(data)
            }
        );

        const result =
            await readResponse(response);

        resultBox.textContent =
            "VOLUNTEER REGISTERED\n\n" +
            JSON.stringify(result, null, 2);

    }

    catch (error) {

        resultBox.textContent =
            "Error:\n" + error.message;
    }
}


async function createTestAssistance() {

    const resultBox =
        document.getElementById("assistanceResult");

    resultBox.textContent =
        "Creating assistance request...";

    const data = {
        zone_id: "suez_01",
        location: "Suez",
        hazard: "flood",
        request_type: "mobility_assistance",
        priority: "high",
        description:
            "A person needs help moving to a safer location."
    };

    try {

        const response = await fetch(
            "/assistance/requests",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(data)
            }
        );

        const result =
            await readResponse(response);

        currentRequestId =
            result.request_id;

        resultBox.textContent =
            "ASSISTANCE REQUEST CREATED\n\n" +
            JSON.stringify(result, null, 2);

    }

    catch (error) {

        resultBox.textContent =
            "Error:\n" + error.message;
    }
}


async function matchTestAssistance() {

    const resultBox =
        document.getElementById("assistanceResult");

    if (!currentRequestId) {

        resultBox.textContent =
            "Create an assistance request first.";

        return;
    }

    resultBox.textContent =
        "Searching for suitable volunteer...";

    try {

        const response = await fetch(
            "/assistance/requests/" +
            currentRequestId +
            "/match",
            {
                method: "POST"
            }
        );

        const result =
            await readResponse(response);

        resultBox.textContent =
            "VOLUNTEER MATCHED\n\n" +
            JSON.stringify(result, null, 2);

    }

    catch (error) {

        resultBox.textContent =
            "Error:\n" + error.message;
    }
}
</script>

</body>

</html>
"""