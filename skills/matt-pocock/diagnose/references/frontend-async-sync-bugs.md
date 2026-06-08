# Frontend Async Sync Bug Pattern

## Common Pattern: Render Before Data Loads

In frontend apps with async data loading (fetch, localStorage + sync), a common bug is:

1. Page loads → render functions called with empty/stale data
2. Async sync starts (fetch to API/GAS/Google Sheets)
3. Sync completes → data updated in memory
4. BUT render functions NOT called again → UI shows stale data

## Symptoms
- Data exists on server but shows 0 in UI
- Counts/stats wrong on first load
- Works after page refresh but not on first visit
- Works in some tabs but not others

## Root Cause
The `.then()` callback after async sync doesn't include ALL render functions that depend on the synced data.

## Fix Pattern
```javascript
// BEFORE (buggy):
syncFromSheet('staff').then(()=>{
  renderContacts(); updateStats();
  // Missing: renderMyLeaders() or renderStaffView()
}).catch(()=>{});

// AFTER (fixed):
syncFromSheet('staff').then(()=>{
  renderContacts(); updateStats();
  renderMyLeaders(); // Add this!
}).catch(()=>{});
```

## Debugging Steps
1. Check which render functions are called in window.onload BEFORE sync
2. Check which render functions are called AFTER sync completes
3. Identify any render functions that depend on synced data but aren't called after sync
4. Add missing render calls to the .then() callback

## Verification
- Check GAS endpoint directly with curl to confirm data exists
- Compare data in memory vs what UI shows
- Add console.log in render functions to verify they're called after sync

## Example from NOVVA VALLE
- Staff panel: renderMyLeaders() not called after sync → leaders showed 0 records
- Admin panel: renderStaffView() not called after sync → staff view showed 0 records
- Fix: Added missing render calls to .then() callbacks
