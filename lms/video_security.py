import os
import re
from flask import request, Response, abort, g
from models import get_db

def user_can_access_lesson(user_id, lesson_id, is_admin=False):
    if is_admin:
        return True
    
    conn = get_db()
    cur = conn.cursor()
    
    # Check if lesson is preview
    cur.execute("SELECT course_id, is_preview FROM lessons WHERE id = ?", (lesson_id,))
    lesson = cur.fetchone()
    if not lesson:
        conn.close()
        return False
        
    if lesson['is_preview'] == 1:
        conn.close()
        return True
        
    if not user_id:
        conn.close()
        return False
        
    # Check enrollment
    cur.execute('''
        SELECT id FROM enrollments 
        WHERE user_id = ? AND course_id = ? AND status = 'active'
    ''', (user_id, lesson['course_id']))
    enrollment = cur.fetchone()
    conn.close()
    
    return enrollment is not None

def stream_video_file(file_path):
    if not os.path.exists(file_path):
        abort(404)
        
    file_size = os.path.getsize(file_path)
    range_header = request.headers.get('Range', None)
    
    if not range_header:
        # Full content response
        with open(file_path, 'rb') as f:
            data = f.read()
        response = Response(data, 200, mimetype='video/mp4')
        response.headers['Content-Length'] = str(file_size)
        response.headers['Accept-Ranges'] = 'bytes'
        response.headers['Content-Disposition'] = 'inline'
        return response
        
    # Byte-range chunking for scrubbing
    byte1, byte2 = 0, None
    m = re.search(r'(\d+)-(\d*)', range_header)
    if m:
        g1, g2 = m.groups()
        byte1 = int(g1)
        if g2:
            byte2 = int(g2)
            
    if byte2 is None:
        byte2 = min(byte1 + 1024 * 1024 - 1, file_size - 1) # 1MB chunks
        
    length = byte2 - byte1 + 1
    
    with open(file_path, 'rb') as f:
        f.seek(byte1)
        data = f.read(length)
        
    response = Response(data, 206, mimetype='video/mp4')
    response.headers['Content-Range'] = f'bytes {byte1}-{byte2}/{file_size}'
    response.headers['Accept-Ranges'] = 'bytes'
    response.headers['Content-Length'] = str(length)
    response.headers['Content-Disposition'] = 'inline'
    return response
