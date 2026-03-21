from django.contrib import admin
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class MyUser(AbstractUser):
    user_types = ((1,'Admin'),(2,'Teacher'),(3,'Student'))
    user_type = models.CharField(default=1, choices=user_types, max_length=10)

class Admin(models.Model):
    id = models.AutoField(primary_key=True)
    admin = models.OneToOneField(MyUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

class Teacher(models.Model):
    GENDER_CHOICES = (('Male','Male'),('Female','Female'),('Other','Other'))
    id = models.AutoField(primary_key=True)
    admin = models.OneToOneField(MyUser, on_delete=models.CASCADE)
    gender = models.CharField(max_length=15, choices=GENDER_CHOICES, default='Other')
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

class Student(models.Model):
    YEAR_CHOICES = ((1,'First Year'),(2,'Second Year'),(3,'Third Year'),(4,'Fourth Year'))
    GENDER_CHOICES = (('Male','Male'),('Female','Female'),('Other','Other'))
    DEPARTMENT_CHOICES = (
        ('CS', 'Computer Science'),
        ('IT', 'Information Technology'),
        ('ENTC', 'Electronics & Telecommunication'),
        ('MECH', 'Mechanical Engineering'),
        ('CIVIL', 'Civil Engineering'),
    )
    id = models.AutoField(primary_key=True)
    admin = models.OneToOneField(MyUser, on_delete=models.CASCADE)
    roll_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    gender = models.CharField(max_length=15, choices=GENDER_CHOICES, default='Other')
    year = models.IntegerField(choices=YEAR_CHOICES, default=1)
    department = models.CharField(max_length=100, choices=DEPARTMENT_CHOICES, default='CS')
    section = models.CharField(max_length=5, default='A')
    college_email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

class Course(models.Model):
    DEPARTMENT_CHOICES = (
        ('CS', 'Computer Science'),
        ('IT', 'Information Technology'),
        ('ENTC', 'Electronics & Telecommunication'),
        ('MECH', 'Mechanical Engineering'),
        ('CIVIL', 'Civil Engineering'),
    )
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100, choices=DEPARTMENT_CHOICES, default='CS')
    year = models.IntegerField()
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

    def __str__(self):
        return f"{self.code} - {self.name}"

class Attendance(models.Model):
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateField()
    is_present = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

    class Meta:
        unique_together = ('student', 'course', 'date')

class InternalMarks(models.Model):
    EXAM_TYPE_CHOICES = (
        ('IA1', 'Internal Assessment 1'),
        ('IA2', 'Internal Assessment 2'),
        ('MID', 'Mid Semester'),
        ('END', 'End Semester'),
    )
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    exam_type = models.CharField(max_length=10, choices=EXAM_TYPE_CHOICES)
    marks_obtained = models.FloatField()
    max_marks = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

class ExamSchedule(models.Model):
    id = models.AutoField(primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    exam_type = models.CharField(max_length=50)
    exam_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    venue = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

class FeeStatus(models.Model):
    STATUS_CHOICES = (('Paid','Paid'),('Pending','Pending'),('Partial','Partial'))
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    semester = models.IntegerField()
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

class Timetable(models.Model):
    DAY_CHOICES = (
        ('Mon','Monday'),('Tue','Tuesday'),('Wed','Wednesday'),
        ('Thu','Thursday'),('Fri','Friday'),('Sat','Saturday'),
    )
    id = models.AutoField(primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    day = models.CharField(max_length=5, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=50)
    objects = models.Manager()

class Notification(models.Model):
    id = models.AutoField(primary_key=True)
    heading = models.CharField(max_length=150)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=20)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

class Result(models.Model):
    title = models.CharField(max_length=50)
    file = models.FileField()
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.TextField()

class Notes(models.Model):
    title = models.CharField(max_length=50)
    file = models.FileField()
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.TextField()

@receiver(post_save, sender=MyUser)
def user_create(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == 1:
            Admin.objects.create(admin=instance)
        if instance.user_type == 2:
            Teacher.objects.create(admin=instance)
        if instance.user_type == 3:
            Student.objects.create(admin=instance)

@receiver(post_save, sender=MyUser)
def user_save(sender, instance, **kwargs):
    if instance.user_type == 1:
        instance.admin.save()
    if instance.user_type == 2:
        instance.teacher.save()
    if instance.user_type == 3:
        instance.student.save()
