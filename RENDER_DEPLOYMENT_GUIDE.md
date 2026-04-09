# Render.com Deployment Guide

This guide walks you through deploying your Salon/Spa/Gym SaaS platform to Render.com.

## Prerequisites

1. **GitHub Account** - Your code must be in a GitHub repository
2. **Render Account** - Sign up at https://render.com (free tier available)
3. **MongoDB Atlas Account** - Sign up at https://www.mongodb.com/cloud/atlas (free tier available)
4. **Paystack Account** - For payments (https://paystack.com)
5. **Cloudinary Account** - For media uploads (https://cloudinary.com)
6. **Resend Account** - For emails (https://resend.com)

## Step 1: Setup MongoDB Atlas

1. Go to https://www.mongodb.com/cloud/atlas
2. Create a free cluster (M0 Sandbox - FREE)
3. Create a database user:
   - Click "Database Access" → "Add New Database User"
   - Username: `salon_user`
   - Password: Generate a strong password (save it!)
4. Whitelist all IPs (for Render):
   - Click "Network Access" → "Add IP Address"
   - Click "Allow Access from Anywhere" (0.0.0.0/0)
   - This is needed because Render uses dynamic IPs
5. Get your connection string:
   - Click "Database" → "Connect" → "Connect your application"
   - Copy the connection string (looks like: `mongodb+srv://salon_user:<password>@cluster0.xxxxx.mongodb.net/`)
   - Replace `<password>` with your actual password
   - Add database name at the end: `mongodb+srv://salon_user:password@cluster0.xxxxx.mongodb.net/salon_db`

## Step 2: Push Code to GitHub

```bash
# Initialize git if not already done
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit for Render deployment"

# Add remote (replace with your repo URL)
git remote add origin https://github.com/yourusername/your-repo.git

# Push to GitHub
git push -u origin main
```

## Step 3: Deploy to Render Using Blueprint

1. Go to https://dashboard.render.com
2. Click "New" → "Blueprint"
3. Connect your GitHub repository
4. Render will detect the `render.yaml` file
5. Click "Apply" to create all services

## Step 4: Configure Environment Variables

After deployment, you need to set the environment variables that are marked as `sync: false`:

### Backend Service Environment Variables

Go to your `salon-backend` service → "Environment" tab:

```bash
# Database (from MongoDB Atlas)
DATABASE_URL=mongodb+srv://salon_user:password@cluster0.xxxxx.mongodb.net/salon_db
DATABASE_NAME=salon_db

# Paystack (from https://dashboard.paystack.com/#/settings/developer)
PAYSTACK_LIVE_SECRET_KEY=sk_live_xxxxx
PAYSTACK_LIVE_PUBLIC_KEY=pk_live_xxxxx
PAYSTACK_WEBHOOK_SECRET=xxxxx

# Cloudinary (from https://cloudinary.com/console)
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# Resend (from https://resend.com/api-keys)
RESEND_API_KEY=re_xxxxx
EMAIL_FROM=Your Salon <noreply@yourdomain.com>

# Termii (optional - for SMS)
TERMII_API_KEY=your_termii_key
TERMII_SENDER_ID=YourSenderID
```

### Celery Worker Environment Variables

Go to your `salon-celery-worker` service → "Environment" tab:

```bash
# Copy the same values from backend
DATABASE_URL=mongodb+srv://salon_user:password@cluster0.xxxxx.mongodb.net/salon_db
DATABASE_NAME=salon_db
JWT_SECRET_KEY=<copy from backend>
SECRET_KEY=<copy from backend>
```

## Step 5: Update Frontend URLs

After backend deploys, you'll get a URL like: `https://salon-backend.onrender.com`

1. Go to `salon-frontend` service → "Environment" tab
2. Update `VITE_API_URL` to your actual backend URL:
   ```
   VITE_API_URL=https://salon-backend.onrender.com/api/v1
   ```

3. Go back to `salon-backend` service → "Environment" tab
4. Update these variables:
   ```
   FRONTEND_URL=https://salon-frontend.onrender.com
   PLATFORM_DOMAIN=salon-frontend.onrender.com
   CORS_ORIGINS=https://salon-frontend.onrender.com
   ```

## Step 6: Configure Paystack Webhooks

1. Go to https://dashboard.paystack.com/#/settings/developer
2. Set webhook URL to: `https://salon-backend.onrender.com/api/v1/webhooks/paystack`
3. Copy the webhook secret and add it to your backend environment variables

## Step 7: Test Your Deployment

1. Visit your frontend URL: `https://salon-frontend.onrender.com`
2. Try registering a new tenant
3. Check backend logs in Render dashboard if issues occur

## Important Notes

### Free Tier Limitations

- **Backend & Worker**: Will spin down after 15 minutes of inactivity (cold starts take ~30 seconds)
- **Redis**: 25MB storage limit
- **No RabbitMQ**: Render doesn't support RabbitMQ on free tier. Your app uses Redis as the Celery broker instead (already configured in code)

### Cold Starts

Free tier services sleep after inactivity. First request after sleep takes 30-60 seconds. Solutions:
- Upgrade to paid plan ($7/month per service)
- Use a cron job to ping your app every 10 minutes (keeps it awake)

### Subdomain Routing

Your app uses tenant subdomains (e.g., `salon1.yourdomain.com`). On Render free tier:
- You get: `salon-frontend.onrender.com`
- Subdomains won't work without a custom domain

To enable subdomains:
1. Buy a domain (e.g., from Namecheap, GoDaddy)
2. Add custom domain in Render: `yourdomain.com`
3. Add wildcard subdomain: `*.yourdomain.com`
4. Update DNS records as instructed by Render
5. Update `PLATFORM_DOMAIN` env var to `yourdomain.com`

### Database Backups

MongoDB Atlas free tier includes:
- Automatic backups (retained for 2 days)
- Point-in-time recovery (paid feature)

### Monitoring

Render provides:
- Service logs (last 7 days on free tier)
- Metrics (CPU, memory, requests)
- Email alerts for service failures

## Troubleshooting

### Backend won't start

Check logs in Render dashboard:
```bash
# Common issues:
1. Missing environment variables
2. Database connection failed (check MongoDB Atlas IP whitelist)
3. Redis connection failed (check Redis service is running)
```

### Frontend shows API errors

1. Check `VITE_API_URL` is correct
2. Check CORS settings in backend
3. Check backend is running (visit `/health` endpoint)

### Celery worker not processing jobs

1. Check worker logs in Render dashboard
2. Verify `REDIS_URL` is set correctly
3. Check Redis service is running

### Webhooks not working

1. Verify webhook URL in Paystack dashboard
2. Check webhook secret matches environment variable
3. Check backend logs for webhook errors

## Scaling Up

When you're ready to upgrade:

1. **Backend**: Upgrade to Starter plan ($7/month)
   - No cold starts
   - Better performance
   
2. **Database**: Upgrade MongoDB Atlas to M10+ ($57/month)
   - More storage
   - Better performance
   - Advanced backups

3. **Redis**: Upgrade to paid plan ($10/month)
   - More memory
   - Better performance

4. **Custom Domain**: Add your domain
   - Professional appearance
   - Subdomain support

## Alternative: RabbitMQ Setup

If you need RabbitMQ (not available on Render free tier):

1. Use CloudAMQP (free tier available): https://www.cloudamqp.com
2. Get connection URL
3. Add to backend environment:
   ```
   RABBITMQ_URL=amqps://user:pass@host/vhost
   ```

## Support

- Render Docs: https://render.com/docs
- MongoDB Atlas Docs: https://docs.atlas.mongodb.com
- Paystack Docs: https://paystack.com/docs

## Cost Summary (Free Tier)

- Render: $0 (3 services: backend, worker, frontend)
- MongoDB Atlas: $0 (M0 cluster)
- Redis: $0 (included with Render)
- Cloudinary: $0 (free tier)
- Resend: $0 (100 emails/day)
- Paystack: $0 (pay per transaction)

**Total: $0/month** (with limitations)

## Next Steps After Deployment

1. Set up custom domain
2. Configure email templates
3. Test payment flow
4. Set up monitoring/alerts
5. Create pricing plans in admin panel
6. Invite team members
