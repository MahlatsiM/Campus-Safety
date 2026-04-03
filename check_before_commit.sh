#!/bin/bash

# Pre-Commit Security Check Script
# Run this before EVERY git commit to ensure no secrets are leaked

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

FAILED=0

echo "========================================"
echo "🔒 PRE-COMMIT SECURITY CHECK"
echo "========================================"
echo ""

# Check 1: .env file should not be staged
echo "1️⃣  Checking for .env in staged files..."
if git diff --cached --name-only | grep -q "^.env$"; then
    echo -e "${RED}❌ CRITICAL: .env file is staged for commit!${NC}"
    echo "   Run: git reset .env"
    FAILED=1
else
    echo -e "${GREEN}✅ .env not staged${NC}"
fi

# Check 2: Search for hardcoded passwords
echo ""
echo "2️⃣  Checking for hardcoded passwords..."
if git diff --cached | grep -i "password.*=.*['\"]" | grep -v "your_secure_password"; then
    echo -e "${RED}❌ Found potential hardcoded password!${NC}"
    FAILED=1
else
    echo -e "${GREEN}✅ No hardcoded passwords found${NC}"
fi

# Check 3: Search for API keys
echo ""
echo "3️⃣  Checking for API keys..."
SUSPICIOUS_PATTERNS=(
    "api[_-]?key.*=.*['\"][a-zA-Z0-9]{20,}"
    "GEOAPIFY.*=.*['\"][a-zA-Z0-9]+"
    "[a-f0-9]{32}"
)

for pattern in "${SUSPICIOUS_PATTERNS[@]}"; do
    if git diff --cached | grep -iE "$pattern" | grep -v "your.*key.*here" | grep -v "example"; then
        echo -e "${RED}❌ Found potential API key!${NC}"
        FAILED=1
        break
    fi
done

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ No API keys found${NC}"
fi

# Check 4: Database credentials
echo ""
echo "4️⃣  Checking for database credentials..."
if git diff --cached | grep -E "(host|user|password).*=.*(localhost|postgres|Mahlatsi)" | grep -v "os.getenv" | grep -v ".env"; then
    echo -e "${RED}❌ Found hardcoded database credentials!${NC}"
    FAILED=1
else
    echo -e "${GREEN}✅ No hardcoded credentials${NC}"
fi

# Check 5: Large files
echo ""
echo "5️⃣  Checking for large files..."
LARGE_FILES=$(git diff --cached --name-only | while read file; do
    if [ -f "$file" ]; then
        size=$(wc -c < "$file")
        if [ $size -gt 1048576 ]; then  # 1MB
            echo "$file ($(( size / 1024 ))KB)"
        fi
    fi
done)

if [ -n "$LARGE_FILES" ]; then
    echo -e "${YELLOW}⚠️  Large files found:${NC}"
    echo "$LARGE_FILES"
    echo "   Consider using Git LFS or .gitignore"
else
    echo -e "${GREEN}✅ No large files${NC}"
fi

# Check 6: .gitignore exists
echo ""
echo "6️⃣  Checking .gitignore..."
if [ ! -f .gitignore ]; then
    echo -e "${RED}❌ .gitignore file missing!${NC}"
    FAILED=1
elif ! grep -q "^.env$" .gitignore; then
    echo -e "${RED}❌ .env not in .gitignore!${NC}"
    FAILED=1
else
    echo -e "${GREEN}✅ .gitignore properly configured${NC}"
fi

# Check 7: Python cache files
echo ""
echo "7️⃣  Checking for Python cache files..."
if git diff --cached --name-only | grep -E "(__pycache__|\.pyc$)"; then
    echo -e "${YELLOW}⚠️  Python cache files staged${NC}"
    echo "   Run: git rm -r --cached __pycache__/"
else
    echo -e "${GREEN}✅ No cache files staged${NC}"
fi

# Check 8: Database files
echo ""
echo "8️⃣  Checking for database files..."
if git diff --cached --name-only | grep -E "\.(db|sqlite|sqlite3)$"; then
    echo -e "${RED}❌ Database file staged!${NC}"
    FAILED=1
else
    echo -e "${GREEN}✅ No database files staged${NC}"
fi

# Check 9: Common secrets in code
echo ""
echo "9️⃣  Checking for common secret patterns..."
SECRET_PATTERNS=(
    "sk-[a-zA-Z0-9]{48}"  # OpenAI
    "ghp_[a-zA-Z0-9]{36}"  # GitHub PAT
    "AKIA[0-9A-Z]{16}"     # AWS Access Key
)

for pattern in "${SECRET_PATTERNS[@]}"; do
    if git diff --cached | grep -E "$pattern"; then
        echo -e "${RED}❌ Found potential secret token!${NC}"
        FAILED=1
        break
    fi
done

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ No secret tokens found${NC}"
fi

# Check 10: TODO/FIXME comments
echo ""
echo "🔟 Checking for TODO/FIXME comments..."
TODO_COUNT=$(git diff --cached | grep -c "TODO\|FIXME" || true)
if [ $TODO_COUNT -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Found $TODO_COUNT TODO/FIXME comments${NC}"
    echo "   Consider addressing before commit"
else
    echo -e "${GREEN}✅ No TODO comments${NC}"
fi

# Summary
echo ""
echo "========================================"
if [ $FAILED -eq 1 ]; then
    echo -e "${RED}❌ SECURITY CHECK FAILED${NC}"
    echo "========================================"
    echo ""
    echo "🚫 DO NOT COMMIT until issues are resolved!"
    echo ""
    echo "Common fixes:"
    echo "  - git reset .env"
    echo "  - Replace hardcoded values with os.getenv()"
    echo "  - Move secrets to .env file"
    echo "  - Update .gitignore"
    echo ""
    exit 1
else
    echo -e "${GREEN}✅ ALL CHECKS PASSED${NC}"
    echo "========================================"
    echo ""
    echo "Safe to commit! 🎉"
    echo ""
    echo "Reminder:"
    echo "  - Write clear commit message"
    echo "  - Double-check staged files: git status"
    echo "  - Push to correct branch"
    echo ""
    exit 0
fi