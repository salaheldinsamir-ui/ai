"""
Student Management Script
Delete and enroll students in the attendance system
With attendance reset feature
"""
import sys
from datetime import datetime
from database.db_manager import DatabaseManager
from config import DATABASE_PATH

def list_students(db):
    """List all enrolled students"""
    students = db.get_all_students()
    
    if not students:
        print("\n✗ No students enrolled yet")
        return []
    
    print("\n" + "="*60)
    print("ENROLLED STUDENTS")
    print("="*60)
    for student in students:
        student_id, name, aruco_id, encoding = student
        print(f"  ID: {student_id} | Name: {name:20s} | ArUco: {aruco_id}")
    print("="*60)
    
    return students

def delete_student(db):
    """Delete a student"""
    students = list_students(db)
    
    if not students:
        return
    
    print("\nEnter student ID to delete (or 'cancel'): ", end='')
    choice = input().strip()
    
    if choice.lower() == 'cancel':
        print("Cancelled")
        return
    
    try:
        student_id = int(choice)
        
        # Find student
        student = None
        for s in students:
            if s[0] == student_id:
                student = s
                break
        
        if not student:
            print(f"\n✗ Student ID {student_id} not found")
            return
        
        # Confirm deletion
        print(f"\n⚠️  Delete student: {student[1]} (ID: {student_id})? (yes/no): ", end='')
        confirm = input().strip().lower()
        
        if confirm == 'yes':
            # Delete student using proper connection
            import sqlite3
            conn = sqlite3.connect(db.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
            cursor.execute("DELETE FROM attendance WHERE student_id = ?", (student_id,))
            conn.commit()
            conn.close()
            
            print(f"\n✓ Student {student[1]} deleted successfully")
        else:
            print("Cancelled")
            
    except ValueError:
        print("\n✗ Invalid student ID")
    except Exception as e:
        print(f"\n✗ Error deleting student: {e}")

def delete_all_students(db):
    """Delete all students"""
    students = list_students(db)
    
    if not students:
        return
    
    print(f"\n⚠️  DELETE ALL {len(students)} STUDENTS? (type 'DELETE ALL' to confirm): ", end='')
    confirm = input().strip()
    
    if confirm == 'DELETE ALL':
        import sqlite3
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM students")
        cursor.execute("DELETE FROM attendance")
        # Reset auto-increment counter so next student starts at ID 1
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='students'")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='attendance'")
        conn.commit()
        conn.close()
        
        print(f"\n✓ All students deleted (IDs reset to start from 1)")
    else:
        print("Cancelled")

def enroll_students():
    """Run the enrollment script"""
    print("\n" + "="*60)
    print("STARTING STUDENT ENROLLMENT")
    print("="*60)
    
    import subprocess
    result = subprocess.run([sys.executable, "enroll_students.py"])
    
    if result.returncode == 0:
        print("\n✓ Enrollment completed")
    else:
        print("\n✗ Enrollment failed")

def reset_student_attendance(db):
    """Reset attendance for a specific student (allows them to take attendance again today)"""
    students = list_students(db)
    
    if not students:
        return
    
    print("\nEnter student ID to reset today's attendance (or 'cancel'): ", end='')
    choice = input().strip()
    
    if choice.lower() == 'cancel':
        print("Cancelled")
        return
    
    try:
        student_id = int(choice)
        
        # Find student
        student = None
        for s in students:
            if s[0] == student_id:
                student = s
                break
        
        if not student:
            print(f"\n✗ Student ID {student_id} not found")
            return
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Check if they have attendance today
        import sqlite3
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, time FROM attendance WHERE student_id = ? AND date = ?",
            (student_id, today)
        )
        records = cursor.fetchall()
        
        if not records:
            print(f"\n✗ {student[1]} has no attendance record for today")
            conn.close()
            return
        
        print(f"\n⚠️  Reset attendance for {student[1]} today? They can take attendance again. (yes/no): ", end='')
        confirm = input().strip().lower()
        
        if confirm == 'yes':
            cursor.execute(
                "DELETE FROM attendance WHERE student_id = ? AND date = ?",
                (student_id, today)
            )
            conn.commit()
            print(f"\n✓ Attendance reset for {student[1]} - they can take attendance again today")
        else:
            print("Cancelled")
        
        conn.close()
            
    except ValueError:
        print("\n✗ Invalid student ID")
    except Exception as e:
        print(f"\n✗ Error resetting attendance: {e}")

def reset_all_attendance_today(db):
    """Reset all attendance for today"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    import sqlite3
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM attendance WHERE date = ?",
        (today,)
    )
    count = cursor.fetchone()[0]
    
    if count == 0:
        print(f"\n✗ No attendance records for today ({today})")
        conn.close()
        return
    
    print(f"\n⚠️  Reset ALL {count} attendance records for today ({today})? (type 'RESET ALL' to confirm): ", end='')
    confirm = input().strip()
    
    if confirm == 'RESET ALL':
        cursor.execute(
            "DELETE FROM attendance WHERE date = ?",
            (today,)
        )
        conn.commit()
        print(f"\n✓ All attendance for today has been reset - all students can take attendance again")
    else:
        print("Cancelled")
    
    conn.close()

def view_today_attendance(db):
    """View today's attendance"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    import sqlite3
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.id, s.name, a.time, a.status 
        FROM attendance a 
        JOIN students s ON a.student_id = s.id 
        WHERE a.date = ?
        ORDER BY a.time DESC
    """, (today,))
    records = cursor.fetchall()
    conn.close()
    
    print("\n" + "="*60)
    print(f"TODAY'S ATTENDANCE ({today})")
    print("="*60)
    
    if not records:
        print("  No attendance recorded today")
    else:
        for student_id, name, time_str, status in records:
            print(f"  ID: {student_id} | {name:20s} | Time: {time_str} | {status}")
    
    print("="*60)
    print(f"Total: {len(records)} students present today")

def main():
    """Main menu"""
    print("="*60)
    print("STUDENT MANAGEMENT SYSTEM")
    print("="*60)
    
    db = DatabaseManager(DATABASE_PATH)
    
    while True:
        print("\nOptions:")
        print("  1. List all students")
        print("  2. Delete a student")
        print("  3. Delete ALL students")
        print("  4. Enroll new students")
        print("  5. View today's attendance")
        print("  6. Reset student attendance (allow re-take)")
        print("  7. Reset ALL attendance today")
        print("  8. Exit")
        print("\nChoice: ", end='')
        
        choice = input().strip()
        
        if choice == '1':
            list_students(db)
            
        elif choice == '2':
            delete_student(db)
            
        elif choice == '3':
            delete_all_students(db)
            
        elif choice == '4':
            enroll_students()
            
        elif choice == '5':
            view_today_attendance(db)
            
        elif choice == '6':
            reset_student_attendance(db)
            
        elif choice == '7':
            reset_all_attendance_today(db)
            
        elif choice == '8':
            print("\nExiting...")
            break
            
        else:
            print("\n✗ Invalid choice")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
