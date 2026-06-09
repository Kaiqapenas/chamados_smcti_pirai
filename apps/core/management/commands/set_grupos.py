from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Define grupos de permissão para um usuário'

    def add_arguments(self, parser):
        parser.add_argument('matricula', type=str, help='Matrícula do usuário')
        parser.add_argument(
            '--administrador',
            action='store_true',
            help='Define como administrador'
        )
        parser.add_argument(
            '--secretario',
            action='store_true',
            help='Define como secretário'
        )
        parser.add_argument(
            '--solicitante',
            action='store_true',
            help='Define como solicitante'
        )
        parser.add_argument(
            '--tecnico',
            action='store_true',
            help='Define como técnico'
        )
        parser.add_argument(
            '--almoxarife',
            action='store_true',
            help='Define como almoxarife'
        )
        parser.add_argument(
            '--remover-todos',
            action='store_true',
            help='Remove todos os grupos do usuário'
        )

    def handle(self, *args, **options):
        matricula = options['matricula']
        
        try:
            user = User.objects.get(matricula=matricula)
        except User.DoesNotExist:
            self.stderr.write(
                f'Erro: Usuário com matrícula {matricula} não encontrado.'
            )
            return

        if options['remover_todos']:
            user.is_administrador = False
            user.is_secretario = False
            user.is_solicitante = False
            user.is_tecnico = False
            user.is_almoxarife = False
            user.save()
            self.stdout.write(
                f'Sucesso: Todos os grupos removidos do usuário {user.first_name} ({matricula})'
            )
            return

        # Define os grupos
        if options['administrador']:
            user.is_administrador = True
        if options['secretario']:
            user.is_secretario = True
        if options['solicitante']:
            user.is_solicitante = True
        if options['tecnico']:
            user.is_tecnico = True
        if options['almoxarife']:
            user.is_almoxarife = True
        
        user.save()
        
        grupos = user.get_grupos()
        if grupos:
            self.stdout.write(
                f'Sucesso: Grupos atualizados para {user.first_name} ({matricula}): {", ".join(grupos)}'
            )
        else:
            self.stdout.write(
                f'Aviso: Nenhum grupo foi definido para {user.first_name} ({matricula})'
            )

# Made with Bob
