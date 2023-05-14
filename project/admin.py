from django.contrib import admin
# Register your models here.
from django.contrib import admin
from .models import User, Shelter, Donation, Dog, Adoption, Euthanization
# Register your models here.

admin.site.register(User),
admin.site.register(Shelter),
admin.site.register(Donation),
admin.site.register(Dog),
admin.site.register(Adoption),
admin.site.register(Euthanization),