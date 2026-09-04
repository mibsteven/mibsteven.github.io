#!/usr/bin/env ruby
# frozen_string_literal: true
# Preserve the original validation command; the HTML parser uses Python stdlib.
exec('python3', File.join(__dir__, 'verify_site.py'))
