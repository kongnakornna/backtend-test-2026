from rest_framework.routers import DefaultRouter

from .views import ClassroomViewSet, SchoolViewSet, StudentViewSet, TeacherViewSet

router = DefaultRouter()
router.register("schools", SchoolViewSet, basename="school")
router.register("classrooms", ClassroomViewSet, basename="classroom")
router.register("teachers", TeacherViewSet, basename="teacher")
router.register("students", StudentViewSet, basename="student")

urlpatterns = router.urls
