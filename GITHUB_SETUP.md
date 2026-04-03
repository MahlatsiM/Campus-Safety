# GitHub Setup Guide

## Repository Description (Short - 350 chars max)

```
Real-time campus safety platform built with Streamlit, Kafka & PostgreSQL. Students report incidents with geolocation, view interactive safety maps, and track trends. Features secure authentication, rate limiting, and event streaming architecture. Demo-ready with synthetic data generation.
```

## Topics/Tags

```
streamlit
kafka
postgresql
python
real-time
safety
geolocation
data-streaming
event-driven
dashboard
plotly
docker
campus-safety
incident-reporting
```

## Pre-Commit Checklist

Before pushing to GitHub, **VERIFY** you've completed ALL of these:

### 🔒 Security (CRITICAL)

- [ ] `.env` file is in `.gitignore` (VERIFY IT'S NOT COMMITTED!)
- [ ] No passwords in any Python files
- [ ] No API keys in any Python files  
- [ ] `.env.example` has placeholder values only
- [ ] Run: `git log --all -- .env` to ensure .env was never committed
- [ ] If .env was committed, you MUST purge it from history:
  ```bash
  git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all
  ```

### 📁 Required Files

- [ ] `.env.example` exists with all variables
- [ ] `.gitignore` includes .env and other sensitive files
- [ ] `requirements.txt` with pinned versions
- [ ] `README.md` complete and accurate
- [ ] `setup.sh` is executable: `chmod +x setup.sh`
- [ ] `init_db.py` runs without errors
- [ ] `schema.sql` is up to date
- [ ] `docker-compose.yml` uses environment variables

### 🧪 Testing

- [ ] Fresh clone test: Clone to new directory and follow README
- [ ] Database initialization works
- [ ] Docker services start successfully
- [ ] Producer generates demo data
- [ ] Consumer processes messages
- [ ] Streamlit app loads without errors
- [ ] Authentication works (register, login, logout)
- [ ] Report submission works
- [ ] Maps display correctly

### 📝 Documentation

- [ ] README has clear installation steps
- [ ] All environment variables documented
- [ ] API key setup instructions included
- [ ] Known limitations listed
- [ ] Security warnings present
- [ ] Contribution guidelines (if applicable)
- [ ] License file exists

## Initial Git Commands

```bash
# Initialize git (if not already done)
git init

# Add files (DOUBLE CHECK .env IS NOT INCLUDED!)
git add .

# Verify .env is NOT staged
git status

# If .env appears, run:
git reset .env

# Commit
git commit -m "Initial commit: Campus Safety Dashboard"

# Create GitHub repo (via web or CLI)
# Then add remote and push
git remote add origin https://github.com/yourusername/campus-safety-dashboard.git
git branch -M main
git push -u origin main
```

## GitHub Repository Setup

### Repository Settings

1. **About Section**:
   - Add description (use the short one above)
   - Add website: Your demo URL (if deployed)
   - Add topics/tags

2. **Security**:
   - Enable "Private vulnerability reporting" (Settings → Security)
   - Add `.env` to "Secrets scanning" exclusions if needed

3. **Branch Protection** (optional but recommended):
   - Require pull request reviews
   - Require status checks to pass

### Create These GitHub Issues (For Tracking)

```markdown
## Enhancement Ideas
- [ ] Add email notifications for nearby incidents
- [ ] Implement admin dashboard
- [ ] Add mobile app support
- [ ] ML-based incident prediction
- [ ] Real-time websocket updates

## Known Bugs
- [ ] Map doesn't center properly on first load
- [ ] Session state clears on page refresh
- [ ] Duplicate report submissions if button clicked twice

## Documentation Needed
- [ ] API documentation
- [ ] Deployment guide for production
- [ ] Video demo/walkthrough
- [ ] Architecture diagrams
```

## Repository Structure Checklist

Your final repository should look like this:

```
campus-safety-dashboard/
├── .env.example              ✅
├── .gitignore                ✅
├── README.md                 ✅
├── requirements.txt          ✅
├── setup.sh                  ✅
├── init_db.py                ✅
├── schema.sql                ✅
├── docker-compose.yml        ✅
├── app.py                    ✅
├── consumer.py               ✅
├── producer.py               ✅
├── auth/
│   └── auth_handlers.py      ✅
├── LICENSE                   ⚠️ (Add if open source)
└── .github/                  ⚠️ (Optional)
    └── workflows/
        └── ci.yml            ⚠️ (Optional CI/CD)
```

## Post-Push Verification

After pushing, verify:

1. Clone your repo in a fresh directory
2. Follow your own README instructions
3. Verify everything works
4. Check GitHub doesn't show any secrets in code

## Common Mistakes to Avoid

❌ **DON'T**:
- Commit `.env` file
- Hardcode passwords or API keys
- Push large database dumps
- Commit virtual environment (`venv/`)
- Include proprietary or sensitive data
- Commit `.DS_Store` or IDE files

✅ **DO**:
- Use `.env.example` as template
- Document all environment variables
- Add clear security warnings
- Test fresh installation
- Keep dependencies updated
- Use meaningful commit messages

## Security Incident Response

If you accidentally committed secrets:

### Immediate Actions:
1. **Revoke compromised credentials immediately**
2. **Remove from history**:
   ```bash
   # For .env file
   git filter-branch --force --index-filter \
   "git rm --cached --ignore-unmatch .env" \
   --prune-empty --tag-name-filter cat -- --all
   
   # Force push
   git push origin --force --all
   ```
3. **Rotate all secrets**:
   - Generate new database password
   - Get new Geoapify API key
   - Update all environments

### Prevention:
- Use `git-secrets` tool
- Enable pre-commit hooks
- Regular security audits

## License Recommendations

For educational/demo projects:

**MIT License** (most permissive):
- ✅ Commercial use allowed
- ✅ Modification allowed
- ✅ Distribution allowed
- ✅ Private use allowed

**Apache 2.0** (with patent grant):
- Similar to MIT but with explicit patent rights

Add a `LICENSE` file with your chosen license.

## Demo Deployment Options

For showcasing your project:

1. **Streamlit Community Cloud** (Free tier):
   - Limited resources
   - No Kafka support
   - Requires public GitHub repo

2. **Heroku** (Paid):
   - Supports Docker
   - Can run Kafka
   - $7-$50/month

3. **DigitalOcean** (Most flexible):
   - Full Docker support
   - ~$5-$20/month
   - Complete control

4. **Local Demo Only**:
   - Most secure for development
   - Use port forwarding for remote demos
   - No hosting costs

## Final Checklist Before Publishing

- [ ] All secrets removed from code
- [ ] `.gitignore` is comprehensive
- [ ] README is complete and tested
- [ ] Fresh installation tested successfully
- [ ] All links in README work
- [ ] Screenshots/demo GIFs added (optional but recommended)
- [ ] Code is commented where necessary
- [ ] No TODO comments in production code
- [ ] Version numbers are correct
- [ ] Contributors are credited

---

**Remember**: Once something is on GitHub, it's essentially public forever, even if you delete it. Triple-check before pushing!