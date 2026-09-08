"""
Generate MONJED AI Rescue Robot Digital Twin - implementation report PDF.
Run:  python docs/_gen_rescue_robot_report_pdf.py
Output: docs/MONJED_AI_Rescue_Robot_Digital_Twin_Report.pdf
"""

from datetime import date
from pathlib import Path

from fpdf import FPDF

OUT = Path(__file__).resolve().parent / "MONJED_AI_Rescue_Robot_Digital_Twin_Report.pdf"


class Doc(FPDF):
    def header(self):
        if self.page_no() == 1:
            return
        self.set_xy(15, 10)
        self.set_font("Helvetica", "I", 9)
        self.set_text_color(90, 90, 90)
        self.cell(
            180,
            8,
            "MONJED AI Rescue Robot Digital Twin - Implementation Report",
            align="L",
        )
        self.set_draw_color(200, 200, 200)
        self.line(15, 18, 195, 18)
        self.set_xy(15, 22)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(
            0,
            10,
            f"Page {self.page_no()}/{{nb}}  |  Project report  |  {date.today().isoformat()}",
            align="C",
        )

    def ensure(self):
        self.set_x(15)

    def h1(self, text):
        self.ensure()
        self.set_font("Helvetica", "B", 15)
        self.set_text_color(15, 55, 90)
        self.multi_cell(180, 8, text)
        self.ln(2)
        self.ensure()

    def h2(self, text):
        self.ln(2)
        self.ensure()
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(25, 70, 110)
        self.multi_cell(180, 7, text)
        self.ln(1)
        self.ensure()

    def body(self, text):
        self.ensure()
        self.set_font("Helvetica", "", 10)
        self.set_text_color(30, 30, 30)
        self.multi_cell(180, 5.5, text)
        self.ln(1)
        self.ensure()

    def bullet(self, text):
        self.ensure()
        self.set_font("Helvetica", "", 10)
        self.set_text_color(30, 30, 30)
        self.cell(6, 5.5, "-")
        self.multi_cell(174, 5.5, text)
        self.ensure()

    def code(self, text):
        self.ensure()
        self.set_font("Courier", "", 8.5)
        self.set_text_color(40, 40, 40)
        self.set_fill_color(240, 244, 248)
        self.multi_cell(180, 4.5, text, fill=True)
        self.ln(1)
        self.ensure()


def build():
    pdf = Doc(format="A4")
    pdf.set_margins(15, 20, 15)
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.alias_nb_pages()

    # Cover
    pdf.add_page()
    pdf.set_xy(15, 36)
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(15, 55, 90)
    pdf.multi_cell(180, 11, "MONJED")
    pdf.set_x(15)
    pdf.set_font("Helvetica", "B", 16)
    pdf.multi_cell(180, 9, "AI Rescue Robot Digital Twin")
    pdf.set_x(15)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(40, 90, 130)
    pdf.multi_cell(180, 8, "Implementation Report")
    pdf.ln(4)
    pdf.set_x(15)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(60, 60, 60)
    pdf.multi_cell(
        180,
        6,
        "What was built, how it works, where it lives in the codebase, "
        "and how it prepares MONJED for real Arduino/ESP32 hardware.",
    )
    pdf.ln(6)
    pdf.set_x(15)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(180, 6, f"Document date: {date.today().isoformat()}")
    pdf.set_x(15)
    pdf.multi_cell(
        180, 6, "Product: MONJED multi-hazard early warning and action (Africa)"
    )
    pdf.set_x(15)
    pdf.multi_cell(180, 6, "Feature route: /admin/rescue-robot  (admin only)")
    pdf.set_x(15)
    pdf.multi_cell(
        180, 6, "API prefix: /rescue-robot  (separate from Leaflet /simulation)"
    )
    pdf.ln(8)
    pdf.set_draw_color(30, 100, 140)
    pdf.set_line_width(0.7)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(8)
    pdf.set_x(15)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(15, 55, 90)
    pdf.multi_cell(180, 6, "Contents")
    for item in [
        "1. Executive summary",
        "2. Relationship to the older map simulation",
        "3. Product goal and design principles",
        "4. End-to-end demo workflow",
        "5. Architecture (sim-to-hardware)",
        "6. Robot model, sensors, and arm",
        "7. 3D environment and disaster scenarios",
        "8. Navigation and autonomous mission controller",
        "9. MONJED command-center UI",
        "10. Backend API and telemetry contract",
        "11. Code map (folders and key files)",
        "12. How to run and demonstrate",
        "13. Future hardware integration path",
        "14. What is intentionally out of scope (V1)",
    ]:
        pdf.set_x(15)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(40, 40, 40)
        pdf.multi_cell(180, 5.5, item)

    # 1
    pdf.add_page()
    pdf.h1("1. Executive summary")
    pdf.body(
        "We built a new interactive MONJED feature: an AI Rescue Robot Digital Twin. "
        "It is a real software simulation (state, sensors, missions, battery, obstacles, "
        "victims, event log), not a fake point-to-point animation. The twin is designed so "
        "simulated hardware drivers can later be replaced by ESP32/Arduino/ROS drivers "
        "without rebuilding the MONJED mission UI."
    )
    pdf.body("Delivered in this implementation:")
    pdf.bullet(
        "Admin command center at /admin/rescue-robot with 3D viewport and ops panels."
    )
    pdf.bullet(
        "Robot MONJED-R01: differential-drive base, ultrasonics, temp, gas, IMU, "
        "battery, GPS, camera, robotic arm and gripper."
    )
    pdf.bullet(
        "Scenarios: Flood, Earthquake, Fire - each with different hazards and behaviors."
    )
    pdf.bullet(
        "Autonomous mission controller: create, dispatch, navigate, avoid, inspect, "
        "detect victim, return, complete."
    )
    pdf.bullet(
        "Demo Mode that runs the full flood response story for judges and partners."
    )
    pdf.bullet(
        "REST API under /rescue-robot that mirrors missions and telemetry into MONJED."
    )
    pdf.bullet(
        "Clear hardware abstraction interfaces (Motor, Sensor, Arm, Telemetry, Mission)."
    )

    pdf.h1("2. Relationship to the older map simulation")
    pdf.body(
        "MONJED already had a Leaflet-based fleet ops tool at /admin/simulation "
        "(roads, drones/rovers, help-queue dispatch). That tool remains unchanged."
    )
    pdf.body("The new digital twin is intentionally separate:")
    pdf.bullet('Route: /admin/rescue-robot (Admin sidebar: "AI rescue robot").')
    pdf.bullet("API: /rescue-robot/* - not /simulation/*.")
    pdf.bullet("Frontend folders: components/rescueRobot and lib/rescueRobot.")
    pdf.bullet(
        "Purpose: 3D digital twin and sensor/arm mission loop for a future physical robot."
    )
    pdf.body(
        "Keeping them separate avoids mixing 2D live-ops GPS dispatch with the "
        "hardware-oriented twin, and lets each evolve independently."
    )

    pdf.h1("3. Product goal and design principles")
    pdf.body(
        "MONJED's loop is: Sense risk -> understand -> decide -> alert -> deploy help "
        "-> track response. The rescue robot extends deploy/track with a robotic responder."
    )
    pdf.h2("Principles used while building")
    pdf.bullet(
        "Real state machine - idle, navigating, avoiding, inspecting, victim detected, "
        "returning, completed, emergency, failed, low battery."
    )
    pdf.bullet(
        "Sensors drive behavior - close ultrasonics trigger avoidance; fire temp/gas can "
        "force emergency retreat; low battery forces return-to-base."
    )
    pdf.bullet(
        "Stable telemetry JSON - same shape for sim today and hardware later."
    )
    pdf.bullet(
        "Start small, make it work - engine + 3D + missions first; then arm, victims, "
        "scenarios, demo."
    )
    pdf.bullet(
        "Integrate into MONJED - React admin auth, Tailwind tokens, FastAPI router "
        "registration, existing api.js helpers."
    )

    # 4
    pdf.add_page()
    pdf.h1("4. End-to-end demo workflow")
    pdf.body(
        "Demo Mode (button in the command center) runs this story automatically:"
    )
    for step in [
        "FLOOD DETECTED - high risk sector loaded in 3D",
        "Affected area identified (Sector A / Building 04)",
        "Mission created (Search and Rescue, HIGH priority)",
        "MONJED-R01 dispatched from safe-zone base",
        "Robot navigates with A* path around flooded / blocked cells",
        "Obstacle detected -> route recalculated",
        "Sensors continuously publish temp, gas, distances, battery, pose",
        "Possible victim detected near Building 04 -> alert + coordinates to MONJED",
        "Inspection completed at target",
        "Robot returns to base",
        "Mission completed - event log shows the full timeline",
    ]:
        pdf.bullet(step)
    pdf.body(
        "Operators can also manually Create Mission, Dispatch, Pause, Resume, "
        "Return to Base, or Stop. Scenario selector switches Flood / Earthquake / Fire."
    )

    pdf.h1("5. Architecture (sim-to-hardware)")
    pdf.body("Communication flow implemented:")
    pdf.code(
        "MONJED Command UI\n"
        "   |\n"
        "Mission Controller (engine.js)\n"
        "   |\n"
        "SimulatedMotors / SimulatedSensors / SimulatedArm\n"
        "   |\n"
        "3D World + Physics tick (requestAnimationFrame)\n"
        "   |\n"
        "Telemetry JSON mirror --> POST /rescue-robot/telemetry\n"
        "   |\n"
        "MONJED mission/event store (backend)"
    )
    pdf.body("Abstraction modules (frontend/src/lib/rescueRobot/interfaces.js):")
    pdf.bullet("MotorInterface - differential-drive velocity commands and pose.")
    pdf.bullet(
        "SensorInterface - ultrasonic, temperature, gas, IMU, battery, GPS, camera."
    )
    pdf.bullet(
        "ArmInterface - MOVE_ARM, OPEN/CLOSE_GRIPPER, PICK/DROP_OBJECT, RESET_ARM."
    )
    pdf.bullet(
        "TelemetryInterface / MissionInterface - publish and lifecycle contracts."
    )
    pdf.body(
        "Today: Simulated* classes implement these. Later: Physical* drivers "
        "(serial/MAVLink/ESP32 gateway) implement the same methods. "
        "MissionController and UI stay the same."
    )

    # 6
    pdf.add_page()
    pdf.h1("6. Robot model, sensors, and arm")
    pdf.h2("Robot MONJED-R01")
    pdf.bullet("Wheeled differential-drive base (four visible wheels in 3D).")
    pdf.bullet("Status beacon color changes with mission state.")
    pdf.bullet("Camera mast representation and front ultrasonic pod.")
    pdf.bullet("Battery strip on the chassis (visual and numeric telemetry).")
    pdf.h2("Simulated sensors (live every tick)")
    pdf.bullet(
        "Ultrasonic: front / left / right distances (ray checks vs world obstacles)."
    )
    pdf.bullet(
        "Temperature: ambient + fire-zone boost; critical levels trigger emergency "
        "in Fire scenario."
    )
    pdf.bullet(
        "Gas level: NORMAL / ELEVATED / HIGH / CRITICAL from proximity to fire zones."
    )
    pdf.bullet("IMU: roll/pitch/yaw and moving flag.")
    pdf.bullet(
        "Battery: drains while operating; critical battery auto return-to-base."
    )
    pdf.bullet("GPS/pose: XZ metres on the twin ground plane.")
    pdf.h2("Robotic arm")
    pdf.bullet("Joints: base, shoulder, elbow, wrist, gripper.")
    pdf.bullet("Commands supported in SimulatedArm.")
    pdf.bullet(
        "Earthquake scenario: approach movable debris, PICK_OBJECT, relocate aside, "
        "replan path."
    )

    pdf.h1("7. 3D environment and disaster scenarios")
    pdf.body(
        "The first environment is a lightweight flooded urban/community area "
        "(roads, buildings, houses, trees, walls, debris, flood pools, safe zone, victims)."
    )
    pdf.h2("Flood")
    pdf.bullet("Impassable flooded zones; robot must path around them.")
    pdf.bullet("Obstacles force avoidance and recalculation.")
    pdf.bullet("Victim near Building 04 for search-and-rescue demo.")
    pdf.h2("Earthquake")
    pdf.bullet("Damaged buildings and debris field.")
    pdf.bullet("Movable debris can be cleared with the arm.")
    pdf.h2("Fire")
    pdf.bullet("Fire zones raise temperature and gas.")
    pdf.bullet(
        "Above safe thresholds -> EMERGENCY status, retreat to base, event logged to MONJED."
    )
    pdf.body(
        "Rendering uses Three.js (vanilla, browser WebGL) with drag-orbit camera. "
        "React Three Fiber was attempted but dropped due to install/peer issues; "
        "vanilla Three keeps the dependency simple (package: three)."
    )

    # 8
    pdf.add_page()
    pdf.h1("8. Navigation and autonomous mission controller")
    pdf.h2("Navigation")
    pdf.bullet(
        "Grid A* planner (navigation.js) treats floods/walls/debris as blocked cells."
    )
    pdf.bullet("Path simplified with line-of-sight shortcuts when clear.")
    pdf.bullet(
        "While driving: follow waypoints; if ultrasonic/front collision risk -> "
        "AVOIDING, rotate, replan (throttled)."
    )
    pdf.bullet(
        "Near destination: treat goal proximity as arrival so the robot can inspect "
        "instead of looping on building walls."
    )
    pdf.h2("Mission phases")
    pdf.bullet("created -> dispatched/en_route -> inspecting -> returning -> completed")
    pdf.bullet("Also: paused, failed/stopped, emergency, low-battery return.")
    pdf.body(
        "The controller is rule/state-based (reliable for V1). Structure allows "
        "swapping in a richer planner later without rewriting the UI."
    )

    pdf.h1("9. MONJED command-center UI")
    pdf.body(
        "Full-page admin console (not AppLayout), matching MONJED ops styling:"
    )
    pdf.bullet("Left: large 3D digital twin viewport.")
    pdf.bullet(
        "Right rail: Hazard/Risk, Robot status, Live telemetry, Create mission, "
        "Controls, Victim alert, Event log."
    )
    pdf.bullet(
        "Working controls: Create Mission, Dispatch, Pause, Resume, Return to Base, "
        "Stop, Demo Mode, Scenario switch."
    )
    pdf.bullet(
        'Victim panel: location, confidence, coordinates, "transmitted to MONJED".'
    )
    pdf.bullet(
        "Theme toggle and link back to Admin; note pointing to legacy /admin/simulation."
    )

    pdf.h1("10. Backend API and telemetry contract")
    pdf.body("FastAPI router registered in backend/app/main.py:")
    pdf.code(
        "GET  /rescue-robot/health\n"
        "POST /rescue-robot/missions\n"
        "GET  /rescue-robot/missions\n"
        "GET  /rescue-robot/missions/{id}\n"
        "POST /rescue-robot/telemetry\n"
        "GET  /rescue-robot/telemetry/latest\n"
        "GET  /rescue-robot/events"
    )
    pdf.body("Example telemetry shape mirrored from the twin:")
    pdf.code(
        "{\n"
        '  "robotId": "MONJED-R01",\n'
        '  "status": "INSPECTING",\n'
        '  "battery": 76,\n'
        '  "temperature": 34,\n'
        '  "gasLevel": "NORMAL",\n'
        '  "position": { "x": 14.2, "y": 8.7 },\n'
        '  "missionId": "MISSION-001",\n'
        '  "ultrasonic": { "front": 1.8, "left": 3.2, "right": 0.9 },\n'
        '  "warnings": ["OBSTACLE_AHEAD"]\n'
        "}"
    )
    pdf.body(
        "Store is in-memory for the twin mirror (fast, demo-friendly). "
        "The real-time tick loop stays in the browser for smooth 3D; the API keeps "
        "MONJED informed."
    )

    # 11
    pdf.add_page()
    pdf.h1("11. Code map (folders and key files)")
    pdf.h2("Frontend")
    pdf.bullet("pages/RescueRobot.jsx - page shell, engine subscribe/tick, API mirror.")
    pdf.bullet(
        "components/rescueRobot/RescueScene.jsx - Three.js scene, robot, world, path."
    )
    pdf.bullet("components/rescueRobot/CommandCenter.jsx - ops panels and controls.")
    pdf.bullet("lib/rescueRobot/engine.js - mission controller and simulation tick.")
    pdf.bullet("lib/rescueRobot/world.js - Flood/Earthquake/Fire scenario definitions.")
    pdf.bullet("lib/rescueRobot/navigation.js - A* and avoidance helpers.")
    pdf.bullet(
        "lib/rescueRobot/simulatedHardware.js - Simulated motors/sensors/arm."
    )
    pdf.bullet("lib/rescueRobot/interfaces.js - hardware contracts.")
    pdf.bullet('App.jsx route + Admin.jsx nav item "AI rescue robot".')
    pdf.bullet(
        "lib/api.js - createRescueMissionRemote, mirrorRescueTelemetry, etc."
    )
    pdf.h2("Backend")
    pdf.bullet("routers/rescue_robot.py - HTTP endpoints.")
    pdf.bullet("schemas/rescue_robot.py - Pydantic models.")
    pdf.bullet("services/rescue_robot_store.py - mission/telemetry/event store.")
    pdf.h2("Dependency")
    pdf.bullet("frontend package.json: three ^0.175.0 (vanilla Three.js).")

    pdf.h1("12. How to run and demonstrate")
    pdf.bullet("Start backend (FastAPI) with existing MONJED setup.")
    pdf.bullet("In frontend/: npm install (ensures three), then npm run dev.")
    pdf.bullet("Sign in as admin -> Admin -> AI rescue robot.")
    pdf.bullet(
        "Click Demo Mode, or manually pick scenario -> Create Mission -> Dispatch Robot."
    )
    pdf.bullet(
        "Watch 3D path, telemetry, event log, and victim alert; wait for return-to-base "
        "completion."
    )
    pdf.body(
        "Verified in development: production Vite build succeeds; automated engine tick "
        "completes flood demo with obstacle + victim + mission completed."
    )

    pdf.h1("13. Future hardware integration path")
    pdf.body("Recommended next steps when buying hardware:")
    pdf.bullet(
        "Keep TelemetryFrame / POST /rescue-robot/telemetry unchanged."
    )
    pdf.bullet(
        "Implement PhysicalMotors, PhysicalSensors, PhysicalArm talking to ESP32/Arduino."
    )
    pdf.bullet(
        "Gateway service (serial/Wi-Fi/LTE) publishes the same JSON MONJED already accepts."
    )
    pdf.bullet(
        "Optional: ROS 2 / Gazebo later for higher-fidelity physics - twin UI/API still applies."
    )
    pdf.bullet(
        "Bill-of-materials can reuse component SKU ideas (FC, GPS, IMU, LiDAR/ultrasonic, "
        "camera, motors, arm servos)."
    )

    pdf.h1("14. What is intentionally out of scope (V1)")
    pdf.bullet("Not a replacement for the Leaflet live help-queue fleet map.")
    pdf.bullet("Not industrial physics or Gazebo-level fidelity.")
    pdf.bullet(
        "Not JWT-locked backend routes (matches current MONJED API pattern; admin gate "
        "is frontend)."
    )
    pdf.bullet("Not React Three Fiber (install issues); vanilla Three.js instead.")
    pdf.bullet(
        "Telemetry mirror is best-effort if API is offline - local twin still runs."
    )

    pdf.ln(6)
    pdf.h2("Closing")
    pdf.body(
        "MONJED now has a working robotic-response digital twin that demonstrates the full "
        "hazard -> mission -> robot action -> sensor data -> MONJED update -> completion "
        "loop, architected for a clean swap from simulated hardware to physical "
        "rescue-robot hardware."
    )
    pdf.body("Primary entry for demos: /admin/rescue-robot -> Demo Mode.")

    pdf.output(str(OUT))
    return OUT


if __name__ == "__main__":
    path = build()
    print(f"Wrote {path}")
