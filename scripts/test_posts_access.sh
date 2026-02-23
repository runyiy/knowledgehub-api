#!/usr/bin/env bash
set -e

BASE_URL="http://172.20.160.1:8000/api/posts"

USER_A_ID=2        # author
USER_B_ID=4        # non author
POST_PUBLIC_ID=1
POST_PRIVATE_ID=2
INVALID_USER_ID=999999
INVALID_POST_ID=999999

echo "== 1) public post, no header (expect 200)"
curl -i "$BASE_URL/$POST_PUBLIC_ID"
echo -e "\n"

echo "== 2) public post, with user B (expect 200)"
curl -i -H "X-User-Id: $USER_B_ID" "$BASE_URL/$POST_PUBLIC_ID"
echo -e "\n"

echo "== 3) private post, no header (expect 401)"
curl -i "$BASE_URL/$POST_PRIVATE_ID" || true
echo -e "\n"

echo "== 4) private post, with user B (expect 403)"
curl -i -H "X-User-Id: $USER_B_ID" "$BASE_URL/$POST_PRIVATE_ID" || true
echo -e "\n"

echo "== 5) private post, with author A (expect 200)"
curl -i -H "X-User-Id: $USER_A_ID" "$BASE_URL/$POST_PRIVATE_ID"
echo -e "\n"

echo "== 6) post not found (expect 404)"
curl -i "$BASE_URL/$INVALID_POST_ID" || true
echo -e "\n"

echo "== 7a) invalid user id on public (expect 401)"
curl -i -H "X-User-Id: $INVALID_USER_ID" "$BASE_URL/$POST_PUBLIC_ID" || true
echo -e "\n"

echo "== 7b) invalid user id on private (expect 401)"
curl -i -H "X-User-Id: $INVALID_USER_ID" "$BASE_URL/$POST_PRIVATE_ID" || true
echo -e "\n"

echo "== 8) list posts, anonymous (expect only public, 200)"
curl -i "$BASE_URL"
echo -e "\n"

echo "== 9) list posts, anonymous mine=true (expect 401)"
curl -i "$BASE_URL?mine=true" || true
echo -e "\n"

echo "== 10) list posts, anonymous is_public=true (expect only public, 200)"
curl -i "$BASE_URL?is_public=true"
echo -e "\n"

echo "== 11) list posts, anonymous is_public=false (expect empty list, 200)"
curl -i "$BASE_URL?is_public=false"
echo -e "\n"

echo "== 12) list posts, user A (expect public + own private)"
curl -i -H "X-User-Id: $USER_A_ID" "$BASE_URL"
echo -e "\n"

echo "== 13) list posts, user A mine=true (expect only own posts)"
curl -i -H "X-User-Id: $USER_A_ID" "$BASE_URL?mine=true"
echo -e "\n"

echo "== 14) list posts, user A is_public=false (expect only own private)"
curl -i -H "X-User-Id: $USER_A_ID" "$BASE_URL?is_public=false"
echo -e "\n"

echo "== 15) list posts, user B (expect only public)"
curl -i -H "X-User-Id: $USER_B_ID" "$BASE_URL"
echo -e "\n"

echo "== 16) list posts, user B is_public=false (expect empty list, 200)"
curl -i -H "X-User-Id: $USER_B_ID" "$BASE_URL?is_public=false"
echo -e "\n"