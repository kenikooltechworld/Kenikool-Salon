# PWA Implementation Guide

## Overview

This document describes the Progressive Web App (PWA) implementation for the Salon Booking System. The PWA features enable a native app-like experience on mobile devices with offline support, push notifications, and installability.

## Features Implemented

### 1. PWA Manifest (`public/manifest.json`)
- App metadata (name, description, icons)
- Display mode: standalone (full-screen app experience)
- Theme colors for browser UI
- App shortcuts for quick actions
- Screenshots for app stores

### 2. Service Worker (`public/service-worker.js`)
- **Caching Strategy:**
  - Static assets: Cache-first with network fallback
  - API requests: Network-first with cache fallback
  - Offline fallback page for failed requests

- **Background Sync:**
  - Queues failed bookings for retry when online
  - Automatic retry with exponential backoff

- **Push Notifications:**
  - Handles incoming push messages
  - Shows notification with actions
  - Handles notification clicks

### 3. Offline Support
- Offline fallback page (`public/offline.html`)
- Cached static assets for offline browsing
- Background sync for pending bookings
- Online/offline status detection

### 4. Install Prompts
- **InstallPWAPrompt Component:**
  - Shows after 30 seconds on mobile devices
  - Platform-specific instructions (iOS vs Android)
  - Dismissible with 7-day cooldown
  - Benefits list to encourage installation

- **PWAUpdatePrompt Component:**
  - Notifies users of new versions
  - One-click update with page reload
  - Automatic service worker update

### 5. React Hooks
- **usePWA:** Install detection and prompt management
- **usePushNotifications:** Push notification permissions and subscriptions

### 6. Mobile Optimizations
- Touch-friendly button sizes (44x44px minimum)
- Safe area insets for iOS notch
- Viewport meta tags for proper scaling
- Apple-specific meta tags for iOS

## File Structure

```
salon/
├── public/
│   ├── manifest.json              # PWA manifest
│   ├── service-worker.js          # Service worker
│   ├── offline.html               # Offline fallback page
│   ├── generate-icons.html        # Icon generator tool
│   └── icon-*.png                 # App icons (to be generated)
├── src/
│   ├── lib/pwa/
│   │   ├── install.ts             # Install utilities
│   │   ├── notifications.ts       # Push notification utilities
│   │   └── register.ts            # Service worker registration
│   ├── hooks/
│   │   ├── usePWA.ts              # PWA install hook
│   │   └── usePushNotifications.ts # Push notifications hook
│   └── components/public/
│       ├── InstallPWAPrompt.tsx   # Install prompt component
│       └── PWAUpdatePrompt.tsx    # Update prompt component
└── index.html                     # Updated with PWA meta tags
```

## Setup Instructions

### 1. Generate App Icons

Open `public/generate-icons.html` in a browser:

```bash
# Navigate to the file in your browser
open salon/public/generate-icons.html
```

1. Enter your salon's initial (e.g., "S" for Salon)
2. Choose brand colors
3. Click "Generate Icons"
4. Click "Download All" to save all icon sizes
5. Place the downloaded icons in `salon/public/`

**Recommended:** Replace generated icons with your actual salon logo in PNG format.

### 2. Configure Push Notifications (Optional)

To enable push notifications, you need VAPID keys:

```bash
# Generate VAPID keys (backend)
cd backend
python -c "from pywebpush import webpush; print(webpush.generate_vapid_keys())"
```

Add to backend `.env`:
```
VAPID_PUBLIC_KEY=your_public_key
VAPID_PRIVATE_KEY=your_private_key
VAPID_CLAIM_EMAIL=mailto:your-email@example.com
```

### 3. Test PWA Locally

PWA features require HTTPS or localhost:

```bash
# Development (localhost works)
cd salon
npm run dev

# Production build
npm run build
npm run preview
```

### 4. Test Installation

**On Android (Chrome):**
1. Open the app in Chrome
2. Wait for install prompt or tap menu → "Install app"
3. Confirm installation

**On iOS (Safari):**
1. Open the app in Safari
2. Tap Share button
3. Tap "Add to Home Screen"
4. Confirm

### 5. Test Offline Mode

1. Install the PWA
2. Open DevTools → Application → Service Workers
3. Check "Offline" checkbox
4. Navigate the app - should show offline page for new requests
5. Previously cached pages should still work

## Usage

### Install Prompt

The install prompt appears automatically after 30 seconds on mobile devices. To customize:

```tsx
<InstallPWAPrompt 
  delay={60000}        // Show after 60 seconds
  position="top"       // Show at top instead of bottom
/>
```

### Push Notifications

To subscribe users to push notifications:

```tsx
import { usePushNotifications } from '@/hooks/usePushNotifications';

function MyComponent() {
  const { subscribe, permission } = usePushNotifications();
  
  const handleSubscribe = async () => {
    const success = await subscribe('YOUR_VAPID_PUBLIC_KEY');
    if (success) {
      console.log('Subscribed to push notifications');
    }
  };
  
  return (
    <button onClick={handleSubscribe}>
      Enable Notifications
    </button>
  );
}
```

### Check PWA Status

```tsx
import { usePWA } from '@/hooks/usePWA';

function MyComponent() {
  const { isInstalled, isInstallable } = usePWA();
  
  return (
    <div>
      {isInstalled && <p>Running as installed app</p>}
      {isInstallable && <p>Can be installed</p>}
    </div>
  );
}
```

## Testing Checklist

### Installation
- [ ] Install prompt appears on mobile
- [ ] Install prompt can be dismissed
- [ ] App installs successfully on Android
- [ ] App installs successfully on iOS
- [ ] App icon appears on home screen
- [ ] App opens in standalone mode

### Offline Support
- [ ] Service worker registers successfully
- [ ] Static assets are cached
- [ ] Offline page shows when network fails
- [ ] Previously visited pages work offline
- [ ] App reconnects when back online

### Push Notifications
- [ ] Permission prompt appears
- [ ] Notifications can be enabled/disabled
- [ ] Push messages are received
- [ ] Notification clicks open correct page
- [ ] Notifications work when app is closed

### Updates
- [ ] Update prompt appears for new versions
- [ ] Update installs successfully
- [ ] No data loss after update
- [ ] Service worker updates correctly

### Mobile Experience
- [ ] Touch targets are large enough (44x44px)
- [ ] No horizontal scrolling
- [ ] Proper spacing on notched devices
- [ ] Smooth animations
- [ ] Fast load times

## Performance Metrics

Target metrics for PWA:

- **First Contentful Paint:** < 1.5s
- **Time to Interactive:** < 3.5s
- **Lighthouse PWA Score:** > 90
- **Cache Hit Rate:** > 80%
- **Install Rate:** > 10% of mobile visitors

## Browser Support

| Feature | Chrome | Safari | Firefox | Edge |
|---------|--------|--------|---------|------|
| Service Worker | ✅ | ✅ | ✅ | ✅ |
| Install Prompt | ✅ | ⚠️ Manual | ✅ | ✅ |
| Push Notifications | ✅ | ⚠️ iOS 16.4+ | ✅ | ✅ |
| Background Sync | ✅ | ❌ | ❌ | ✅ |
| Offline Support | ✅ | ✅ | ✅ | ✅ |

⚠️ = Partial support or requires specific version
❌ = Not supported

## Troubleshooting

### Service Worker Not Registering

1. Check browser console for errors
2. Ensure HTTPS or localhost
3. Verify `service-worker.js` is accessible
4. Clear browser cache and reload

### Install Prompt Not Showing

1. Check if already installed
2. Verify manifest.json is valid
3. Ensure all required icons exist
4. Check browser compatibility
5. Try incognito/private mode

### Push Notifications Not Working

1. Verify VAPID keys are configured
2. Check notification permissions
3. Ensure service worker is active
4. Test with browser DevTools
5. Check backend push endpoint

### Offline Mode Issues

1. Check service worker status in DevTools
2. Verify cache storage
3. Test network throttling
4. Check offline.html exists
5. Review service worker logs

## Security Considerations

1. **HTTPS Required:** PWA features only work over HTTPS (except localhost)
2. **Content Security Policy:** Ensure CSP allows service workers
3. **VAPID Keys:** Keep private key secure, never expose in frontend
4. **Push Subscriptions:** Store securely in backend database
5. **Cache Validation:** Implement cache versioning to prevent stale content

## Future Enhancements

- [ ] Add Web Share API for sharing bookings
- [ ] Implement periodic background sync for updates
- [ ] Add badge API for unread notifications count
- [ ] Implement app shortcuts for common actions
- [ ] Add file handling for appointment confirmations
- [ ] Implement contact picker API
- [ ] Add payment request API integration

## Resources

- [MDN PWA Guide](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps)
- [Google PWA Checklist](https://web.dev/pwa-checklist/)
- [Service Worker Cookbook](https://serviceworke.rs/)
- [Web Push Protocol](https://web.dev/push-notifications-overview/)
- [Workbox (Advanced SW)](https://developers.google.com/web/tools/workbox)

## Support

For issues or questions about the PWA implementation:
1. Check browser console for errors
2. Review this documentation
3. Test in different browsers
4. Check service worker status in DevTools
5. Contact development team

---

**Last Updated:** 2026-03-25
**Version:** 1.0.0
**Status:** ✅ Implemented
