# mibsteven.github.io

Simple GitHub Pages site for a developer website.

## Purpose

This site hosts:

- A lightweight portfolio / app showcase
- Individual pages for each app
- A chronological updates archive
- Support information
- Privacy Policy
- Terms of Use
- `app-ads.txt`

## Structure

- `index.html`: Main landing page
- `updates.html`: App launches, major updates, development notes, and milestones
- `apps/`: One page per app
- `privacy.html`: Shared privacy policy
- `terms.html`: Shared terms of use
- `support.html`: Support page
- `app-ads.txt`: App advertising authorization file

## Add A New App

1. Create a new HTML page inside `apps/`.
2. Add a new card in `index.html` linking to that app page.
3. Add the app to `support.html`.
4. If the app has different privacy behavior, create a dedicated privacy page or update `privacy.html`.

## Add A New Update

1. Add the full entry to `updates.html` in reverse chronological order.
2. Use a semantic `<time datetime="YYYY-MM-DD">` date.
3. Choose one category: new app, update, development, or milestone.
4. Keep only the three most recent or most meaningful entries in the homepage preview.
5. When several entries cover the same app in a short period, keep the newest result on the homepage and preserve the earlier story in the archive.

## Deploy With GitHub Pages

1. Push this repository to GitHub.
2. Open the repository `Settings`.
3. Go to `Pages`.
4. Under `Build and deployment`, choose `Deploy from a branch`.
5. Select the `main` branch and the `/ (root)` folder.
6. Save and wait for GitHub Pages to publish the site.

If this is your personal site, the repository name should usually be:

`mibsteven.github.io`

Then the site URL will look like:

`https://mibsteven.github.io/`

## Current Notes

- 向量財管 / VectraFin has an app page describing its local-first personal finance model.
- 英語救星 / EnglishSaver has an expanded app page describing its AI English practice, vocabulary-to-story flow, iOS / visionOS versions, and privacy model.
- 師記 and Melody Journal do not collect personal data.
- 台北菜價 uses Google advertising services.
- 注音故事 has an app page and is available on the App Store.
- Notelyra has an app page and is available on the App Store.
- Shared legal pages are acceptable as long as app behavior remains mostly consistent.
- Taiwan Animals has an app page for its iOS, iPadOS, and visionOS nature learning experience.
