"""
Web-based Student Management UI with Enrollment
Access from any device - works as WiFi hotspot on Raspberry Pi
Run: python web_manager.py
Access: http://192.168.4.1:5000 (hotspot) or http://<raspberry-pi-ip>:5000
"""
from flask import Flask, render_template_string, request, redirect, url_for, jsonify, Response
import sqlite3
from datetime import datetime
import threading
import time
import os
import subprocess
from config import DATABASE_PATH, HARDWARE_MODE, BASE_DIR

app = Flask(__name__)

# Global enrollment state
enrollment_state = {
    'active': False,
    'step': 'idle',  # idle, name_entered, capturing_face, capturing_aruco, complete, error
    'message': '',
    'student_name': '',
    'progress': 0
}

# HTML Template with modern smooth UI
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Attendance System</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <style>
        :root {
            --primary: #6366f1;
            --primary-dark: #4f46e5;
            --secondary: #8b5cf6;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --dark: #1e293b;
            --light: #f8fafc;
            --gray: #64748b;
        }
        
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
            min-height: 100vh;
            color: var(--light);
            padding: 16px;
            padding-bottom: 100px;
        }
        
        .container {
            max-width: 480px;
            margin: 0 auto;
        }
        
        /* Header */
        .header {
            text-align: center;
            padding: 20px 0;
            margin-bottom: 20px;
        }
        
        .header h1 {
            font-size: 28px;
            font-weight: 700;
            background: linear-gradient(135deg, #6366f1, #a855f7, #ec4899);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 8px;
        }
        
        .header .subtitle {
            color: var(--gray);
            font-size: 14px;
        }
        
        .time-badge {
            display: inline-block;
            background: rgba(99, 102, 241, 0.2);
            border: 1px solid rgba(99, 102, 241, 0.3);
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 13px;
            color: #a5b4fc;
            margin-top: 12px;
        }
        
        /* Cards */
        .card {
            background: rgba(30, 41, 59, 0.8);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 24px;
            margin-bottom: 16px;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .card:hover {
            transform: translateY(-2px);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
        }
        
        .card h2 {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .card h2 .icon {
            font-size: 24px;
        }
        
        /* Stats Grid */
        .stats-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-bottom: 20px;
        }
        
        .stat-card {
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            border-radius: 16px;
            padding: 20px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }
        
        .stat-card::before {
            content: '';
            position: absolute;
            top: -50%;
            right: -50%;
            width: 100%;
            height: 100%;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 50%;
        }
        
        .stat-card.green {
            background: linear-gradient(135deg, #059669 0%, #10b981 100%);
        }
        
        .stat-number {
            font-size: 42px;
            font-weight: 700;
            line-height: 1;
            margin-bottom: 4px;
        }
        
        .stat-label {
            font-size: 12px;
            opacity: 0.9;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        /* Navigation Grid */
        .nav-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }
        
        .nav-btn {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 8px;
            padding: 24px 16px;
            border-radius: 16px;
            text-decoration: none;
            color: white;
            font-weight: 600;
            font-size: 14px;
            transition: all 0.3s ease;
            border: none;
            cursor: pointer;
            position: relative;
            overflow: hidden;
        }
        
        .nav-btn::before {
            content: '';
            position: absolute;
            inset: 0;
            background: linear-gradient(180deg, rgba(255,255,255,0.1) 0%, transparent 100%);
        }
        
        .nav-btn:active {
            transform: scale(0.95);
        }
        
        .nav-btn .icon {
            font-size: 32px;
        }
        
        .nav-btn.students {
            background: linear-gradient(135deg, #059669, #10b981);
        }
        
        .nav-btn.attendance {
            background: linear-gradient(135deg, #0284c7, #0ea5e9);
        }
        
        .nav-btn.enroll {
            background: linear-gradient(135deg, #7c3aed, #a855f7);
            grid-column: span 2;
        }
        
        .nav-btn.reset {
            background: linear-gradient(135deg, #ea580c, #f97316);
        }
        
        .nav-btn.settings {
            background: linear-gradient(135deg, #4b5563, #6b7280);
        }
        
        /* Buttons */
        .btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            padding: 12px 20px;
            border-radius: 12px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            border: none;
            transition: all 0.2s;
            text-decoration: none;
            color: white;
        }
        
        .btn:active {
            transform: scale(0.95);
        }
        
        .btn-primary {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
        }
        
        .btn-success {
            background: linear-gradient(135deg, #059669, #10b981);
        }
        
        .btn-danger {
            background: linear-gradient(135deg, #dc2626, #ef4444);
        }
        
        .btn-warning {
            background: linear-gradient(135deg, #d97706, #f59e0b);
        }
        
        .btn-dark {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .btn-block {
            width: 100%;
            padding: 16px;
            font-size: 16px;
        }
        
        .btn-sm {
            padding: 8px 12px;
            font-size: 12px;
        }
        
        /* Forms */
        .form-group {
            margin-bottom: 16px;
        }
        
        .form-label {
            display: block;
            font-size: 14px;
            font-weight: 500;
            margin-bottom: 8px;
            color: var(--gray);
        }
        
        .form-input {
            width: 100%;
            padding: 14px 16px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            font-size: 16px;
            color: white;
            transition: border-color 0.2s;
        }
        
        .form-input:focus {
            outline: none;
            border-color: var(--primary);
            background: rgba(255, 255, 255, 0.08);
        }
        
        .form-input::placeholder {
            color: var(--gray);
        }
        
        /* Alerts */
        .alert {
            padding: 16px;
            border-radius: 12px;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 14px;
        }
        
        .alert-success {
            background: rgba(16, 185, 129, 0.2);
            border: 1px solid rgba(16, 185, 129, 0.3);
            color: #6ee7b7;
        }
        
        .alert-danger {
            background: rgba(239, 68, 68, 0.2);
            border: 1px solid rgba(239, 68, 68, 0.3);
            color: #fca5a5;
        }
        
        .alert-info {
            background: rgba(99, 102, 241, 0.2);
            border: 1px solid rgba(99, 102, 241, 0.3);
            color: #a5b4fc;
        }
        
        .alert-warning {
            background: rgba(245, 158, 11, 0.2);
            border: 1px solid rgba(245, 158, 11, 0.3);
            color: #fcd34d;
        }
        
        /* Table */
        .table-wrapper {
            overflow-x: auto;
            margin: 0 -24px;
            padding: 0 24px;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
        }
        
        th, td {
            padding: 14px 12px;
            text-align: left;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        th {
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--gray);
            font-weight: 600;
        }
        
        td {
            font-size: 14px;
        }
        
        tr:last-child td {
            border-bottom: none;
        }
        
        /* Badge */
        .badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
        }
        
        .badge-success {
            background: rgba(16, 185, 129, 0.2);
            color: #6ee7b7;
        }
        
        .badge-warning {
            background: rgba(245, 158, 11, 0.2);
            color: #fcd34d;
        }
        
        /* Empty State */
        .empty-state {
            text-align: center;
            padding: 40px 20px;
            color: var(--gray);
        }
        
        .empty-state .icon {
            font-size: 48px;
            margin-bottom: 16px;
            opacity: 0.5;
        }
        
        /* Progress */
        .progress-bar {
            height: 8px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
            overflow: hidden;
            margin: 16px 0;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--primary), var(--secondary));
            border-radius: 4px;
            transition: width 0.3s;
        }
        
        /* Status Indicator */
        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 8px;
        }
        
        .status-dot.online {
            background: #10b981;
            box-shadow: 0 0 8px #10b981;
        }
        
        .status-dot.offline {
            background: #ef4444;
        }
        
        /* Enrollment Steps */
        .enroll-step {
            display: flex;
            align-items: center;
            gap: 16px;
            padding: 16px;
            background: rgba(255, 255, 255, 0.03);
            border-radius: 12px;
            margin-bottom: 12px;
        }
        
        .step-number {
            width: 36px;
            height: 36px;
            border-radius: 50%;
            background: rgba(99, 102, 241, 0.2);
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 14px;
            color: var(--primary);
        }
        
        .step-number.active {
            background: var(--primary);
            color: white;
        }
        
        .step-number.complete {
            background: var(--success);
            color: white;
        }
        
        .step-content h4 {
            font-size: 14px;
            margin-bottom: 4px;
        }
        
        .step-content p {
            font-size: 12px;
            color: var(--gray);
        }
        
        /* Loading Spinner */
        .spinner {
            width: 40px;
            height: 40px;
            border: 3px solid rgba(255, 255, 255, 0.1);
            border-top-color: var(--primary);
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        /* Pulse Animation */
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .pulse {
            animation: pulse 2s ease-in-out infinite;
        }
        
        /* Bottom Nav */
        .bottom-nav {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: rgba(15, 23, 42, 0.95);
            backdrop-filter: blur(10px);
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            padding: 12px 16px;
            padding-bottom: max(12px, env(safe-area-inset-bottom));
            display: flex;
            justify-content: space-around;
            z-index: 100;
        }
        
        .bottom-nav a {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 4px;
            color: var(--gray);
            text-decoration: none;
            font-size: 11px;
            transition: color 0.2s;
        }
        
        .bottom-nav a.active,
        .bottom-nav a:hover {
            color: var(--primary);
        }
        
        .bottom-nav .icon {
            font-size: 24px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📋 Smart Attendance</h1>
            <p class="subtitle">Raspberry Pi Attendance System</p>
            <div class="time-badge">
                <span class="status-dot online"></span>
                {{ current_time }}
            </div>
        </div>
        
        {% if message %}
        <div class="alert alert-{{ message_type }}">
            {{ message }}
        </div>
        {% endif %}
        
        {{ content | safe }}
    </div>
    
    <nav class="bottom-nav">
        <a href="/" class="{{ 'active' if page == 'home' else '' }}">
            <span class="icon">🏠</span>
            Home
        </a>
        <a href="/students" class="{{ 'active' if page == 'students' else '' }}">
            <span class="icon">👥</span>
            Students
        </a>
        <a href="/enroll" class="{{ 'active' if page == 'enroll' else '' }}">
            <span class="icon">➕</span>
            Enroll
        </a>
        <a href="/attendance" class="{{ 'active' if page == 'attendance' else '' }}">
            <span class="icon">✅</span>
            Attendance
        </a>
    </nav>
</body>
</html>
"""

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_local_ip():
    """Get the local IP address of the Raspberry Pi"""
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "192.168.4.1"

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
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-number">{student_count}</div>
            <div class="stat-label">Students Enrolled</div>
        </div>
        <div class="stat-card green">
            <div class="stat-number">{attendance_count}</div>
            <div class="stat-label">Present Today</div>
        </div>
    </div>
    
    <div class="card">
        <h2><span class="icon">⚡</span> Quick Actions</h2>
        <div class="nav-grid">
            <a href="/students" class="nav-btn students">
                <span class="icon">👥</span>
                Students
            </a>
            <a href="/attendance" class="nav-btn attendance">
                <span class="icon">✅</span>
                Attendance
            </a>
            <a href="/enroll" class="nav-btn enroll">
                <span class="icon">➕</span>
                Enroll New Student
            </a>
            <a href="/reset" class="nav-btn reset">
                <span class="icon">🔄</span>
                Reset
            </a>
            <a href="/settings" class="nav-btn settings">
                <span class="icon">⚙️</span>
                Settings
            </a>
        </div>
    </div>
    """
    
    return render_template_string(HTML_TEMPLATE, 
                                  content=content,
                                  current_time=datetime.now().strftime("%A, %B %d • %H:%M"),
                                  message=request.args.get('message'),
                                  message_type=request.args.get('type', 'info'),
                                  page='home')

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
            <h2><span class="icon">👥</span> Enrolled Students</h2>
            <div class="empty-state">
                <div class="icon">📭</div>
                <p>No students enrolled yet</p>
                <a href="/enroll" class="btn btn-primary" style="margin-top: 16px;">
                    ➕ Enroll First Student
                </a>
            </div>
        </div>
        """
    else:
        rows = ""
        for s in students:
            rows += f"""
            <tr>
                <td><strong>{s['name']}</strong></td>
                <td><span class="badge badge-success">#{s['aruco_id']}</span></td>
                <td>
                    <form action="/delete_student/{s['id']}" method="POST" style="display:inline;" 
                          onsubmit="return confirm('Delete {s['name']}?');">
                        <button type="submit" class="btn btn-danger btn-sm">🗑️</button>
                    </form>
                </td>
            </tr>
            """
        
        content = f"""
        <div class="card">
            <h2><span class="icon">👥</span> Students ({len(students)})</h2>
            <div class="table-wrapper">
                <table>
                    <tr>
                        <th>Name</th>
                        <th>ArUco ID</th>
                        <th>Action</th>
                    </tr>
                    {rows}
                </table>
            </div>
        </div>
        <div class="card">
            <a href="/enroll" class="btn btn-success btn-block">➕ Enroll New Student</a>
            <form action="/delete_all_students" method="POST" style="margin-top: 12px;"
                  onsubmit="return confirm('⚠️ DELETE ALL STUDENTS? This cannot be undone!');">
                <button type="submit" class="btn btn-danger btn-block">🗑️ Delete All Students</button>
            </form>
        </div>
        """
    
    return render_template_string(HTML_TEMPLATE, 
                                  content=content,
                                  current_time=datetime.now().strftime("%A, %B %d • %H:%M"),
                                  message=request.args.get('message'),
                                  message_type=request.args.get('type', 'info'),
                                  page='students')

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
        message = f"✓ Deleted: {student['name']}"
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
    
    return redirect(url_for('students', message="✓ All students deleted", type="success"))

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
    
    attendance_rate = int((len(records) / total_students * 100)) if total_students > 0 else 0
    
    if not records:
        content = f"""
        <div class="card">
            <h2><span class="icon">✅</span> Today's Attendance</h2>
            <p style="color: var(--gray); margin-bottom: 16px;">{datetime.now().strftime("%A, %B %d, %Y")}</p>
            <div class="empty-state">
                <div class="icon">📋</div>
                <p>No attendance recorded today</p>
                <p style="font-size: 12px; margin-top: 8px;">Start the attendance system to begin tracking</p>
            </div>
        </div>
        """
    else:
        rows = ""
        for r in records:
            rows += f"""
            <tr>
                <td><strong>{r['name']}</strong></td>
                <td>{r['time']}</td>
                <td><span class="badge badge-success">✓ {r['status']}</span></td>
            </tr>
            """
        
        content = f"""
        <div class="stats-grid">
            <div class="stat-card green">
                <div class="stat-number">{len(records)}/{total_students}</div>
                <div class="stat-label">Present Today</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{attendance_rate}%</div>
                <div class="stat-label">Attendance Rate</div>
            </div>
        </div>
        
        <div class="card">
            <h2><span class="icon">✅</span> Attendance Log</h2>
            <div class="table-wrapper">
                <table>
                    <tr>
                        <th>Student</th>
                        <th>Time</th>
                        <th>Status</th>
                    </tr>
                    {rows}
                </table>
            </div>
        </div>
        """
    
    return render_template_string(HTML_TEMPLATE, 
                                  content=content,
                                  current_time=datetime.now().strftime("%A, %B %d • %H:%M"),
                                  message=request.args.get('message'),
                                  message_type=request.args.get('type', 'info'),
                                  page='attendance')

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
            <h2><span class="icon">🔄</span> Reset Attendance</h2>
            <p style="color: var(--gray); margin-bottom: 16px;">{datetime.now().strftime("%A, %B %d, %Y")}</p>
            <div class="empty-state">
                <div class="icon">✨</div>
                <p>No attendance to reset</p>
            </div>
        </div>
        """
    else:
        rows = ""
        for r in records:
            rows += f"""
            <tr>
                <td><strong>{r['name']}</strong></td>
                <td>{r['time']}</td>
                <td>
                    <form action="/reset_student/{r['id']}" method="POST" style="display:inline;">
                        <button type="submit" class="btn btn-warning btn-sm">Reset</button>
                    </form>
                </td>
            </tr>
            """
        
        content = f"""
        <div class="card">
            <h2><span class="icon">🔄</span> Reset Attendance</h2>
            <p style="color: var(--gray); margin-bottom: 16px;">Reset a student so they can check in again</p>
            <div class="table-wrapper">
                <table>
                    <tr>
                        <th>Student</th>
                        <th>Time</th>
                        <th>Action</th>
                    </tr>
                    {rows}
                </table>
            </div>
        </div>
        <div class="card">
            <form action="/reset_all" method="POST" 
                  onsubmit="return confirm('Reset ALL attendance for today?');">
                <button type="submit" class="btn btn-danger btn-block">🔄 Reset All Today</button>
            </form>
        </div>
        """
    
    return render_template_string(HTML_TEMPLATE, 
                                  content=content,
                                  current_time=datetime.now().strftime("%A, %B %d • %H:%M"),
                                  message=request.args.get('message'),
                                  message_type=request.args.get('type', 'info'),
                                  page='reset')

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
        message = f"✓ Reset: {student['name']}"
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
    
    return redirect(url_for('reset_page', message="✓ All attendance reset for today", type="success"))

# ============================================================
# ENROLLMENT ROUTES - Web-based student enrollment
# ============================================================

@app.route('/enroll')
def enroll_page():
    """Enrollment page with web-based enrollment"""
    content = """
    <div class="card">
        <h2><span class="icon">➕</span> Enroll New Student</h2>
        <p style="color: var(--gray); margin-bottom: 20px;">
            Add a new student to the attendance system
        </p>
        
        <form action="/enroll/start" method="POST" id="enrollForm">
            <div class="form-group">
                <label class="form-label">Student Name</label>
                <input type="text" name="student_name" class="form-input" 
                       placeholder="Enter student's full name" required
                       pattern="[A-Za-z ]{2,50}" title="Name should be 2-50 letters">
            </div>
            
            <div class="form-group">
                <label class="form-label">ArUco Marker ID</label>
                <input type="number" name="aruco_id" class="form-input" 
                       placeholder="Enter marker ID (0-249)" required
                       min="0" max="249">
                <p style="font-size: 12px; color: var(--gray); margin-top: 8px;">
                    Each student needs a unique ArUco marker ID
                </p>
            </div>
            
            <button type="submit" class="btn btn-success btn-block">
                🚀 Start Enrollment
            </button>
        </form>
    </div>
    
    <div class="card">
        <h2><span class="icon">📋</span> Enrollment Steps</h2>
        
        <div class="enroll-step">
            <div class="step-number">1</div>
            <div class="step-content">
                <h4>Enter Details</h4>
                <p>Enter student name and ArUco marker ID</p>
            </div>
        </div>
        
        <div class="enroll-step">
            <div class="step-number">2</div>
            <div class="step-content">
                <h4>Face Capture</h4>
                <p>Student positions face in front of camera</p>
            </div>
        </div>
        
        <div class="enroll-step">
            <div class="step-number">3</div>
            <div class="step-content">
                <h4>ArUco Scan</h4>
                <p>Show ArUco marker to camera</p>
            </div>
        </div>
        
        <div class="enroll-step">
            <div class="step-number">4</div>
            <div class="step-content">
                <h4>Complete</h4>
                <p>Student is enrolled and ready for attendance</p>
            </div>
        </div>
    </div>
    
    <div class="card">
        <h2><span class="icon">🖨️</span> Generate ArUco Markers</h2>
        <p style="color: var(--gray); margin-bottom: 16px;">
            Print ArUco markers for students
        </p>
        <form action="/enroll/generate_markers" method="POST">
            <div class="form-group">
                <label class="form-label">Start ID</label>
                <input type="number" name="start_id" class="form-input" value="0" min="0">
            </div>
            <div class="form-group">
                <label class="form-label">Count</label>
                <input type="number" name="count" class="form-input" value="30" min="1" max="100">
            </div>
            <button type="submit" class="btn btn-primary btn-block">
                🖨️ Generate Markers
            </button>
        </form>
    </div>
    """
    
    return render_template_string(HTML_TEMPLATE, 
                                  content=content,
                                  current_time=datetime.now().strftime("%A, %B %d • %H:%M"),
                                  message=request.args.get('message'),
                                  message_type=request.args.get('type', 'info'),
                                  page='enroll')

@app.route('/enroll/start', methods=['POST'])
def enroll_start():
    """Start the enrollment process"""
    student_name = request.form.get('student_name', '').strip()
    aruco_id = request.form.get('aruco_id', '')
    
    if not student_name or not aruco_id:
        return redirect(url_for('enroll_page', message="Please fill all fields", type="danger"))
    
    try:
        aruco_id = int(aruco_id)
    except:
        return redirect(url_for('enroll_page', message="Invalid ArUco ID", type="danger"))
    
    # Check if ArUco ID already exists
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM students WHERE aruco_id = ?", (aruco_id,))
    existing = cursor.fetchone()
    conn.close()
    
    if existing:
        return redirect(url_for('enroll_page', 
                                message=f"ArUco ID {aruco_id} already used by {existing['name']}", 
                                type="danger"))
    
    # Redirect to enrollment process page
    return redirect(url_for('enroll_process', name=student_name, aruco_id=aruco_id))

@app.route('/enroll/process')
def enroll_process():
    """Enrollment process page with live status"""
    student_name = request.args.get('name', '')
    aruco_id = request.args.get('aruco_id', '')
    
    content = f"""
    <div class="card">
        <h2><span class="icon">📸</span> Enrolling: {student_name}</h2>
        <p style="color: var(--gray);">ArUco Marker: #{aruco_id}</p>
        
        <div id="enrollment-status">
            <div class="alert alert-info">
                <span class="pulse">⏳</span> Preparing enrollment...
            </div>
            
            <div class="progress-bar">
                <div class="progress-fill" id="progress" style="width: 0%"></div>
            </div>
            
            <div id="step-status" style="margin-top: 16px;">
                <div class="enroll-step">
                    <div class="step-number active" id="step1">1</div>
                    <div class="step-content">
                        <h4>Face Capture</h4>
                        <p id="step1-text">Position face in front of camera</p>
                    </div>
                </div>
                
                <div class="enroll-step">
                    <div class="step-number" id="step2">2</div>
                    <div class="step-content">
                        <h4>ArUco Verification</h4>
                        <p id="step2-text">Waiting...</p>
                    </div>
                </div>
                
                <div class="enroll-step">
                    <div class="step-number" id="step3">3</div>
                    <div class="step-content">
                        <h4>Save to Database</h4>
                        <p id="step3-text">Waiting...</p>
                    </div>
                </div>
            </div>
        </div>
        
        <div id="result" style="display: none; margin-top: 20px;"></div>
    </div>
    
    <script>
        // Start enrollment process
        const studentName = "{student_name}";
        const arucoId = "{aruco_id}";
        
        async function startEnrollment() {{
            try {{
                const response = await fetch('/api/enroll', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ name: studentName, aruco_id: parseInt(arucoId) }})
                }});
                
                const data = await response.json();
                
                if (data.success) {{
                    document.getElementById('progress').style.width = '100%';
                    document.getElementById('step1').className = 'step-number complete';
                    document.getElementById('step2').className = 'step-number complete';
                    document.getElementById('step3').className = 'step-number complete';
                    document.getElementById('step1-text').textContent = '✓ Face captured';
                    document.getElementById('step2-text').textContent = '✓ Marker verified';
                    document.getElementById('step3-text').textContent = '✓ Saved successfully';
                    
                    document.getElementById('result').innerHTML = `
                        <div class="alert alert-success">
                            ✅ <strong>${{studentName}}</strong> enrolled successfully!
                        </div>
                        <a href="/enroll" class="btn btn-success btn-block">➕ Enroll Another</a>
                        <a href="/students" class="btn btn-dark btn-block" style="margin-top: 8px;">👥 View Students</a>
                    `;
                    document.getElementById('result').style.display = 'block';
                }} else {{
                    document.getElementById('result').innerHTML = `
                        <div class="alert alert-danger">
                            ❌ Enrollment failed: ${{data.error}}
                        </div>
                        <a href="/enroll" class="btn btn-warning btn-block">🔄 Try Again</a>
                    `;
                    document.getElementById('result').style.display = 'block';
                }}
            }} catch (error) {{
                document.getElementById('result').innerHTML = `
                    <div class="alert alert-danger">
                        ❌ Error: ${{error.message}}
                    </div>
                    <a href="/enroll" class="btn btn-warning btn-block">🔄 Try Again</a>
                `;
                document.getElementById('result').style.display = 'block';
            }}
        }}
        
        // Check enrollment status
        async function checkStatus() {{
            try {{
                const response = await fetch('/api/enroll/status');
                const data = await response.json();
                
                if (data.step === 'capturing_face') {{
                    document.getElementById('progress').style.width = '33%';
                    document.getElementById('step1-text').textContent = 'Capturing face...';
                }} else if (data.step === 'capturing_aruco') {{
                    document.getElementById('progress').style.width = '66%';
                    document.getElementById('step1').className = 'step-number complete';
                    document.getElementById('step1-text').textContent = '✓ Face captured';
                    document.getElementById('step2').className = 'step-number active';
                    document.getElementById('step2-text').textContent = 'Scanning marker...';
                }} else if (data.step === 'saving') {{
                    document.getElementById('progress').style.width = '90%';
                    document.getElementById('step2').className = 'step-number complete';
                    document.getElementById('step2-text').textContent = '✓ Marker verified';
                    document.getElementById('step3').className = 'step-number active';
                    document.getElementById('step3-text').textContent = 'Saving...';
                }}
                
                if (data.active) {{
                    setTimeout(checkStatus, 500);
                }}
            }} catch (e) {{}}
        }}
        
        // Start after page load
        setTimeout(() => {{
            startEnrollment();
            checkStatus();
        }}, 1000);
    </script>
    """
    
    return render_template_string(HTML_TEMPLATE, 
                                  content=content,
                                  current_time=datetime.now().strftime("%A, %B %d • %H:%M"),
                                  message=None,
                                  message_type='info',
                                  page='enroll')

@app.route('/api/enroll', methods=['POST'])
def api_enroll():
    """API endpoint for enrollment - runs the actual enrollment"""
    global enrollment_state
    
    data = request.get_json()
    student_name = data.get('name', '')
    aruco_id = data.get('aruco_id', 0)
    
    enrollment_state['active'] = True
    enrollment_state['student_name'] = student_name
    enrollment_state['step'] = 'starting'
    
    try:
        # Import enrollment modules
        from ai.face_detector import FaceDetector
        from ai.face_recognition import FaceRecognizer
        from ai.aruco_detector import ArucoDetector
        from hardware.camera import Camera
        from database.db_manager import DatabaseManager
        from config import (FACE_DETECTION_BACKEND, FACE_MODEL, ARUCO_DICT,
                          CAMERA_INDEX, CAMERA_WIDTH, CAMERA_HEIGHT)
        
        # Initialize components
        camera = Camera(mode=HARDWARE_MODE, camera_index=CAMERA_INDEX,
                       width=CAMERA_WIDTH, height=CAMERA_HEIGHT)
        face_detector = FaceDetector(backend=FACE_DETECTION_BACKEND)
        face_recognizer = FaceRecognizer(model_name=FACE_MODEL, backend=FACE_DETECTION_BACKEND)
        aruco_detector = ArucoDetector(dictionary=ARUCO_DICT)
        db = DatabaseManager(DATABASE_PATH)
        
        # Warm up camera
        for _ in range(5):
            camera.read_frame()
            time.sleep(0.1)
        
        # Step 1: Capture face
        enrollment_state['step'] = 'capturing_face'
        time.sleep(2)  # Give user time to position
        
        face_embedding = None
        for attempt in range(30):
            frame = camera.read_frame()
            if frame is None:
                continue
            
            faces = face_detector.detect_faces(frame)
            if len(faces) == 1:
                face_roi, _ = face_detector.get_single_face(frame)
                if face_roi is not None:
                    face_embedding = face_recognizer.generate_embedding(face_roi)
                    if face_embedding is not None:
                        break
            time.sleep(0.2)
        
        if face_embedding is None:
            camera.release()
            enrollment_state['active'] = False
            return jsonify({'success': False, 'error': 'Could not capture face. Please try again.'})
        
        # Step 2: Verify ArUco marker
        enrollment_state['step'] = 'capturing_aruco'
        time.sleep(2)
        
        detected_aruco = None
        for attempt in range(30):
            frame = camera.read_frame()
            if frame is None:
                continue
            
            marker_ids, corners = aruco_detector.detect_markers(frame)
            if aruco_id in marker_ids:
                detected_aruco = aruco_id
                break
            time.sleep(0.2)
        
        camera.release()
        
        if detected_aruco is None:
            enrollment_state['active'] = False
            return jsonify({'success': False, 'error': f'ArUco marker #{aruco_id} not detected. Show the marker to camera.'})
        
        # Step 3: Save to database
        enrollment_state['step'] = 'saving'
        student_id = db.add_student(student_name, aruco_id, face_embedding)
        
        enrollment_state['active'] = False
        enrollment_state['step'] = 'complete'
        
        if student_id:
            return jsonify({'success': True, 'student_id': student_id})
        else:
            return jsonify({'success': False, 'error': 'Failed to save student. ArUco ID may already exist.'})
            
    except Exception as e:
        enrollment_state['active'] = False
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/enroll/status')
def api_enroll_status():
    """Get enrollment status"""
    return jsonify(enrollment_state)

@app.route('/enroll/generate_markers', methods=['POST'])
def generate_markers():
    """Generate ArUco markers"""
    try:
        from ai.aruco_detector import ArucoDetector
        from config import ARUCO_DICT
        import cv2
        
        start_id = int(request.form.get('start_id', 0))
        count = int(request.form.get('count', 30))
        
        detector = ArucoDetector(dictionary=ARUCO_DICT)
        output_dir = os.path.join(BASE_DIR, "aruco_markers")
        os.makedirs(output_dir, exist_ok=True)
        
        for i in range(count):
            marker_id = start_id + i
            marker_img = detector.generate_marker(marker_id, size=200)
            filename = os.path.join(output_dir, f"aruco_marker_{marker_id}.png")
            cv2.imwrite(filename, marker_img)
        
        return redirect(url_for('enroll_page', 
                                message=f"✓ Generated {count} markers in aruco_markers folder", 
                                type="success"))
    except Exception as e:
        return redirect(url_for('enroll_page', message=f"Error: {str(e)}", type="danger"))

# ============================================================
# SETTINGS PAGE
# ============================================================

@app.route('/settings')
def settings_page():
    """Settings and system information"""
    local_ip = get_local_ip()
    
    content = f"""
    <div class="card">
        <h2><span class="icon">📡</span> Network Access</h2>
        <p style="color: var(--gray); margin-bottom: 16px;">Connect to this system from any device</p>
        
        <div class="alert alert-info">
            <strong>Web UI Address:</strong><br>
            http://{local_ip}:5000
        </div>
        
        <p style="font-size: 13px; color: var(--gray); margin-top: 12px;">
            Connect your phone to the same WiFi network or the Pi's hotspot, 
            then open the address above in your browser.
        </p>
    </div>
    
    <div class="card">
        <h2><span class="icon">📶</span> WiFi Hotspot Setup</h2>
        <p style="color: var(--gray); margin-bottom: 16px;">
            Make your Raspberry Pi a WiFi hotspot for direct phone connection
        </p>
        
        <div class="alert alert-warning">
            <strong>Setup Commands (run on Pi):</strong>
        </div>
        
        <pre style="background: rgba(0,0,0,0.3); padding: 12px; border-radius: 8px; 
                    font-size: 12px; overflow-x: auto; color: #a5b4fc;">
# Install hostapd and dnsmasq
sudo apt install hostapd dnsmasq -y

# Create hotspot config
sudo nmcli device wifi hotspot \\
  ssid "AttendancePi" \\
  password "attendance123"

# The Pi will broadcast:
# SSID: AttendancePi
# Password: attendance123
# Access UI at: http://192.168.4.1:5000
        </pre>
        
        <a href="/settings/hotspot_guide" class="btn btn-primary btn-block" style="margin-top: 12px;">
            📖 Full Hotspot Guide
        </a>
    </div>
    
    <div class="card">
        <h2><span class="icon">⚙️</span> System Info</h2>
        <table>
            <tr>
                <td style="color: var(--gray);">Hardware Mode</td>
                <td><strong>{HARDWARE_MODE}</strong></td>
            </tr>
            <tr>
                <td style="color: var(--gray);">Database</td>
                <td><strong>{os.path.basename(DATABASE_PATH)}</strong></td>
            </tr>
            <tr>
                <td style="color: var(--gray);">Local IP</td>
                <td><strong>{local_ip}</strong></td>
            </tr>
        </table>
    </div>
    
    <div class="card">
        <h2><span class="icon">🔧</span> Service Control</h2>
        <p style="color: var(--gray); margin-bottom: 16px;">Manage attendance service</p>
        
        <form action="/settings/service" method="POST" style="display: flex; gap: 8px;">
            <button type="submit" name="action" value="restart" class="btn btn-warning" style="flex: 1;">
                🔄 Restart
            </button>
            <button type="submit" name="action" value="stop" class="btn btn-danger" style="flex: 1;">
                ⏹️ Stop
            </button>
            <button type="submit" name="action" value="start" class="btn btn-success" style="flex: 1;">
                ▶️ Start
            </button>
        </form>
    </div>
    """
    
    return render_template_string(HTML_TEMPLATE, 
                                  content=content,
                                  current_time=datetime.now().strftime("%A, %B %d • %H:%M"),
                                  message=request.args.get('message'),
                                  message_type=request.args.get('type', 'info'),
                                  page='settings')

@app.route('/settings/hotspot_guide')
def hotspot_guide():
    """Complete hotspot setup guide"""
    content = """
    <div class="card">
        <h2><span class="icon">📶</span> WiFi Hotspot Setup Guide</h2>
        <p style="color: var(--gray); margin-bottom: 20px;">
            Turn your Raspberry Pi into a WiFi hotspot so you can connect directly 
            from your phone without needing an external router.
        </p>
        
        <h3 style="font-size: 16px; margin: 20px 0 12px;">Method 1: Using nmcli (Easiest)</h3>
        <pre style="background: rgba(0,0,0,0.3); padding: 12px; border-radius: 8px; 
                    font-size: 11px; overflow-x: auto; color: #a5b4fc;">
# Create hotspot (one command!)
sudo nmcli device wifi hotspot ssid "AttendancePi" password "attendance123"

# To make it permanent (start on boot):
sudo nmcli connection modify Hotspot connection.autoconnect yes
        </pre>
        
        <h3 style="font-size: 16px; margin: 20px 0 12px;">Method 2: Using hostapd (Advanced)</h3>
        <pre style="background: rgba(0,0,0,0.3); padding: 12px; border-radius: 8px; 
                    font-size: 11px; overflow-x: auto; color: #a5b4fc;">
# 1. Install required packages
sudo apt update
sudo apt install hostapd dnsmasq -y

# 2. Stop services for configuration
sudo systemctl stop hostapd
sudo systemctl stop dnsmasq

# 3. Configure static IP for wlan0
sudo nano /etc/dhcpcd.conf
# Add at the end:
interface wlan0
    static ip_address=192.168.4.1/24
    nohook wpa_supplicant

# 4. Configure DHCP server
sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig
sudo nano /etc/dnsmasq.conf
# Add:
interface=wlan0
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h

# 5. Configure access point
sudo nano /etc/hostapd/hostapd.conf
# Add:
interface=wlan0
driver=nl80211
ssid=AttendancePi
hw_mode=g
channel=7
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=attendance123
wpa_key_mgmt=WPA-PSK
rsn_pairwise=CCMP

# 6. Point hostapd to config
sudo nano /etc/default/hostapd
# Set: DAEMON_CONF="/etc/hostapd/hostapd.conf"

# 7. Enable and start services
sudo systemctl unmask hostapd
sudo systemctl enable hostapd
sudo systemctl enable dnsmasq
sudo reboot
        </pre>
        
        <h3 style="font-size: 16px; margin: 20px 0 12px;">After Setup</h3>
        <div class="alert alert-success">
            <strong>Connect from your phone:</strong><br>
            1. WiFi: <strong>AttendancePi</strong><br>
            2. Password: <strong>attendance123</strong><br>
            3. Open browser: <strong>http://192.168.4.1:5000</strong>
        </div>
    </div>
    
    <a href="/settings" class="btn btn-dark btn-block">← Back to Settings</a>
    """
    
    return render_template_string(HTML_TEMPLATE, 
                                  content=content,
                                  current_time=datetime.now().strftime("%A, %B %d • %H:%M"),
                                  message=None,
                                  message_type='info',
                                  page='settings')

@app.route('/settings/service', methods=['POST'])
def service_control():
    """Control the attendance service"""
    action = request.form.get('action', '')
    
    try:
        if HARDWARE_MODE == "RASPBERRY_PI":
            if action == 'restart':
                subprocess.run(['sudo', 'systemctl', 'restart', 'attendance.service'], check=True)
                message = "✓ Attendance service restarted"
            elif action == 'stop':
                subprocess.run(['sudo', 'systemctl', 'stop', 'attendance.service'], check=True)
                message = "✓ Attendance service stopped"
            elif action == 'start':
                subprocess.run(['sudo', 'systemctl', 'start', 'attendance.service'], check=True)
                message = "✓ Attendance service started"
            else:
                message = "Unknown action"
            msg_type = "success"
        else:
            message = "Service control only available on Raspberry Pi"
            msg_type = "warning"
    except Exception as e:
        message = f"Error: {str(e)}"
        msg_type = "danger"
    
    return redirect(url_for('settings_page', message=message, type=msg_type))

if __name__ == '__main__':
    local_ip = get_local_ip()
    
    print("=" * 60)
    print("  📋 SMART ATTENDANCE SYSTEM - WEB MANAGER")
    print("=" * 60)
    print()
    print("  🌐 Access the Web UI from any device:")
    print()
    print(f"     http://{local_ip}:5000")
    print()
    print("  📱 If using WiFi Hotspot mode:")
    print()
    print("     http://192.168.4.1:5000")
    print()
    print("  📶 To setup WiFi Hotspot on Raspberry Pi:")
    print()
    print('     sudo nmcli device wifi hotspot ssid "AttendancePi" password "attendance123"')
    print()
    print("=" * 60)
    print("  Press Ctrl+C to stop the server")
    print("=" * 60)
    
    # Run on all interfaces so it's accessible from other devices
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
