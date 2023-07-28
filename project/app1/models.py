from django.db import models
from django.contrib.auth.models import AbstractUser
from enum import Enum


class RoleChoices(Enum):
    ADMIN = 'Admin'
    PROF = 'Professor'
    STUDENT = 'Student'

    @classmethod
    def choices(cls):
        return [(choice.value, choice.name) for choice in cls]


class SubjectStatusChoices(Enum):
    EN = 'Enrolled'
    PA = 'Passed'
    FA = 'Failed'

    @classmethod
    def choices(cls):
        return [(choice.value, choice.name) for choice in cls]
    

class StudentStatusChoices(Enum):
    NONE = 'None'
    IR = 'Irregular'
    RE = 'Regular'

    @classmethod
    def choices(cls):
        return [(choice.value, choice.name) for choice in cls]


class Role(models.Model):
    role = models.CharField(max_length=20, choices=RoleChoices.choices())

    def __str__(self):
        return self.role


class StudentStatus(models.Model):
    status = models.CharField(max_length=30, choices=StudentStatusChoices.choices())

    def __str__(self):
        return self.status


class SubjectStatus(models.Model):
    status = models.CharField(max_length=30, choices=SubjectStatusChoices.choices())

    def __str__(self):
        return self.status


class User(AbstractUser):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, blank="true", null="true")
    status = models.ForeignKey(StudentStatus, on_delete=models.CASCADE, blank="true", null="true")


class Subjects(models.Model):
    name = models.CharField(max_length=30)
    code = models.CharField(max_length=10)
    program = models.TextField()
    ects = models.IntegerField()
    sem_reg = models.IntegerField()
    sem_irr = models.IntegerField()
    elective = models.CharField(max_length=3)
    professor = models.ForeignKey(User, on_delete=models.CASCADE, blank="true", null="true")

    def __str__(self):
        return self.name

class User_Subjects(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    subjects = models.ForeignKey(Subjects, on_delete=models.CASCADE, blank=True, null=True)
    status = models.ForeignKey(SubjectStatus, on_delete=models.CASCADE, blank=True, null=True, default=1)