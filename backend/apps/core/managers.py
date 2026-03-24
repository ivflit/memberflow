from django.db import models


class TenantManager(models.Manager):
    def for_tenant(self, organization):
        return self.get_queryset().filter(organization=organization)
