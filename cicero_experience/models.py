from django.db import models


class Visitantes(models.Model):
    data_chekin = models.DateTimeField(auto_now_add=True)
    pais = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=100, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    transporte = models.CharField(max_length=100, blank=True, null=True)
    idade = models.IntegerField(blank=True, null=True)