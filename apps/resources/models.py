from django.db import models


def resource_file_path(instance, filename):
    return f"resources/{instance.uuid}/{filename}"


class ResourceCategory(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(unique=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ("order", "name")
        verbose_name_plural = "Resource categories"

    def save(self, *args, **kwargs):
        from django.utils.text import slugify
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Language(models.Model):
    name = models.CharField(max_length=60, unique=True)
    code = models.CharField(max_length=10, blank=True)

    def __str__(self):
        return self.name


class TargetAudience(models.Model):
    name = models.CharField(max_length=80, unique=True)

    def __str__(self):
        return self.name


class Resource(models.Model):
    VISIBILITY = (
        ("public", "Public — anyone can view/download"),
        ("request", "Request Access — visitors must request approval"),
        ("staff", "Internal — staff only"),
    )

    title = models.CharField(max_length=250)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to=resource_file_path)
    external_url = models.URLField(blank=True, help_text="Optional link instead of an uploaded file.")
    category = models.ForeignKey(ResourceCategory, on_delete=models.PROTECT, related_name="resources")
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, blank=True, related_name="resources")
    audiences = models.ManyToManyField(TargetAudience, blank=True, related_name="resources")
    visibility = models.CharField(max_length=10, choices=VISIBILITY, default="public")
    view_count = models.PositiveIntegerField(default=0)
    download_count = models.PositiveIntegerField(default=0)
    published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    uuid = models.UUIDField(editable=False, unique=True, blank=True, null=True)

    class Meta:
        ordering = ("-created_at",)

    def save(self, *args, **kwargs):
        import uuid as _uuid
        from django.utils.text import slugify
        if not self.pk and not self.uuid:
            self.uuid = _uuid.uuid4()
        base_slug = slugify(self.title)[:200]
        slug = base_slug
        i = 2
        qs = Resource.objects.all()
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        while qs.filter(slug=slug).exists():
            slug = f"{base_slug}-{i}"
            i += 1
        self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def is_public(self):
        return self.visibility == "public"


class AccessRequest(models.Model):
    STATUS = (("pending", "Pending"), ("approved", "Approved"), ("denied", "Denied"))

    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name="access_requests")
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    organization = models.CharField(max_length=150, blank=True)
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.full_name} → {self.resource.title} ({self.status})"
