from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.views.generic import RedirectView
from django.urls import reverse_lazy
from django.contrib.auth import logout, login, authenticate

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, AccessMixin

from .forms import RegisterForm, LoginForm, ProjectForm, VacancyForm
from .models import User, Project, ProjectMember, Vacancy


class UserLoginView(UserPassesTestMixin, AccessMixin, FormView):
    form_class = LoginForm
    template_name = 'login-form.html'

    def test_func(self):
        return not self.request.user.is_authenticated

    def get_success_url(self):
        return reverse_lazy('account-view', kwargs={'pk': self.request.user.id})

    def handle_no_permission(self):
        return redirect(self.get_success_url())

    def form_valid(self, form):
        u = authenticate(
            email=form.cleaned_data.get('email'),
            password=form.cleaned_data.get('password'),
        )
        login(self.request, u)
        return super().form_valid(form)


# register / login / logout stuff
class UserRegisterView(FormView):
    form_class = RegisterForm
    template_name = 'register-form.html'
    success_url = reverse_lazy('login-view')

    def form_valid(self, form):
        u = User.objects.create_user(
            email=form.cleaned_data.get('email'),
            password=form.cleaned_data.get('password'),
            first_name=form.cleaned_data.get('first_name'),
            last_name=form.cleaned_data.get('last_name'),
            login_method='e',
        )
        return super().form_valid(form)


class UserLogoutView(LoginRequiredMixin, RedirectView):
    url = reverse_lazy('login-view')

    login_url = reverse_lazy('login-view')

    def get(self, request, *args, **kwargs):
        logout(request)
        return super(UserLogoutView, self).get(request, *args, **kwargs)


# User Self-management stuff
class UserSettingsView:
    pass


class UserPageView(DetailView):
    model = User
    template_name = 'user-page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['me'] = self.request.user
        context['is_my_page'] = self.request.user == context['object']
        return context


class ProjectCreateView(FormView):
    form_class = ProjectForm
    template_name = 'create-project-page.html'
    success_url = reverse_lazy('login-view')

    def form_valid(self, form):
        p = Project.objects.create(**form.cleaned_data)
        pm = ProjectMember.objects.create(
            user=self.request.user,
            status='in',
            role='owner',
            project=p
        )
        return super().form_valid(form)


class VacancyCreateView(FormView):
    form_class = VacancyForm
    template_name = 'create-project-page.html'
    success_url = reverse_lazy('login-view')

    def get_initial(self):
        initial = super(VacancyCreateView, self).get_initial()
        p = get_object_or_404(Project, pk=self.kwargs['project_id'])
        initial['project'] = p
        return initial


    def form_valid(self, form):
        v = Vacancy.objects.create(**form.cleaned_data)
        pm = ProjectMember.objects.create(
            user=self.request.user,
            status='in',
            role='owner',
            project=form.cleaned_data['project'],
            vacancy=v
        )
        return super().form_valid(form)



class ProjectInvitePeopleView:
    pass


class ProjectVacancyListView:
    pass


class ProjectVacancyView:
    pass


# Searching things
class UsersListView:
    pass


class ProjectsListView:
    pass


class VacanciesListView:
    pass