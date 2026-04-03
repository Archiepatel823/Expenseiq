/* ============================================================
   main.js — Shared JavaScript for all pages
   Handles: date auto-fill, delete confirmation, flash dismiss
   ============================================================ */


/* ── 1. Auto-fill today's date in any date input ─────────────
   Runs on add_expense page — sets the date field to today
   if it hasn't already been filled.
   ──────────────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', function () {

  var dateInput = document.getElementById('date');

  if (dateInput && !dateInput.value) {
    // toISOString() → "2026-04-03T00:00:00.000Z"
    // split('T')[0] → "2026-04-03"  (the format HTML date input needs)
    var today = new Date().toISOString().split('T')[0];
    dateInput.value = today;
  }


  /* ── 2. Delete confirmation for all delete buttons ──────────
     Finds every form that has the class "delete-form" and
     asks the user to confirm before submitting.
     ──────────────────────────────────────────────────────────── */
  var deleteForms = document.querySelectorAll('.delete-form');

  deleteForms.forEach(function(form) {
    form.addEventListener('submit', function(event) {
      var confirmed = window.confirm('Are you sure you want to delete this expense?');
      if (!confirmed) {
        event.preventDefault();   // stop form submit if user clicked Cancel
      }
    });
  });


  /* ── 3. Auto-dismiss flash messages after 4 seconds ─────────
     Finds all flash messages and fades them out automatically.
     ──────────────────────────────────────────────────────────── */
  var flashMessages = document.querySelectorAll('.flash');

  flashMessages.forEach(function(flash) {
    setTimeout(function() {
      flash.style.transition = 'opacity 0.5s ease';
      flash.style.opacity    = '0';

      // Remove from DOM after fade completes
      setTimeout(function() {
        flash.remove();
      }, 500);

    }, 4000);  // 4000ms = 4 seconds
  });

});
