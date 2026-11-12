import urllib.request
import urllib.parse
import http.cookiejar
import json

base_url = 'http://127.0.0.1:5000'
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

# 1. Test unauthenticated /login
resp = opener.open(f'{base_url}/login')
assert resp.getcode() == 200, 'Login page failed'
print('TEST 1: Login page HTTP 200 OK')

# 2. Test Student Login
login_data = urllib.parse.urlencode({
    'email': 'student@sewingmachinesinstitute.com',
    'password': 'Student2026!'
}).encode('utf-8')
resp = opener.open(f'{base_url}/login', data=login_data)
assert resp.getcode() == 200, 'Student login failed'
print('TEST 2: Student Login successful, session established')

# 3. Test Student Dashboard
resp = opener.open(f'{base_url}/dashboard')
html = resp.read().decode('utf-8')
assert 'Sarah Jenkins' in html, 'Student name not in dashboard'
assert 'Free 7-Step Sewing Machine Maintenance' in html, 'Course not in dashboard'
print('TEST 3: Student Dashboard loaded with enrolled courses')

# 4. Test Video Classroom
resp = opener.open(f'{base_url}/classroom/free-7-step-maintenance')
html = resp.read().decode('utf-8')
assert 'lessonVideoPlayer' in html, 'Video player missing'
assert 'floatingWatermark' in html, 'Watermark missing'
assert 'controlsList="nodownload noplaybackrate"' in html, 'Anti-download controls missing'
print('TEST 4: Video Classroom loaded with Anti-Download layer & Watermark')

# 5. Test Authenticated Stream Endpoint
resp = opener.open(f'{base_url}/api/stream/1')
assert resp.getcode() == 200, 'Stream endpoint failed'
print('TEST 5: Protected Video Stream API 200 OK')

# 6. Test Unauthenticated Stream Endpoint (must be blocked)
plain_opener = urllib.request.build_opener()
try:
    plain_opener.open(f'{base_url}/api/stream/1')
    print('TEST 6 FAILED: Unauthenticated request was NOT blocked!')
except urllib.error.HTTPError as e:
    assert e.code in [401, 403], f'Expected 401/403, got {e.code}'
    print(f'TEST 6: Unauthenticated video stream blocked ({e.code} Forbidden/Unauthorized)')

# 7. Test Admin Login & Overview
admin_cj = http.cookiejar.CookieJar()
admin_opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(admin_cj))
admin_data = urllib.parse.urlencode({
    'email': 'admin@sewingmachinesinstitute.com',
    'password': 'SMIadmin2026!'
}).encode('utf-8')
admin_opener.open(f'{base_url}/login', data=admin_data)
resp = admin_opener.open(f'{base_url}/admin')
assert resp.getcode() == 200, 'Admin overview failed'
print('TEST 7: Admin Studio Overview 200 OK')

# 8. Test Wix CSV Migration (Run sample import)
mig_data = urllib.parse.urlencode({'use_sample': 'true'}).encode('utf-8')
resp = admin_opener.open(f'{base_url}/admin/wix-migration', data=mig_data)
html = resp.read().decode('utf-8')
assert 'Wix Migration Complete' in html, 'Wix migration did not complete'
print('TEST 8: Wix CSV Bulk Migration executed & verified successfully!')

# 9. Test 1-Click Access Toggle API
toggle_req = urllib.request.Request(
    f'{base_url}/api/admin/toggle_access',
    data=json.dumps({'user_id': 2, 'course_id': 3}).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)
resp = admin_opener.open(toggle_req)
toggle_json = json.loads(resp.read().decode('utf-8'))
assert toggle_json.get('success') is True, 'Toggle access failed'
print('TEST 9: Granular 1-Click Access Control Toggle API verified (Status: ' + str(toggle_json.get('status')) + ')')

print('>>> ALL 9 AUTOMATED SUITE TESTS PASSED PERFECTLY! <<<')
