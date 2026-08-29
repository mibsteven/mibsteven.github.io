#!/usr/bin/env ruby
# frozen_string_literal: true

require "pathname"
require "uri"

ROOT = Pathname.new(__dir__).parent.expand_path

def read(relative_path)
  ROOT.join(relative_path).read(encoding: "UTF-8")
end

def assert(condition, message)
  raise "FAIL: #{message}" unless condition
end

def section(html, id)
  match = html.match(/<section\b[^>]*\bid="#{Regexp.escape(id)}"[^>]*>.*?<\/section>/m)
  assert(match, "missing ##{id} section")
  match[0]
end

index = read("index.html")
updates = read("updates.html")
privacy = read("privacy.html")
css = read("assets/site.css")
javascript = read("assets/site.js")

ordered_sections = %w[featured audiences updates apps]
section_positions = ordered_sections.map { |id| index.index(%(<section id="#{id}")) }
assert(section_positions.none?(&:nil?), "homepage is missing a required section")
assert(section_positions == section_positions.sort, "homepage section hierarchy is out of order")
assert(!index.include?('id="product-lines"'), "legacy product-lines section is still present")

updates_preview = section(index, "updates")
assert(updates_preview.scan(/<article class="panel update-card/).length == 6, "homepage must show three updates per language")
assert(updates_preview.scan(/update-card-featured/).length == 2, "homepage must have one featured update per language")
assert(updates_preview.scan(/<time class="update-date" datetime="\d{4}-\d{2}-\d{2}">/).length == 6, "homepage update dates must use semantic time elements")
assert(updates_preview.scan(/href="updates\.html"/).length == 2, "homepage must link to the full updates archive in both languages")

archive_sections = updates.scan(/<section class="updates-archive"[^>]*>.*?<\/section>/m)
assert(archive_sections.length == 2, "updates archive must have Traditional Chinese and English sections")
archive_sections.each do |archive|
  dates = archive.scan(/<time datetime="(\d{4}-\d{2}-\d{2})">/).flatten
  assert(dates.length == 20, "each language archive must contain twenty dated entries")
  assert(dates == dates.sort.reverse, "archive entries must be reverse chronological")
end

assert(index.scan(/class="panel app-card"/).length == 58, "homepage must retain 29 apps per language")
assert(index.scan(/class="apps is-collapsed"/).length == 2, "both app lists must start collapsed")
assert(index.scan(/data-app-toggle/).length == 2, "both languages need an app-list toggle")
assert(css.include?(".apps.is-collapsed > .app-card:nth-child(n + 9)"), "collapsed app lists must show eight cards")
assert(javascript.include?('document.querySelectorAll("[data-app-toggle]")'), "app-list toggle behavior is missing")

app_icons = index.scan(/<img class="app-icon[^>]*>/)
assert(app_icons.length == 68, "homepage app icon count changed unexpectedly")
assert(app_icons.all? { |tag| tag.include?('loading="lazy"') && tag.include?('width="68"') && tag.include?('height="68"') }, "homepage app icons must be lazy-loaded with fixed dimensions")
assert(app_icons.all? { |tag| tag.include?('src="assets/apps/thumbs/') }, "homepage must use optimized icon thumbnails")

thumbnail_files = ROOT.join("assets/apps/thumbs").children.select(&:file?)
thumbnail_bytes = thumbnail_files.sum(&:size)
assert(thumbnail_files.length == 29, "expected 29 optimized app thumbnails")
assert(thumbnail_bytes < 4 * 1024 * 1024, "optimized thumbnails exceed the 4 MB budget")

spatial_electronics_lab = read("apps/spatial-electronics-lab.html")
assert(spatial_electronics_lab.include?("Apple Vision Pro · 開發中"), "Spatial Electronics Lab development status is missing")
assert(spatial_electronics_lab.include?("Code Studio"), "Spatial Electronics Lab Code Studio description is missing")
assert(spatial_electronics_lab.include?("../privacy.html") && spatial_electronics_lab.include?("../terms.html"), "Spatial Electronics Lab legal links are missing")

assert(privacy.include?("最後更新：2026 年 8 月 30 日") && privacy.include?("Last updated: August 30, 2026"), "privacy policy date is not current in both languages")
assert(privacy.scan(/<h2>Spatial Electronics Lab<\/h2>/).length == 2, "privacy policy must include Spatial Electronics Lab in both languages")
assert(privacy.include?("Universal Clipboard") && privacy.include?("Cloud sync is currently disabled"), "Spatial Electronics Lab clipboard or cloud-sync privacy boundary is missing")

realm_atlas = read("apps/realm-atlas.html")
assert(realm_atlas.scan(/<video\b/).length == 2, "RealmAtlas must include one gameplay video per language")
assert(realm_atlas.scan(%r{src="\.\./assets/videos/realm-atlas-gameplay\.mp4"}).length == 2, "RealmAtlas gameplay source is missing")
assert(realm_atlas.scan(%r{poster="\.\./assets/screenshots/realm-atlas-gameplay-poster\.jpg"}).length == 2, "RealmAtlas gameplay poster is missing")
gameplay_video = ROOT.join("assets/videos/realm-atlas-gameplay.mp4")
assert(gameplay_video.exist?, "RealmAtlas gameplay video file is missing")
assert(gameplay_video.size < 6 * 1024 * 1024, "RealmAtlas gameplay video exceeds the 6 MB budget")

assert(css.include?("@media (max-width: 560px)"), "mobile breakpoint is missing")
assert(css.include?("grid-template-columns: repeat(3, minmax(0, 1fr))"), "mobile primary navigation must use three columns")
assert(css.include?('.nav a[data-i18n="navPrivacy"]'), "legal navigation links must be removed from the primary navigation")
assert(javascript.include?('updatesLink.dataset.i18n = "navUpdates"'), "updates navigation injection is missing on secondary pages")

missing_targets = []
html_files = ROOT.glob("**/*.html").reject { |path| path.to_s.include?("/dist/") || path.to_s.include?("/marketing/") }
html_files.each do |html_file|
  html = html_file.read(encoding: "UTF-8")
  html.scan(/(?:href|src)="([^"]+)"/).flatten.each do |target|
    next if target.start_with?("#", "mailto:", "data:", "http://", "https://")

    clean_target = target.split(/[?#]/, 2).first
    next if clean_target.nil? || clean_target.empty?

    resolved = html_file.dirname.join(URI.decode_www_form_component(clean_target)).cleanpath
    missing_targets << "#{html_file.relative_path_from(ROOT)}: #{target}" unless resolved.exist?
  end
end
assert(missing_targets.empty?, "missing internal targets:\n#{missing_targets.join("\n")}")

puts "PASS: homepage hierarchy, updates archive, app disclosure, navigation, media budgets, responsive rules, and #{html_files.length} HTML files verified."
