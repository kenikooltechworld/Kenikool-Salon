# Salon Landing Page Upgrade Implementation Plan

## Overview
Upgrade the `salon` landing page to match the advanced structure and features of the `salons` landing page. This includes adding animations, carousels, modals, and enhanced UX patterns.

---

## Phase 1: Dependencies & Setup

### 1.1 Install Required Dependencies
- [x] `framer-motion` - For animations and transitions (added to package.json)
- [x] `swiper` - For carousel/slider functionality (added to package.json)
- [x] Verify `react-router-dom` is installed
- [x] Verify custom UI components (Button, Card, Badge) exist

**Status:** COMPLETE - Dependencies added to package.json (pending npm install)
**Notes:** Check `salon/package.json` for existing dependencies

**Implementation Details:**

#### Framer Motion Installation
```bash
npm install framer-motion
```
- Version: ^10.x or latest
- Used for: All animations, transitions, and motion effects
- Key imports needed:
  - `motion` - For animated components
  - `AnimatePresence` - For exit animations
  - `useInView` - For scroll-triggered animations (optional)

#### Swiper Installation
```bash
npm install swiper
```
- Version: ^11.x or latest
- Used for: Carousels in testimonials and features sections
- Key imports needed:
  - `Swiper, SwiperSlide` - Core carousel components
  - `Navigation, Pagination, Autoplay` - Swiper modules
  - CSS imports: `swiper/css`, `swiper/css/navigation`, `swiper/css/pagination`

#### Verify Existing Dependencies
Check `salon/package.json` for:
- `react-router-dom` - Should already exist (used for routing)
- Custom UI components location: `salon/src/components/ui/`
  - Button component: `salon/src/components/ui/button.tsx`
  - Card component: `salon/src/components/ui/card.tsx`
  - Badge component: Check if exists, if not create it

#### Badge Component (if missing)
If Badge component doesn't exist, create minimal version:
```typescript
// salon/src/components/ui/badge.tsx
interface BadgeProps {
  variant?: 'default' | 'accent' | 'secondary';
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
}

export function Badge({ variant = 'default', size = 'md', children }: BadgeProps) {
  const variantClasses = {
    default: 'bg-primary text-white',
    accent: 'bg-accent text-white',
    secondary: 'bg-secondary text-white',
  };
  
  const sizeClasses = {
    sm: 'px-2 py-1 text-xs',
    md: 'px-3 py-1.5 text-sm',
    lg: 'px-4 py-2 text-base',
  };
  
  return (
    <span className={`inline-block rounded-full font-semibold ${variantClasses[variant]} ${sizeClasses[size]}`}>
      {children}
    </span>
  );
}
```

---

## Phase 2: Hero Section Enhancement

### 2.1 Update Hero Section (`salon/src/components/landing/hero-section.tsx`)
- [x] Add Framer Motion imports
- [x] Create `AnimatedCounter` component for statistics
- [x] Create `StatisticsSection` component
- [x] Add animation variants (fadeInUp, staggerContainer, scaleIn, floatingElement)
- [x] Implement video background with fallback to image
- [x] Add floating animated blobs and icons
- [x] Add `prefers-reduced-motion` accessibility support
- [x] Add statistics with intersection observer for lazy animation
- [x] Implement responsive design for mobile/tablet/desktop
- [x] Add Badge component for "Trusted by X+ salons" text

**Status:** COMPLETE - Full hero section with animations, statistics, and accessibility
**Complexity:** High
**Estimated Time:** 2-3 hours
**Dependencies:** Framer Motion, custom icons, Badge component

**Implementation Details:**

#### Key Imports
```typescript
import { motion } from 'framer-motion';
import { useState, useEffect, useRef } from 'react';
import { SparklesIcon } from '@/components/icons';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
```

#### Animation Variants to Define
```typescript
const fadeInUpVariants = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.6, ease: 'easeOut' } },
};

const staggerContainerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.15, delayChildren: 0.2 },
  },
};

const floatingElementVariants = {
  animate: {
    y: [0, 40, 0],
    x: [0, 25, 0],
    transition: { duration: 8, repeat: Infinity, ease: 'easeInOut' },
  },
};
```

#### AnimatedCounter Component
- Use `requestAnimationFrame` for smooth counting
- Respect `prefers-reduced-motion` media query
- Accept props: `end` (number), `duration` (seconds), `suffix` (string)
- Example: `<AnimatedCounter end={500} duration={2} suffix="+" />`
- Implementation: Count from 0 to end value over duration seconds

#### StatisticsSection Component
- Display 3 stats: Active Salons (500+), Bookings (10000+), Happy Customers (50000+)
- Use Intersection Observer to trigger animation when section comes into view
- Implement staggered animation for each stat
- Show stat label below the number
- Responsive: Stack vertically on mobile, 3 columns on desktop

#### Video Background
- Try to load video from Pexels or similar
- Fallback to image if video fails
- Show placeholder image while video loads
- Add dark overlay (black/60%) on top
- Responsive: Hide video on mobile, show only on desktop

#### Floating Elements
- Large blob top-right (primary color, 10% opacity)
- Large blob bottom-left (accent color, 10% opacity)
- Small icon boxes (top-left, bottom-right) with sparkles icon
- Use `willChange: 'transform'` for performance
- Skip animations if `prefers-reduced-motion` is set

#### Hero Content Structure
```
Badge: "✨ Trusted by 10,000+ salons across Africa"
H1: "Manage Your Salon, Spa & Gym Business"
P: "All-in-one platform for appointments..."
Buttons: "Start Free Trial" + "Sign In"
Subtext: "No credit card required • 30-day free trial • Cancel anytime"
Statistics: 3 animated counters
```

#### Responsive Breakpoints
- Mobile (<640px): Single column, smaller text, no video, no floating elements
- Tablet (640-1024px): Adjusted spacing, smaller floating elements
- Desktop (>1024px): Full layout with video and all floating elements

---

## Phase 3: Features Section Enhancement

### 3.1 Create Feature Card Component (`salon/src/components/landing/feature-card.tsx`)
- [ ] Create new file with FeatureCard component
- [ ] Add hover animations (scale, shadow)
- [ ] Add image loading states with skeleton
- [ ] Add "Click to Learn More" overlay on hover
- [ ] Implement lazy image loading

**Status:** Not Started
**Complexity:** Medium
**Estimated Time:** 1-1.5 hours

**Implementation Details:**

#### FeatureCard Props Interface
```typescript
interface FeatureCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  colorClass: string; // e.g., 'bg-primary/10'
  imageUrl: string;
  details?: string;
  benefits?: string[];
  onCardClick?: () => void;
}
```

#### Key Features
- Image container with aspect-video ratio
- Icon in colored circle (12-16px size)
- Title and description text
- Hover state: Scale 1.05, shadow increase
- Image hover: Scale 1.1 (zoom effect)
- "Click to Learn More" overlay appears on hover
- Lazy load images with loading skeleton
- Smooth transitions (0.3s duration)

#### Animation Variants
```typescript
const cardVariants = {
  rest: { scale: 1, boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)' },
  hover: {
    scale: 1.05,
    boxShadow: '0 20px 25px rgba(0, 0, 0, 0.15)',
    transition: { duration: 0.3 },
  },
};

const imageVariants = {
  rest: { scale: 1 },
  hover: { scale: 1.1, transition: { duration: 0.3 } },
};
```

#### Image Loading State
- Show gradient skeleton while loading
- Fade in image when loaded
- Fallback color: gray-200 to gray-300 gradient
- Use `onLoad` callback to set loaded state

### 3.2 Create Feature Detail Modal (`salon/src/components/landing/feature-detail-modal.tsx`)
- [ ] Create new file with FeatureDetailModal component
- [ ] Add modal animations (backdrop, scale, slide)
- [ ] Display feature image, title, description
- [ ] Show benefits list with staggered animation
- [ ] Add close button and CTA buttons
- [ ] Implement AnimatePresence for smooth exit

**Status:** Not Started
**Complexity:** Medium
**Estimated Time:** 1.5-2 hours

**Implementation Details:**

#### Modal Props Interface
```typescript
interface FeatureDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  feature: {
    icon: React.ReactNode;
    title: string;
    description: string;
    colorClass: string;
    imageUrl: string;
    details?: string;
    benefits?: string[];
  };
}
```

#### Modal Structure
```
Backdrop (semi-transparent black, clickable to close)
  Modal Container
    Header (sticky)
      Icon + Title
      Close Button (X)
    Content (scrollable)
      Feature Image
      Description
      Key Features Section
      Benefits List (with checkmarks)
    Footer (sticky)
      Close Button
      Learn More Button
```

#### Animation Variants
```typescript
const backdropVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1 },
  exit: { opacity: 0 },
};

const modalVariants = {
  hidden: { opacity: 0, scale: 0.95, y: 20 },
  visible: { opacity: 1, scale: 1, y: 0, transition: { duration: 0.3 } },
  exit: { opacity: 0, scale: 0.95, y: 20, transition: { duration: 0.2 } },
};
```

#### Benefits List Animation
- Stagger children with delay
- Each benefit fades in and slides from left
- Use checkmark icon (✓) in primary color
- Delay: 0.3s + index * 0.05s

### 3.3 Update Features Section (`salon/src/components/landing/features-section.tsx`)
- [ ] Add Framer Motion and Swiper imports
- [ ] Expand features from 6 to 12 (add: Marketing, Loyalty, Packages, Promo, Gift Cards)
- [ ] Add feature images/assets (create placeholder or use emojis)
- [ ] Implement desktop grid with stagger animations
- [ ] Implement mobile carousel with Swiper
- [ ] Add feature click handler to open modal
- [ ] Add responsive breakpoints for carousel
- [ ] Implement skeleton loaders for loading state

**Status:** Not Started
**Complexity:** High
**Estimated Time:** 2-3 hours
**Dependencies:** FeatureCard, FeatureDetailModal, Swiper

**Implementation Details:**

#### 12 Features List
1. Point of Sale (POS) - CreditCardIcon
2. Online Booking - CalendarIcon
3. Client Management - UsersIcon
4. Staff Management - ScissorsIcon
5. Inventory Management - ListIcon
6. Analytics & Reports - ChartIcon
7. Marketing Campaigns - SparklesIcon
8. Loyalty Programs - TrendingUpIcon
9. Packages & Memberships - PackageIcon
10. Promo Codes - TagIcon
11. Gift Cards - GiftIcon
12. Smart Notifications - BellIcon

#### Feature Data Structure
```typescript
interface Feature {
  icon: React.ReactNode;
  title: string;
  description: string;
  colorClass: string;
  imageUrl: string;
  details?: string;
  benefits?: string[];
}
```

#### Desktop Layout
- 3-column grid on lg screens
- 2-column grid on md screens
- 1-column on sm screens
- Stagger animation: children appear with 0.1s delay between each
- Scroll-triggered animation using `whileInView`

#### Mobile Carousel (Swiper)
```typescript
<Swiper
  modules={[Pagination, Autoplay]}
  spaceBetween={20}
  slidesPerView={1}
  pagination={{ clickable: true }}
  autoplay={{ delay: 5000, disableOnInteraction: false }}
  breakpoints={{
    320: { slidesPerView: 1, spaceBetween: 16 },
    640: { slidesPerView: 2, spaceBetween: 16 },
    1024: { slidesPerView: 2, spaceBetween: 20 },
  }}
>
```

#### Modal State Management
```typescript
const [selectedFeature, setSelectedFeature] = useState<Feature | null>(null);
const [isModalOpen, setIsModalOpen] = useState(false);

const handleFeatureClick = (feature: Feature) => {
  setSelectedFeature(feature);
  setIsModalOpen(true);
};
```

#### Skeleton Loader Component
- Show 8 skeleton cards while loading
- Each skeleton: gray gradient boxes for image, title, description
- Pulse animation on skeleton
- Replace with actual cards when loaded

#### Animation Variants
```typescript
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.1, delayChildren: 0.2 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.6 } },
};
```

---

## Phase 4: Benefits Section Enhancement

### 4.1 Create Benefit Item Component (`salon/src/components/landing/benefit-item.tsx`)
- [ ] Create new file with BenefitItem component
- [ ] Display icon, title, and description
- [ ] Use CheckIcon from custom icons

**Status:** Not Started
**Complexity:** Low
**Estimated Time:** 30 minutes

### 4.2 Update Benefits Section (`salon/src/components/landing/benefits-section.tsx`)
- [ ] Add Framer Motion imports
- [ ] Refactor to use BenefitItem component
- [ ] Add image showcase with lazy loading
- [ ] Add gradient CTA card
- [ ] Implement staggered animations for benefits list
- [ ] Add responsive 2-column grid

**Status:** Not Started
**Complexity:** Medium
**Estimated Time:** 1-1.5 hours
**Dependencies:** BenefitItem component

---

## Phase 5: Testimonials Section Enhancement

### 5.1 Create Testimonial Card Component (within testimonials-section.tsx)
- [ ] Add video testimonial support
- [ ] Add video player modal with iframe support
- [ ] Display star ratings with fill
- [ ] Show customer photo, name, role, salon, location
- [ ] Add play button overlay for video testimonials

**Status:** Not Started
**Complexity:** Medium
**Estimated Time:** 1.5-2 hours

### 5.2 Update Testimonials Section (`salon/src/components/landing/testimonials-section.tsx`)
- [ ] Add Swiper carousel with Navigation, Pagination, Autoplay
- [ ] Expand testimonials from 3 to 6 with real data
- [ ] Add video testimonial support
- [ ] Implement responsive breakpoints (1, 2, 3 slides)
- [ ] Add navigation arrows
- [ ] Add pause on hover functionality
- [ ] Implement video player modal

**Status:** Not Started
**Complexity:** High
**Estimated Time:** 2-2.5 hours
**Dependencies:** Swiper, video player modal

---

## Phase 6: Pricing Section Enhancement

### 6.1 Update Pricing Section (`salon/src/components/landing/pricing-preview-section.tsx`)
- [ ] Add Framer Motion imports
- [ ] Expand from 3 to 6 pricing tiers (add Enterprise, Unlimited)
- [ ] Add monthly/annual billing toggle
- [ ] Implement price animation on toggle
- [ ] Add savings calculation and badge
- [ ] Add "Most Popular" badge for Professional plan
- [ ] Implement feature list with staggered animation
- [ ] Add responsive card hover effects
- [ ] Add animation variants for all elements

**Status:** Not Started
**Complexity:** High
**Estimated Time:** 2-2.5 hours
**Dependencies:** Framer Motion

---

## Phase 7: FAQ Section Enhancement

### 7.1 Update FAQ Section (`salon/src/components/landing/faq-section.tsx`)
- [ ] Add Framer Motion and AnimatePresence imports
- [ ] Add icon support for each FAQ item
- [ ] Implement smooth height animation on expand/collapse
- [ ] Add chevron rotation animation
- [ ] Implement staggered animation for FAQ items
- [ ] Add responsive design

**Status:** Not Started
**Complexity:** Medium
**Estimated Time:** 1-1.5 hours
**Dependencies:** Framer Motion

---

## Phase 8: Conversion Elements Enhancement

### 8.1 Update Sticky CTA (`salon/src/components/landing/sticky-cta.tsx`)
- [ ] Add Framer Motion imports
- [ ] Implement spring animation on appearance
- [ ] Add pulsing shadow animation
- [ ] Add dismiss functionality
- [ ] Implement scroll-triggered visibility (after 80% of window height)
- [ ] Add responsive design

**Status:** Not Started
**Complexity:** Medium
**Estimated Time:** 1-1.5 hours
**Dependencies:** Framer Motion

### 8.2 Update Floating CTA (`salon/src/components/landing/floating-cta.tsx`)
- [ ] Add Framer Motion imports
- [ ] Add WhatsApp button (green)
- [ ] Add Phone button (blue)
- [ ] Implement staggered spring animation
- [ ] Add hover scale effects
- [ ] Add "Need help?" label
- [ ] Implement responsive positioning

**Status:** Not Started
**Complexity:** Medium
**Estimated Time:** 1-1.5 hours
**Dependencies:** Framer Motion

### 8.3 Update Exit Intent Popup (`salon/src/components/landing/exit-intent-popup.tsx`)
- [ ] Add Framer Motion and AnimatePresence imports
- [ ] Implement mouse leave detection
- [ ] Add mobile timer (30 seconds)
- [ ] Add discount code display (e.g., "SALON20")
- [ ] Implement spring animation
- [ ] Add backdrop with click to dismiss
- [ ] Add "Limited time" message
- [ ] Implement two CTA buttons

**Status:** Not Started
**Complexity:** Medium
**Estimated Time:** 1.5-2 hours
**Dependencies:** Framer Motion

---

## Phase 9: Additional Components

### 9.1 Create Sticky Header Component (`salon/src/components/landing/sticky-header.tsx`)
- [ ] Create new file with StickyHeader component
- [ ] Implement scroll-based visibility
- [ ] Add mobile hamburger menu with animated dropdown
- [ ] Add navigation links with smooth scroll
- [ ] Add logo animation
- [ ] Add Sign In and Start Free Trial buttons
- [ ] Implement glass-morphism effect
- [ ] Add responsive design

**Status:** Not Started
**Complexity:** High
**Estimated Time:** 2-2.5 hours
**Dependencies:** Framer Motion, AnimatePresence

### 9.2 Update CTA Section (`salon/src/components/landing/cta-section.tsx`)
- [ ] Add Framer Motion imports
- [ ] Add gradient background animation
- [ ] Implement text animations
- [ ] Add button hover effects

**Status:** Not Started
**Complexity:** Low
**Estimated Time:** 30 minutes

### 9.3 Update Landing Footer (`salon/src/components/landing/landing-footer.tsx`)
- [ ] Add Framer Motion imports
- [ ] Implement scroll-triggered animations
- [ ] Add responsive design improvements

**Status:** Not Started
**Complexity:** Low
**Estimated Time:** 30 minutes

---

## Phase 10: How It Works Section

### 10.1 Update How It Works Section (`salon/src/components/landing/how-it-works-section.tsx`)
- [ ] Add Framer Motion imports
- [ ] Implement staggered animations
- [ ] Add scroll-triggered animations
- [ ] Improve responsive design

**Status:** Not Started
**Complexity:** Low
**Estimated Time:** 1 hour

---

## Phase 11: Home Page Integration

### 11.1 Update Home Page (`salon/src/pages/Home.tsx`)
- [ ] Add StickyHeader component (if needed)
- [ ] Verify all components are properly imported
- [ ] Update component structure if needed
- [ ] Test responsive design

**Status:** Not Started
**Complexity:** Low
**Estimated Time:** 30 minutes

---

## Phase 12: Index File Updates

### 12.1 Update Landing Components Index (`salon/src/components/landing/index.ts`)
- [ ] Add exports for new components (FeatureCard, FeatureDetailModal, BenefitItem, StickyHeader)
- [ ] Verify all exports are correct

**Status:** Not Started
**Complexity:** Low
**Estimated Time:** 15 minutes

---

## Phase 13: Testing & Validation

### 13.1 Component Testing
- [ ] Test all animations on different screen sizes
- [ ] Test accessibility (prefers-reduced-motion)
- [ ] Test carousel functionality
- [ ] Test modal open/close
- [ ] Test scroll-triggered animations
- [ ] Test video loading and playback

**Status:** Not Started
**Complexity:** Medium
**Estimated Time:** 2-3 hours

### 13.2 Browser Testing
- [ ] Test on Chrome, Firefox, Safari, Edge
- [ ] Test on mobile devices
- [ ] Test on tablets
- [ ] Verify performance

**Status:** Not Started
**Complexity:** Medium
**Estimated Time:** 1-2 hours

---

## Implementation Order (Recommended)

1. **Phase 1:** Install dependencies
2. **Phase 2:** Hero section (foundation for animations)
3. **Phase 4:** Benefit item component (simple, builds confidence)
4. **Phase 5:** Testimonials (uses Swiper)
5. **Phase 6:** Pricing (complex toggle logic)
6. **Phase 3:** Features (most complex, depends on other patterns)
7. **Phase 7:** FAQ (uses animation patterns from hero)
8. **Phase 8:** Conversion elements (uses animation patterns)
9. **Phase 9:** Additional components (sticky header, etc.)
10. **Phase 10:** How it works (simple animations)
11. **Phase 11:** Home page integration
12. **Phase 12:** Index file updates
13. **Phase 13:** Testing & validation

---

## Key Implementation Notes

### Animation Patterns to Reuse
- `fadeInUpVariants` - Fade in with upward movement
- `staggerContainerVariants` - Stagger children animations
- `scaleInVariants` - Scale from small to normal
- `floatingElementVariants` - Continuous floating motion
- `cardHoverVariants` - Scale and shadow on hover

### Accessibility Considerations
- Always check `prefers-reduced-motion` media query
- Provide fallback for animations
- Ensure keyboard navigation works
- Test with screen readers

### Performance Optimization
- Use `willChange` CSS property for animated elements
- Lazy load images
- Use Intersection Observer for scroll-triggered animations
- Implement skeleton loaders for loading states
- Use `requestAnimationFrame` for smooth counters

### Responsive Design Breakpoints
- Mobile: < 640px
- Tablet: 640px - 1024px
- Desktop: > 1024px

### Component Dependencies
- Framer Motion: All animated components
- Swiper: Testimonials, Features carousels
- Custom Icons: All sections
- Custom UI Components: Button, Card, Badge

---

## Checklist for Completion

- [ ] All phases completed
- [ ] All components tested
- [ ] Animations smooth on all devices
- [ ] Accessibility verified
- [ ] Performance optimized
- [ ] Browser compatibility confirmed
- [ ] Mobile responsiveness verified
- [ ] All imports correct
- [ ] No console errors
- [ ] Landing page fully functional

---

## Notes & Observations

### From Salons Investigation
- Uses 12 features instead of 6
- Includes video testimonials
- Has 6 pricing tiers with toggle
- Includes sticky header
- Has salon directory section (not needed for salon)
- Uses real images and data
- Implements advanced animations throughout
- Uses Swiper for carousels
- Includes feature detail modals
- Has discount codes in exit popup

### Customizations for Salon
- Keep 6 features (or expand to 12 if needed)
- Skip salon directory section
- Use placeholder images/emojis if real images unavailable
- Adapt pricing to salon-specific tiers
- Customize testimonials with salon-specific data
- Adapt discount codes to salon promotions

---

## Timeline Estimate

**Total Estimated Time:** 20-28 hours
- Phase 1: 30 minutes
- Phase 2: 2-3 hours
- Phase 3: 4-5 hours
- Phase 4: 1.5-2 hours
- Phase 5: 2-2.5 hours
- Phase 6: 2-2.5 hours
- Phase 7: 1-1.5 hours
- Phase 8: 3-4 hours
- Phase 9: 2.5-3 hours
- Phase 10: 1 hour
- Phase 11: 30 minutes
- Phase 12: 15 minutes
- Phase 13: 2-3 hours

**Recommended Pace:** 4-6 hours per day over 4-5 days

---

## Success Criteria

✅ All animations working smoothly
✅ Responsive design on all devices
✅ Accessibility features implemented
✅ Performance optimized
✅ No console errors
✅ All components properly integrated
✅ Landing page matches salons quality
✅ User experience enhanced
