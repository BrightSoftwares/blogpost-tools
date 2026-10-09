# Pinned by digest (incident 2026-10-08): `:latest` was rebuilt from Dockerfile.netlify
# (netlify-cli 27.11.0) when PR #52 merged; that CLI runs a framework build inside
# `netlify deploy` (`bundle exec jekyll build`), which fails ("bundle: command not found")
# because this image has no Ruby. This digest is the last image that deployed the fleet
# green (tag sha-6c77011, built 2024-02-26). Unpin only after the rebuilt :latest
# (entrypoint passes --no-build) is verified on a non-production site run.
FROM fullbright/action-netlify-deploy:sha-6c77011@sha256:1d1b17ff88b84134987363ee476e7c01e3760f1b0f3f6b1210519e5bf0fbcf2e

ENTRYPOINT ["/entrypoint.sh"]
