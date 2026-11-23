from rest_framework import serializers

from apis.models import Classroom, School, Student, Teacher


# ---------- School ----------

class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ['id', 'name', 'abbreviation', 'address']


class SchoolDetailSerializer(SchoolSerializer):
    # Values are annotated on the queryset in SchoolViewSet.get_queryset
    classroom_count = serializers.IntegerField(read_only=True)
    teacher_count = serializers.IntegerField(read_only=True)
    student_count = serializers.IntegerField(read_only=True)

    class Meta(SchoolSerializer.Meta):
        fields = SchoolSerializer.Meta.fields + ['classroom_count', 'teacher_count', 'student_count']


# ---------- Short nested representations ----------

class ClassroomSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        fields = ['id', 'school', 'year_level', 'section']


class TeacherSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ['id', 'first_name', 'last_name', 'gender']


class StudentSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'first_name', 'last_name', 'gender']


# ---------- Classroom ----------

class ClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        fields = ['id', 'school', 'year_level', 'section']

    def validate_year_level(self, value):
        if value < 1:
            raise serializers.ValidationError('year_level must be at least 1.')
        return value

    def validate(self, attrs):
        # Moving a classroom to another school would break the rule that a
        # teacher only teaches classrooms in their own school.
        school = attrs.get('school')
        if self.instance and school and school != self.instance.school:
            if self.instance.teachers.exclude(school=school).exists():
                raise serializers.ValidationError(
                    {'school': 'Cannot move classroom: it has teachers from another school.'}
                )
        return attrs


class ClassroomDetailSerializer(ClassroomSerializer):
    school = SchoolSerializer(read_only=True)
    teachers = TeacherSummarySerializer(many=True, read_only=True)
    students = StudentSummarySerializer(many=True, read_only=True)

    class Meta(ClassroomSerializer.Meta):
        fields = ClassroomSerializer.Meta.fields + ['teachers', 'students']


# ---------- Teacher ----------

class TeacherSerializer(serializers.ModelSerializer):
    classrooms = serializers.PrimaryKeyRelatedField(
        queryset=Classroom.objects.all(), many=True, required=False
    )

    class Meta:
        model = Teacher
        fields = ['id', 'school', 'first_name', 'last_name', 'gender', 'classrooms']

    def validate(self, attrs):
        school = attrs.get('school', getattr(self.instance, 'school', None))
        if 'classrooms' in attrs:
            classrooms = attrs['classrooms']
        elif self.instance:
            classrooms = list(self.instance.classrooms.all())
        else:
            classrooms = []

        invalid = [c.id for c in classrooms if c.school_id != school.id]
        if invalid:
            raise serializers.ValidationError(
                {'classrooms': f'Classrooms {invalid} do not belong to the teacher\'s school.'}
            )
        return attrs


class TeacherDetailSerializer(TeacherSerializer):
    classrooms = ClassroomSummarySerializer(many=True, read_only=True)


# ---------- Student ----------

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'first_name', 'last_name', 'gender', 'classroom']


class StudentDetailSerializer(StudentSerializer):
    classroom = ClassroomSummarySerializer(read_only=True)
