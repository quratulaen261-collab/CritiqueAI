import requests
from bs4 import BeautifulSoup


def analyze_website(url: str) -> dict:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # ── Basic info ──
        title = soup.title.string.strip() if soup.title and soup.title.string else "No Title Found"
        meta_desc_tag = soup.find("meta", attrs={"name": "description"})
        meta_desc = meta_desc_tag["content"].strip() if meta_desc_tag and meta_desc_tag.get("content") else "No meta description"

        # ── Headings ──
        h1_tags = [h.get_text(strip=True) for h in soup.find_all("h1")]
        h2_tags = [h.get_text(strip=True) for h in soup.find_all("h2")]
        h3_tags = [h.get_text(strip=True) for h in soup.find_all("h3")]

        # ── Images ──
        images = soup.find_all("img")
        img_without_alt = [img for img in images if not img.get("alt")]

        # ── Links ──
        links = soup.find_all("a", href=True)
        internal_links = [l for l in links if url.split("/")[2] in l["href"] or l["href"].startswith("/")]
        external_links = [l for l in links if l["href"].startswith("http") and url.split("/")[2] not in l["href"]]

        # ── Page size ──
        page_size_kb = round(len(response.content) / 1024, 1)

        # ── Score calculation ──
        score = 100
        issues = []
        suggestions = []

        # Title checks
        if title == "No Title Found":
            score -= 20
            issues.append("Page has no title tag")
            suggestions.append("Add a descriptive <title> tag — it's the most important SEO element")
        elif len(title) < 30:
            score -= 10
            issues.append(f"Title is too short ({len(title)} chars)")
            suggestions.append("Make your title 50–60 characters long for best SEO results")
        elif len(title) > 60:
            score -= 5
            issues.append(f"Title is too long ({len(title)} chars, may be cut off in search results)")
            suggestions.append("Shorten your title to under 60 characters so it displays fully in Google")

        # Meta description checks
        if meta_desc == "No meta description":
            score -= 15
            issues.append("No meta description found")
            suggestions.append("Add a meta description (150–160 chars) to improve click-through rates in search")
        elif len(meta_desc) < 80:
            score -= 5
            issues.append("Meta description is too short")
            suggestions.append("Expand your meta description to 150–160 characters for better visibility")

        # H1 checks
        if len(h1_tags) == 0:
            score -= 15
            issues.append("No H1 heading found")
            suggestions.append("Add exactly one H1 heading — it tells search engines what your page is about")
        elif len(h1_tags) > 1:
            score -= 5
            issues.append(f"Multiple H1 tags found ({len(h1_tags)}) — use only one per page")
            suggestions.append("Keep only one H1 per page; use H2 and H3 for subheadings")

        # Image ALT checks
        if len(img_without_alt) > 0:
            penalty = min(15, len(img_without_alt) * 3)
            score -= penalty
            issues.append(f"{len(img_without_alt)} image(s) missing ALT text")
            suggestions.append(f"Add descriptive ALT text to all {len(img_without_alt)} image(s) — helps SEO and accessibility")

        # H2 check
        if len(h2_tags) == 0:
            score -= 5
            issues.append("No H2 subheadings found")
            suggestions.append("Add H2 subheadings to break up content and improve readability")

        # Page size check
        if page_size_kb > 500:
            score -= 5
            issues.append(f"Page size is large ({page_size_kb} KB)")
            suggestions.append("Optimize images and minify CSS/JS to reduce page load time")

        # Always add general suggestions
        suggestions.append("Ensure your page loads in under 3 seconds for best user retention")
        suggestions.append("Add structured data (Schema.org) to enhance rich results in Google")
        suggestions.append("Make sure your site is mobile-responsive — Google uses mobile-first indexing")

        score = max(0, score)

        # ── Score label ──
        if score >= 80:
            score_label = "Good"
        elif score >= 60:
            score_label = "Needs Work"
        elif score >= 40:
            score_label = "Poor"
        else:
            score_label = "Critical"

        return {
            "success": True,
            "url": url,
            "score": score,
            "score_label": score_label,
            "stats": {
                "title": title,
                "title_length": len(title),
                "meta_description": meta_desc,
                "meta_desc_length": len(meta_desc),
                "h1_count": len(h1_tags),
                "h1_tags": h1_tags[:3],
                "h2_count": len(h2_tags),
                "h3_count": len(h3_tags),
                "total_images": len(images),
                "images_missing_alt": len(img_without_alt),
                "total_links": len(links),
                "internal_links": len(internal_links),
                "external_links": len(external_links),
                "page_size_kb": page_size_kb,
            },
            "issues": issues,
            "suggestions": suggestions,
        }

    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Could not connect to the website. Check the URL and try again."}
    except requests.exceptions.Timeout:
        return {"success": False, "error": "The website took too long to respond (timeout after 10s)."}
    except requests.exceptions.HTTPError as e:
        return {"success": False, "error": f"Website returned an error: {e}"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}
