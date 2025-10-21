from django import forms
from .models import TaskList, Task
from django.contrib.auth import get_user_model

User = get_user_model()

class TaskListForm(forms.ModelForm):
    class Meta:
        model = TaskList
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Task List Name'}),
        }

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date', 'assignee', 'is_done']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Task Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Task Description'}),
            'due_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'assignee': forms.Select(attrs={'class': 'form-control'}),
            'is_done': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }