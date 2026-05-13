from rest_framework import serializers
from .models import Eleitor, Eleicao, Candidato, AptidaoEleitor, RegistroVotacao, Voto
import re
from django.core.exceptions import ValidationError
from django.utils import timezone

class EleitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Eleitor
        fields = '__all__'

    def validar_cpf(self, value):
        padrao = r'^\d{3}\.\d{3}\.\d{3}-\d{2}$'

        if not re.match(padrao, value):
            raise serializers.ValidationError(
                "O CPF deve ser no formato 000.000.000-00."
            )
        
        return value

class EleicaoSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display')
    total_candidatos = serializers.SerializerMethodField()
    total_aptos = serializers.IntegerField(source='aptos.count')

    class Meta:
        model = Eleicao
        fields = ['titulo','descricao','tipo','data_inicio',
        'data_fim','status','permite_branco','criada_por',
        'status_display','total_candidatos','total_aptos']

    def get_total_candidatos(self, obj):
        return obj.candidatos.count()

class CandidatoSerializer(serializers.ModelSerializer):
    eleicao_titulo = serializers.CharField(source=eleicao.titulo, read_only=True)

    class Meta:
        model = Candidato
        fields = ['eleicao','numero','nome','nome_urna',
        'partido_ou_chapa','porposta','foto_url','eleicao_titulo']
    
    def validar_numero(self, value):
        if value == 0:
            raise serializers.ValidationError(
                "Não existe candidato de numero 0, pois é reservado para votos 'branco'"
            )
        return value

class AptidaoEleitorSerializer(serializers.ModelSerializer):
    eleitor_nome = serializers.CharField(source='eleitor.nome', read_only=True)
    eleicao_titulo = serializers.CharField(source='eleicao.titulo', read_only=True)

    class Meta:
        model = AptidaoEleitor
        fields = [ 'eleitor','eleicao','data_inclusao',
        'eleitor_nome', 'eleicao_titulo']

class RegistroVotacaoSerializer(serializers.ModelSerializer):
    eleitor_nome = serializers.CharField(source='eleitor.nome', read_only=True)
    eleicao_titulo = serializers.CharField(source='eleicao.titulo', read_only=True)

    class Meta:
        model = RegistroVotacao
        fields = ['eleitor','eleicao','data_inclusao',
                'eleitor_nome','eleicao_titulo']
        read_only_fields = ['eleitor','eleicao','data_inclusao']

class VotoSerializer(serializers.ModelSerializer):
    candidato_nome_urna = serializers.CharField(source='candidato.nome_urna', read_only=True, allow_null=True)
    em_branco_display = serializers.SerializerMethodField()

    class Meta:
        model = Voto
        fields = ['eleicao', 'candidato','em_branco',
                'data_hora','comprovante_hash','candidato_nome_urna',
                'em_branco_display']
        read_only_fields = fields

    def get_em_branco_display(self, obj):
        return 'BRANCO' if obj.em_branco else None

class VotacaoInputSerializer(serializers.ModelSerializer):
     eleitor_id = serializers.IntegerField()
     eleicao_id = serializers.IntegerField()
     candidato_id = serializers.IntegerField(required=False)
     em_branco = serializers.BooleanField(required=False, default=False)

    def validate(self, data): 

        eleitor_id = data.get('eleitor_id')
        eleicao_id = data.get('eleicao_id')
        candidato_id = data.get('candidato_id')
        em_branco = data.get('em_branco', False)

        try:
            eleicao = Eleicao.objects.get(id=eleicao_id)
        except Eleicao.DoesNotExist:
            raise serializers.ValidationError("A eleição não existe.")
        
        if eleicao.status != 'aberta':
            raise serializers.ValidationError("Eleição não está aberta")
        
        agora = timezone.now()
        if not (eleicao.data_inicio <= agora <= eleicao.data_fim):
            raise serializers.ValidationError("Votação ainda não começou")
        
         if not aptos.objects.filter(eleitor_id=eleitor_id, eleicao_id=eleicao_id).exists():
            raise serializers.ValidationError("Não está apto para votar.")

         if candidato_id:
            try:
                candidato = Candidato.objects.get(id=candidato_id)
                if candidato.eleicao_id != eleicao_id:
                    raise serializers.ValidationError("O candidato não está nessa eleição.")
            
            except Candidato.DoesNotExist:
                raise serializers.ValidationError("O candidato não existe.")
        
        if em_branco and candidato_id:
            raise serializers.ValidationError(
                "Não pode votar em um candidato e em branco ao mesmo tempo."
            )
        if not em_branco and not candidato_id:
            raise serializers.ValidationError(
                "Você deve escolher um candidato ou voto em branco."
            )
        return data