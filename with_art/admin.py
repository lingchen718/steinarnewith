from django.contrib import admin
from .models import ArtProject, Entry, CurrentProject, CurrentEntry, ContactMessage


# ============================================================
# ArtProject
# ============================================================

class EntryInline(admin.TabularInline):
    model = Entry
    extra = 1
    fields = ('title', 'image', 'video', 'order')
    verbose_name = 'entry'
    verbose_name_plural = 'entries'


@admin.register(ArtProject)
class ArtProjectAdmin(admin.ModelAdmin):
    list_display  = ['title', 'has_cover_image', 'has_cover_video', 'is_current', 'date_added', 'order']
    inlines       = [EntryInline]
    list_filter   = ['is_current', 'date_added']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    list_editable  = ['is_current', 'order']
    actions        = ['resequence_artprojects']

    def has_cover_image(self, obj):
        return bool(obj.cover_image)
    has_cover_image.boolean = True
    has_cover_image.short_description = 'Image'

    def has_cover_video(self, obj):
        return bool(obj.cover_video)
    has_cover_video.boolean = True
    has_cover_video.short_description = 'Video'

    @admin.action(description="Resequence by current sort order (1, 2, 3, …)")
    def resequence_artprojects(self, request, queryset):
        ordered = ArtProject.objects.order_by('order', '-date_added', 'id')
        for i, project in enumerate(ordered, start=1):
            project.order = i
            project.save(update_fields=['order'])
        self.message_user(request, f"{queryset.count()} projects resequenced.")


# ============================================================
# Entry (standalone backup admin)
# ============================================================

@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display  = ['title', 'artproject', 'has_image', 'has_video', 'order']
    list_filter   = ['artproject', 'order']
    search_fields = ['title']
    autocomplete_fields = ['artproject']
    actions        = ['resequence_entries']

    def has_image(self, obj):
        return bool(obj.image)
    has_image.boolean = True
    has_image.short_description = 'Image'

    def has_video(self, obj):
        return bool(obj.video)
    has_video.boolean = True
    has_video.short_description = 'Video'

    @admin.action(description="Resequence entries by current sort order (per project: 1, 2, 3, …)")
    def resequence_entries(self, request, queryset):
        ordered = Entry.objects.order_by('artproject_id', 'order', 'id')
        last_parent = None
        n = 0
        for entry in ordered:
            if entry.artproject_id != last_parent:
                n = 1
                last_parent = entry.artproject_id
            else:
                n += 1
            entry.order = n
            entry.save(update_fields=['order'])
        self.message_user(request, f"{queryset.count()} entries resequenced.")


# ============================================================
# CurrentProject — now with inline entries
# ============================================================

class CurrentEntryInline(admin.TabularInline):
    """Mirror of EntryInline, scoped to CurrentEntry."""
    model = CurrentEntry
    extra = 1
    fk_name = 'current_project'         # explicit since FK name ≠ model name
    fields = ('title', 'image', 'video', 'order')
    verbose_name = 'current entry'
    verbose_name_plural = 'current entries'


@admin.register(CurrentProject)
class CurrentProjectAdmin(admin.ModelAdmin):
    list_display  = ['title', 'is_published', 'date_added', 'order']
    inlines       = [CurrentEntryInline]
    list_filter   = ['is_published', 'date_added']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    list_editable  = ['is_published', 'order']
    actions        = ['resequence_currentprojects']

    @admin.action(description="Resequence by current sort order (1, 2, 3, …)")
    def resequence_currentprojects(self, request, queryset):
        ordered = CurrentProject.objects.order_by('order', '-date_added', 'id')
        for i, project in enumerate(ordered, start=1):
            project.order = i
            project.save(update_fields=['order'])
        self.message_user(request, f"{queryset.count()} current projects resequenced.")


# ============================================================
# CurrentEntry (standalone backup admin, optional)
# ============================================================

@admin.register(CurrentEntry)
class CurrentEntryAdmin(admin.ModelAdmin):
    list_display  = ['title', 'current_project', 'has_image', 'has_video', 'order']
    list_filter   = ['current_project', 'order']
    search_fields = ['title']
    autocomplete_fields = ['current_project']
    actions        = ['resequence_currententries']

    def has_image(self, obj):
        return bool(obj.image)
    has_image.boolean = True
    has_image.short_description = 'Image'

    def has_video(self, obj):
        return bool(obj.video)
    has_video.boolean = True
    has_video.short_description = 'Video'

    @admin.action(description="Resequence current entries by current sort order (per project: 1, 2, 3, …)")
    def resequence_currententries(self, request, queryset):
        ordered = CurrentEntry.objects.order_by('current_project_id', 'order', 'id')
        last_parent = None
        n = 0
        for entry in ordered:
            if entry.current_project_id != last_parent:
                n = 1
                last_parent = entry.current_project_id
            else:
                n += 1
            entry.order = n
            entry.save(update_fields=['order'])
        self.message_user(request, f"{queryset.count()} current entries resequenced.")


# ============================================================
# ContactMessage
# ============================================================

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at', 'is_read')
    list_filter = ('subject', 'is_read', 'created_at')
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('name', 'email', 'subject', 'message', 'budget', 'created_at')
