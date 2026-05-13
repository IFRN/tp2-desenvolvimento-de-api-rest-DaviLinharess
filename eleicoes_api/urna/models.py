from django.db import models
from django.core.exceptions import ValidationError

class Eleitor(models.Model):
    nome = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    cpf = models.CharField(max_length=14, unique=True)
    data_nascimento = models.DateField()
    ativo = models.BooleanField(default=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nome} - {self.ativo}"

class Eleicao(models.Model):
    class TipoChoices(models.TextChoices):
        ESTUDANTIL = 'estudantil', 'Estudantil'
        SINDICAL = 'sindical', 'Sindical'
        ASSOCIACAO = 'associacao', 'Associação'
        CONDOMINIO = 'condominio', 'Condomínio'
        CONSELHO = 'conselho', 'Conselho'
        OUTRA = 'outra', 'Outra'

    class StatusChoices(models.TextChoices):
        RASCUNHO = 'rascunho', 'Rascunho'
        ABERTA = 'aberta', 'Aberta'
        ENCERRADA = 'encerrada', 'Encerrada'
        APURADA = 'apurada', 'Apurada'

    titulo = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    tipo = models.CharField(max_length=20, choices = TipoChoices.choices)
    data_inicio = models.DateTimeField()
    data_fim = models.DateTimeField()
    status = models.CharField(max_length=20, choices = StatusChoices.choices)
    permite_branco = models.BooleanField(default=True)
    criada_por = models.ForeignKey(Eleitor, on_delete=models.PROTECT, related_name='eleicoes_criadas')

    def clean(self):

        if self.data_fim < self.data_inicio:
            raise ValidationError("A Data de fim deve ser após a data de inicio")

    def __str__(self):
        return f"{self.titulo} - {self.tipo}"
    

class Candidato(models.Model):
    eleicao = models.ForeignKey(Eleicao, on_delete=models.CASCADE, related_name='candidatos')
    numero = models.PositiveIntegerField() #Número de exibição do candidato
    nome = models.CharField(max_length=150)
    nome_urna = models.CharField(max_length=50)
    partido_ou_chapa = models.CharField(max_length=100, unique=True)
    proposta = models.TextField(blank=True)
    foto_url = models.URLField(blank=True)

    class Meta:
        unique_together = [('eleicao', 'numero')]

    def __str__(self):
        return f"{self.nome} ({self.partido_ou_chapa}) - {self.eleicao}"


class AptidaoEleitor(models.Model):
    eleitor = models.ForeignKey(Eleitor, on_delete=models.PROTECT, related_name='aptidoes')
    eleicao = models.ForeignKey(Eleicao, on_delete=models.CASCADE, related_name='aptos')
    data_inclusao = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('eleitor', 'eleicao')]
    
    def __str__(self):
        return f"{self.eleitor} - {self.eleicao}"

class RegistroVotacao(models.Model):
    eleitor = models.ForeignKey(Eleitor, on_delete=models.PROTECT, related_name='registros_votacao')
    eleicao = models.ForeignKey(Eleicao, on_delete=models.PROTECT, related_name='registros_votacao')
    data_hora = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('eleitor', 'eleicao')]

    def __str__(self):
        return f"{self.eleitor} - {self.eleicao}"

class Voto(models.Model):
    eleicao = models.ForeignKey(Eleicao, on_delete=models.PROTECT, related_name='votos')
    candidato = models.ForeignKey(Candidato, on_delete=models.PROTECT, related_name='votos', null=True, blank=True)
    em_branco = models.BooleanField(default=False)
    data_hora = models.DateTimeField(auto_now_add=True)
    comprovante_hash = models.CharField(max_length=64, unique=True)

    def clean(self):

        if (em_branco==True and candidato==None) or (em_branco==False and candidato is not None):
            raise ValidationError("Erro de Validação")


