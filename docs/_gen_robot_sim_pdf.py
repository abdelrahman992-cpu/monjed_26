from fpdf import FPDF
from pathlib import Path
from datetime import date


class Doc(FPDF):
    def header(self):
        if self.page_no() == 1:
            return
        self.set_xy(15, 10)
        self.set_font("Helvetica", "I", 9)
        self.set_text_color(90, 90, 90)
        self.cell(180, 8, "MONJED Robot Simulation Concept Brief", align="L")
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
            f"Page {self.page_no()}/{{nb}}  |  Project planning  |  {date.today().isoformat()}",
            align="C",
        )

    def ensure(self):
        self.set_x(15)

    def h1(self, text):
        self.ensure()
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(20, 60, 50)
        self.multi_cell(180, 9, text)
        self.ln(2)
        self.ensure()

    def h2(self, text):
        self.ln(2)
        self.ensure()
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(30, 80, 65)
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
        self.cell(8, 5.5, "-")
        self.multi_cell(172, 5.5, text)
        self.ensure()


def build():
    pdf = Doc(format="A4")
    pdf.set_margins(15, 20, 15)
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.alias_nb_pages()

    pdf.add_page()
    pdf.set_xy(15, 40)
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(15, 55, 45)
    pdf.multi_cell(180, 12, "MONJED")
    pdf.set_x(15)
    pdf.set_font("Helvetica", "B", 18)
    pdf.multi_cell(180, 10, "Web-Based Robot Simulation")
    pdf.set_x(15)
    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(60, 60, 60)
    pdf.ln(4)
    pdf.set_x(15)
    pdf.multi_cell(
        180,
        7,
        "Concept, Look and Feel, Simulated Workstreams, and Budget Brief",
    )
    pdf.ln(6)
    pdf.set_x(15)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(180, 6, f"Document date: {date.today().isoformat()}")
    pdf.set_x(15)
    pdf.multi_cell(180, 6, "Audience: product, engineering, partners, and funders")
    pdf.set_x(15)
    pdf.multi_cell(180, 6, "Related live systems: API (Render), Frontend (Vercel)")
    pdf.ln(10)
    pdf.set_draw_color(30, 100, 80)
    pdf.set_line_width(0.6)
    y = pdf.get_y()
    pdf.line(15, y, 120, y)
    pdf.ln(10)
    pdf.set_x(15)
    pdf.set_font("Helvetica", "I", 10)
    pdf.multi_cell(
        180,
        6,
        "This brief describes a browser-based robot / drone mission simulator that visualizes how MONJED turns disaster risk into coordinated field action - without requiring physical robots for demos, training, or planning.",
    )

    pdf.add_page()
    pdf.h1("1. Purpose")
    pdf.body(
        "MONJED already connects early warning (flood / earthquake risk), decisions, community help requests, volunteers, and alerts. The robot simulation extends that story into autonomous or semi-autonomous field assets: robots and drones that can be tasked when risk rises or when people request help."
    )
    pdf.body(
        "The simulation is not a full robotics operating system (not Gazebo / ROS replacement). It is a web mission simulator: map, agents, MONJED decisions, and outcomes - designed for demos, training, and scenario planning."
    )
    pdf.h2("Goals")
    pdf.bullet(
        "Show the full loop: hazard -> MONJED risk/decision -> robot task -> status update"
    )
    pdf.bullet("Train operators and partners without hardware")
    pdf.bullet("Support fundraising and partner demos on monjed.vercel.app")
    pdf.bullet(
        "Optionally write mission records into the same admin / ops views as real dispatches"
    )

    pdf.add_page()
    pdf.h1("2. How it will look (UX)")
    pdf.body(
        "Primary surface: a full-page Simulation screen inside the MONJED web app (same visual language as Map / Admin / Volunteer dashboards)."
    )
    pdf.h2("Layout (desktop)")
    pdf.bullet(
        "Left / center (dominant): interactive map (Leaflet or MapLibre) with flood/quake zones, shelters, blocked roads, and robot icons"
    )
    pdf.bullet(
        "Right panel: scenario controls (Play / Pause / Speed), injected hazard, selected robot details, linked help request, mission log"
    )
    pdf.bullet(
        "Top bar: scenario name, risk level badge, connection mode (Live API vs Mock)"
    )
    pdf.bullet(
        "Bottom ticker (optional): alert / SMS / dispatch events for storytelling"
    )
    pdf.h2("Visual language")
    pdf.bullet(
        "Robots: simple markers with status color (idle / en route / on site / returning / failed)"
    )
    pdf.bullet(
        "Paths: animated routes from base to target (no heavy 3D required for v1)"
    )
    pdf.bullet("Hazards: translucent zone overlays consistent with existing risk map")
    pdf.bullet("Missions: cards that mirror assistance / volunteer assignment UI")
    pdf.h2("Mobile")
    pdf.body(
        "Map-first with a bottom sheet for controls. Full multi-robot editing stays desktop-first."
    )
    pdf.h2("v1 look summary")
    pdf.bullet("2D map simulation (not Unity/WebGL required)")
    pdf.bullet("1-3 robots + 1 flood scenario in a known MONJED zone")
    pdf.bullet("Playable in the browser at monjed.vercel.app/simulation")

    pdf.add_page()
    pdf.h1("3. What work it will simulate")
    pdf.body(
        "The simulator models disaster-response field work that MONJED could coordinate - starting with software-defined missions that later can map to real robots."
    )
    pdf.h2("Mission types (v1 focus)")
    pdf.bullet(
        "Reconnaissance: drone/robot surveys a flooded area after a HIGH risk decision"
    )
    pdf.bullet(
        "Last-mile check-in: robot navigates toward a help-request location to confirm status"
    )
    pdf.bullet(
        "Supply drop cue: simulate carrying water / first-aid markers to a shelter waypoint"
    )
    pdf.bullet(
        "Hazard confirmation: validate community report evidence near a risk hotspot"
    )
    pdf.h2("Mission types (later)")
    pdf.bullet("Multi-robot area coverage and battery constraints")
    pdf.bullet("Blocked-route replanning when roads flood")
    pdf.bullet("Failure modes: lost link, low battery, inaccessible target")
    pdf.bullet("Human-in-the-loop: operator approve / reject before dispatch")
    pdf.h2("What is intentionally NOT simulated in v1")
    pdf.bullet("Full physics, LIDAR, SLAM, or motor control")
    pdf.bullet("Real radio / cellular network modeling")
    pdf.bullet("Hardware safety certification")
    pdf.h2("Link to MONJED product work")
    pdf.bullet(
        "Uses same concepts as pipeline risk, assistance requests, volunteer matching, and alerts"
    )
    pdf.bullet(
        "Can call live Render API or a mock decision engine for offline demos"
    )
    pdf.bullet("Can create mission records visible in admin ops views")

    pdf.add_page()
    pdf.h1("4. System design (high level)")
    pdf.h2("Components")
    pdf.bullet("Frontend sim UI (React + map + agent tick loop)")
    pdf.bullet(
        "Simulation engine (client-side first): positions, ETA, status transitions"
    )
    pdf.bullet(
        "MONJED API (optional live): risk/decision/assistance endpoints on Render"
    )
    pdf.bullet(
        "Mission API (new, small): create/list/update simulated missions in MongoDB"
    )
    pdf.bullet(
        "Scenario packs (JSON): map bounds, agents, waypoints, scripted events"
    )
    pdf.h2("Modes")
    pdf.bullet("Mock mode: no backend required - ideal for demos and flaky networks")
    pdf.bullet("Live mode: risk/decision from https://monjed.onrender.com")
    pdf.bullet("Hybrid: live help requests + local robot motion")
    pdf.h2("Suggested API additions (minimal)")
    pdf.bullet(
        "POST /simulation/missions - create a mission from a help request or scenario"
    )
    pdf.bullet("GET /simulation/missions - list missions for admin/sim UI")
    pdf.bullet(
        "PATCH /simulation/missions/{id} - update status (en_route, on_site, completed, failed)"
    )
    pdf.bullet("GET /simulation/scenarios - list packaged scenarios")
    pdf.body(
        "Existing MONJED endpoints (pipeline, assistance, dashboard) remain the source of truth for risk and human help queues. Simulation should not fork that logic."
    )

    pdf.add_page()
    pdf.h1("5. Delivery phases")
    pdf.h2("Phase 0 - Concept lock (1 week)")
    pdf.bullet("Agree scenarios, robot roles, and success demo script")
    pdf.bullet("Wireframe Simulation page")
    pdf.h2("Phase 1 - Web MVP (3-5 weeks)")
    pdf.bullet("Map + 1 scenario + 1-3 agents + play/pause")
    pdf.bullet("Mock decision path + mission log")
    pdf.bullet("Deploy on Vercel next to existing frontend")
    pdf.h2("Phase 2 - API integration (2-3 weeks)")
    pdf.bullet("Mission endpoints + Mongo persistence")
    pdf.bullet("Live mode against Render API")
    pdf.bullet("Admin panel: view simulated missions")
    pdf.h2("Phase 3 - Training / partner polish (2-4 weeks)")
    pdf.bullet("2-3 scenario packs, failure modes, replay")
    pdf.bullet("Optional light 3D or richer animation if needed")
    pdf.h2("Phase 4 - Hardware bridge (optional, separate budget)")
    pdf.bullet("ROS / vendor SDK adapters outside the browser")
    pdf.bullet("Only after web mission model is stable")

    pdf.add_page()
    pdf.h1("6. Budget estimate")
    pdf.body(
        "Figures are planning ranges in USD for a small team. They exclude physical robots unless noted. Local salaries vary by country; use the band that matches your hiring market."
    )
    pdf.h2("A) Software-only web simulation (recommended start)")
    pdf.ensure()
    pdf.set_font("Helvetica", "B", 10)
    pdf.multi_cell(
        180, 6, "Total: about USD 8,000 - 25,000  (or 6-12 person-weeks)"
    )
    pdf.ln(1)
    pdf.bullet("Product / UX design: USD 1,000 - 3,000")
    pdf.bullet("Frontend simulation UI + map agents: USD 4,000 - 12,000")
    pdf.bullet("Backend mission API + Mongo models: USD 1,500 - 5,000")
    pdf.bullet("QA, scenarios, demo polish: USD 1,000 - 3,000")
    pdf.bullet("Contingency (15%): included in upper bound")
    pdf.h2("B) Hosting / API / tools (monthly, ongoing)")
    pdf.bullet("Vercel frontend: USD 0 - 20 (hobby/pro)")
    pdf.bullet(
        "Render backend: USD 0 - 25 (free/starter; paid if always-on needed)"
    )
    pdf.bullet("MongoDB Atlas: USD 0 - 30 (free M0 often enough for sim MVP)")
    pdf.bullet("Domains / monitoring / SMS sandbox extras: USD 0 - 20")
    pdf.bullet("Monthly ops total (MVP): about USD 0 - 100")
    pdf.h2("C) If you buy contractor time (example mix)")
    pdf.bullet(
        "1 fullstack engineer at USD 25-60/hr x 160-240 hrs: USD 4,000 - 14,400"
    )
    pdf.bullet(
        "Part-time designer at USD 20-40/hr x 20-40 hrs: USD 400 - 1,600"
    )
    pdf.bullet("PM / demo scripting: USD 500 - 2,000")

    pdf.add_page()
    pdf.h1("7. Budget - optional extensions")
    pdf.h2("D) Richer 3D web scene (optional)")
    pdf.bullet("Three.js / light WebGL scene: add USD 3,000 - 10,000")
    pdf.bullet(
        "Only if partners require cinematic demos; not required for ops value"
    )
    pdf.h2("E) Physical robot pilot (separate from web sim)")
    pdf.bullet("Education / hobby UGV or drone kit: USD 300 - 3,000 per unit")
    pdf.bullet("Field-ready inspection drone: USD 2,000 - 15,000+")
    pdf.bullet("Ground robot (research/light industrial): USD 5,000 - 50,000+")
    pdf.bullet("Integration engineer (ROS / vendor SDK): USD 5,000 - 30,000")
    pdf.body(
        "Recommendation: do not buy robots until the web mission model and MONJED dispatch UX are proven."
    )
    pdf.h2("F) What you already have (cost avoided)")
    pdf.bullet("MONJED frontend (React/Vite) deployed on Vercel")
    pdf.bullet("MONJED API on Render")
    pdf.bullet("Risk/decision/assistance domain model")
    pdf.bullet("Map concepts already in product")
    pdf.body(
        "Building simulation on top of this stack is cheaper than a greenfield robotics demo."
    )

    pdf.add_page()
    pdf.h1("8. Risks and success criteria")
    pdf.h2("Risks")
    pdf.bullet("Overbuilding physics instead of mission storytelling")
    pdf.bullet("Confusing partners that the browser agents are real robots")
    pdf.bullet(
        "API cold starts (Render free tier) hurting live demos - use Mock mode for shows"
    )
    pdf.bullet(
        "Empty Mongo / missing env on deploy blocking login-related flows"
    )
    pdf.h2("Success criteria for MVP")
    pdf.bullet(
        "A partner can open /simulation and understand MONJED action loop in under 3 minutes"
    )
    pdf.bullet(
        "One scripted flood scenario runs end-to-end without engineer help"
    )
    pdf.bullet("Mission states are visible and explainable")
    pdf.bullet("Works on desktop Chrome/Edge; acceptable on tablet")

    pdf.add_page()
    pdf.h1("9. Recommendation")
    pdf.body(
        "Build a web-based 2D mission simulator first. Keep robots as map agents controlled by a simple state machine, driven by MONJED risk/decision/help-request concepts. Add a thin mission API only when you need persistence and admin visibility."
    )
    pdf.body(
        "Budget to approve for a credible MVP: target USD 10,000-18,000 software (or equivalent internal sprint capacity), plus under USD 100/month hosting. Defer physical robots to a later pilot with a separate hardware budget."
    )
    pdf.h2("Immediate next steps")
    pdf.bullet("Approve Phase 1 scope (1 scenario, 1-3 agents, mock mode)")
    pdf.bullet("Choose owner (frontend-led) and 2 demo scripts")
    pdf.bullet("Add /simulation route on the existing Vercel frontend")
    pdf.bullet(
        "Keep Render API as optional live brain; Mongo mission collection when ready"
    )
    pdf.ln(8)
    pdf.set_x(15)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(80, 80, 80)
    pdf.multi_cell(
        180,
        5,
        "End of brief. This document is a planning artifact for MONJED robot simulation and does not authorize procurement by itself.",
    )

    out = Path(
        r"c:\Users\Adesh\Desktop\MONJED\docs\MONJED_Robot_Simulation_Concept_Budget.pdf"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(out))
    print(f"Wrote {out}")
    print(f"pages {pdf.page_no()}")


if __name__ == "__main__":
    build()
