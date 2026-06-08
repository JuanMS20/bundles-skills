# Frontend Bug Patterns

Common bugs in vanilla JS frontend apps with event-driven UIs.

## 1. Modal Closes When Selecting Text

**Symptom**: Click inside a modal to select/copy text → modal closes.

**Root cause**: Click event propagates (bubbles) from modal content to overlay. `closeIfOutside` on overlay detects `e.target === overlay` — but if click starts in a gap or propagates, it triggers close.

**Fix**: Add `event.stopPropagation()` on the modal content div:

```html
<div class="modal-overlay" onclick="closeIfOutside(event,'myModal')">
  <div class="modal" onclick="event.stopPropagation()">
    <!-- modal content -->
  </div>
</div>
```

**Why it works**: Clicks inside `.modal` stop bubbling before reaching `.modal-overlay`. Clicks directly on the overlay still fire `closeIfOutside` normally.

**Apply to**: ALL modals with `closeIfOutside` pattern. Check: admin, staff, leader modals.

## 2. Stats Show 0 After Async Data Load

**Symptom**: Leader cards show 0 records even though data exists in the server.

**Root cause**: Render function called BEFORE async fetch completes. After fetch, only some render functions are re-invoked — the one for leader stats is missed.

```
window.onload →
  1. renderMyLeaders() ← shows 0 (contacts empty)
  2. syncFromSheet() ← async, takes time
  3. renderContacts() + updateStats() ← updated
  4. renderMyLeaders() ← NEVER called again ← BUG
```

**Fix**: Add the missing render call inside the `.then()` callback:

```javascript
syncFromSheet('staff').then(()=>{
  renderContacts(); updateStats();
  renderMyLeaders(); // Fix: update leader stats after sync
}).catch(()=>{});
```

**Pattern**: After ANY async data load, verify ALL dependent render functions are re-invoked, not just some.

## 3. Testing These Patterns

### Modal test (Node.js mock)
```javascript
function closeIfOutside(e, overlayId) {
  return e.target === overlayId ? 'CLOSE' : 'KEEP_OPEN';
}

// Click on overlay → closes
closeIfOutside({ target: 'overlay' }, 'overlay') === 'CLOSE';

// Click on modal content → keeps open
closeIfOutside({ target: 'modal' }, 'overlay') === 'KEEP_OPEN';
```

### Async timing test (Node.js mock)
```javascript
let contacts = [];
let renderCalled = 0;

function renderMyLeaders() {
  renderCalled++;
  return contacts.filter(c => c.lider === 'L1').length;
}

// Before sync: 0
renderMyLeaders(); // returns 0

// After sync: should re-render
contacts = [{ id: 'C1', lider: 'L1' }];
renderMyLeaders(); // returns 1
// Verify renderMyLeaders was called AFTER sync
```

## 4. GAS Endpoint Testing

Test Google Apps Script endpoints directly via curl:

```bash
# GET request
curl -sL "GAS_URL?action=get&lider=ALL" | python -m json.tool

# Verify response structure
curl -sL "GAS_URL?action=getLeaders" | python -m json.tool | head -50
```

**Key**: Use `-L` flag to follow redirects (GAS redirects to googleusercontent.com).

## 5. Input Validation Pattern

For numeric-only fields with max length:

```html
<input type="tel" maxlength="10" oninput="onlyNumbers(this)">
```

```javascript
function onlyNumbers(el) {
  el.value = el.value.replace(/\D/g, '');
}
```

**Colombian document lengths**:
- CC: max 10 digits
- Celular: max 10 digits
- Both use `type="tel"` for mobile numeric keyboard
