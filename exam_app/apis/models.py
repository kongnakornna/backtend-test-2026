from django.db import models


class Gender(models.TextChoices):
    MALE = "M", "Male"
    FEMALE = "F", "Female"
    OTHER = "O", "Other"


class School(models.Model):
    name = models.CharField(max_length=255)
    abbreviation = models.CharField(max_length=50)
    address = models.TextField()

    def __str__(self) -> str:
        return self.name


class Classroom(models.Model):
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="classrooms",
    )
    year_level = models.PositiveSmallIntegerField()
    section = models.CharField(max_length=50)

    class Meta:
        unique_together = ("school", "year_level", "section")

    def __str__(self) -> str:
        return f"{self.school.abbreviation} {self.year_level}/{self.section}"


class Teacher(models.Model):
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="teachers",
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=Gender.choices)
    classrooms = models.ManyToManyField(
        Classroom,
        related_name="teachers",
        blank=True,
    )

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Student(models.Model):
    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.CASCADE,
        related_name="students",
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=Gender.choices)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"
