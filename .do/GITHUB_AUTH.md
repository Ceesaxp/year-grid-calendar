# Connecting GitHub to Digital Ocean

Quick guide to authorize Digital Ocean to access your GitHub repositories.

## Why This Is Needed

Digital Ocean App Platform needs access to your GitHub repository to:
- Automatically deploy on git push
- Pull your source code for builds
- Set up webhooks for CI/CD

## Step-by-Step Instructions

### Method 1: Via Web Dashboard (Recommended)

1. **Go to Digital Ocean Apps**
   - Visit: https://cloud.digitalocean.com/apps
   - Click the green **"Create App"** button

2. **Select GitHub as Source**
   - Choose **"GitHub"** option
   - Click **"Manage Access"** or **"Authorize GitHub"**

3. **Authorize on GitHub**
   - You'll be redirected to GitHub
   - Log in to your GitHub account
   - Review the permissions Digital Ocean is requesting:
     - Read access to code
     - Write access to webhooks
     - Access to repository metadata

4. **Grant Repository Access**
   - Choose **"All repositories"** (easier), or
   - Choose **"Only select repositories"** (more secure)
   - Select `year-grid-calendar` if using selective access
   - Click **"Install & Authorize"**

5. **Complete Authorization**
   - You'll be redirected back to Digital Ocean
   - GitHub is now connected! ✅

6. **Return to CLI Deployment**
   - Now run `./deploy-do.sh` again
   - Choose option 1 (with GitHub integration)

### Method 2: From App Creation Flow

1. **Start Creating an App**
   ```bash
   # This will fail but guide you to authenticate
   doctl apps create --spec .do/app.yaml
   ```

2. **Follow the Error Message**
   - The error will contain a link to authorize GitHub
   - Click the link or visit: https://cloud.digitalocean.com/apps

3. **Complete Authorization** (same as Method 1, steps 3-5)

4. **Retry Deployment**
   ```bash
   ./deploy-do.sh
   ```

## Verify Connection

After authorizing, verify GitHub is connected:

1. **Via Dashboard:**
   - Go to: https://cloud.digitalocean.com/account/api
   - Look for "GitHub" under "Connected Accounts"
   - Status should show "Connected" with a green checkmark

2. **Via CLI:**
   ```bash
   # List your apps (should work without errors)
   doctl apps list
   ```

## Permissions Requested

Digital Ocean requests these GitHub permissions:

| Permission | Reason |
|------------|--------|
| **Read code** | To clone and build your repository |
| **Webhook write** | To deploy automatically on push |
| **Repo metadata** | To list branches and commits |
| **Deployments** | To create deployment statuses |

**Note:** Digital Ocean cannot:
- ❌ Modify your code
- ❌ Delete repositories
- ❌ Access private data outside the repo
- ❌ Push commits

## Troubleshooting

### "GitHub user not authenticated" Error

**Problem:**
```
Error: POST https://api.digitalocean.com/v2/apps: 400
GitHub user not authenticated
```

**Solution:**
1. Go to https://cloud.digitalocean.com/apps
2. Click "Create App" → "GitHub"
3. Complete authorization flow
4. Retry deployment

### "Repository not found" Error

**Problem:**
```
Error: repository not found or not accessible
```

**Solutions:**
1. **Check repository access:**
   - Go to: https://github.com/settings/installations
   - Find "DigitalOcean"
   - Click "Configure"
   - Ensure `year-grid-calendar` is selected

2. **Update app.yaml:**
   - Verify repo name: `ceesaxp/year-grid-calendar`
   - Verify branch: `main` (not `master`)

3. **Re-authorize:**
   - Revoke and re-grant access with all repos

### Can't Authorize (Private Repo)

If you're using a private repository:

1. Ensure you're the repo owner or have admin access
2. Organization repos may need org admin approval
3. Check organization settings allow third-party apps

**Alternative:** Use option 2 in `deploy-do.sh` for manual deployment without GitHub

## Revoke Access

To disconnect GitHub from Digital Ocean:

1. **On GitHub:**
   - Go to: https://github.com/settings/installations
   - Find "DigitalOcean"
   - Click "Configure" → "Uninstall"

2. **On Digital Ocean:**
   - Go to: https://cloud.digitalocean.com/account/api
   - Under "Connected Accounts" → "GitHub"
   - Click "Disconnect"

## Alternative: Deploy Without GitHub

If you prefer not to connect GitHub:

```bash
./deploy-do.sh
# Choose option 2: "Create new app (without GitHub)"
```

**Pros:**
- No GitHub authorization needed
- More control over deployments

**Cons:**
- No automatic deploys on push
- Manual updates required
- Can't see GitHub commits in DO dashboard

## Security Best Practices

1. **Use selective repository access** (not all repos)
2. **Review permissions** before authorizing
3. **Audit connected apps** periodically on GitHub
4. **Revoke access** when no longer needed
5. **Use deploy keys** for extra security (advanced)

## Next Steps

After connecting GitHub:

1. ✅ GitHub authorization complete
2. Run deployment script:
   ```bash
   ./deploy-do.sh
   ```
3. Choose option 1 (with GitHub integration)
4. Wait for deployment (5-10 minutes)
5. Access your app at provided URL

## Support

- **GitHub Help:** https://docs.github.com/en/developers/apps
- **DO Help:** https://docs.digitalocean.com/products/app-platform/how-to/manage-github-access/
- **Community:** https://www.digitalocean.com/community

## Quick Reference

```bash
# Authorize GitHub (via browser)
open https://cloud.digitalocean.com/apps

# Verify connection
doctl apps list

# Deploy with GitHub
./deploy-do.sh  # Choose option 1

# Deploy without GitHub  
./deploy-do.sh  # Choose option 2
```

---

**Last Updated:** 2024
**Estimated Time:** 2-3 minutes
