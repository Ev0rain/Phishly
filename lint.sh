#!/bin/bash
# Phishly Code Quality Check Script
# Runs black and flake8 on the entire codebase

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Track errors
ERRORS=0

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Phishly Code Quality Check${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Count Python files
PYTHON_FILES=$(find . -name "*.py" -type f -not -path "./.venv/*" -not -path "./venv/*" -not -path "*/__pycache__/*" -not -path "./.git/*" | wc -l)
echo -e "${BLUE}📁 Python files found:${NC} $PYTHON_FILES"
echo ""

# Run Black
echo -e "${YELLOW}🎨 Running Black (code formatter)...${NC}"
if uv run python -m black --check webadmin/*.py webadmin/**/*.py alembic/*.py alembic/**/*.py db/*.py redis/*.py worker/*.py 2>&1 | grep -v "VIRTUAL_ENV" > /tmp/black_output.txt; then
    REFORMATTED=$(grep "would be left unchanged" /tmp/black_output.txt | grep -oE "[0-9]+" | head -1)
    echo -e "   ${GREEN}✓ All $REFORMATTED files properly formatted${NC}"
else
    echo -e "   ${RED}✗ Formatting issues found:${NC}"
    cat /tmp/black_output.txt | grep "would reformat"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# Run Flake8
echo -e "${YELLOW}🔍 Running Flake8 (linter)...${NC}"
FLAKE8_OUTPUT=$(uv run python -m flake8 webadmin/*.py webadmin/**/*.py db/*.py redis/*.py worker/*.py \
    --max-line-length=100 \
    --extend-ignore=E203,W503,D100,D101,D200,D205,D400,D401 \
    --count 2>&1 | grep -v "VIRTUAL_ENV" || true)

ERROR_COUNT=$(echo "$FLAKE8_OUTPUT" | tail -1)

if [ "$ERROR_COUNT" -eq 0 ] 2>/dev/null; then
    echo -e "   ${GREEN}✓ No linting errors found${NC}"
else
    echo -e "   ${RED}✗ $ERROR_COUNT linting error(s) found:${NC}"
    echo "$FLAKE8_OUTPUT" | head -n -1
    ERRORS=$((ERRORS + 1))
fi
echo ""

# Summary
echo -e "${BLUE}========================================${NC}"
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed! Code is clean.${NC}"
    exit 0
else
    echo -e "${RED}❌ $ERRORS check(s) failed. Please fix the issues above.${NC}"
    echo ""
    echo "To auto-fix formatting issues, run:"
    echo "  uv run python -m black webadmin/ db/ redis/ worker/ alembic/"
    exit 1
fi
