# Legacy Selenium Tools

This folder keeps older Selenium-based capture and probe scripts for historical UI parity work.

Current Svelte UIUX verification should use Playwright:

```powershell
cd C:\workspace\folio\svelte_app
npm.cmd run test:ui
npm.cmd run capture:ui -- --base-url http://127.0.0.1:5174
```

The root `requirements-dev.txt` still keeps `selenium` because Streamlit and external gallery collection legacy tools outside this folder may still depend on it.
