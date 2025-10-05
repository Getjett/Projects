# 🔧 Backtest Error Fix - "Error running backtest: [object Object]"

## Problem
When clicking "Run Backtest", you get an error: `Error running backtest: [object Object]`

## Root Cause
The backend server is either:
1. **Not running** ❌
2. **Not accessible** at http://localhost:8000 ❌
3. **Returning an error** that's not being properly displayed ❌

## Solution

### Step 1: Start the Backend Server

Open a **NEW terminal** (don't close your frontend terminal):

```powershell
# Navigate to backend directory
cd "d:\New folder\Projects\TradingAlgos\TradingStrategyPlatform\backend"

# Start the backend server
python app.py
```

**Expected Output:**
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
🚀 Starting Universal Trading Strategy Platform API...
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Step 2: Verify Backend is Running

Open a browser and go to:
- **http://localhost:8000** - Should show API info
- **http://localhost:8000/api/docs** - Should show Swagger UI

### Step 3: Test the Backtest Again

1. Go back to your Strategy Builder
2. Complete all 5 steps
3. Click "Run Backtest"
4. You should now see: "✅ Backtest started!"

## Improvements Made

### 1. **Better Error Messages** ✅
The error handler now properly displays:
- Connection errors
- Backend errors
- Detailed error messages (not [object Object])

### 2. **Backend Health Check** ✅
Before running backtest, the app now checks if backend is running:
```typescript
const healthCheck = await fetch('http://localhost:8000/');
if (!healthCheck.ok) {
  alert('Backend server is not running!');
}
```

### 3. **Enhanced Logging** ✅
Added console logs to track:
- Backtest request being sent
- Backtest response received
- Any errors encountered

### 4. **Better Result Display** ✅
Backtest results now show:
```
📊 Backtest Completed!

Total Trades: 45
Win Rate: 55.56%
Net Profit: ₹25,000
Net Profit %: 25%
Max Drawdown: 8%
Profit Factor: 3.5

Check console for detailed results!
```

## Testing Instructions

### Test 1: Backend Not Running
1. Make sure backend is NOT running
2. Click "Run Backtest"
3. **Expected:** Alert saying "Backend server is not running!"

### Test 2: Backend Running
1. Start backend: `python app.py`
2. Wait for "Uvicorn running on http://0.0.0.0:8000"
3. Click "Run Backtest"
4. **Expected:** "✅ Backtest started!"
5. After 3 seconds: Results displayed

### Test 3: Check Console
1. Open browser DevTools (F12)
2. Go to Console tab
3. Click "Run Backtest"
4. **Expected logs:**
   ```
   Sending backtest request: {strategyId: "temp-...", startDate: "2024-01-01", ...}
   Backtest response: {backtestId: "...", status: "PROCESSING", message: "..."}
   Backtest results: {id: "...", metrics: {...}, ...}
   ```

## Common Errors & Solutions

### Error: "Cannot connect to backend server"
**Cause:** Backend is not running

**Solution:**
```bash
cd backend
python app.py
```

### Error: "Port 8000 is already in use"
**Cause:** Another process is using port 8000

**Solution:**
```powershell
# Find the process
netstat -ano | findstr :8000

# Kill it (replace <PID> with actual PID)
taskkill /PID <PID> /F

# Start backend again
python app.py
```

### Error: "Import 'fastapi' could not be resolved"
**Cause:** Backend dependencies not installed

**Solution:**
```bash
cd backend
pip install -r requirements.txt
python app.py
```

### Error: Backend starts but crashes immediately
**Cause:** Missing dependencies or Python version issue

**Solution:**
```bash
# Check Python version (should be 3.9+)
python --version

# Reinstall dependencies
pip install -r requirements.txt --upgrade

# Try running again
python app.py
```

## Verification Checklist

Before clicking "Run Backtest":

- [ ] Backend terminal is open
- [ ] Backend shows "Uvicorn running on http://0.0.0.0:8000"
- [ ] http://localhost:8000 returns API info (test in browser)
- [ ] http://localhost:8000/api/docs shows Swagger UI
- [ ] Frontend is running at http://localhost:3000
- [ ] Strategy Builder page is accessible
- [ ] All 5 steps of strategy are completed

When clicking "Run Backtest":

- [ ] Alert shows "✅ Backtest started!"
- [ ] No error messages appear
- [ ] After 3 seconds, results are displayed
- [ ] Console shows request/response logs
- [ ] No red errors in browser console

## Expected Flow

### 1. Click "Run Backtest"
```
Frontend → Health Check → http://localhost:8000/
         ↓ (Success)
Frontend → POST → http://localhost:8000/api/backtest/run
         ↓
Backend → Process Request → Generate Sample Trades
         ↓
Backend → Return Response → {backtestId: "...", status: "PROCESSING"}
         ↓
Frontend → Show Alert → "✅ Backtest started!"
```

### 2. Wait 3 Seconds
```
Frontend → GET → http://localhost:8000/api/backtest/{id}
         ↓
Backend → Return Results → {metrics: {...}, trades: [...]}
         ↓
Frontend → Show Alert → "📊 Backtest Completed! ..."
```

## Quick Start Both Servers

Use the provided startup script:

```powershell
# In PowerShell
cd "d:\New folder\Projects\TradingAlgos\TradingStrategyPlatform"
.\start.ps1
```

This will automatically start both backend and frontend in separate windows!

## Manual Start (Both Servers)

**Terminal 1 - Backend:**
```bash
cd backend
python app.py
```
Leave this running!

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```
Leave this running!

## Debug Mode

If you still get errors, enable debug mode:

1. **Open browser console** (F12)
2. **Run backtest**
3. **Check console logs** for:
   - "Sending backtest request:" - Shows request data
   - "Backtest response:" - Shows backend response
   - "API Error:" - Shows any API errors
4. **Check Network tab**:
   - Look for POST to `/backtest/run`
   - Check status code (should be 202)
   - Check response body

## Files Modified

- `frontend/src/pages/StrategyBuilder.tsx` - Added health check and better error handling
- `frontend/src/services/api.ts` - Added better error messages

## Still Having Issues?

If backtest still doesn't work:

1. **Check backend logs** in the terminal where you ran `python app.py`
2. **Check browser console** for detailed error messages
3. **Verify port 8000** is accessible: `curl http://localhost:8000` or visit in browser
4. **Try the test script**:
   ```bash
   python test_backend.py
   ```
5. **Check CORS settings** - Should allow http://localhost:3000

## Success!

When everything works correctly:

1. ✅ Backend runs without errors
2. ✅ Frontend connects successfully
3. ✅ "Run Backtest" shows success message
4. ✅ Results display after 3 seconds
5. ✅ Console shows all logs
6. ✅ No [object Object] errors

**Happy Backtesting! 📊🚀**
