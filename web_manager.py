"""
Web-based Student Management UI
Access from any device on the same network
Run: python web_manager.py
Access: http://<raspberry-pi-ip>:5000
"""
from flask import Flask, render_template_string, request, redirect, url_for, jsonify
import sqlite3
from datetime import datetime
from config import DATABASE_PATH

app = Flask(__name__)

# HTML Template with mobile-friendly UI
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Attendance System Manager</title>
    <style>
        * {
            box-sizing: border-box;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        body {
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
        }
        h1 {
            color: white;
            text-align: center;
            margin-bottom: 20px;
            font-size: 24px;
        }
        .card {
            background: white;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .card h2 {
            margin-top: 0;
            color: #333;
            font-size: 18px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        .nav-buttons {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-bottom: 20px;
        }
        .nav-btn {
            padding: 15px;
            border: none;
            border-radius: 10px;
            font-size: 14px;
            font-weight: bold;
            cursor: pointer;
            text-decoration: none;
            text-align: center;
            color: white;
            transition: transform 0.2s;
        }
        .nav-btn:hover {
            transform: scale(1.02);
        }
        .nav-btn.students { background: #4CAF50; }
        .nav-btn.attendance { background: #2196F3; }
        .nav-btn.reset { background: #FF9800; }
        .nav-btn.home { background: #9C27B0; }
        
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            padding: 12px 8px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }
        th {
            background: #f5f5f5;
            font-weight: 600;
            color: #333;
        }
        tr:hover {
            background: #f9f9f9;
        }
        .btn {
            padding: 8px 16px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            transition: opacity 0.2s;
        }
        .btn:hover {
            opacity: 0.8;
        }
        .btn-danger {
            background: #f44336;
            color: white;
        }
        .btn-warning {
            background: #FF9800;
            color: white;
        }
        .btn-success {
            background: #4CAF50;
            color: white;
        }
        .btn-block {
            width: 100%;
            padding: 15px;
            font-size: 16px;
            margin-top: 10px;
        }
        .alert {
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 15px;
        }
        .alert-success {
            background: #d4edda;
            color: #155724;
        }
        .alert-danger {
            background: #f8d7da;
            color: #721c24;
        }
        .alert-info {
            background: #d1ecf1;
            color: #0c5460;
        }
        .stat-box {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 20px;
        }
        .stat {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        .stat-number {
            font-size: 36px;
            font-weight: bold;
        }
        .stat-label {
            font-size: 12px;
            opacity: 0.9;
        }
        .empty-state {
            text-align: center;
            padding: 40px;
            color: #666;
        }
        .badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
        }
        .badge-success {
            background: #d4edda;
            color: #155724;
        }
        .time-display {
            text-align: center;
            color: white;
            margin-bottom: 20px;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📋 Attendance Manager</h1>
        <div class="time-display">{{ current_time }}</div>
        
        {% if message %}
        <div class="alert alert-{{ message_type }}">
            {{ message }}
        </div>
        {% endif %}
        
        {{ content | safe }}
    </div>
</body>
</html>
"""

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    """Home page with stats and navigation"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get stats
    cursor.execute("SELECT COUNT(*) FROM students")
    student_count = cursor.fetchone()[0]
    
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("SELECT COUNT(*) FROM attendance WHERE date = ?", (today,))
    attendance_count = cursor.fetchone()[0]
    
    conn.close()
    
    content = f"""
    <div class="stat-box">
        <div class="stat">
            <div class="stat-number">{student_count}</div>
            <div class="stat-label">Students Enrolled</div>
        </div>
        <div class="stat">
            <div class="stat-number">{attendance_count}</div>
            <div class="stat-label">Present Today</div>
        </div>
    </div>
    
    <div class="card">
        <h2>📌 Quick Actions</h2>
        <div class="nav-buttons">
            <a href="/students" class="nav-btn students">👥 Students</a>
            <a href="/attendance" class="nav-btn attendance">✅ Attendance</a>
            <a href="/reset" class="nav-btn reset">🔄 Reset</a>
            <a href="/enroll" class="nav-btn home">➕ Enroll Info</a>
        </div>
    </div>
    """
    
    return render_template_string(HTML_TEMPLATE, 
                                  content=content,
                                  current_time=datetime.now().strftime("%Y-%m-%d %H:%M"),
                                  message=request.args.get('message'),
                                  message_type=request.args.get('type', 'info'))

@app.route('/students')
def students():
    """List all students"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, aruco_id FROM students ORDER BY name")
    students = cursor.fetchall()
    conn.close()
    
    if not students:
        content = """
        <div class="card">
            <h2>👥 Enrolled Students</h2>
            <div class="empty-state">
                <p>No students enrolled yet</p>
                <p>Use the enrollment script on Raspberry Pi</p>
            </div>
        </div>
        <a href="/" class="nav-btn home btn-block">← Back to Home</a>
        """
    else:
        rows = ""
        for s in students:
            rows += f"""
            <tr>
                <td>{s['id']}</td>
                <td>{s['name']}</td>
                <td>{s['aruco_id']}</td>
                <td>
                    <form action="/delete_student/{s['id']}" method="POST" style="display:inline;" 
                          onsubmit="return confirm('Delete {s['name']}?');">
                        <button type="submit" class="btn btn-danger">Delete</button>
                    </form>
                </td>
            </tr>
            """
        
        content = f"""
        <div class="card">
            <h2>👥 Enrolled Students ({len(students)})</h2>
            <table>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>ArUco</th>
                    <th>Action</th>
                </tr>
                {rows}
            </table>
        </div>
        <div class="card">
            <form action="/delete_all_students" method="POST" 
                  onsubmit="return confirm('DELETE ALL STUDENTS? This cannot be undone!');">
                <button type="submit" class="btn btn-danger btn-block">🗑️ Delete All Students</button>
            </form>
        </div>
        <a href="/" class="nav-btn home btn-block">← Back to Home</a>
        """
    
    return render_template_string(HTML_TEMPLATE, 
                                  content=content,
                                  current_time=datetime.now().strftime("%Y-%m-%d %H:%M"),
                                  message=request.args.get('message'),
                                  message_type=request.args.get('type', 'info'))

@app.route('/delete_student/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    """Delete a student"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get student name first
    cursor.execute("SELECT name FROM students WHERE id = ?", (student_id,))
    student = cursor.fetchone()
    
    if student:
        cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
        cursor.execute("DELETE FROM attendance WHERE student_id = ?", (student_id,))
        conn.commit()
        message = f"Deleted student: {student['name']}"
        msg_type = "success"
    else:
        message = "Student not found"
        msg_type = "danger"
    
    conn.close()
    return redirect(url_for('students', message=message, type=msg_type))

@app.route('/delete_all_students', methods=['POST'])
def delete_all_students():
    """Delete all students"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students")
    cursor.execute("DELETE FROM attendance")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='students'")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='attendance'")
    conn.commit()
    conn.close()
    
    return redirect(url_for('students', message="All students deleted. IDs reset.", type="success"))

@app.route('/attendance')
def attendance():
    """View today's attendance"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.id, s.name, a.time, a.status 
        FROM attendance a 
        JOIN students s ON a.student_id = s.id 
        WHERE a.date = ?
        ORDER BY a.time DESC
    """, (today,))
    records = cursor.fetchall()
    
    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]
    conn.close()
    
    if not records:
        content = f"""
        <div class="card">
            <h2>✅ Today's Attendance ({today})</h2>
            <div class="empty-state">
                <p>No attendance recorded today</p>
            </div>
        </div>
        <a href="/" class="nav-btn home btn-block">← Back to Home</a>
        """
    else:
        rows = ""
        for r in records:
            rows += f"""
            <tr>
                <td>{r['name']}</td>
                <td>{r['time']}</td>
                <td><span class="badge badge-success">{r['status']}</span></td>
                <td>
                    <form action="/reset_student/{r['id']}" method="POST" style="display:inline;">
                        <button type="submit" class="btn btn-warning">Reset</button>
                    </form>
                </td>
            </tr>
            """
        
        content = f"""
        <div class="card">
            <h2>✅ Today's Attendance ({today})</h2>
            <p><strong>{len(records)}</strong> of <strong>{total_students}</strong> students present</p>
            <table>
                <tr>
                    <th>Name</th>
                    <th>Time</th>
                    <th>Status</th>
                    <th>Action</th>
                </tr>
                {rows}
            </table>
        </div>
        <a href="/" class="nav-btn home btn-block">← Back to Home</a>
        """
    
    return render_template_string(HTML_TEMPLATE, 
                                  content=content,
                                  current_time=datetime.now().strftime("%Y-%m-%d %H:%M"),
                                  message=request.args.get('message'),
                                  message_type=request.args.get('type', 'info'))

@app.route('/reset')
def reset_page():
    """Reset options page"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Get students with attendance today
    cursor.execute("""
        SELECT s.id, s.name, a.time 
        FROM attendance a 
        JOIN students s ON a.student_id = s.id 
        WHERE a.date = ?
        ORDER BY s.name
    """, (today,))
    records = cursor.fetchall()
    conn.close()
    
    if not records:
        content = f"""
        <div class="card">
            <h2>🔄 Reset Attendance ({today})</h2>
            <div class="empty-state">
                <p>No attendance to reset today</p>
            </div>
        </div>
        <a href="/" class="nav-btn home btn-block">← Back to Home</a>
        """
    else:
        rows = ""
        for r in records:
            rows += f"""
            <tr>
                <td>{r['name']}</td>
                <td>{r['time']}</td>
                <td>
                    <form action="/reset_student/{r['id']}" method="POST" style="display:inline;">
                        <button type="submit" class="btn btn-warning">Reset</button>
                    </form>
                </td>
            </tr>
            """
        
        content = f"""
        <div class="card">
            <h2>🔄 Reset Attendance ({today})</h2>
            <p>Reset a student's attendance so they can check in again</p>
            <table>
                <tr>
                    <th>Name</th>
                    <th>Time</th>
                    <th>Action</th>
                </tr>
                {rows}
            </table>
        </div>
        <div class="card">
            <form action="/reset_all" method="POST" 
                  onsubmit="return confirm('Reset ALL attendance for today?');">
                <button type="submit" class="btn btn-danger btn-block">🔄 Reset ALL Today</button>
            </form>
        </div>
        <a href="/" class="nav-btn home btn-block">← Back to Home</a>
        """
    
    return render_template_string(HTML_TEMPLATE, 
                                  content=content,
                                  current_time=datetime.now().strftime("%Y-%m-%d %H:%M"),
                                  message=request.args.get('message'),
                                  message_type=request.args.get('type', 'info'))

@app.route('/reset_student/<int:student_id>', methods=['POST'])
def reset_student(student_id):
    """Reset a student's attendance for today"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM students WHERE id = ?", (student_id,))
    student = cursor.fetchone()
    
    if student:
        cursor.execute("DELETE FROM attendance WHERE student_id = ? AND date = ?", 
                      (student_id, today))
        conn.commit()
        message = f"Reset attendance for {student['name']}"
        msg_type = "success"
    else:
        message = "Student not found"
        msg_type = "danger"
    
    conn.close()
    return redirect(url_for('reset_page', message=message, type=msg_type))

@app.route('/reset_all', methods=['POST'])
def reset_all():
    """Reset all attendance for today"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM attendance WHERE date = ?", (today,))
    conn.commit()
    conn.close()
    
    return redirect(url_for('reset_page', message="All attendance for today has been reset", type="success"))

@app.route('/enroll')
def enroll_info():
    """Show enrollment instructions"""
    content = """
    <div class="card">
        <h2>➕ How to Enroll Students</h2>
        <p>To enroll new students, you need to use the Raspberry Pi directly:</p>
        <ol>
            <li>SSH into your Raspberry Pi or use keyboard/monitor</li>
            <li>Stop the attendance service:
                <br><code>sudo systemctl stop attendance.service</code></li>
            <li>Run the enrollment script:
                <br><code>cd ~/ai && python enroll_students.py</code></li>
            <li>Follow the on-screen instructions</li>
            <li>Restart the attendance service:
                <br><code>sudo systemctl start attendance.service</code></li>
        </ol>
    </div>
    <a href="/" class="nav-btn home btn-block">← Back to Home</a>
    """
    
    return render_template_string(HTML_TEMPLATE, 
                                  content=content,
                                  current_time=datetime.now().strftime("%Y-%m-%d %H:%M"),
                                  message=None,
                                  message_type='info')

if __name__ == '__main__':
    print("="*50)
    print("ATTENDANCE MANAGER WEB UI")
    print("="*50)
    print("\nAccess from any device on the same network:")
    print("  http://<raspberry-pi-ip>:5000")
    print("\nTo find your Pi's IP address, run: hostname -I")
    print("\nPress Ctrl+C to stop the server")
    print("="*50)
    
    # Run on all interfaces so it's accessible from other devices
    app.run(host='0.0.0.0', port=5000, debug=False)
