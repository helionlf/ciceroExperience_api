from django.db import models


class Visitantes(models.Model):
    data_chekin = models.DateTimeField(auto_now_add=True)
    data = models.DateField(auto_now_add=True)
    fingerprint = models.CharField(max_length=128)

    pais = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=100, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    
    FAIXAS_ETARIAS = (
        ('crianca', 'Criança (até 12 anos)'),
        ('adolescente', 'Adolescente (13 a 17 anos)'),
        ('jovem_adulto', 'Jovem Adulto (18 a 29 anos)'),
        ('adulto', 'Adulto (30 a 59 anos)'),
        ('idoso', 'Idoso (60+ anos)'),
        ('nao_informado', 'Não Informado'),
    )
    faixa_etaria = models.CharField(
        max_length=20,
        choices=FAIXAS_ETARIAS,
        default='nao_informado',
        blank=True,
        null=True
    )

    OPCOES_GRUPO = (
        ('sim', 'Sim'),
        ('nao', 'Não'),
        ('desconhecido', 'Desconhecido'),
    )
    grupo = models.CharField(
        max_length=20,
        choices=OPCOES_GRUPO,
        default='desconhecido',
        blank=True,
        null=True
    )

    OPCOES_GENERO = (
        ('masculino', 'Masculino'),
        ('feminino', 'Feminino'),
        ('outros', 'Outros'),
        ('nao_informado', 'Não Informar'),
    )
    genero = models.CharField(
        max_length=20,
        choices=OPCOES_GENERO,
        default='nao_informado',
        blank=True,
        null=True
    )

    OPCOES_COR_RACA = (
        ('preto', 'Preto'),
        ('pardo', 'Pardo'),
        ('indigena', 'Indígena'),
        ('branco', 'Branco'),
        ('amarelo', 'Amarelo'),
        ('nao_informado', 'Não Informar'),
    )
    cor_raca = models.CharField(
        max_length=20,
        choices=OPCOES_COR_RACA,
        default='nao_informado',
        blank=True,
        null=True
    )

    class Meta:
        unique_together = ("fingerprint", "data")
