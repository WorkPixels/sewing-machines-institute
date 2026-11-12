/* ==========================================================================
   SMI University - Classroom Player & Anti-Download Security Engine
   ========================================================================== */

document.addEventListener('DOMContentLoaded', function() {
  const videoPlayer = document.getElementById('lessonVideoPlayer');
  const watermarkEl = document.getElementById('floatingWatermark');
  const markCompleteBtn = document.getElementById('markCompleteBtn');

  // 1. Anti-Download: Disable Context Menu (Right Click) across theater
  const videoWrap = document.querySelector('.video-player-wrap');
  if (videoWrap) {
    videoWrap.addEventListener('contextmenu', function(e) {
      e.preventDefault();
      showSecurityNotice("Video downloads and right-click actions are disabled to protect course content.");
      return false;
    });
  }

  // 2. Anti-Download: Intercept Developer Tools / Save Shortcuts
  window.addEventListener('keydown', function(e) {
    // Block Ctrl+S, Ctrl+U, Ctrl+Shift+I, F12
    if ((e.ctrlKey && (e.key === 's' || e.key === 'u' || e.key === 'S' || e.key === 'U')) ||
        (e.ctrlKey && e.shiftKey && (e.key === 'I' || e.key === 'i' || e.key === 'J' || e.key === 'j')) ||
        e.key === 'F12') {
      e.preventDefault();
      showSecurityNotice("Content inspection and direct saving are restricted by SMI University security policy.");
      return false;
    }
  });

  // 3. Dynamic Forensics Floating Watermark
  if (watermarkEl && videoWrap) {
    function animateWatermark() {
      const maxX = Math.max(10, videoWrap.clientWidth - watermarkEl.clientWidth - 40);
      const maxY = Math.max(10, videoWrap.clientHeight - watermarkEl.clientHeight - 40);

      const randomX = Math.floor(Math.random() * maxX);
      const randomY = Math.floor(Math.random() * maxY);

      watermarkEl.style.left = randomX + 'px';
      watermarkEl.style.top = randomY + 'px';
    }

    // Move watermark every 4 seconds to deter screen recording and cropping
    setInterval(animateWatermark, 4000);
    animateWatermark();
  }

  // 4. Progress Toggle (Mark Complete)
  if (markCompleteBtn) {
    markCompleteBtn.addEventListener('click', function() {
      const lessonId = this.getAttribute('data-lesson-id');
      const courseId = this.getAttribute('data-course-id');
      const isCompleted = this.getAttribute('data-completed') === '1';

      fetch('/api/progress/toggle', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          lesson_id: lessonId,
          course_id: courseId,
          completed: !isCompleted
        })
      })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          const newStatus = data.completed;
          markCompleteBtn.setAttribute('data-completed', newStatus ? '1' : '0');
          if (newStatus) {
            markCompleteBtn.innerHTML = '&#10003; Lesson Completed';
            markCompleteBtn.className = 'btn btn-mint btn-sm';
          } else {
            markCompleteBtn.innerHTML = 'Mark Lesson Complete';
            markCompleteBtn.className = 'btn btn-outline btn-sm';
          }

          // Update sidebar checkbox
          const sideCheckbox = document.getElementById('sidebar-check-' + lessonId);
          if (sideCheckbox) {
            if (newStatus) {
              sideCheckbox.classList.add('checked');
              sideCheckbox.innerHTML = '&#10003;';
            } else {
              sideCheckbox.classList.remove('checked');
              sideCheckbox.innerHTML = '';
            }
          }
        }
      })
      .catch(err => console.error('Error toggling progress:', err));
    });
  }

  // 5. Track video playback position periodically
  if (videoPlayer) {
    let lastSavedTime = 0;
    videoPlayer.addEventListener('timeupdate', function() {
      const currentSeconds = Math.floor(videoPlayer.currentTime);
      if (currentSeconds - lastSavedTime >= 15) {
        lastSavedTime = currentSeconds;
        const lessonId = markCompleteBtn ? markCompleteBtn.getAttribute('data-lesson-id') : null;
        if (lessonId) {
          navigator.sendBeacon('/api/progress/time', JSON.stringify({
            lesson_id: lessonId,
            seconds: currentSeconds
          }));
        }
      }
    });
  }
});

function switchLessonTab(tabName) {
  const allTabs = document.querySelectorAll('.tab-nav-btn');
  const allPanes = document.querySelectorAll('.tab-pane-content');

  allTabs.forEach(t => t.classList.remove('active'));
  allPanes.forEach(p => p.style.display = 'none');

  const selectedBtn = document.getElementById('tab-btn-' + tabName);
  const selectedPane = document.getElementById('tab-pane-' + tabName);

  if (selectedBtn) selectedBtn.classList.add('active');
  if (selectedPane) selectedPane.style.display = 'block';
}

function showSecurityNotice(msg) {
  const existing = document.getElementById('securityNoticeBox');
  if (existing) existing.remove();

  const notice = document.createElement('div');
  notice.id = 'securityNoticeBox';
  notice.style.position = 'fixed';
  notice.style.bottom = '20px';
  notice.style.right = '20px';
  notice.style.background = '#1B263B';
  notice.style.color = '#FFFFFF';
  notice.style.border = '2px solid #9B5E3C';
  notice.style.padding = '12px 18px';
  notice.style.borderRadius = '8px';
  notice.style.fontSize = '13px';
  notice.style.fontWeight = 'bold';
  notice.style.boxShadow = '0 10px 25px rgba(0,0,0,0.4)';
  notice.style.zIndex = '9999';
  notice.innerText = '🛡️ ' + msg;

  document.body.appendChild(notice);
  setTimeout(() => {
    notice.style.opacity = '0';
    notice.style.transition = 'opacity 0.5s ease';
    setTimeout(() => notice.remove(), 500);
  }, 3500);
}
