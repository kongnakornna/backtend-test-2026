from django.db import models


class Gender(models.TextChoices):
    MALE = 'M', 'Male'
    FEMALE = 'F', 'Female'
    OTHER = 'O', 'Other'


class School(models.Model):
    name = models.CharField(max_length=255)
    abbreviation = models.CharField(max_length=50)
    address = models.TextField()

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name


class Classroom(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='classrooms')
    year_level = models.PositiveSmallIntegerField()  # ชั้นปี
    section = models.CharField(max_length=20)  # ทับ

    class Meta:
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(
                fields=['school', 'year_level', 'section'],
                name='unique_classroom_per_school',
            ),
        ]

    def __str__(self):
        return f'{self.school.abbreviation} {self.year_level}/{self.section}'


class Teacher(models.Model):
    # A teacher belongs to one school so they can be counted/filtered by school
    # even before being assigned to any classroom.
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='teachers')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=Gender.choices)
    classrooms = models.ManyToManyField(Classroom, related_name='teachers', blank=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Student(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='students')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=Gender.choices)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
