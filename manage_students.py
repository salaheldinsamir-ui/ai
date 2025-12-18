"""
Student Management Script
Delete and enroll students in the attendance system
"""
import sys
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
        student_id, name, aruco_id, encoding, enrolled_date = student
        print(f"  ID: {student_id} | Name: {name:20s} | ArUco: {aruco_id} | Date: {enrolled_date}")
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
            # Delete student
            cursor = db.conn.cursor()
            cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
            cursor.execute("DELETE FROM attendance WHERE student_id = ?", (student_id,))
            db.conn.commit()
            
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
        cursor = db.conn.cursor()
        cursor.execute("DELETE FROM students")
        cursor.execute("DELETE FROM attendance")
        db.conn.commit()
        
        print(f"\n✓ All students deleted")
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
        print("  5. Exit")
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
