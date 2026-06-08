# Frontend App Verification Patterns

When verifying frontend apps (especially localStorage-based ones without test frameworks), use this pattern:

## 1. Syntax Check
```bash
node -c path/to/file.js  # Returns empty if OK, error message if syntax error
```

## 2. Structure Verification
```bash
# Check function references exist
cat file.js | grep -n "functionName"

# Check HTML references match JS
cat index.html | grep -n "elementId\|functionName"
```

## 3. Logic Tests with Mock Data
Create a Node.js test script that simulates the behavior:

```javascript
// Mock the data structures
const mockData = [...];
const mockUser = {...};

// Test each function's logic
function testFunction() {
  // Simulate the function's logic
  const result = mockData.filter(...);
  console.log(`Test: ${result.length === expected ? '✓ PASS' : '✗ FAIL'}`);
}

// Run all tests
testFunction();
```

## 4. Cross-Check Related Code
- Verify no duplicate function names across files
- Check that modified functions aren't called elsewhere with different expectations
- Ensure HTML elements referenced in JS exist

## 5. Report Format
```
=== VERIFICATION REPORT ===
Files Modified: [list]
Syntax Check: ✓/✗
Structure Check: ✓/✗
Logic Tests: X/Y PASS
Related Code: ✓/✗

SUMMARY: [status]
```

## Common Pitfalls

1. **Missing element IDs**: HTML must have elements that JS references
2. **Script order**: Dependencies must load before dependents
3. **Variable scope**: Global variables must be accessible where used
4. **Event handlers**: onclick/onchange must reference defined functions
5. **Async timing in page initialization**: If page renders UI from async data (fetch/API), the render function must be called AGAIN after the async completes. Common bug: render once on load, async fetch finishes, but dependent UI (like stats, lists) never re-renders.

## Debugging Pattern: Async Timing Bugs

**Symptom**: Data exists in API/database but UI shows empty/zero.

**How to diagnose**:
```bash
# 1. Verify API returns data
curl -sL "YOUR_API_URL?action=get" | head -100

# 2. Check if render functions are called AFTER async completes
grep -n "syncFromSheet\|renderContacts\|renderMyLeaders" file.js

# 3. Look for the pattern:
#    renderX()  ← called BEFORE sync
#    syncFromSheet().then(() => {
#      renderContacts()  ← re-rendered
#      renderMyLeaders() ← MISSING! This is the bug
#    })
```

**Root cause**: Page initializes with empty local data → async fetch completes → some UI re-renders, but dependent UI doesn't.

**Fix**: Call ALL dependent render functions inside the `.then()` callback:
```javascript
syncFromSheet('staff').then(() => {
  renderContacts();
  updateStats();
  renderMyLeaders();  // Add this!
});
```

**Verification**: Check that stats/counts match API data, not localStorage.

## Common Frontend Bugs & Fixes

### Modal closes when clicking inside (event propagation)

**Symptom**: Modal with `closeIfOutside` closes when user clicks inside to select text.

**Root cause**: Click events bubble from modal content → overlay → `closeIfOutside` detects click on overlay → closes modal.

**Fix**: Add `event.stopPropagation()` to the modal content div:
```html
<div class="modal-overlay" onclick="closeIfOutside(event,'modalId')">
  <div class="modal" onclick="event.stopPropagation()">
    <!-- modal content -->
  </div>
</div>
```

**Why it works**: stopPropagation prevents the click from reaching the overlay, so closeIfOutside never fires for clicks inside the modal.

**Verification**: Test both directions:
- Click outside modal (on overlay) → should close ✓
- Click inside modal → should stay open ✓
- Select text inside modal → should stay open ✓

## Testing Patterns for Frontend Features

### Test: Input Maxlength Validation
```javascript
function simulateInput(value, maxlength) {
  let processed = value.replace(/\D/g, ''); // onlyNumbers
  if (processed.length > maxlength) {
    processed = processed.substring(0, maxlength);
  }
  return processed;
}

// Test cases
const tests = [
  { input: "3158993189", maxlength: 10, expected: "3158993189" },  // OK
  { input: "31589931890", maxlength: 10, expected: "3158993189" }, // Truncated
  { input: "abc315def8993189", maxlength: 10, expected: "3158993189" } // Cleaned + truncated
];
```

### Test: Event Propagation (stopPropagation)
```javascript
let propagationStopped = false;
const mockEvent = {
  target: { className: 'modal' },
  stopPropagation: () => { propagationStopped = true; }
};

// Simulate modal onclick
if (mockEvent.target.className === 'modal') {
  mockEvent.stopPropagation();
}

// Verify: click inside modal should NOT close it
const wouldClose = false; // Because propagation was stopped
console.log(propagationStopped ? "PASS" : "FAIL");
```

### Test: Async Data Sync (render after fetch)
```javascript
// Simulate the bug: render called BEFORE async completes
let contacts = [];
let renderCount = 0;

function renderMyLeaders() {
  renderCount++;
  return leaders.map(l => ({
    name: l.nombre,
    records: contacts.filter(c => c.lider === l.id).length
  }));
}

// BEFORE sync: should show 0
renderMyLeaders(); // renderCount = 1
console.log(contacts.length === 0 ? "PASS" : "FAIL"); // Empty

// AFTER sync: should show correct counts
contacts = [{ id: 'C1', lider: 'L1' }]; // Sync completes
renderMyLeaders(); // renderCount = 2
console.log(contacts.length > 0 ? "PASS" : "FAIL"); // Has data
```

### Test: Verify External API Connectivity (GAS)
```bash
# GAS URLs return 302 redirect first, then JSON
# Use -L flag to follow redirects
curl -sL "YOUR_GAS_URL?action=get&lider=ALL" | head -200

# If you see HTML redirect instead of JSON, the redirect wasn't followed
# If you see {"ok":true,"contacts":[...]}, the API is working
```

### Test: Duplicate Code Across Files
```bash
# Check if same function exists in multiple files (potential conflict)
grep -rn "function closeIfOutside" /path/to/project/
grep -rn "function renderContacts" /path/to/project/
```
