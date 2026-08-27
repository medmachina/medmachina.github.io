#!/usr/bin/env python3
"""
Interactive Publication Curator for MedMachina
Searches Europe PMC / PubMed for relevant clinical publications for each robot,
displays title, abstract, citation count, and provides interactive controls:
  a: approve (saves to robot's JSON)
  r: reject (adds to blacklist)
  p: previous
  s: skip
  q: quit
"""

import re
import sys
import os
import json
import glob
import textwrap
import urllib.parse
import urllib.request

PUBLIC_DIR = os.path.join(os.path.dirname(__file__), "..", "public")
ROBOTS_DIR = os.path.join(PUBLIC_DIR, "robots")
BLACKLIST_FILE = os.path.join(PUBLIC_DIR, "publications_blacklist.json")

def load_blacklist():
    if os.path.exists(BLACKLIST_FILE):
        try:
            with open(BLACKLIST_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()

def save_blacklist(blacklist):
    with open(BLACKLIST_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(list(blacklist)), f, indent=2)

def search_europe_pmc(robot_name, company_name=None, other_names=None):
    """
    Search Europe PMC REST API for high-impact publications specifically discussing the device.
    """
    terms = [robot_name]
    if company_name:
        terms.append(f"{company_name} {robot_name}")
    if other_names and isinstance(other_names, list):
        for on in other_names:
            if on:
                terms.append(on)

    sub_queries = []
    for t in terms:
        clean_t = t.strip()
        sub_queries.append(f'TITLE:"{clean_t}" OR ABSTRACT:"{clean_t}"')

    query_str = f'({" OR ".join(sub_queries)}) AND (surgical OR robot OR robotics OR medical OR radiosurgery OR arthroplasty OR ultrasound)'
    clean_query = urllib.parse.quote(query_str)
    url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={clean_query}&format=json&resultType=core&pageSize=25&sort=CITED%20desc"
    
    headers = {"User-Agent": "MedMachina-Curator/1.0"}
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
            results = data.get("resultList", {}).get("result", [])
            papers = []
            
            # Prepare lowercase relevance terms (including space/hyphen variations)
            check_terms = set()
            for t in terms:
                if not t:
                    continue
                tl = t.strip().lower()
                if len(tl) > 2:
                    check_terms.add(tl)
                    check_terms.add(tl.replace("-", " "))
                    check_terms.add(tl.replace(" ", "-"))
                    for part in re.split(r'[^a-zA-Z0-9]+', tl):
                        if len(part) > 2 and part not in {"robot", "robotic", "system", "medical", "surgical"}:
                            check_terms.add(part)

            for item in results:
                title = item.get("title", "").rstrip(".")
                doi = item.get("doi", "")
                pmid = item.get("pmid", "")
                
                j_info = item.get("journalInfo", {})
                journal = j_info.get("journal", {}).get("title") or j_info.get("journal", {}).get("medlineAbbreviation") or item.get("journalTitle", "")
                
                year = item.get("pubYear")
                citations = item.get("citedByCount", 0)
                
                raw_abstract = item.get("abstractText", "")
                abstract = re.sub(r'<[^>]+>', '', raw_abstract).strip() if raw_abstract else "No abstract available."
                
                # Relevance Verification: Must mention device in title or abstract
                full_text = f"{title} {abstract}".lower()
                is_relevant = any(ct in full_text for ct in check_terms)
                if not is_relevant:
                    continue

                if doi:
                    paper_url = f"https://doi.org/{doi}"
                elif pmid:
                    paper_url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                else:
                    paper_url = ""
                    
                paper_id = pmid or doi or title
                
                if title and paper_url:
                    papers.append({
                        "paper_id": paper_id,
                        "title": title,
                        "url": paper_url,
                        "year": int(year) if year and str(year).isdigit() else None,
                        "journal": journal,
                        "doi": doi or None,
                        "pmid": pmid or None,
                        "citations": int(citations) if citations is not None else 0,
                        "abstract": abstract,
                        "search_terms": list(check_terms)
                    })
            return papers
    except Exception as e:
        print(f"API Search Error for '{robot_name}': {e}")
        return []

def highlight_keywords(text, keywords):
    if not text or not keywords:
        return text
    terms = set()
    for kw in keywords:
        if not kw:
            continue
        raw_kw = kw.strip()
        if len(raw_kw) > 2:
            terms.add(raw_kw)
            terms.add(raw_kw.replace("-", " "))
            terms.add(raw_kw.replace(" ", "-"))
        parts = [p for p in re.split(r'[^a-zA-Z0-9]+', raw_kw) if len(p) > 2]
        for p in parts:
            terms.add(p)
            
    if not terms:
        return text
        
    sorted_terms = sorted(terms, key=len, reverse=True)
    pattern = re.compile(r'(' + '|'.join(re.escape(t) for t in sorted_terms) + r')', re.IGNORECASE)
    return pattern.sub(r'\033[1;33m\1\033[0m', text)

def print_paper_card(robot_name, paper, idx, total, search_terms=None):
    if search_terms is None:
        search_terms = paper.get("search_terms", [robot_name])
        
    title_text = highlight_keywords(paper['title'], search_terms)
    print("\n" + "=" * 80)
    print(f" Robot System  : {robot_name}")
    print(f" Candidate     : [{idx + 1}/{total}]")
    print(f" Title         : {title_text}")
    print(f" Journal / Year: {paper.get('journal', 'N/A')} ({paper.get('year', 'N/A')})")
    print(f" Citations     : {paper.get('citations', 0)} citations")
    if paper.get('doi'):
        print(f" DOI           : {paper['doi']}")
    if paper.get('pmid'):
        print(f" PMID          : {paper['pmid']}")
    print(f" Link          : {paper['url']}")
    print("-" * 80)
    
    abstract_text = paper.get('abstract', 'No abstract available.')
    wrapped_abstract = textwrap.fill(abstract_text, width=78, initial_indent=" ", subsequent_indent=" ")
    highlighted_abstract = highlight_keywords(wrapped_abstract, search_terms)
    print(" ABSTRACT:")
    print(highlighted_abstract)
    print("=" * 80)

FIELD_PUBS_FILE = os.path.join(PUBLIC_DIR, "publications.json")

def load_field_pubs():
    if os.path.exists(FIELD_PUBS_FILE):
        try:
            with open(FIELD_PUBS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_field_pub(paper):
    pubs = load_field_pubs()
    urls = set(p.get("url") for p in pubs if "url" in p)
    if paper["url"] in urls:
        print(f"Publication '{paper['title'][:50]}...' already in field publications list.")
        return
    
    pub_entry = {
        "title": paper["title"],
        "url": paper["url"],
        "year": paper["year"],
        "journal": paper["journal"],
        "doi": paper["doi"],
        "pmid": paper["pmid"],
        "citations": paper["citations"],
        "abstract": paper["abstract"]
    }
    pub_entry = {k: v for k, v in pub_entry.items() if v is not None}
    pubs.append(pub_entry)
    
    with open(FIELD_PUBS_FILE, "w", encoding="utf-8") as f:
        json.dump(pubs, f, indent=2)
    print(f"✓ Added '{paper['title'][:50]}...' to field-wide publications ({FIELD_PUBS_FILE})")

def curate_robot(robot_path, blacklist):
    with open(robot_path, "r", encoding="utf-8") as f:
        robot_data = json.load(f)

    robot_name = robot_data.get("name", "")
    robot_id = robot_data.get("id", os.path.splitext(os.path.basename(robot_path))[0])
    company_name = robot_data.get("company", {}).get("name") if isinstance(robot_data.get("company"), dict) else None
    other_names = robot_data.get("other_names", [])

    # Load field-wide publications
    field_pubs = load_field_pubs()
    field_urls = set(p.get("url") for p in field_pubs if p.get("url"))
    field_dois = set(p.get("doi") for p in field_pubs if p.get("doi"))
    field_pmids = set(p.get("pmid") for p in field_pubs if p.get("pmid"))
    field_titles = set(p.get("title", "").lower().strip() for p in field_pubs if p.get("title"))

    # Load robot-specific existing publications
    existing_pubs = robot_data.get("publications", [])
    robot_urls = set(p.get("url") for p in existing_pubs if p.get("url"))
    robot_dois = set(p.get("doi") for p in existing_pubs if p.get("doi"))
    robot_pmids = set(p.get("pmid") for p in existing_pubs if p.get("pmid"))
    robot_titles = set(p.get("title", "").lower().strip() for p in existing_pubs if p.get("title"))

    print(f"\nFetching candidates for: {robot_name}...")
    candidates = search_europe_pmc(robot_name, company_name=company_name, other_names=other_names)
    
    # Filter out blacklisted items, robot existing items, and field existing items
    filtered_candidates = []
    for c in candidates:
        pid = c.get("paper_id")
        purl = c.get("url")
        doi = c.get("doi")
        pmid = c.get("pmid")
        title_clean = c.get("title", "").lower().strip()

        # Check Blacklist
        if pid in blacklist or (purl and purl in blacklist) or (doi and doi in blacklist) or (pmid and pmid in blacklist):
            continue

        # Check Robot-Specific Publications
        if (purl and purl in robot_urls) or (doi and doi in robot_dois) or (pmid and pmid in robot_pmids) or (title_clean and title_clean in robot_titles):
            continue

        # Check Field-Wide Publications
        if (purl and purl in field_urls) or (doi and doi in field_dois) or (pmid and pmid in field_pmids) or (title_clean and title_clean in field_titles):
            continue

        filtered_candidates.append(c)

    if not filtered_candidates:
        print(f"No new candidates found for {robot_name}.")
        return

    idx = 0
    while idx < len(filtered_candidates):
        paper = filtered_candidates[idx]
        print_paper_card(robot_name, paper, idx, len(filtered_candidates))
        
        choice = input("Action [a]pprove (this robot), [f]ield (whole field), [r]eject (blacklist), [s]kip, [p]revious, [q]uit: ").strip().lower()
        
        if choice == 'a':
            pub_entry = {
                "title": paper["title"],
                "url": paper["url"],
                "year": paper["year"],
                "journal": paper["journal"],
                "doi": paper["doi"],
                "pmid": paper["pmid"],
                "citations": paper["citations"]
            }
            # Clean null values
            pub_entry = {k: v for k, v in pub_entry.items() if v is not None}
            
            if "publications" not in robot_data:
                robot_data["publications"] = []
            robot_data["publications"].append(pub_entry)
            
            with open(robot_path, "w", encoding="utf-8") as f:
                json.dump(robot_data, f, indent=2)
            print(f"✓ Approved & saved '{paper['title'][:50]}...' to {os.path.basename(robot_path)}")
            idx += 1
            
        elif choice == 'f':
            save_field_pub(paper)
            idx += 1
            
        elif choice == 'r':
            blacklist.add(paper["paper_id"])
            if paper.get("url"):
                blacklist.add(paper["url"])
            if paper.get("doi"):
                blacklist.add(paper["doi"])
            if paper.get("pmid"):
                blacklist.add(paper["pmid"])
            save_blacklist(blacklist)
            print(f"✗ Blacklisted '{paper['title'][:50]}...'")
            idx += 1
            
        elif choice == 'p':
            if idx > 0:
                idx -= 1
            else:
                print("Already at the first candidate.")
                
        elif choice == 's':
            idx += 1
            
        elif choice == 'q':
            print("Exiting curation.")
            sys.exit(0)
        else:
            print("Invalid input. Please enter 'a', 'r', 's', 'p', or 'q'.")

def main():
    blacklist = load_blacklist()
    
    target_robot = None
    if len(sys.argv) > 1:
        target_robot = sys.argv[1]

    robot_files = sorted(glob.glob(os.path.join(ROBOTS_DIR, "*.json")))
    
    for r_file in robot_files:
        r_id = os.path.splitext(os.path.basename(r_file))[0]
        if target_robot and target_robot not in (r_id, r_file):
            continue
        curate_robot(r_file, blacklist)

if __name__ == "__main__":
    main()
