from rest_framework import serializers

from .models import Classroom, School, Student, Teacher


class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ["id", "name", "abbreviation", "address"]


class SchoolDetailSerializer(SchoolSerializer):
    classroom_count = serializers.SerializerMethodField()
    teacher_count = serializers.SerializerMethodField()
    student_count = serializers.SerializerMethodField()

    class Meta(SchoolSerializer.Meta):
        fields = SchoolSerializer.Meta.fields + [
            "classroom_count",
            "teacher_count",
            "student_count",
        ]

    def get_classroom_count(self, obj: School) -> int:
        return obj.classrooms.count()

    def get_teacher_count(self, obj: School) -> int:
        return obj.teachers.count()

    def get_student_count(self, obj: School) -> int:
        return Student.objects.filter(classroom__school=obj).count()


class ClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        fields = ["id", "school", "year_level", "section"]


class TeacherSerializer(serializers.ModelSerializer):
    classrooms = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Classroom.objects.all(),
        required=False,
    )

    class Meta:
        model = Teacher
        fields = [
            "id",
            "school",
            "first_name",
            "last_name",
            "gender",
            "classrooms",
        ]

    def validate(self, attrs):
        school = attrs.get("school") or getattr(self.instance, "school", None)
        classrooms = attrs.get("classrooms")

        if classrooms is None and self.instance:
            classrooms = self.instance.classrooms.all()

        if school and classrooms:
            for classroom in classrooms:
                if classroom.school_id != school.id:
                    raise serializers.ValidationError(
                        {
                            "classrooms": (
                                "All classrooms must belong to the same school."
                            )
                        }
                    )

        return attrs


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = [
            "id",
            "classroom",
            "first_name",
            "last_name",
            "gender",
        ]


class ClassroomDetailSerializer(ClassroomSerializer):
    teachers = TeacherSerializer(many=True, read_only=True)
    students = StudentSerializer(many=True, read_only=True)

    class Meta(ClassroomSerializer.Meta):
        fields = ClassroomSerializer.Meta.fields + ["teachers", "students"]


class TeacherDetailSerializer(TeacherSerializer):
    classrooms = ClassroomSerializer(many=True, read_only=True)

    class Meta(TeacherSerializer.Meta):
        fields = TeacherSerializer.Meta.fields


class StudentDetailSerializer(StudentSerializer):
    classroom = ClassroomSerializer(read_only=True)

    class Meta(StudentSerializer.Meta):
        fields = StudentSerializer.Meta.fields
