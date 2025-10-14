from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError

class ServiceActionMixin:
    """
    A mixin to encapsulate common create, update, and delete logic
    for ViewSets that interact with a service layer.
    """
    service = None # Must be set by the ViewSet

    def _handle_service_action(self, action_func, *args, **kwargs):
        try:
            result = action_func(*args, **kwargs)
            return result
        except ValidationError as e:
            return Response({'detail': e.message_dict}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create_with_service(self, serializer, service_method_name, *args, **kwargs):
        def _create():
            obj = getattr(self.service, service_method_name)(serializer.validated_data, *args, **kwargs)
            headers = self.get_success_headers(serializer.data)
            return Response(self.get_serializer(obj).data, status=status.HTTP_201_CREATED, headers=headers)
        return self._handle_service_action(_create)

    def update_with_service(self, instance, serializer, service_method_name, *args, **kwargs):
        def _update():
            obj = getattr(self.service, service_method_name)(instance.pk, serializer.validated_data, *args, **kwargs)
            return Response(self.get_serializer(obj).data)
        return self._handle_service_action(_update)

    def destroy_with_service(self, instance, service_method_name, *args, **kwargs):
        def _destroy():
            if not getattr(self.service, service_method_name)(instance.pk, *args, **kwargs):
                return Response(status=status.HTTP_404_NOT_FOUND)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return self._handle_service_action(_destroy)
