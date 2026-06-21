# SDTS Website — Claude Code Instructions

## Repository
- **GitHub**: https://github.com/sdtsweb/SDTS
- **Local path**: C:\Users\sangeetha\Documents\SDTS
- **Default branch**: `main`
- **Tech stack**: Static HTML/CSS/JS (Selecao Bootstrap template)
- **Update frequency**: 6–8 times per year

## Change Workflow (REQUIRED — follow every time without being asked)

When the user requests any change to this website, ALWAYS:

### 1. Pull latest main
```powershell
git checkout main
git pull origin main
```

### 2. Create a branch
```powershell
git checkout -b update/<short-description>
```
Branch naming — all lowercase, hyphens, no spaces:
- `update/homepage-hero-text`
- `update/nav-menu-links`
- `update/add-volunteer-form-field`
- `update/bts-section-content`

### 3. Make the requested changes
Edit the relevant HTML/CSS/JS files. The main pages are:
- `index.html` — Homepage
- `TamilLibrary.html`, `talent-search.html`, `volunteer.html` — Content pages
- `sdts-connect.html`, `sponsor-an-event.html`, `previous-teams.html` — Event/info pages
- `privacy-policy.html` — Policy
- `bts/` — Bharathiyar Tamil School sub-site
- `assets/` — Images, CSS, JS vendor files

### 4. Validate locally
Start the Python preview server:
```powershell
cd C:\Users\sangeetha\Documents\SDTS
python -m http.server 8080
```
Open http://localhost:8080 in a browser and verify the change looks correct.
Stop the server with Ctrl+C when done reviewing.

### 5. Commit
```powershell
git add -A
git commit -m "Short description of what changed and why"
```

### 6. Push to origin
```powershell
git push origin <branch-name>
```

### 7. Report back to the user
Always end by telling the user:
- Which branch was pushed
- The GitHub compare/PR URL: `https://github.com/sdtsweb/SDTS/compare/<branch-name>`
- What to do next: review the diff on GitHub, then merge to main

## Rules
- NEVER commit directly to `main`
- Each change request = one branch = one PR
- Commit messages must describe what changed (not just "update")
- This is a static site — no build step needed, changes are deploy-on-merge

## Git Identity (configured globally)
- Email: wkeynoping@gmail.com
