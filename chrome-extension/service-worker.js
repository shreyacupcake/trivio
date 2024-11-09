// service-worker.js

// Set panel behavior when the extension is first installed or updated
chrome.runtime.onInstalled.addListener(() => {
  chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true });
  console.log("Extension installed or updated, panel behavior set.");
});

// Log to console and open side panel when the extension icon is clicked
chrome.action.onClicked.addListener((tab) => {
  console.log("Extension icon clicked by the user.");
});
