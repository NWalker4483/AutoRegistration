import os,sys,inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir) 
from manager import Manager
from student import Student
manager = Manager()
manager.AddStudent(Student("niwal7", None))
manager.AddCourseSubscribtion("202070","TEST","101","111111","niwal7")
for _ in range(4):
    manager.CheckCourseAvailability()
