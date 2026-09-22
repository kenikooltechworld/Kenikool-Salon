# Owner Dashboard Issues Audit

Date: 2026-09-21
Scope: Backend (`backend/app/services/owner_dashboard_service.py`, `backend/app/routes/owner_dashboard.py`) + Frontend (`salon/src/pages/dashboard/Dashboard.tsx`, `salon/src/components/owner/*`, `salon/src/hooks/owner/*`)

---

## 1. Revenue Analytics — Data Shape Mismatch

**Severity:** High  
**Files involved:**
- Backend: `backend/app/services/owner_dashboard_service.py:855-917`
- Frontend: `salon/src/hooks/owner/useRevenueAnalytics.ts`, `salon/src/components/owner/D3BarChart.tsx`, `salon/src/components/owner/RevenueChart.tsx`

**Problem:** Backend returns three different shapes for the time-series data:
- `dailyRevenue`: `[{date: "2026-03-20", revenue: 5000}, ...]`
- `weeklyRevenue`: `[{week: "2026-W12", revenue: 5000}, ...]`
- `monthlyRevenue`: `[{month: "2026-03", revenue: 5000}, ...]`

Frontend `RevenueDataPoint` interface expects all of them to have `{date: string; revenue: number}`.

`D3BarChart` reads `item.date` for every period, so weekly/monthly views render blank or broken because `date` is `undefined`.

`RevenueChart` CSV export also reads `item.date`, so CSV export fails for weekly/monthly.

---

## 2. Currency Fallback is Wrong

**Severity:** Medium  
**Files involved:**
- Frontend: `salon/src/pages/dashboard/Dashboard.tsx:36`

**Problem:** When tenant settings are not yet loaded, currency falls back to `"USD"`. The entire app is Naira-based and should fall back to `"NGN"`. This affects every `formatCurrency()` call on the dashboard while settings are loading.

---

## 3. Staff Performance — Attendance/Satisfaction Are Meaningless Defaults

**Severity:** Medium  
**Files involved:**
- Backend: `backend/app/services/owner_dashboard_service.py:1037-1041`

**Problem:**
- `attendance` is hardcoded to `100.0` for every staff member, regardless of actual attendance data. There is no attendance model/tracking in the codebase, so this value is purely decorative.
- `satisfaction` reads `staff.rating`, which is often `null` for new staff, so average satisfaction shows `0.0/5`. There is no customer review/rating flow wired into staff records.

Result: The dashboard shows fake 100% attendance and 0-star satisfaction, which is misleading.

---

## 4. Pending Actions — Optimistic UI vs Backend Refetch Race

**Severity:** High  
**Files involved:**
- Frontend: `salon/src/hooks/owner/usePendingActions.ts`
- Backend: `backend/app/services/owner_dashboard_service.py:1099-1129`

**Problem:** 
- Frontend optimistically removes the action from the cache on click, then refetches.
- If the backend server has not been restarted with the latest code, `mark_action_complete` and `dismiss_action` only invalidate the cache without updating any underlying database record.
- The refetch therefore returns the same action, and it reappears in the UI.
- Even with the latest backend code, if the action type is not a `Payment` or `TimeOffRequest` (e.g., inventory alert), the backend still does nothing except invalidate cache, so the refetch returns the same inventory alert.

**Sub-issue:** Inventory alerts have no writable status field in the `Inventory` model, so “mark complete” / “dismiss” cannot actually change their state.

---

## 5. Revenue Chart — Period Query Param Ignored

**Severity:** Low  
**Files involved:**
- Backend: `backend/app/services/owner_dashboard_service.py:755-935`
- Frontend: `salon/src/components/owner/RevenueChart.tsx`, `salon/src/hooks/owner/useRevenueAnalytics.ts`

**Problem:** Backend `get_revenue_analytics` always returns `dailyRevenue`, `weeklyRevenue`, and `monthlyRevenue` together, and hardcodes `"period": "daily"` in the response. The frontend’s `period` query param and local period selector are effectively ignored on the backend side. This does not break the UI because the frontend filters locally, but it wastes bandwidth and the `period` field in the response is misleading.

---

## 6. Revenue Analytics — Empty Data Shows Blank Chart

**Severity:** Low  
**Files involved:**
- Frontend: `salon/src/components/owner/RevenueChart.tsx:187-203`, `salon/src/components/owner/D3BarChart.tsx:259-268`

**Problem:** When there are no payments in the selected date range, the chart shows a plain “No data available” message inside the card. This is functional but inconsistent with the rest of the dashboard, which uses `Skeleton` loaders and empty states with icons. It also makes the chart section collapse visually compared to the Staff Performance card.

---

## 7. Backend Dashboard Metrics Cache Staleness

**Severity:** Medium  
**Files involved:**
- Backend: `backend/app/services/owner_dashboard_service.py:34-41, 56`

**Problem:** `get_all_metrics` caches the entire metrics payload for 30 seconds. If a user marks a pending action as complete, the metrics endpoint can still return stale cached data for up to 30 seconds. The pending-payments count and total amount in the metric cards will not reflect the change until the cache expires or is invalidated.

The `invalidate_cache` method exists and is called in `mark_action_complete` / `dismiss_action`, but only if those methods are actually executed with the updated backend code. If the server is still running the old code, the cache is never invalidated.

---

## Summary

| # | Issue | Severity | Backend fix needed | Frontend fix needed |
|---|---|---|---|---|
| 1 | Revenue analytics weekly/monthly data shape mismatch | High | Yes — normalize keys | Yes — handle `week`/`month` keys |
| 2 | Currency fallback USD instead of NGN | Medium | No | Yes |
| 3 | Attendance/satisfaction are fake defaults | Medium | Yes — real tracking or hide | No |
| 4 | Pending action refetch race / inventory alerts uncompletable | High | Yes — update records or remove from list | Yes — optimistic UI already done |
| 5 | Revenue backend ignores period param | Low | Yes | No |
| 6 | Empty revenue chart bare message | Low | No | Yes |
| 7 | Metrics cache staleness after action complete | Medium | Yes — invalidate on mutations | No |
