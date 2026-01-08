# SEO Deployment Checklist

Complete this checklist when deploying the Year Grid Calendar Generator to ensure all SEO features are properly configured.

## Pre-Deployment

### 1. Environment Configuration

- [ ] Set `BASE_URL` environment variable to production domain
  ```bash
  export BASE_URL=https://yourdomain.com
  ```
  Or in Docker/Docker Compose:
  ```yaml
  environment:
    - BASE_URL=https://yourdomain.com
  ```

- [ ] Verify BASE_URL is correct (no trailing slash)
- [ ] Test that BASE_URL environment variable is being read correctly

### 2. Content Review

- [ ] Review meta description (should be compelling and under 160 characters)
- [ ] Review keywords (ensure they match your target audience)
- [ ] Verify OG image exists and is high quality (`/static/android-chrome-512x512.png`)
- [ ] Check that all links are HTTPS (not HTTP)
- [ ] Ensure page title is descriptive and includes keywords

### 3. Local Testing

- [ ] Start application locally
- [ ] Access `http://localhost:8000/` and verify page loads
- [ ] Access `http://localhost:8000/robots.txt` - should return plain text
- [ ] Access `http://localhost:8000/sitemap.xml` - should return XML
- [ ] View page source and verify:
  - [ ] Meta tags are present
  - [ ] Open Graph tags have correct BASE_URL
  - [ ] Twitter Card tags are present
  - [ ] JSON-LD structured data is valid JSON
  - [ ] Canonical URL points to production domain

### 4. Code Quality

- [ ] Run diagnostics: `python -m py_compile web/app.py`
- [ ] No syntax errors in Python code
- [ ] All imports resolve correctly
- [ ] FastAPI app starts without errors

## Deployment

### 5. Deploy Application

- [ ] Deploy to production environment
- [ ] Verify application is accessible at production URL
- [ ] Check application logs for errors
- [ ] Test homepage loads correctly
- [ ] Test PDF generation works
- [ ] Verify static files (favicons, images) are served correctly

### 6. DNS & SSL

- [ ] Domain DNS is properly configured
- [ ] SSL certificate is valid and active
- [ ] HTTPS redirect is working (HTTP → HTTPS)
- [ ] www redirect configured (if applicable)

## Post-Deployment Validation

### 7. Endpoint Testing

- [ ] `https://yourdomain.com/` loads successfully
- [ ] `https://yourdomain.com/robots.txt` returns correct content
- [ ] `https://yourdomain.com/sitemap.xml` returns valid XML
- [ ] `https://yourdomain.com/health` returns healthy status
- [ ] All URLs in sitemap are accessible

### 8. Meta Tags Validation

View page source and verify:
- [ ] Title tag is correct and includes production domain
- [ ] Meta description is present and descriptive
- [ ] Canonical URL points to `https://yourdomain.com/`
- [ ] All Open Graph URLs use production domain (not localhost)
- [ ] All Twitter Card URLs use production domain
- [ ] JSON-LD structured data contains production URL

### 9. Social Media Preview Testing

Test with actual tools:

**Facebook/LinkedIn:**
- [ ] Go to https://developers.facebook.com/tools/debug/
- [ ] Enter your production URL
- [ ] Click "Scrape Again" to refresh cache
- [ ] Verify:
  - [ ] Image displays correctly
  - [ ] Title is correct
  - [ ] Description is compelling
  - [ ] URL is correct

**Twitter:**
- [ ] Go to https://cards-dev.twitter.com/validator
- [ ] Enter your production URL
- [ ] Verify:
  - [ ] Card preview displays correctly
  - [ ] Image loads
  - [ ] Title and description are correct

**Generic Testing:**
- [ ] Use https://www.opengraph.xyz/ to test overall preview
- [ ] Share link on Slack/Discord to test preview

### 10. Structured Data Validation

- [ ] Go to https://search.google.com/test/rich-results
- [ ] Enter your production URL
- [ ] Verify no errors in structured data
- [ ] Check that WebApplication type is recognized
- [ ] Verify feature list is parsed correctly

Alternative validators:
- [ ] https://validator.schema.org/
- [ ] https://search.google.com/structured-data/testing-tool

### 11. SEO Audit

**Google Lighthouse:**
- [ ] Open Chrome DevTools (F12)
- [ ] Navigate to Lighthouse tab
- [ ] Run audit for "Desktop" and "Mobile"
- [ ] SEO score should be 90+
- [ ] Address any critical issues

**PageSpeed Insights:**
- [ ] Go to https://pagespeed.web.dev/
- [ ] Enter your production URL
- [ ] Check both Mobile and Desktop scores
- [ ] Review SEO suggestions

### 12. Accessibility Check

- [ ] Lighthouse Accessibility score is 90+
- [ ] Keyboard navigation works
- [ ] Screen reader compatibility (test with NVDA/VoiceOver)
- [ ] Color contrast is sufficient
- [ ] All form fields have labels
- [ ] ARIA labels are present where needed

## Search Engine Registration

### 13. Google Search Console

- [ ] Add property for your domain
- [ ] Verify ownership (DNS, HTML file, or HTML tag method)
- [ ] Submit sitemap: `https://yourdomain.com/sitemap.xml`
- [ ] Request indexing for homepage
- [ ] Set preferred domain (www vs non-www)
- [ ] Monitor for crawl errors

### 14. Bing Webmaster Tools

- [ ] Sign up at https://www.bing.com/webmasters
- [ ] Add and verify your site
- [ ] Submit sitemap: `https://yourdomain.com/sitemap.xml`
- [ ] Configure URL inspection tool

### 15. Other Search Engines (Optional)

- [ ] Yandex Webmaster (if targeting Russian market)
- [ ] Baidu Webmaster (if targeting Chinese market)

## Monitoring Setup

### 16. Analytics

- [ ] Google Analytics installed (if desired)
- [ ] Custom events set up for:
  - [ ] Calendar generation
  - [ ] File downloads
  - [ ] Form submissions
- [ ] Goals configured (if using GA)
- [ ] UTM parameters tested

### 17. Search Console Monitoring

Configure alerts for:
- [ ] Indexing errors
- [ ] Security issues
- [ ] Manual actions
- [ ] Mobile usability issues

### 18. Performance Monitoring

- [ ] Set up uptime monitoring (UptimeRobot, Pingdom, etc.)
- [ ] Configure error logging/tracking
- [ ] Set up performance monitoring
- [ ] Create alerting for downtime

## Content & Marketing

### 19. Initial Content

- [ ] Create social media posts announcing launch
- [ ] Prepare email announcement (if applicable)
- [ ] Write blog post about the tool (if you have a blog)
- [ ] Create tutorial/how-to content

### 20. Backlink Strategy

- [ ] Submit to tool directories
- [ ] Post on Product Hunt (if appropriate)
- [ ] Share on Reddit (relevant subreddits)
- [ ] Share on Hacker News (Show HN)
- [ ] Add to GitHub Awesome Lists

## Ongoing Maintenance

### 21. Weekly Tasks

- [ ] Check Google Search Console for errors
- [ ] Review organic search traffic
- [ ] Monitor site uptime
- [ ] Check for broken links

### 22. Monthly Tasks

- [ ] Review search rankings for target keywords
- [ ] Update sitemap lastmod date (if content changed)
- [ ] Analyze social media referral traffic
- [ ] Review and optimize meta descriptions based on CTR
- [ ] Check competitor rankings

### 23. Quarterly Tasks

- [ ] Run full SEO audit
- [ ] Review and update keywords
- [ ] Update structured data if needed
- [ ] Create new content/features
- [ ] Analyze user behavior and optimize

## Troubleshooting

### Common Issues

**Issue: Robots.txt not accessible**
- Check web server configuration
- Verify endpoint is registered in FastAPI
- Check firewall/CDN settings

**Issue: Social media previews not updating**
- Clear cache in Facebook Debugger
- Force refresh in Twitter Card Validator
- Check that OG tags are in HTML <head>

**Issue: Not appearing in search results**
- Wait 2-4 weeks for initial indexing
- Check robots.txt isn't blocking crawlers
- Verify sitemap was submitted successfully
- Check Google Search Console for indexing errors

**Issue: Low SEO score in Lighthouse**
- Ensure meta description is 150-160 characters
- Add alt text to all images
- Fix any broken links
- Improve page load speed

**Issue: Structured data errors**
- Validate JSON with https://jsonlint.com/
- Check Schema.org documentation
- Use Google Rich Results Test for specific errors

## Success Metrics

Track these KPIs:

**Week 1-2:**
- [ ] Site indexed by Google
- [ ] Sitemap processed successfully
- [ ] No critical errors in Search Console

**Month 1:**
- [ ] 10+ indexed pages (including cached versions)
- [ ] First organic visitors
- [ ] Social shares tracked

**Month 3:**
- [ ] 100+ organic impressions
- [ ] Ranking for brand name
- [ ] Growing organic traffic trend

**Month 6:**
- [ ] 500+ organic impressions
- [ ] Ranking for some long-tail keywords
- [ ] Measurable organic traffic
- [ ] Good CTR (2-5%) from search

## Resources

- **Documentation**: `SEO_IMPROVEMENTS.md` (detailed docs)
- **Quick Reference**: `SEO_QUICK_REFERENCE.md` (cheat sheet)
- **Summary**: `SUMMARY.md` (overview)
- **Tests**: `test_seo.py` (automated testing)

## Sign-off

- [ ] All checklist items completed
- [ ] Site is live and accessible
- [ ] SEO features verified and working
- [ ] Monitoring configured
- [ ] Team notified of launch

**Deployed by:** ___________________  
**Date:** ___________________  
**Production URL:** ___________________  
**Search Console:** [ ] Configured  
**Analytics:** [ ] Configured  

---

**Version:** 1.0  
**Last Updated:** 2026-01-08  
**Status:** Ready for Use
