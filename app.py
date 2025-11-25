from fastapi import FastAPI, Request
from pydantic import BaseModel
from ai_generator import generate_response
from competitor_scrapper import analyze_competitors
from seo_analyser import seo_recommendations
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import uvicorn
import os
import json
from datetime import datetime
from pathlib import Path

app = FastAPI()

# static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
# serve generated static sites
GENERATED_DIR = "generated_sites"
os.makedirs(GENERATED_DIR, exist_ok=True)
app.mount("/generated_sites", StaticFiles(directory=GENERATED_DIR), name="generated_sites")

templates = Jinja2Templates(directory="templates")

# homepage route
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Pydantic model for the AI endpoint (keep existing endpoint)
class ClientRequest(BaseModel):
    industry: str
    style: str
    goals: str
    competitors: list

@app.post("/generate-portfolio-advice")
async def generate_portfolio_advice(data: ClientRequest):
    ai_text = generate_response(data.industry, data.style, data.goals)
    competitor_data = analyze_competitors(data.competitors)
    seo_data = seo_recommendations(data.industry)

    return {
        "copywriting": ai_text,
        "competitor_analysis": competitor_data,
        "seo_tips": seo_data,
        "design_guidelines": [
            "Use responsive design (CSS Grid/Flexbox)",
            "Optimize images for fast loading",
            "Implement accessibility (WCAG standards)"
        ]
    }

# --- NEW: Generate full multi-page site endpoint ---
class FullSiteRequest(BaseModel):
    industry: str
    style: str
    goals: str
    competitors: list = []
    project_descriptions: str = ""
    ai_copy: str
    seo_tips: dict
    design_guidelines: list
    theme: str

def _theme_css(theme_name: str) -> str:
    """Return CSS string for the requested theme. Three themes supported."""
    if theme_name == "minimalistic":
        return """
/* Minimalistic theme */
:root {
  --bg: #f7f3f1;
  --card: #ffffff;
  --accent: #d4a5a5; /* dusty rose */
  --muted: #cdb9b9;
  --text: #222;
  --mono: 'Courier New', monospace;
}
body { background: var(--bg); color: var(--text); font-family: Arial, sans-serif; margin:0; }
.container { max-width:1000px; margin:40px auto; padding:24px; }
.header { display:flex; justify-content:space-between; align-items:center; }
.hero { background:var(--card); padding:32px; border-radius:12px; box-shadow:0 6px 18px rgba(0,0,0,0.06); font-family: var(--mono); }
.section { background: var(--card); margin-top:20px; padding:18px; border-radius:10px; }
.btn { display:inline-block; padding:10px 14px; background:var(--accent); color:white; border-radius:8px; text-decoration:none; }
.skills { display:flex; gap:8px; flex-wrap:wrap; }
.skill { background:var(--muted); padding:6px 10px; border-radius:6px; font-family:var(--mono); }
.footer { margin-top:30px; text-align:center; color:#666; font-size:0.9rem; }
"""
    elif theme_name == "bold":
        return """
/* Bold theme */
:root {
  --bg: #3F27F5;
  --card: #071032;
  --accent: #00c2ff;
  --accent2: #ffd400;
  --text: #ffffff;
  --fancy: 'Impact, fantasy';
}
body { background: linear-gradient(120deg,#071032 0%, #0d1225 100%); color:var(--text); font-family: Arial, sans-serif; margin:0; }
.container { max-width:1100px; margin:40px auto; padding:28px; }
.header { display:flex; justify-content:space-between; align-items:center; }
.hero { background:linear-gradient(90deg,var(--card), #13173a); padding:36px; border-radius:12px; box-shadow:0 10px 30px rgba(0,0,0,0.5); font-family: var(--fancy); }
.section { background: rgba(255,255,255,0.03); margin-top:20px; padding:18px; border-radius:10px; border: 1px solid rgba(255,255,255,0.04); }
.btn { display:inline-block; padding:10px 14px; background:var(--accent); color:#021024; border-radius:8px; font-family: var(--fancy); text-decoration:none; }
.skills { display:flex; gap:10px; flex-wrap:wrap; }
.skill { background:var(--accent2); color:#071032; padding:8px 12px; border-radius:14px; font-weight:bold; }
.footer { margin-top:30px; text-align:center; color:#9aa0c0; font-size:0.9rem; }
"""
    else:  # modern
        return """
/* Modern theme */
:root {
  --bg: #0b1221;
  --card: #0f1724;
  --accent: #5b7cff;
  --muted: #9aa7d6;
  --text: #e6eef8;
  --serif: 'Georgia, serif';
}
body { background: var(--bg); color:var(--text); font-family: Arial, sans-serif; margin:0; }
.container { max-width:1000px; margin:40px auto; padding:24px; }
.header { display:flex; justify-content:space-between; align-items:center; }
.hero { background:linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01)); padding:36px; border-radius:12px; box-shadow:0 6px 18px rgba(0,0,0,0.6); font-family: var(--serif); }
.section { background: var(--card); margin-top:20px; padding:18px; border-radius:10px; }
.btn { display:inline-block; padding:10px 14px; background:var(--accent); color:white; border-radius:8px; text-decoration:none; }
.skills { display:flex; gap:8px; flex-wrap:wrap; }
.skill { background:transparent; border:1px solid var(--muted); color:var(--muted); padding:6px 10px; border-radius:6px; }
.footer { margin-top:30px; text-align:center; color:#93a3d6; font-size:0.9rem; }
"""

def _make_index_html(payload: dict) -> str:
    # payload contains: industry, style, goals, ai_copy, seo_tips, design_guidelines, theme
    industry = payload.get("industry", "")
    style = payload.get("style", "")
    goals = payload.get("goals", "")
    ai_copy = payload.get("ai_copy", "")
    seo = payload.get("seo_tips", {}).get("recommended_keywords", [])
    guidelines = payload.get("design_guidelines", [])
    theme = payload.get("theme", "modern")

    # simple projects placeholders (can be expanded)
    projects_html = """
    <div class="section">
      <h2>Projects</h2>
      <div style="display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:16px;">
        <div style="padding:12px; border-radius:8px; background:rgba(255,255,255,0.03);">
          <h3>Project One</h3>
          <p>Short description of the project, technologies used, role, and impact.</p>
        </div>
        <div style="padding:12px; border-radius:8px; background:rgba(255,255,255,0.03);">
          <h3>Project Two</h3>
          <p>Short description of the project, technologies used, role, and impact.</p>
        </div>
        <div style="padding:12px; border-radius:8px; background:rgba(255,255,255,0.03);">
          <h3>Project Three</h3>
          <p>Short description of the project, technologies used, role, and impact.</p>
        </div>
      </div>
    </div>
    """

    # skills from ai or placeholder
    skills_html = "<div class='skills'>" + "".join([f"<div class='skill'>{s}</div>" for s in (payload.get('skills') or ['Design', 'Frontend', 'UX'])]) + "</div>"

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>{industry} Portfolio - Generated</title>
  <link rel="stylesheet" href="style.css" />
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>{industry} • {style}</h1>
      <nav>
        <a href="index.html">Home</a> |
        <a href="projects.html">Projects</a> |
        <a href="contact.html">Contact</a>
      </nav>
    </div>

    <div class="hero section">
      <h2>Hi — I'm a {industry} professional</h2>
      <p style="white-space:pre-line;">
Welcome to my portfolio — here you can explore my skills, projects, and experience.
</p>

      <a class="btn" href="projects.html">View Projects</a>
    </div>

    <div class="section">
      <h2>About</h2>
      <p>{goals}</p>
    </div>

    <div class="section">
      <h2>Skills</h2>
      {skills_html}
    </div>

    {projects_html}

    <div class="section footer">
      <p>Keywords: {', '.join(seo)}</p>
      <p>Built with AI Portfolio Assistant</p>
    </div>
  </div>
</body>
</html>"""
    return html

def _make_projects_html(payload: dict) -> str:
    ai_copy = payload.get("ai_copy", "")
    industry = payload.get("industry", "")
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Projects - {industry}</title>
  <link rel="stylesheet" href="style.css" />
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>Projects</h1>
      <nav>
        <a href="index.html">Home</a> |
        <a href="projects.html">Projects</a> |
        <a href="contact.html">Contact</a>
      </nav>
    </div>

    <div class="section">
      <h2>Highlighted Projects</h2>
      <div style="display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:16px;">
        <div style="padding:14px; border-radius:8px; background:rgba(255,255,255,0.02);">
          <h3>Project One</h3>
          <p style="white-space:pre-line;">{payload.get("project_descriptions") or "Project details coming soon!"}</p>

        </div>
        <div style="padding:14px; border-radius:8px; background:rgba(255,255,255,0.02);">
          <h3>Project Two</h3>
          <p>Project summary and outcomes.</p>
        </div>
        <div style="padding:14px; border-radius:8px; background:rgba(255,255,255,0.02);">
          <h3>Case Study</h3>
          <p>Another description.</p>
        </div>
      </div>
    </div>

    <div class="section footer">
      <p>Built with AI Portfolio Assistant</p>
    </div>
  </div>
</body>
</html>"""
    return html

def _make_contact_html(payload: dict) -> str:
    industry = payload.get("industry", "")
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Contact - {industry}</title>
  <link rel="stylesheet" href="style.css" />
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>Contact</h1>
      <nav>
        <a href="index.html">Home</a> |
        <a href="projects.html">Projects</a> |
        <a href="contact.html">Contact</a>
      </nav>
    </div>

    <div class="section">
      <h2>Get in touch</h2>
      <form action="mailto:you@example.com" method="post" enctype="text/plain">
        <label>Name</label><br/>
        <input type="text" name="name" style="width:100%; padding:8px; margin-bottom:8px;" /><br/>
        <label>Email</label><br/>
        <input type="email" name="email" style="width:100%; padding:8px; margin-bottom:8px;" /><br/>
        <label>Message</label><br/>
        <textarea name="message" style="width:100%; padding:8px; margin-bottom:8px;"></textarea><br/>
        <button class="btn" type="submit">Send</button>
      </form>
    </div>

    <div class="section footer">
      <p>Built with AI Portfolio Assistant</p>
    </div>
  </div>
</body>
</html>"""
    return html

@app.post("/generate-full-site")
async def generate_full_site(payload: FullSiteRequest):
    # Convert payload to dict
    data = payload.dict()

    # Create a unique output folder
    ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    folder = f"site_{ts}"
    outdir = Path(GENERATED_DIR) / folder
    outdir.mkdir(parents=True, exist_ok=True)

    # Create style.css based on theme
    css = _theme_css(data.get("theme", "modern"))
    (outdir / "style.css").write_text(css, encoding="utf-8")

    # Create index.html, projects.html, contact.html
    (outdir / "index.html").write_text(_make_index_html(data), encoding="utf-8")
    (outdir / "projects.html").write_text(_make_projects_html(data), encoding="utf-8")
    (outdir / "contact.html").write_text(_make_contact_html(data), encoding="utf-8")

    site_url = f"/generated_sites/{folder}/index.html"
    return JSONResponse({"site_url": site_url})

# Run locally with: python app.py
if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
