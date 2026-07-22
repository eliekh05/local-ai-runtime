# frozen_string_literal: true

# Homebrew formula for local-ai-runtime
# Install: brew install ./Formula/local-ai-runtime.rb
# Or via tap: brew tap YOUR_USER/tap && brew install local-ai-runtime

class LocalAiRuntime < Formula
  desc "BYOK hybrid local AI chat runtime — run any model from anywhere"
  homepage "https://github.com/youruser/local-ai-runtime"
  url "https://github.com/youruser/local-ai-runtime/archive/refs/tags/v0.1.0.tar.gz"
  sha256 "REPLACE_WITH_ACTUAL_SHA256"
  license "MIT"

  depends_on "uv"

  def install
    # Install the Python package via uv
    system "uv", "sync", "--frozen", "--no-dev", "--directory", buildpath.to_s

    # Create wrapper script
    (bin/"local-ai-runtime").write <<~SCRIPT
      #!/bin/sh
      exec uv run --directory "#{buildpath}" local-ai-runtime "$@"
    SCRIPT
  end

  test do
    system "#{bin}/local-ai-runtime", "--help"
  end
end
