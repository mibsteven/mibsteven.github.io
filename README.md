# Apps by Yu-Hsiang Chang

Static, bilingual developer website published with GitHub Pages. No framework, package installation, or hosted database is needed.

## Structure

- `index.html`: Search, seven use categories, selected products, and recent work.
- `apps.html`: Complete searchable catalogue with category, device, download type, and sorting controls.
- `apps/`: Authored product pages and app-specific legal pages.
- `data/apps.json`: Public product metadata, categories, recommendation order, and screenshot references.
- `data/media-sources.json`: Source records for optimised product screenshots.
- `assets/showcase/`: WebP images for catalogue covers and new product galleries.
- `updates.html`: Chronological launch and update archive.
- `support.html`: About, support email draft, and every app’s support link.
- `privacy.html`, `terms.html`, `app-ads.txt`: Shared legal and advertising files.
- `sitemap.xml`, `robots.txt`: Search discovery.

## Edit and build

```sh
python3 Tools/build_site.py
ruby Tools/verify_site.rb
python3 -m http.server 8765 --bind 127.0.0.1
```

Preview at `http://127.0.0.1:8765/`. The validator can also be run directly with `python3 Tools/verify_site.py`.

`build_site.py` regenerates the homepage, catalogue, support page, sitemap, shared navigation, and marked sections of product pages. Edit those areas through the generator or product data. Authored product copy outside `<!-- generated:… -->` sections remains editable in each HTML file. Generated HTML is committed so GitHub Pages needs no build step.

## Add or update an app

1. Create `apps/<id>.html` with Traditional Chinese and English `data-lang-panel` sections, descriptive metadata, and actual product information. Keep stable URLs.
2. Add an entry to `data/apps.json` with bilingual name, short use-based summary, search aliases, primary `category`, browse `categories`, `platforms`, `pricing`, App Store URL, unique `rank`, `updated` date, and screenshot references. `updated` means the public store version’s release date, not the website edit date. `storeVerified` records the last manual store check.
3. Use `paid` for paid downloads, `free` for free downloads, and `trial` for the two-lesson Spatial Electronics Lab trial. State subscriptions, ads, IAP access, or essential controller requirements in bilingual `notes`. Do not imply every free download has every feature free.
4. Choose device tags for the platforms being presented: `iphone`, `ipad`, `mac`, `vision`, `tv`. Distinguish native experiences from optional compatibility in the product copy and link to the store’s current requirements. Do not claim an unreleased platform is available.
5. Assign one primary category and any genuinely relevant additional browse categories. Counts overlap across categories; the complete catalogue always contains unique apps. For example, Shiji is in tools and education.
6. Add actual app screenshots as WebP, at most 1440 pixels on either side and under 500 KB each. Supply `src`, `width`, and `height` per language. A single-language image can be reused with an honest caption; avoid fabricated UI. Record the project-relative source or public App Store image URL in `data/media-sources.json`.
7. `media[0]` supplies the catalogue and homepage cover. Use `existing: true` when the authored page already displays the imagery and should not get a duplicate gallery. Add bilingual captions to `CAPTIONS` in the generator for new gallery images.
8. Review app-specific privacy and terms, add a dated entry to `updates.html`, then build and validate.

## Maintain discovery

- Use an optional `related` list of app IDs for product-specific recommendations. Otherwise related apps come from the primary category. Keep the free app’s audience in mind: Zodiac points to reading and wildlife learning.
- Set `featured: true` on two to four apps to refresh the homepage. Recommendation order uses `rank`; it is editorial, not a download leaderboard.
- Review the selected apps and recent-work section when a meaningful release ships. Update the explicit recent-work entries in the generator rather than presenting an old product as newly released.
- Evaluate free discovery apps, paid downloads, and IAP trials separately. Private sales reports do not belong in this public repository.
- Read prices and device requirements from the current local App Store. The site avoids fixed currency prices that go stale between regions.
- Query links are shareable: `apps.html?lang=zh&category=music&platform=ipad`. Supported parameters: `q`, `category`, `platform`, `price`, `sort`, `lang`.
- Catalogue detail links preserve the filters in `browse`; the return link restores those filters and the product position. Local links retain the selected language.
- Without JavaScript, Traditional Chinese content and the complete static catalogue remain readable. JavaScript enables filters, language switching, and email draft formatting. Blocked local storage must not prevent reading.
- No analytics provider is installed. Future evaluation should distinguish visits to an app page, outgoing App Store clicks, paid purchases, and IAP unlocks. Do not infer website conversions from downloads alone.

## Validation and publishing

The validator checks catalogue/page coverage, category membership, bilingual catalogue and support entries, duplicate IDs, local links and anchors, alt text, screenshot provenance and budgets, sitemap coverage, purchase copy, the existing RealmAtlas video, and legal content.

Before publishing, also check desktop and mobile layouts, English switching, Chinese and English searches, combined filters, empty results, resetting, sorting, browser back, and returning from a product page.

Push the reviewed website changes to the GitHub Pages branch (`main`, root folder) to publish. The existing `Tools/push_github_pages.command` helper is unchanged. Building locally does not deploy the site.
