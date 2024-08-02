from django.shortcuts import render
from django.template import loader
# Create your views here.
from django.http import HttpResponse
from app.models import Question

def exibir_empresa(request):
    question=Question.objects.all()
    template=loader.get_template("frontend/pages-empresas.html")
    rendered_template=template.render(context={"question":question}, request=request)
    return HttpResponse(rendered_template)
def index(request):
    question=Question.objects.all()
    template=loader.get_template("frontend/index.html")
    rendered_template=template.render(context={"question":question}, request=request)
    return HttpResponse(rendered_template)
def login(request):
    question=Question.objects.all()
    template=loader.get_template("frontend/pages-login.html")
    rendered_template=template.render(context={"question":question}, request=request)
    return HttpResponse(rendered_template)
def transações(request):
    question=Question.objects.all()
    template=loader.get_template("frontend/historico-transacoes.html")
    rendered_template=template.render(context={"question":question}, request=request)
    return HttpResponse(rendered_template)
def colaboradores(request):
    question=Question.objects.all()
    template=loader.get_template("frontend/pages-colaboradores.html")
    rendered_template=template.render(context={"question":question}, request=request)
    return HttpResponse(rendered_template)
def perfil(request):
    question=Question.objects.all()
    template=loader.get_template("frontend/page-perfil.html")
    rendered_template=template.render(context={"question":question}, request=request)
    return HttpResponse(rendered_template)
def tributos(request):
    question=Question.objects.all()
    template=loader.get_template("frontend/tributos.html")
    rendered_template=template.render(context={"question":question}, request=request)
    return HttpResponse(rendered_template)
def page_404(request):
    question=Question.objects.all()
    template=loader.get_template("frontend/pages-error-404.html")
    rendered_template=template.render(context={"question":question}, request=request)
    return HttpResponse(rendered_template)