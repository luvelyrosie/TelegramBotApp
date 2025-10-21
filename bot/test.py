from tasks.models import Task
from accounts.models import Profile

tg_id = 1392783196
profiles = Profile.objects.filter(telegram_id=tg_id)
user_ids = profiles.values_list("user_id", flat=True)
tasks = Task.objects.filter(assignee_id__in=list(user_ids))
print(tasks)