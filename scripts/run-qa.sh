#!/bin/bash
# =============================================================================
# Tendril QA Runner - Full Frontend QA Suite
# =============================================================================
# Usage:
#   ./scripts/run-qa.sh              # Run full QA suite
#   ./scripts/run-qa.sh --chromium   # Run Chromium only
#   ./scripts/run-qa.sh --mobile     # Run mobile viewports only
#   ./scripts/run-qa.sh --report     # Open HTML report
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
WEB_DIR="$PROJECT_ROOT/web"
QA_OUTPUT="$WEB_DIR/qa-output"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║           🌱 Tendril Full QA Testing Suite                  ║"
echo "║           Date: $(date '+%Y-%m-%d %H:%M:%S')                     ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Create output directories
mkdir -p "$QA_OUTPUT/screenshots"
mkdir -p "$QA_OUTPUT/videos"

cd "$WEB_DIR"

# Check if docker services are running
check_services() {
  echo -e "${BLUE}Checking services...${NC}"

  API_URL="${E2E_API_URL:-http://localhost:8000}"
  WEB_URL="${E2E_BASE_URL:-http://localhost:3000}"

  if curl -s "$API_URL/health" > /dev/null 2>&1 || curl -s "$API_URL/v1/health" > /dev/null 2>&1; then
    echo -e "  ${GREEN}✓${NC} API server is running at $API_URL"
  else
    echo -e "  ${YELLOW}⚠${NC} API server not reachable at $API_URL"
    echo -e "  ${YELLOW}  Run: docker-compose up -d${NC}"
    echo -e "  ${YELLOW}  Or set E2E_API_URL to your API endpoint${NC}"
  fi

  if curl -s "$WEB_URL" > /dev/null 2>&1; then
    echo -e "  ${GREEN}✓${NC} Web server is running at $WEB_URL"
  else
    echo -e "  ${YELLOW}⚠${NC} Web server not reachable at $WEB_URL"
    echo -e "  ${YELLOW}  Playwright will attempt to start it via 'npm run dev'${NC}"
  fi

  echo ""
}

# Run tests based on argument
run_tests() {
  local PROJECT_FILTER=""
  local DESCRIPTION="Full QA Suite (All browsers, all viewports)"

  case "$1" in
    --chromium)
      PROJECT_FILTER="--project=chromium-desktop-1280 --project=chromium-desktop-1920 --project=chromium-desktop-2560 --project=chromium-mobile-375-portrait --project=chromium-mobile-428-portrait --project=chromium-mobile-375-landscape --project=chromium-mobile-428-landscape --project=chromium-tablet-768-portrait --project=chromium-tablet-768-landscape"
      DESCRIPTION="Chromium Only (all viewports)"
      ;;
    --firefox)
      PROJECT_FILTER="--project=firefox-desktop-1280 --project=firefox-desktop-1920"
      DESCRIPTION="Firefox Only"
      ;;
    --webkit)
      PROJECT_FILTER="--project=webkit-desktop-1280 --project=webkit-desktop-1920 --project=webkit-mobile-375-portrait --project=webkit-mobile-428-portrait --project=webkit-mobile-375-landscape --project=webkit-mobile-428-landscape --project=webkit-tablet-768-portrait --project=webkit-tablet-768-landscape"
      DESCRIPTION="WebKit Only (all viewports)"
      ;;
    --mobile)
      PROJECT_FILTER="--project=chromium-mobile-375-portrait --project=chromium-mobile-428-portrait --project=chromium-mobile-375-landscape --project=chromium-mobile-428-landscape --project=webkit-mobile-375-portrait --project=webkit-mobile-428-portrait --project=webkit-mobile-375-landscape --project=webkit-mobile-428-landscape"
      DESCRIPTION="Mobile Viewports (Chromium + WebKit)"
      ;;
    --tablet)
      PROJECT_FILTER="--project=chromium-tablet-768-portrait --project=chromium-tablet-768-landscape --project=webkit-tablet-768-portrait --project=webkit-tablet-768-landscape"
      DESCRIPTION="Tablet Viewports"
      ;;
    --desktop)
      PROJECT_FILTER="--project=chromium-desktop-1280 --project=chromium-desktop-1920 --project=chromium-desktop-2560 --project=firefox-desktop-1280 --project=firefox-desktop-1920 --project=webkit-desktop-1280 --project=webkit-desktop-1920"
      DESCRIPTION="Desktop Viewports (All Browsers)"
      ;;
    --pwa)
      PROJECT_FILTER="--project=pwa-chromium-mobile --project=pwa-chromium-desktop"
      DESCRIPTION="PWA Mode Tests"
      ;;
    --quick)
      PROJECT_FILTER="--project=chromium-desktop-1280"
      DESCRIPTION="Quick Smoke Test (Chromium 1280px)"
      ;;
    --report)
      echo -e "${BLUE}Opening QA Report...${NC}"
      npx playwright show-report "$QA_OUTPUT/playwright-report"
      exit 0
      ;;
    *)
      DESCRIPTION="Full QA Suite (All 22 browser+viewport combos)"
      ;;
  esac

  echo -e "${BLUE}Running: ${DESCRIPTION}${NC}"
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo ""

  # Run Playwright
  npx playwright test --config=playwright.config.ts $PROJECT_FILTER 2>&1 | tee "$QA_OUTPUT/qa-run.log"
  local EXIT_CODE=${PIPESTATUS[0]}

  echo ""
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

  if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ ALL TESTS PASSED${NC}"
  else
    echo -e "${RED}❌ SOME TESTS FAILED (exit code: $EXIT_CODE)${NC}"
  fi

  echo ""
  echo -e "${BLUE}Reports:${NC}"
  echo -e "  HTML Report: $QA_OUTPUT/playwright-report/index.html"
  echo -e "  JSON Results: $QA_OUTPUT/qa-results.json"
  echo -e "  Run Log: $QA_OUTPUT/qa-run.log"
  echo ""
  echo -e "  View report: ${YELLOW}npm run qa:report${NC}"

  return $EXIT_CODE
}

# Main
check_services
run_tests "$1"
