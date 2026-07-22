#!/usr/bin/env python3
import html
import json
import os
import re
from urllib.parse import quote, unquote
from datetime import datetime

BASE_URL = "https://medmachina.github.io"
PUBLIC_DIR = os.path.join(os.path.dirname(__file__), "..", "public")
DIST_DIR = os.path.join(os.path.dirname(__file__), "..", "dist")

def load_json(filename):
    filepath = os.path.join(PUBLIC_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def generate_robots_txt():
    content = f"""User-agent: *
Allow: /

Sitemap: {BASE_URL}/sitemap.xml
"""
    robots_path = os.path.join(PUBLIC_DIR, "robots.txt")
    with open(robots_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Generated {robots_path}")

    if os.path.exists(DIST_DIR):
        dist_robots = os.path.join(DIST_DIR, "robots.txt")
        with open(dist_robots, "w", encoding="utf-8") as f:
            f.write(content)

def generate_sitemap(robots_data, companies_data):
    today = datetime.now().strftime("%Y-%m-%d")

    urls = [
        {"loc": f"{BASE_URL}/", "priority": "1.0", "changefreq": "daily"},
        {"loc": f"{BASE_URL}/companies", "priority": "0.8", "changefreq": "weekly"},
        {"loc": f"{BASE_URL}/contribute", "priority": "0.5", "changefreq": "monthly"},
        {"loc": f"{BASE_URL}/links", "priority": "0.5", "changefreq": "monthly"},
    ]

    for robot in robots_data:
        if "id" in robot:
            urls.append({
                "loc": f"{BASE_URL}/robot/{robot['id']}",
                "priority": "0.9",
                "changefreq": "weekly"
            })

    for company in companies_data:
        if "name" in company:
            encoded_name = quote(company['name'])
            urls.append({
                "loc": f"{BASE_URL}/company/{encoded_name}",
                "priority": "0.8",
                "changefreq": "weekly"
            })

    xml_entries = []
    for u in urls:
        escaped_loc = html.escape(u['loc'], quote=True)
        xml_entries.append(f"""  <url>
    <loc>{escaped_loc}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>{u['changefreq']}</changefreq>
    <priority>{u['priority']}</priority>
  </url>""")

    entries_str = "\n".join(xml_entries)
    sitemap_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{entries_str}
</urlset>
"""
    sitemap_path = os.path.join(PUBLIC_DIR, "sitemap.xml")
    with open(sitemap_path, "w", encoding="utf-8") as f:
        f.write(sitemap_content)
    print(f"Generated {sitemap_path} ({len(urls)} URLs)")

    if os.path.exists(DIST_DIR):
        dist_sitemap = os.path.join(DIST_DIR, "sitemap.xml")
        with open(dist_sitemap, "w", encoding="utf-8") as f:
            f.write(sitemap_content)

def build_prerender_html(template, title, description, canonical_url, image_url, json_ld, prerender_body):
    escaped_title = html.escape(title)
    escaped_description = html.escape(description, quote=True)
    escaped_canonical_url = html.escape(canonical_url, quote=True)

    html_out = template

    # Replace <title>
    html_out = re.sub(r'<title>.*?</title>', lambda m: f'<title>{escaped_title}</title>', html_out)

    # Replace or add meta description
    if '<meta name="description"' in html_out:
        html_out = re.sub(r'<meta name="description"[^>]*>', lambda m: f'<meta name="description" content="{escaped_description}" />', html_out)
    else:
        html_out = html_out.replace('</head>', f'  <meta name="description" content="{escaped_description}" />\n  </head>')

    # Replace or add canonical
    if '<link rel="canonical"' in html_out:
        html_out = re.sub(r'<link rel="canonical"[^>]*>', lambda m: f'<link rel="canonical" href="{escaped_canonical_url}" />', html_out)
    else:
        html_out = html_out.replace('</head>', f'  <link rel="canonical" href="{escaped_canonical_url}" />\n  </head>')

    # Open Graph replacement
    html_out = re.sub(r'<meta property="og:title"[^>]*>', lambda m: f'<meta property="og:title" content="{escaped_title}" />', html_out)
    html_out = re.sub(r'<meta property="og:description"[^>]*>', lambda m: f'<meta property="og:description" content="{escaped_description}" />', html_out)
    html_out = re.sub(r'<meta property="og:url"[^>]*>', lambda m: f'<meta property="og:url" content="{escaped_canonical_url}" />', html_out)
    if image_url:
        full_image = image_url if image_url.startswith('http') else f"{BASE_URL}{image_url}"
        escaped_image_url = html.escape(full_image, quote=True)
        html_out = re.sub(r'<meta property="og:image"[^>]*>', lambda m: f'<meta property="og:image" content="{escaped_image_url}" />', html_out)

    # JSON-LD injection
    if json_ld:
        json_str = json.dumps(json_ld, indent=2)
        script_tag = f'<script type="application/ld+json" id="seo-jsonld">\n{json_str}\n</script>'
        if '<script type="application/ld+json"' in html_out:
            html_out = re.sub(r'<script type="application/ld\+json"[^>]*>.*?</script>', lambda m: script_tag, html_out, flags=re.DOTALL)
        else:
            html_out = html_out.replace('</head>', f'  {script_tag}\n  </head>')

    # Ingest pre-rendered HTML into <div id="app"></div>
    if prerender_body:
        html_out = html_out.replace('<div id="app"></div>', f'<div id="app">{prerender_body}</div>')

    return html_out

def prerender_dist(robots_data, companies_data):
    index_path = os.path.join(DIST_DIR, "index.html")
    if not os.path.exists(index_path):
        print(f"Skipping prerender: {index_path} not found.")
        return

    with open(index_path, "r", encoding="utf-8") as f:
        template = f.read()

    # Pre-render robots pages
    robot_company_map = {}
    for company in companies_data:
        c_name = company.get("name", "")
        for r_id in company.get("robots", []):
            robot_company_map[r_id] = c_name

    for robot in robots_data:
        r_id = robot.get("id")
        if not r_id:
            continue
        
        name = robot.get("name", r_id)
        comp_name = robot_company_map.get(r_id, "")
        title = f"{name}{' by ' + comp_name if comp_name else ''} - Medical Robot | Med Machina"
        intro_yr = robot.get("introduction_year", "N/A")
        description = f"Specifications, regulatory history, videos, and manufacturer details for {name}{' (' + comp_name + ')' if comp_name else ''} (introduced {intro_yr})."
        canonical_url = f"{BASE_URL}/robot/{r_id}"
        
        photos = robot.get("photos", [])
        image_url = photos[0]["url"] if photos and isinstance(photos, list) and len(photos) > 0 and "url" in photos[0] else "/og/og-home.png"

        json_ld = {
            "@context": "https://schema.org",
            "@type": "MedicalDevice",
            "name": name,
            "description": description,
            "url": canonical_url,
            "image": image_url if image_url.startswith("http") else f"{BASE_URL}{image_url}"
        }
        if comp_name:
            json_ld["manufacturer"] = {
                "@type": "Organization",
                "name": comp_name
            }

        body_html = f"""
<div class="container py-4">
  <h1>{name}</h1>
  <p class="lead">{description}</p>
  <ul>
    <li><strong>Manufacturer:</strong> {comp_name or 'N/A'}</li>
    <li><strong>Introduction Year:</strong> {intro_yr}</li>
    <li><strong>Category/Tags:</strong> {', '.join(robot.get('tags', []))}</li>
  </ul>
</div>
"""
        rendered = build_prerender_html(template, title, description, canonical_url, image_url, json_ld, body_html)
        target_dir = os.path.join(DIST_DIR, "robot", r_id)
        os.makedirs(target_dir, exist_ok=True)
        with open(os.path.join(target_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(rendered)

    print(f"Pre-rendered {len(robots_data)} robot detail pages in dist/robot/")

    # Pre-render companies pages
    for company in companies_data:
        name = company.get("name")
        if not name:
            continue
        
        encoded_name = quote(name)
        title = f"{name} - Medical Robotics Company | Med Machina"
        desc_text = company.get("description", "")
        description = f"{desc_text}. Explore surgical robotics portfolio and regulatory approvals for {name}." if desc_text else f"Explore surgical robotics portfolio and company information for {name}."
        canonical_url = f"{BASE_URL}/company/{encoded_name}"
        
        same_as = []
        if company.get("linkedin_url"):
            same_as.append(company["linkedin_url"])
        if company.get("opencorporates_url"):
            same_as.append(company["opencorporates_url"])
        if company.get("urls") and len(company["urls"]) > 0:
            same_as.append(company["urls"][0].get("url"))

        json_ld = {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": name,
            "description": description,
            "url": canonical_url,
            "sameAs": [s for s in same_as if s]
        }
        if company.get("country"):
            json_ld["address"] = {"@type": "PostalAddress", "addressCountry": company["country"]}

        body_html = f"""
<div class="container py-4">
  <h1>{name}</h1>
  <p class="lead">{description}</p>
  <ul>
    <li><strong>Country:</strong> {company.get('country', 'N/A')}</li>
    <li><strong>Robots Portfolio:</strong> {', '.join(company.get('robots', []))}</li>
  </ul>
</div>
"""
        rendered = build_prerender_html(template, title, description, canonical_url, "/og/og-home.png", json_ld, body_html)
        target_dir = os.path.join(DIST_DIR, "company", name)
        os.makedirs(target_dir, exist_ok=True)
        with open(os.path.join(target_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(rendered)

    print(f"Pre-rendered {len(companies_data)} company detail pages in dist/company/")

    # Pre-render static sub-routes
    static_routes = [
        {
            "path": "companies",
            "title": "Medical Robotics Companies | Med Machina",
            "description": "Browse companies manufacturing medical and surgical robotics systems worldwide.",
            "body": "<div class='container py-4'><h1>Medical Robotics Companies</h1><p>Browse global medical and surgical robotics manufacturers.</p></div>"
        },
        {
            "path": "contribute",
            "title": "How to Contribute | Med Machina",
            "description": "Learn how to contribute data or request updates for the Med Machina surgical robotics directory.",
            "body": "<div class='container py-4'><h1>How to Contribute</h1><p>Guidelines for contributing data to Med Machina.</p></div>"
        },
        {
            "path": "links",
            "title": "Medical Robotics Links & Resources | Med Machina",
            "description": "Curated links and resources for medical robotics, regulatory databases, and industry news.",
            "body": "<div class='container py-4'><h1>Medical Robotics Resources</h1><p>Curated links and database resources.</p></div>"
        }
    ]

    for s_route in static_routes:
        canonical_url = f"{BASE_URL}/{s_route['path']}"
        rendered = build_prerender_html(template, s_route['title'], s_route['description'], canonical_url, "/og/og-home.png", None, s_route['body'])
        target_dir = os.path.join(DIST_DIR, s_route['path'])
        os.makedirs(target_dir, exist_ok=True)
        with open(os.path.join(target_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(rendered)

    print("Pre-rendered static sub-routes in dist/")

def main():
    robots_data = load_json("robots.json")
    companies_data = load_json("companies.json")

    generate_robots_txt()
    generate_sitemap(robots_data, companies_data)
    
    if os.path.exists(DIST_DIR):
        prerender_dist(robots_data, companies_data)

if __name__ == "__main__":
    main()
