#!/usr/bin/env bash
# DCO check: every non-merge commit in BASE..HEAD needs a Signed-off-by trailer
# whose address is exactly the commit author's address. Addresses are compared
# as fixed text (plus signs, brackets and dots are not pattern syntax).
set -euo pipefail
: "${BASE:?BASE commit required}" "${HEAD:?HEAD commit required}"
DEPENDABOT_EMAIL='49699333+dependabot[bot]@users.noreply.github.com'

# On merge_group builds GitHub either replays the PR's commits (rebase) or
# writes one synthetic squash commit. A replay keeps each commit's author and
# sign-off, so the normal rule applies unchanged. A squash commit is authored by
# the PR author's profile email and its message concatenates the original
# sign-offs, so no human ever signs it; the original commits were verified when
# the PR was checked. The strict rule cannot apply to it. Skip only that exact
# shape, and only on merge_group: a human commit lacking a matching sign-off
# still fails.
EVENT_NAME="${EVENT_NAME:-}"

fail=0
for sha in $(git rev-list --no-merges "$BASE..$HEAD"); do
  author_email=$(git log -1 --format='%ae' "$sha")
  subject=$(git log -1 --format='%s' "$sha")
  if [ "${PR_AUTHOR:-}" = "dependabot[bot]" ] && [ "$author_email" = "$DEPENDABOT_EMAIL" ]; then
    echo "Skipping Dependabot commit $sha ($subject)"
    continue
  fi
  ok=0
  while IFS= read -r value; do
    [[ "$value" == *"<$author_email>" ]] && ok=1
  done < <(git log -1 --format='%(trailers:key=Signed-off-by,valueonly,separator=%x0A)' "$sha")
  if [ "$ok" -ne 1 ]; then
    echo "::error::Commit $sha ($subject) has no Signed-off-by line matching its author <$author_email>."
    fail=1
  fi
done
if [ "$fail" -ne 0 ]; then
  if [ "$EVENT_NAME" = "merge_group" ]; then
    count=$(git rev-list --no-merges "$BASE..$HEAD" | wc -l | tr -d ' ')
    if [ "$count" = "1" ]; then
      sha=$(git rev-list --no-merges "$BASE..$HEAD")
      subject=$(git log -1 --format=%s "$sha")
      if [[ "$subject" =~ \(#[0-9]+\)$ ]] && git log -1 --format=%B "$sha" | grep -q "^Signed-off-by:"; then
        echo "merge_group squash build: skipping the synthetic commit $sha; the original commits were verified at pull_request."
        exit 0
      fi
    fi
  fi
  echo "Fix with: git rebase --signoff $BASE && git push --force-with-lease"
  exit 1
fi
echo "All commits are signed off."
