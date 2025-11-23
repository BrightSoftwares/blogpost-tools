#!/bin/bash
# Save as migrate-jekyll-repos.sh

#TOKEN="fake" # update here or send it through env variable in command line
REPOS=(
  "BrightSoftwares/corporate-website"
  "BrightSoftwares/foolywise.com"
  "BrightSoftwares/ieatmyhealth.com"
  "BrightSoftwares/joyousbyflora-posts"
  "BrightSoftwares/keke.li"
  "BrightSoftwares/modabyflora-corporate"
  "BrightSoftwares/olympics-paris2024.com"
  "Causting/causting.com"
  "Causting/space-up-planet.com"
  "sergioafanou/smart-cv"
)

WORKDIR="/tmp/jekyll-migration"
mkdir -p "$WORKDIR"
cd "$WORKDIR"

for REPO in "${REPOS[@]}"; do
  echo "========================================"
  echo "Processing: $REPO"
  echo "========================================"
  
  REPO_NAME=$(basename "$REPO")
  
  # Clone the repo
  git clone "https://${TOKEN}@github.com/${REPO}.git" "$REPO_NAME"
  cd "$REPO_NAME"
  
  # Find and update workflow files
  find .github/workflows -name "*.yml" -type f | while read -r WORKFLOW; do
    echo "  Checking: $WORKFLOW"
    
    # Check if it uses jekyll-action
    if grep -q "jekyll-action" "$WORKFLOW"; then
      echo "  -> Updating: $WORKFLOW"
      
      # Replace fullbright/jekyll-action@master with new action
      sed -i 's|fullbright/jekyll-action@master|BrightSoftwares/blogpost-tools/jekyll-action@main|g' "$WORKFLOW"
      
      # Also handle if already partially migrated
      sed -i 's|fullbright/jekyll-action@main|BrightSoftwares/blogpost-tools/jekyll-action@main|g' "$WORKFLOW"
      
      # Remove pre_build_commands for imagemagick (since it's now built-in)
      # This is a simple removal - complex cases may need manual review
      sed -i '/pre_build_commands:.*imagemagick/d' "$WORKFLOW"
    fi
  done
  
  # Check for changes
  if [ -n "$(git status --porcelain)" ]; then
    echo "  Committing changes..."
    git add .
    git commit -m "Migrate to BrightSoftwares/blogpost-tools/jekyll-action

- Update action reference from fullbright/jekyll-action to blogpost-tools
- ImageMagick is now built into the Docker image (no pre_build_commands needed)"
    
    echo "  Pushing changes..."
    git push origin HEAD
  else
    echo "  No changes needed"
  fi
  
  cd "$WORKDIR"
  echo ""
done

echo "========================================"
echo "Migration complete!"
echo "========================================"